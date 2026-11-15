"""Stress test of the answering pipeline (retrieval + ranking + validation) over a scenario x question matrix.

Offline by default (template narrator, no cost). `--live` uses the model configured in .env (paid API calls).
Writes a markdown report; exits 1 when a hard invariant fails. Usage:
    PYTHONPATH=src python scripts/stress_rag.py [--live] [--max-live N] [--scenarios id,id] [--out path]
"""

import argparse
import json
import os
import re
import statistics
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from psi_fire.application.answer_types import AnswerResult, AnswerStatus
from psi_fire.application.answer_validation import record_values, system_facts
from psi_fire.application.explore import LoadExplorer
from psi_fire.domain.answering import Claim, IssueCode
from psi_fire.domain.manual import GravityRegime
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario, RankedInvestigation, RelevanceRanker
from psi_fire.infrastructure.answering_factory import AnsweringPipeline, build_answering_pipeline
from psi_fire.infrastructure.explorer import FileSnapshotProvider

ROOT = Path(__file__).resolve().parents[1]
SLOW_SECONDS = 10.0       # offline runs should be instant; slower means retrieval regressed
MIN_HIT_RATE = 0.3        # share of retrieved passages that contain an expected term; below it is a WARN
SAMPLE_SCENARIOS = ("user_o2_38078", "lunar_standard", "user_o2_15_psi_14")  # shown with passages in the report


@dataclass
class Run:
    scenario: str
    question: str
    status: str = "n/a"
    attempts: int = 0
    passages: int = 0
    hit_rate: float | None = None
    claims: int = 0
    citations: int = 0
    seconds: float = 0.0
    issue_codes: tuple[str, ...] = ()
    shortlist: tuple[tuple[str, float], ...] = ()
    top_passages: tuple[str, ...] = ()
    round: int = 0
    raw: dict | None = None  # everything needed to re-analyse this run offline (scripts/attribute_failures.py)
    claim_stats: tuple[tuple[int, int, int], ...] = ()  # (attempt, claims in draft, claims with an issue)
    undeclared: tuple[tuple[str, str, str], ...] = ()  # (number, explanation, sentence) of the final rejection


@dataclass
class Report:
    runs: list[Run] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def scenario_of(spec: dict) -> HabitatScenario:
    return HabitatScenario(spec["name"], spec["o2"], spec["psi"], GravityRegime(spec["gravity"]))


def question_text(spec: dict) -> str:
    return spec["text"] * spec.get("repeat", 1)


def hit_rate(result: AnswerResult, terms: list[str]) -> float | None:
    passages = result.attempts[0].passages if result.attempts else ()
    if not terms or not passages:
        return None
    return sum(any(t in p.text.casefold() for t in terms) for p in passages) / len(passages)


def invariant_failures(result: AnswerResult, scenario_spec: dict) -> list[str]:
    problems = []
    if not result.limitations:
        problems.append("no limitations shown")
    if result.shortlist and not result.breakdown_text:
        problems.append("no deterministic breakdown")
    if result.status in (AnswerStatus.APPROVED, AnswerStatus.PARTIAL):
        ids = {r.investigation.id for r in result.shortlist}
        if not result.draft or not result.draft.claims:
            problems.append("approved without claims")
        elif any(not c.citations for c in result.draft.claims):
            problems.append("approved claim without citation")
        elif any(c.investigation_id not in ids for claim in result.draft.claims for c in claim.citations):
            problems.append("citation outside the shortlist")
        if not result.traceability or any((not e.source_file or not e.locator) and e.citation.kind.value != "breakdown"
                                         for e in result.traceability):
            problems.append("citation without source file or locator")
        if result.status == AnswerStatus.PARTIAL and not (
                0 < result.claims_withheld < result.claims_total and len(result.draft.claims) == result.claims_total - result.claims_withheld):
            problems.append("partial answer with inconsistent claim counts")
    elif result.draft is not None:
        problems.append("rejected answer still exposes a draft")
    if scenario_spec.get("expect_extrapolation") and not any(
            "extrapolation" in n or "cannot be compared" in n for n in result.limitations):
        problems.append("extrapolated scenario without an extrapolation limitation")
    return problems


