"""Why do passage quotes fail validation? Reruns the runs of a stress report that had `quote_mismatch` (paid, uses .env)
and classifies every rejected quote against the passage it cites. Usage:
    PYTHONPATH=src python scripts/diagnose_quotes.py docs/rag-stress-report-live3.md
"""

import difflib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from psi_fire.application.answer_validation import _flat
from psi_fire.application.explore import LoadExplorer
from psi_fire.domain.answering import CitationKind, IssueCode
from psi_fire.infrastructure.answering_factory import build_answering_pipeline
from psi_fire.infrastructure.explorer import FileSnapshotProvider

sys.path.insert(0, str(Path(__file__).parent))
import stress_rag

ROOT = Path(__file__).resolve().parents[1]
NEAR_EXACT = 0.9  # share of the quote found as one contiguous block of the passage


def classify(quote: str, passage_text: str) -> tuple[str, float]:
    q, p = _flat(quote), _flat(passage_text)
    block = difflib.SequenceMatcher(None, q, p, autojunk=False).find_longest_match(0, len(q), 0, len(p))
    share = block.size / max(len(q), 1)
    return ("near-exact (formatting)" if share >= NEAR_EXACT else "paraphrase or merged sentences"), share


def main(report: str) -> None:
    load_dotenv(ROOT / ".env")
    cases = json.loads((ROOT / "data/eval/stress_cases.json").read_text(encoding="utf-8"))
    scenarios = {s["id"]: s for s in cases["scenarios"]}
    questions = {q["id"]: q for q in cases["questions"]}
    wanted = re.findall(r"^- (\S+) / (\S+): .*quote_mismatch", (ROOT / report).read_text(encoding="utf-8"), re.MULTILINE)
    pipeline = build_answering_pipeline(ROOT, dict(os.environ))
    investigations = LoadExplorer(FileSnapshotProvider(ROOT))().investigations
    kinds: Counter[str] = Counter()
    examples: list[str] = []
    for scenario_id, question_id in wanted:
        result = pipeline.answerer(investigations, stress_rag.scenario_of(scenarios[scenario_id]),
                                   stress_rag.question_text(questions[question_id]))
        for attempt in result.attempts:
            if not attempt.draft or not any(i.code == IssueCode.QUOTE_MISMATCH for i in attempt.issues):
                continue
            for claim in attempt.draft.claims:
                for c in (c for c in claim.citations if c.kind == CitationKind.PASSAGE and c.quote):
                    page = [p for p in attempt.passages if (p.investigation_id, p.source_file, p.locator) ==
                            (c.investigation_id, c.source_file, c.locator)]
                    if not page or _flat(c.quote) in _flat(page[0].text):
                        continue
                    kind, share = classify(c.quote, page[0].text)
                    kinds[kind] += 1
                    if len(examples) < 8:
                        examples.append(f"[{kind}, {share:.2f}] {scenario_id}/{question_id} {c.investigation_id} {c.locator}\n"
                                        f"  quote:   {c.quote[:180]!r}\n  passage: {' '.join(page[0].text.split())[:180]!r}")
    print(f"reran {len(wanted)} runs; rejected quotes by kind: {dict(kinds)}")
    print("\n".join(examples))


if __name__ == "__main__":
    main(sys.argv[1])
