"""Replay the first-attempt drafts of a `stress_rag.py --dump` file through the CURRENT repair steps and validator.

No API calls: it answers "how many of the recorded drafts would pass now?" after a validator or repair change.
Usage:  PYTHONPATH=src python scripts/replay_dump.py data/eval/dumps/live6.jsonl
"""

import json
import sys
from collections import Counter
from pathlib import Path

from psi_fire.application.answer_types import Passage, ValidationContext
from psi_fire.application.answer_validation import RuleBasedValidator
from psi_fire.application.answering import (
    clean_identifiers,
    reclassify_breakdown_citations,
    validated_subset,
    with_declared_figures,
    with_figure_citations,
)
from psi_fire.application.explore import LoadExplorer
from psi_fire.domain.answering import Draft
from psi_fire.domain.ranking import RelevanceRanker
from psi_fire.infrastructure.explorer import FileSnapshotProvider
from psi_fire.infrastructure.solution_catalog import JsonSolutionCatalog

sys.path.insert(0, str(Path(__file__).parent))
import stress_rag

ROOT = Path(__file__).resolve().parents[1]


def main(path: str) -> None:
    cases = json.loads((ROOT / "data/eval/stress_cases.json").read_text(encoding="utf-8"))
    scenarios = {s["id"]: s for s in cases["scenarios"]}
    questions = {q["id"]: q for q in cases["questions"]}
    investigations = LoadExplorer(FileSnapshotProvider(ROOT))().investigations
    validator = RuleBasedValidator(JsonSolutionCatalog(ROOT / "data/solutions_catalog.json"))
    before = after = partial = total = 0
    codes: Counter[str] = Counter()
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        run = json.loads(line)
        attempt = run["attempts"][0]
        if not attempt["draft"]:
            continue
        total += 1
        before += not attempt["issues"]
        scenario = stress_rag.scenario_of(scenarios[run["scenario"]])
        question = stress_rag.question_text(questions[run["question"]])
        ranked = {r.investigation.id: r for r in RelevanceRanker().rank(investigations, scenario)}
        shortlist = tuple(ranked[i] for i in attempt["shortlist"])
        passages = tuple(Passage(**p) for p in attempt["passages"])
        draft = with_declared_figures(with_figure_citations(clean_identifiers(reclassify_breakdown_citations(
            Draft.model_validate(attempt["draft"]), shortlist)), shortlist), shortlist, scenario, question)
        issues = validator.validate(draft, ValidationContext(scenario, shortlist, passages, question))
        after += not issues
        if issues:
            subset = validated_subset(draft, issues)
            partial += subset is not None and not validator.validate(subset, ValidationContext(scenario, shortlist, passages, question))
        codes.update({i.code.value for i in issues})
    print(f"first-attempt drafts: {total}; clean when recorded: {before} ({before / total:.0%}); "
          f"clean when replayed now: {after} ({after / total:.0%})")
    print(f"with partial answers (first attempt only): full {after} + partial {partial} = {after + partial} "
          f"({(after + partial) / total:.0%}); still insufficient: {total - after - partial}")
    print("remaining issue codes (drafts affected):", dict(codes.most_common()))


if __name__ == "__main__":
    main(sys.argv[1])