_NUMBER_IN_MESSAGE = re.compile(r"number ([0-9.]+)")
NEAR_REL, NEAR_ABS = 0.01, 0.05


def _near(a: float, b: float) -> bool:
    return abs(a - b) <= max(NEAR_ABS, NEAR_REL * abs(b))


def explain_number(number: float, claim: Claim, shortlist: tuple[RankedInvestigation, ...]) -> str:
    """Where the digits probably came from, to decide which tolerance (if any) would be honest."""
    cited = {c.investigation_id for c in claim.citations}
    for item in shortlist:
        exact, scores = system_facts(item)
        if any(_near(number, v) for v in exact) or any(abs(number - v) <= 0.005 for v in scores):
            return ("system fact of a cited investigation" if item.investigation.id in cited
                    else "system fact of an UNCITED investigation")
    for item in (i for i in shortlist if i.investigation.id in cited):
        if any(_near(number, v) for p in item.investigation.test_points for _, v, _ in record_values(p)):
            return "value of an uncited record of a cited investigation"
    pages = [float(d) for c in claim.citations if c.locator for d in re.findall(r"\d+", c.locator)]
    if number in pages:
        return "page number from a citation locator"
    return "not a known fact (model-stated)"


def undeclared_details(result: AnswerResult) -> tuple[tuple[str, str, str], ...]:
    draft = result.attempts[-1].draft if result.attempts else None
    if draft is None:
        return ()
    details = []
    for issue in result.issues:
        match = _NUMBER_IN_MESSAGE.search(issue.message)
        if issue.code == IssueCode.UNDECLARED_NUMBER and match and issue.claim_index is not None:
            claim = draft.claims[issue.claim_index]
            number = float(match.group(1))
            details.append((match.group(1), explain_number(number, claim, result.shortlist),
                            " ".join(claim.text.split())))
    return tuple(details)


def raw_record(scenario_spec: dict, question_spec: dict, round_index: int, result: AnswerResult) -> dict:
    """Drafts, issues and retrieved passages of every attempt, so a root cause can be segmented without new API calls."""
    return {
        "scenario": scenario_spec["id"], "question": question_spec["id"], "round": round_index,
        "status": result.status.value, "scenario_values": [scenario_spec["o2"], scenario_spec["psi"]],
        "shortlist": [r.investigation.id for r in result.shortlist],
        "attempts": [{
            "attempt": a.attempt, "shortlist": list(a.shortlist_ids),
            "issues": [{"code": i.code.value, "message": i.message, "claim_index": i.claim_index} for i in a.issues],
            "draft": a.draft.model_dump(mode="json") if a.draft else None,
            "passages": [{"investigation_id": p.investigation_id, "source_file": p.source_file,
                          "locator": p.locator, "text": p.text} for p in a.passages],
        } for a in result.attempts],
    }


def one_run(pipeline: AnsweringPipeline, investigations: tuple[Investigation, ...], scenario_spec: dict,
            question_spec: dict, report: Report, round_index: int = 0) -> AnswerResult | None:
    label = f"{scenario_spec['id']} x {question_spec['id']}"
    run = Run(scenario_spec["id"], question_spec["id"], round=round_index)
    report.runs.append(run)
    try:
        scenario = scenario_of(scenario_spec)
    except ValueError:
        run.status = "rejected-input"
        if not scenario_spec.get("expect_rejected"):
            report.failures.append(f"{label}: valid scenario was rejected")
        return None
    if scenario_spec.get("expect_rejected"):
        report.failures.append(f"{label}: invalid scenario was accepted")
    started = time.perf_counter()
    try:
        result = pipeline.answerer(investigations, scenario, question_text(question_spec))
    except Exception as error:  # noqa: BLE001 - any crash is a stress-test finding, not something to hide
        run.status = "CRASH"
        report.failures.append(f"{label}: unhandled {type(error).__name__}: {error}")
        return None
    run.seconds = time.perf_counter() - started
    run.status, run.attempts = result.status.value, len(result.attempts)
    run.issue_codes = tuple(sorted({i.code.value for i in result.issues}))
    run.undeclared = undeclared_details(result)
    run.raw = raw_record(scenario_spec, question_spec, round_index, result)
    run.claim_stats = tuple(
        (a.attempt, len(a.draft.claims) if a.draft else 0, len({i.claim_index for i in a.issues if i.claim_index is not None}))
        for a in result.attempts)
    run.shortlist = tuple((r.investigation.id, round(r.score, 6)) for r in result.shortlist)
    first = result.attempts[0].passages if result.attempts else ()
    run.passages = len(first)
    run.top_passages = tuple(f"{p.investigation_id} {p.locator}: {' '.join(p.text.split())[:110]}" for p in first[:4])
    run.hit_rate = hit_rate(result, [t.casefold() for t in question_spec.get("expect_terms", [])])
    if result.draft:
        run.claims, run.citations = len(result.draft.claims), sum(len(c.citations) for c in result.draft.claims)
    report.failures += [f"{label}: {p}" for p in invariant_failures(result, scenario_spec)]
    if run.seconds > SLOW_SECONDS and pipeline.narrator_label.startswith("Template"):
        report.warnings.append(f"{label}: slow offline run ({run.seconds:.1f}s)")
    if run.hit_rate is not None and run.hit_rate < MIN_HIT_RATE:
        report.warnings.append(f"{label}: low retrieval relevance (hit rate {run.hit_rate:.2f}, {run.passages} passages)")
    if question_spec.get("expect_terms") and result.shortlist and run.passages == 0:
        report.warnings.append(f"{label}: retrieval returned nothing")
    return result


