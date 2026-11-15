from pathlib import Path

import pytest

from psi_fire.application.explore import LoadExplorer
from psi_fire.domain.answering import Citation, CitationKind, Claim, numbers_in
from psi_fire.domain.ranking import (
    DEFAULT_CRITERIA,
    LUNAR_BASE,
    HabitatScenario,
    RelevanceRanker,
    limitations,
)
from psi_fire.infrastructure.explorer import FileSnapshotProvider

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def investigations():
    return LoadExplorer(FileSnapshotProvider(ROOT))().investigations


def test_weights_sum_to_one_and_other_sums_are_rejected():
    assert sum(c.weight for c in DEFAULT_CRITERIA) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        RelevanceRanker(DEFAULT_CRITERIA[:2])


def test_ranking_is_deterministic_independent_of_input_order_and_scores_are_bounded(investigations):
    ranker = RelevanceRanker()
    forward = ranker.rank(investigations, LUNAR_BASE)
    backward = ranker.rank(tuple(reversed(investigations)), LUNAR_BASE)
    assert [(r.investigation.id, r.score) for r in forward] == [(r.investigation.id, r.score) for r in backward]
    assert [r.rank for r in forward] == list(range(1, len(forward) + 1))
    assert all(0 <= r.score <= 1 for r in forward)
    top = forward[0]
    assert top.score == pytest.approx(sum(s.contribution for s in top.breakdown.scores), abs=1e-3)
    assert all(s.evidence for s in top.breakdown.scores if s.criterion == "oxygen_proximity" and s.value > 0)


def test_a_scenario_inside_the_tested_range_scores_full_oxygen_proximity(investigations):
    flex = next(i for i in investigations if i.id == "FLEX")
    inside = HabitatScenario("Inside", 25.0, 20.0)
    score = next(s for s in RelevanceRanker().rank((flex,), inside)[0].breakdown.scores
                 if s.criterion == "oxygen_proximity")
    assert score.value == 1.0 and "inside the tested range" in score.rationale


def test_limitations_flag_partial_gravity_extrapolation_and_oxidizer_stream_oxygen(investigations):
    ranked = RelevanceRanker().rank(investigations, LUNAR_BASE)
    notes = limitations(LUNAR_BASE, ranked)
    assert any("no partial-gravity data" in n for n in notes)
    assert any("outside the tested range" in n for n in notes)
    assert any("oxidizer" in n and "ACME-CFI-G" in n for n in notes)
    assert not any("partial" in n for n in limitations(HabitatScenario("Earth", 21, 14.7), ranked))


@pytest.mark.parametrize("o2, psi", [(-1, 10), (101, 10), (30, -0.1)])
def test_invalid_scenarios_are_rejected(o2, psi):
    with pytest.raises(ValueError):
        HabitatScenario("bad", o2, psi)


def test_numbers_in_ignores_ids_and_bracketed_citations():
    assert numbers_in("[PSI-26] and BASS-II at 30.5 percent, O2 and 10 psi") == (30.5, 10.0)
    claim = Claim(text="x", citations=(Citation(kind=CitationKind.METADATA, investigation_id="A", field="pillars"),))
    assert claim.figures == ()
