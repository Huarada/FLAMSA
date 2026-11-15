"""Segment rejected answers by pipeline stage, offline (no API calls), from a `stress_rag.py --dump` file.

Stages: R retrieval (right text existed but was not retrieved), P packaging (payload, schema or prompt gave the model
too little or an ambiguous contract), G generation (the model wrote something unsupported), V validation (the
validator is stricter than the evidence requires: a candidate for tolerance), plus the retry effect (E).
Usage:  PYTHONPATH=src python scripts/attribute_failures.py data/eval/dumps/run.jsonl [--out docs/rag-failure-attribution.md]
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from psi_fire.application.answer_validation import _flat, quote_in, record_values
from psi_fire.application.explore import LoadExplorer
from psi_fire.domain.answering import Citation
from psi_fire.infrastructure.explorer import FileSnapshotProvider
from psi_fire.infrastructure.passage_index import PdfPassageSearch

ROOT = Path(__file__).resolve().parents[1]
STAGES = {"R": "retrieval", "P": "packaging (payload/schema/prompt)", "G": "generation (model)", "V": "validation (tolerance candidate)"}
UNIT_FACTORS = {"fraction x100 (mole fraction vs percent)": 100.0, "kPa to psi": 0.145038, "psi to kPa": 6.894757,
                "atm to psi": 14.6959, "mmHg to psi": 0.0193368}
NEAR = 0.02  # relative closeness when testing unit-conversion explanations


def near(a: float, b: float) -> bool:
    return abs(a - b) <= max(0.05, NEAR * abs(b))


def passage_claims(claim: dict) -> list[Citation]:
    return [Citation(**c) for c in claim["citations"] if c["kind"] == "passage"]


def quote_stage(citation: Citation, attempt: dict, corpus: PdfPassageSearch) -> tuple[str, str]:
    quote = _flat(citation.quote or "")
    cited = [p for p in attempt["passages"] if (p["investigation_id"], p["source_file"], p["locator"]) ==
             (citation.investigation_id, citation.source_file, citation.locator)]
    if not cited:
        return "G", "cited a passage that was not retrieved in this attempt"
    if any(quote_in(quote, _flat(p["text"])) for p in cited):
        return "V", "quote is valid (passes the matcher now)"
    for p in corpus.passages_of(citation.investigation_id):
        if quote_in(quote, _flat(p.text)):
            same_page = p.locator == citation.locator and p.source_file == citation.source_file
            return ("R", "quote exists on the cited page but in a chunk that was not retrieved") if same_page else \
                ("G", f"quote exists elsewhere ({p.locator}); the locator is wrong")
    squeezed = re.sub(r"\W+", "", quote)
    if any(squeezed and squeezed in re.sub(r"\W+", "", _flat(p["text"])) for p in cited):
        return "V", "differs only by punctuation or spacing"
    return "G", "text not found anywhere in the investigation's documents (paraphrase or invention)"


def number_stage(value: float, claim: dict, shortlist: list[dict], inv_points: dict) -> tuple[str, str]:
    cited_ids = {c["investigation_id"] for c in claim["citations"]}
    quotes = " ".join(c.get("quote") or "" for c in claim["citations"])
    if re.search(rf"(?<![\w.]){re.escape(f'{value:g}')}(?![\w])", quotes):
        return "V", "the number appears in a cited quote (verbatim from the document)"
    pages = [float(d) for c in claim["citations"] if c.get("locator") for d in re.findall(r"\d+", c["locator"])]
    if value in pages:
        return "V", "a page number from a citation locator"
    for item in shortlist:
        if item["id"] in inv_points and any(near(value, v) for p in inv_points[item["id"]] for _, v, _ in record_values(p)):
            return ("G", "value of an uncited record of a cited investigation") if item["id"] in cited_ids else \
                ("G", "value of a record of an investigation the claim does not cite")
    return "G", "not a known fact (model-stated or derived)"


def mismatch_stage(message: str, claim: dict, inv_points: dict) -> tuple[str, str]:
    match = re.search(r"([a-z_0-9]+) ([0-9.]+) differs from the record", message)
    if not match:
        return "G", "figure disagrees with the computed breakdown or the record"
    value = float(match.group(2))
    inv_id = next((f["investigation_id"] for f in claim["figures"] if f["column"] == match.group(1)), None)
    for p in inv_points.get(inv_id, ()):
        if any(near(value, v) for _, v, _ in record_values(p)):
            return "G", "value belongs to a different record of the same investigation"
    for label, factor in UNIT_FACTORS.items():
        for p in inv_points.get(inv_id, ()):
            if any(near(value, v * factor) or near(value * factor, v) for _, v, _ in record_values(p)):
                return "P", f"looks like a unit confusion: {label}"
    return "G", "value matches no record of the investigation"


def citation_stage(message: str, claim: dict, inv_points: dict, presented: dict) -> tuple[str, str]:
    missing = re.search(r"has no test point (\S+)\.", message)
    if missing:
        return "G", "cited a test point that does not exist"
    if "not in the retrieved shortlist" in message:
        return "G", "cited an investigation outside the shortlist"
    if "not retrieved in this attempt" in message:
        return "G", "cited a passage that was not retrieved"
    if "no record citation for it" in message or "needs the test_point_id" in message:
        return "G", "record figure without its record citation"
    return "G", message[:80]


def analyse(dump: list[dict]) -> str:
    investigations = LoadExplorer(FileSnapshotProvider(ROOT))().investigations
    points = {i.id: i.test_points for i in investigations}
    corpus = PdfPassageSearch(ROOT, ROOT / "data/rag_corpus.json", ROOT / "data/rag_index/passages.json")
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    notes: dict[tuple[str, str, str], int] = Counter()
    examples: dict[tuple[str, str, str], str] = {}
    first_fail = second_ok = 0
    claims_total = claims_failed = 0
    for run in dump:
        attempts = run["attempts"]
        if attempts and attempts[0]["issues"]:
            first_fail += 1
            second_ok += len(attempts) > 1 and run["status"] == "approved"
        for attempt in attempts[:1]:  # first attempt: the model's unassisted behaviour
            draft = attempt["draft"]
            if not draft:
                continue
            shortlist = [{"id": i} for i in attempt["shortlist"]]
            claims_total += len(draft["claims"])
            claims_failed += len({i["claim_index"] for i in attempt["issues"] if i["claim_index"] is not None})
            for issue in attempt["issues"]:
                code, index = issue["code"], issue["claim_index"]
                claim = draft["claims"][index] if index is not None else {"citations": [], "figures": [], "text": ""}
                if code == "quote_mismatch":
                    results = [quote_stage(c, attempt, corpus) for c in passage_claims(claim)]
                    stage, why = next(((s, w) for s, w in results if s != "V"), results[0] if results else ("G", "?"))
                elif code == "undeclared_number":
                    m = re.search(r"number ([0-9.]+)", issue["message"])
                    stage, why = number_stage(float(m.group(1)), claim, shortlist, points) if m else ("G", "?")
                elif code == "number_mismatch":
                    stage, why = mismatch_stage(issue["message"], claim, points)
                elif code == "malformed_citation":
                    stage, why = "P", "the flat citation schema allowed an incomplete or unsupported citation"
                elif code == "unknown_citation":
                    stage, why = citation_stage(issue["message"], claim, points, {})
                elif code == "empty_draft":
                    stage, why = "P", "no claims returned"
                else:
                    stage, why = "G", code
                counts[code][stage] += 1
                notes[(code, stage, why)] += 1
                examples.setdefault((code, stage, why), " ".join(claim.get("text", "").split())[:200] or issue["message"][:200])
    lines = ["# RAG failure attribution (first attempt, offline)", "",
             (f"Runs analysed: {len(dump)}. First-attempt claims: {claims_total}; with an issue: {claims_failed} "
              f"({claims_failed / max(claims_total, 1):.2f}). Runs whose first attempt had issues: {first_fail}; "
              f"approved after the retry: {second_ok} ({second_ok / max(first_fail, 1):.2f})."), "",
             "## Issues by code and stage", "", "| Code | " + " | ".join(f"{k} {v}" for k, v in STAGES.items()) + " | Total |",
             "|---|" + "---|" * (len(STAGES) + 1)]
    for code, by in sorted(counts.items(), key=lambda kv: -sum(kv[1].values())):
        lines.append(f"| {code} | " + " | ".join(str(by.get(s, 0)) for s in STAGES) + f" | {sum(by.values())} |")
    lines += ["", "## Root-cause breakdown", ""]
    for (code, stage, why), n in notes.most_common(40):
        lines += [f"- **{code} / {stage}** x{n}: {why}", f"  - e.g. {examples[(code, stage, why)]}"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dump")
    parser.add_argument("--out", default="docs/rag-failure-attribution.md")
    args = parser.parse_args()
    rows = [json.loads(line) for line in (ROOT / args.dump).read_text(encoding="utf-8").splitlines() if line.strip()]
    text = analyse(rows)
    (ROOT / args.out).write_text(text, encoding="utf-8")
    print(text.split("## Root-cause breakdown")[0])
    sys.exit(0)