def cross_checks(report: Report, scenarios: list[dict], investigations: tuple[Investigation, ...]) -> None:
    """Scores must be exactly the domain ranker's for the scenario, whatever the question or retry (a retry only
    widens the shortlist, so compare per investigation, not the whole list)."""
    for scenario in (s for s in scenarios if not s.get("expect_rejected")):
        expected = {r.investigation.id: round(r.score, 6) for r in RelevanceRanker().rank(investigations, scenario_of(scenario))}
        for run in (r for r in report.runs if r.scenario == scenario["id"] and r.shortlist):
            scores = [s for _, s in run.shortlist]
            if any(expected.get(i) != s for i, s in run.shortlist) or scores != sorted(scores, reverse=True):
                report.failures.append(f"{run.scenario} x {run.question}: shortlist scores differ from the domain ranking")


def determinism_check(pipeline: AnsweringPipeline, investigations: tuple[Investigation, ...], scenarios: list[dict],
                      question: dict, report: Report) -> None:
    for spec in (s for s in scenarios if not s.get("expect_rejected")):
        scenario, text = scenario_of(spec), question_text(question)
        first = pipeline.answerer(investigations, scenario, text)
        second = pipeline.answerer(investigations, scenario, text)
        # attempt 1 always uses the strict settings, so it is comparable even if a model retried in only one run
        if first.attempts and second.attempts and (
                first.attempts[0].shortlist_ids != second.attempts[0].shortlist_ids
                or first.attempts[0].passages != second.attempts[0].passages):
            report.failures.append(f"{spec['id']}: first-attempt shortlist or retrieved passages are not deterministic")


def run_matrix(pipeline: AnsweringPipeline, investigations: tuple[Investigation, ...], cases: dict,
               scenario_ids: set[str] | None = None, max_runs: int | None = None, repeats: int = 1,
               workers: int = 1) -> Report:
    report = Report()
    scenarios = [s for s in cases["scenarios"] if not scenario_ids or s["id"] in scenario_ids]
    tasks = [(s, q, r) for r in range(repeats) for s in scenarios for q in cases["questions"]]
    if max_runs is not None:
        tasks = tasks[:max_runs]

    def execute(task: tuple[dict, dict, int]) -> Report:
        local = Report()
        one_run(pipeline, investigations, task[0], task[1], local, task[2])
        return local

    if tasks:
        results = [execute(tasks[0])]  # first alone: warms the passage cache before threads share it
        if workers > 1:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                results += list(pool.map(execute, tasks[1:]))
        else:
            results += [execute(task) for task in tasks[1:]]
        for local in results:
            report.runs += local.runs
            report.failures += local.failures
            report.warnings += local.warnings
    cross_checks(report, scenarios, investigations)
    determinism_check(pipeline, investigations, scenarios[:3] if max_runs else scenarios, cases["questions"][0], report)
    return report


