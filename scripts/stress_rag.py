"""Stress test of the answering pipeline (retrieval + ranking + validation) over a scenario x question matrix.

Offline by default (template narrator, no cost). `--live` uses the model configured in .env (paid API calls).
Writes a markdown report; exits 1 when a hard invariant fails. Usage:
    PYTHONPATH=src python scripts/stress_rag.py [--live] [--max-live N] [--scenarios id,id] [--out path]
"""

import argparse
import json
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from psi_fire.application.answer_types import AnswerResult, AnswerStatus
from psi_fire.application.explore import LoadExplorer
from psi_fire.domain.manual import GravityRegime
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario, RelevanceRanker
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
    if result.status == AnswerStatus.APPROVED:
        ids = {r.investigation.id for r in result.shortlist}
        if not result.draft or not result.draft.claims:
            problems.append("approved without claims")
        elif any(not c.citations for c in result.draft.claims):
            problems.append("approved claim without citation")
        elif any(c.investigation_id not in ids for claim in result.draft.claims for c in claim.citations):
            problems.append("citation outside the shortlist")
        if not result.traceability or any(not e.source_file or not e.locator for e in result.traceability):
            problems.append("citation without source file or locator")
    elif result.draft is not None:
        problems.append("rejected answer still exposes a draft")
    if scenario_spec.get("expect_extrapolation") and not any(
            "extrapolation" in n or "cannot be compared" in n for n in result.limitations):
        problems.append("extrapolated scenario without an extrapolation limitation")
    return problems


def one_run(pipeline: AnsweringPipeline, investigations: tuple[Investigation, ...], scenario_spec: dict,
            question_spec: dict, report: Report) -> AnswerResult | None:
    label = f"{scenario_spec['id']} x {question_spec['id']}"
    run = Run(scenario_spec["id"], question_spec["id"])
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
               scenario_ids: set[str] | None = None, max_runs: int | None = None) -> Report:
    report = Report()
    scenarios = [s for s in cases["scenarios"] if not scenario_ids or s["id"] in scenario_ids]
    for scenario in scenarios:
        for question in cases["questions"]:
            if max_runs is not None and len(report.runs) >= max_runs:
                break
            one_run(pipeline, investigations, scenario, question, report)
    cross_checks(report, scenarios, investigations)
    determinism_check(pipeline, investigations, scenarios[:3] if max_runs else scenarios, cases["questions"][0], report)
    return report


def render(report: Report, cases: dict, label: str) -> str:
    lines = ["# RAG stress report", "", (f"Narrator: **{label}**. Runs: {len(report.runs)}. "
             f"Hard failures: **{len(report.failures)}**. Warnings: {len(report.warnings)}."), "",
             "## Per scenario", "", "| Scenario | Runs | Approved | Insufficient | Avg passages | Avg seconds |", "|---|---|---|---|---|---|"]
    for s in cases["scenarios"]:
        runs = [r for r in report.runs if r.scenario == s["id"]]
        if not runs:
            continue
        live = [r for r in runs if r.status in {"approved", "insufficient_evidence"}]
        lines.append(f"| {s['id']} ({s['o2']:g}% / {s['psi']:g} psi) | {len(runs)} | "
                     f"{sum(r.status == 'approved' for r in runs)} | {sum(r.status == 'insufficient_evidence' for r in runs)} | "
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
    lines += ["", "## Retrieved passages for the regions you asked about", ""]
    for r in report.runs:
        if r.scenario in SAMPLE_SCENARIOS and r.question in {"rank_default", "rag_flame_spread", "rag_droplet", "rag_co2"}:
            lines += [f"**{r.scenario} / {r.question}** ({r.status}; ranking {', '.join(i for i, _ in r.shortlist)})"]
            lines += [f"- {p}" for p in r.top_passages] or ["- no passages"]
            lines += [""]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="use the model from .env (paid API calls)")
    parser.add_argument("--max-live", type=int, default=60, help="cap on runs when --live")
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
                        args.max_live if args.live else None)
    text = render(report, cases, pipeline.narrator_label)
    (ROOT / args.out).write_text(text, encoding="utf-8")
    print(text.split("## Per scenario")[0])
    print(f"Report written to {args.out}")
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