def variance_section(report: Report) -> list[str]:
    rounds = sorted({r.round for r in report.runs})
    if len(rounds) < 2:
        return []
    per_round = [sum(r.status in {"approved", "partial"} for r in report.runs if r.round == k) for k in rounds]
    cells: dict[tuple[str, str], list[str]] = {}
    for r in report.runs:
        if r.status in {"approved", "partial", "insufficient_evidence"}:
            cells.setdefault((r.scenario, r.question), []).append(r.status)
    always = [c for c, s in cells.items() if all(x != "insufficient_evidence" for x in s)]
    never = [c for c, s in cells.items() if all(x == "insufficient_evidence" for x in s)]
    mixed = [c for c in cells if c not in always and c not in never]
    lines = ["", "## Variance across repeated rounds", "",
             (f"Answered (full or partial) per round: {per_round} (mean {statistics.mean(per_round):.1f}, "
              f"std {statistics.pstdev(per_round):.1f})."), "",
             (f"Cells always approved: {len(always)}; never approved: {len(never)}; "
              f"mixed (same input, different outcome): {len(mixed)}."), ""]
    lines += [f"- mixed: {s} / {q}: {len(cells[(s, q)]) - cells[(s, q)].count('insufficient_evidence')} of {len(cells[(s, q)])} answered"
              for s, q in sorted(mixed)]
    return lines


def attempts_section(report: Report) -> list[str]:
    """Is the failure per claim or per answer, and does the retry repair anything?"""
    live = [r for r in report.runs if r.claim_stats]
    if not live:
        return []
    first = [r.claim_stats[0] for r in live if r.claim_stats[0][1] > 0]
    claims, failing = sum(c for _, c, _ in first), sum(f for _, _, f in first)
    p = failing / max(claims, 1)
    mean_claims = claims / max(len(first), 1)
    observed = sum(1 for _, _, f in first if f > 0) / max(len(first), 1)
    retried = [r for r in live if len(r.claim_stats) > 1]
    recovered = [r for r in retried if r.status in {"approved", "partial"}]
    return ["", "## Claim-level versus answer-level failure (first attempt)", "",
            (f"Drafts: {len(first)}; mean claims per draft {mean_claims:.1f}; claims with an issue {failing} of "
             f"{claims} (per-claim failure rate {p:.2f})."),
            (f"Answers with at least one failing claim: {observed:.2f}. If claims failed independently at that rate, "
             f"the expected answer failure would be {1 - (1 - p) ** mean_claims:.2f}."),
            (f"Runs that needed a second attempt: {len(retried)}; of those approved after the retry: "
             f"{len(recovered)} ({len(recovered) / max(len(retried), 1):.2f}).")]


def undeclared_section(report: Report) -> list[str]:
    items = [(n, why, sentence) for r in report.runs for n, why, sentence in r.undeclared]
    if not items:
        return []
    lines = ["", "## Numbers behind `undeclared_number` (final rejection of each run)", "",
             "| Explanation | Count |", "|---|---|"]
    lines += [f"| {why} | {n} |" for why, n in Counter(w for _, w, _ in items).most_common()]
    lines += ["", "Most frequent values:", ""]
    lines += [f"- {value}: {n}" for value, n in Counter(v for v, _, _ in items).most_common(12)]
    lines += ["", "Examples (number | explanation | sentence):", ""]
    seen: set[tuple[str, str]] = set()
    for number, why, sentence in items:
        if (number, why) not in seen and len(seen) < 30:
            seen.add((number, why))
            lines.append(f"- {number} | {why} | {sentence[:230]}")
    return lines


def render(report: Report, cases: dict, label: str) -> str:
    lines = ["# RAG stress report", "", (f"Narrator: **{label}**. Runs: {len(report.runs)}. "
             f"Hard failures: **{len(report.failures)}**. Warnings: {len(report.warnings)}."), "",
             "## Per scenario", "", "| Scenario | Runs | Approved (full) | Partial | Insufficient | Avg passages | Avg seconds |", "|---|---|---|---|---|---|---|"]
    for s in cases["scenarios"]:
        runs = [r for r in report.runs if r.scenario == s["id"]]
        if not runs:
            continue
        live = [r for r in runs if r.status in {"approved", "insufficient_evidence"}]
        lines.append(f"| {s['id']} ({s['o2']:g}% / {s['psi']:g} psi) | {len(runs)} | "
                     f"{sum(r.status == 'approved' for r in runs)} | {sum(r.status == 'partial' for r in runs)} | "
                     f"{sum(r.status == 'insufficient_evidence' for r in runs)} | "
                     f"{sum(r.passages for r in live) / max(len(live), 1):.1f} | "
                     f"{sum(r.seconds for r in live) / max(len(live), 1):.2f} |")
    lines += ["", "## Per question (retrieval relevance proxy)", "", "| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |",
              "|---|---|---|---|---|---|"]
    for q in cases["questions"]:
        runs = [r for r in report.runs if r.question == q["id"] and r.status != "rejected-input"]
        if not runs:
            continue
        hits = [r.hit_rate for r in runs if r.hit_rate is not None]
        lines.append(f"| {q['id']} | {q['category']} | {len(runs)} | {sum(r.passages for r in runs) / len(runs):.1f} | "
                     f"{(f'{sum(hits) / len(hits):.2f}' if hits else 'n/a')} | "
                     f"{sum(r.status == 'insufficient_evidence' for r in runs)} |")
    lines += ["", "## Hard failures", ""] + ([f"- {f}" for f in report.failures] or ["None."])
    lines += ["", "## Warnings", ""] + ([f"- {w}" for w in report.warnings] or ["None."])
    counts = Counter(code for r in report.runs for code in r.issue_codes)
    lines += ["", "## Validator issue codes in rejected runs (runs affected)", ""] + (
        [f"- {code}: {n}" for code, n in counts.most_common()] or ["None."])
    rejected = [r for r in report.runs if r.status == "insufficient_evidence"]
    lines += ["", "## Rejected runs (scenario / question: codes)", ""] + (
        [f"- {r.scenario} / {r.question}: {', '.join(r.issue_codes)}" for r in rejected] or ["None."])
    lines += variance_section(report) + attempts_section(report) + undeclared_section(report)
    lines += ["", "## Retrieved passages for the regions you asked about", ""]
    for r in (r for r in report.runs if r.round == 0):
        if r.scenario in SAMPLE_SCENARIOS and r.question in {"rank_default", "rag_flame_spread", "rag_droplet", "rag_co2"}:
            lines += [f"**{r.scenario} / {r.question}** ({r.status}; ranking {', '.join(i for i, _ in r.shortlist)})"]
            lines += [f"- {p}" for p in r.top_passages] or ["- no passages"]
            lines += [""]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="use the model from .env (paid API calls)")
    parser.add_argument("--max-live", type=int, default=60, help="cap on runs when --live")
    parser.add_argument("--repeats", type=int, default=1, help="rounds of the whole matrix, to measure model variance")
    parser.add_argument("--workers", type=int, default=1, help="parallel calls (use 6-8 with --live)")
    parser.add_argument("--dump", default="", help="write every run's drafts, issues and passages to this JSONL file")
    parser.add_argument("--scenarios", default="", help="comma-separated scenario ids")
    parser.add_argument("--out", default="docs/rag-stress-report.md")
    args = parser.parse_args()
    cases = json.loads((ROOT / "data/eval/stress_cases.json").read_text(encoding="utf-8"))
    env: dict[str, str] = {}
    if args.live:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
        env = dict(os.environ)
    pipeline = build_answering_pipeline(ROOT, env)
    investigations = LoadExplorer(FileSnapshotProvider(ROOT))().investigations
    report = run_matrix(pipeline, investigations, cases, set(filter(None, args.scenarios.split(","))) or None,
                        args.max_live if args.live else None, args.repeats, args.workers)
    if args.dump:
        dump = ROOT / args.dump
        dump.parent.mkdir(parents=True, exist_ok=True)
        dump.write_text("\n".join(json.dumps(r.raw) for r in report.runs if r.raw) + "\n", encoding="utf-8")
    text = render(report, cases, pipeline.narrator_label)
    (ROOT / args.out).write_text(text, encoding="utf-8")
    print(text.split("## Per scenario")[0])
    print(f"Report written to {args.out}")
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
