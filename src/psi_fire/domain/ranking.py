"""Deterministic relevance ranking of investigations for a habitat scenario (ADR-0004, SPEC-003).

The score is a weighted sum of criteria in [0, 1]. Nothing here calls an LLM: the narrator only
describes a ScoreBreakdown that this module computed.
"""

from dataclasses import dataclass
from typing import Protocol

from psi_fire.domain.manual import FireSafetyPillar, GravityRegime
from psi_fire.domain.model import FuelPhase, Investigation, O2Basis, ProvenanceStatus, RecordLevel, TestPoint

# Demonstration scenario shared with the Dashboard coverage map (single source of the numbers).
LUNAR_O2_PERCENT = 30.0
LUNAR_PRESSURE_PSI = 10.2

# Criterion weights (sum to 1). Changing one is a DECISION in the ADR.
WEIGHT_OXYGEN = 0.30
WEIGHT_PRESSURE = 0.20
WEIGHT_PILLAR = 0.15
WEIGHT_FUEL_PHASE = 0.15
WEIGHT_RICHNESS = 0.20

O2_DISTANCE_SCALE = 20.0       # percentage points at which oxygen proximity reaches 0
PRESSURE_DISTANCE_SCALE = 14.7  # psi at which pressure proximity reaches 0
RICHNESS_FULL_TESTS = 100       # individual tests that give full data-richness credit
MAX_EVIDENCE_POINTS = 3         # test points cited as evidence for one criterion
SCORE_DECIMALS = 3


@dataclass(frozen=True)
class HabitatScenario:
    name: str
    o2_percent: float
    pressure_psi: float
    gravity: GravityRegime = GravityRegime.NORMAL
    pillars_of_interest: tuple[FireSafetyPillar, ...] = tuple(FireSafetyPillar)
    fuel_phases_of_interest: tuple[FuelPhase, ...] = (FuelPhase.SOLID,)  # habitat materials are mostly solids

    def __post_init__(self) -> None:
        if not 0 <= self.o2_percent <= 100:
            raise ValueError("Scenario oxygen must be within 0-100 percent.")
        if self.pressure_psi < 0:
            raise ValueError("Scenario pressure must not be negative.")


LUNAR_BASE = HabitatScenario("Lunar base", LUNAR_O2_PERCENT, LUNAR_PRESSURE_PSI, GravityRegime.PARTIAL_EMULATED)


@dataclass(frozen=True)
class CriterionResult:
    value: float          # in [0, 1]
    rationale: str
    evidence: tuple[str, ...] = ()  # test_point_ids supporting the value


class RelevanceCriterion(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def weight(self) -> float: ...  # read-only so frozen dataclasses satisfy the protocol

    def evaluate(self, inv: Investigation, scenario: HabitatScenario) -> CriterionResult: ...


@dataclass(frozen=True)
class CriterionScore:
    criterion: str
    weight: float
    value: float
    contribution: float
    rationale: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class ScoreBreakdown:
    scores: tuple[CriterionScore, ...]

    @property
    def total(self) -> float:
        return round(sum(s.contribution for s in self.scores), SCORE_DECIMALS)


@dataclass(frozen=True)
class RankedInvestigation:
    investigation: Investigation
    rank: int
    breakdown: ScoreBreakdown

    @property
    def score(self) -> float:
        return self.breakdown.total


def _ambient(inv: Investigation, field: str) -> list[tuple[TestPoint, float, float]]:
    rows = []
    for tp in inv.test_points:
        low, high = getattr(tp, f"{field}_min"), getattr(tp, f"{field}_max")
        if low is None or high is None or (field == "o2_percent" and tp.o2_basis != O2Basis.AMBIENT):
            continue
        rows.append((tp, low, high))
    return rows


def _proximity(inv: Investigation, field: str, target: float, scale: float, label: str) -> CriterionResult:
    rows = _ambient(inv, field)
    if not rows:
        return CriterionResult(0.0, f"No {label} reported for ambient conditions.")
    scored = sorted(((0.0 if low <= target <= high else min(abs(target - low), abs(target - high)), tp.test_point_id)
                     for tp, low, high in rows))
    distance = scored[0][0]
    evidence = tuple(tp_id for _, tp_id in scored[:MAX_EVIDENCE_POINTS])
    value = round(max(0.0, 1 - distance / scale), SCORE_DECIMALS)
    inside = "inside the tested range" if distance == 0 else f"{distance:.1f} away from the nearest test"
    return CriterionResult(value, f"Scenario {label} is {inside}.", evidence)


@dataclass(frozen=True)
class OxygenProximity:
    name: str = "oxygen_proximity"
    weight: float = WEIGHT_OXYGEN

    def evaluate(self, inv: Investigation, scenario: HabitatScenario) -> CriterionResult:
        return _proximity(inv, "o2_percent", scenario.o2_percent, O2_DISTANCE_SCALE, "oxygen (% ambient)")


@dataclass(frozen=True)
class PressureProximity:
    name: str = "pressure_proximity"
    weight: float = WEIGHT_PRESSURE

    def evaluate(self, inv: Investigation, scenario: HabitatScenario) -> CriterionResult:
        return _proximity(inv, "pressure_psi", scenario.pressure_psi, PRESSURE_DISTANCE_SCALE, "pressure (psi)")


@dataclass(frozen=True)
class PillarMatch:
    name: str = "pillar_match"
    weight: float = WEIGHT_PILLAR

    def evaluate(self, inv: Investigation, scenario: HabitatScenario) -> CriterionResult:
        manual = inv.manual_metadata
        if manual is None or manual.pillars.value is None or not scenario.pillars_of_interest:
            return CriterionResult(0.0, "Fire-safety pillars are not reported for this investigation.")
        shared = set(manual.pillars.value) & set(scenario.pillars_of_interest)
        value = round(len(shared) / len(set(scenario.pillars_of_interest)), SCORE_DECIMALS)
        names = ", ".join(sorted(p.value for p in shared)) or "none"
        return CriterionResult(value, f"Shared fire-safety pillars: {names}.")


@dataclass(frozen=True)
class FuelPhaseMatch:
    name: str = "fuel_phase_match"
    weight: float = WEIGHT_FUEL_PHASE

    def evaluate(self, inv: Investigation, scenario: HabitatScenario) -> CriterionResult:
        known = [tp for tp in inv.test_points if tp.fuel_phase is not None]
        if not known:
            return CriterionResult(0.0, "No fuel phase reported.")
        hits = [tp for tp in known if tp.fuel_phase in scenario.fuel_phases_of_interest]
        wanted = ", ".join(p.value for p in scenario.fuel_phases_of_interest)
        return CriterionResult(round(len(hits) / len(known), SCORE_DECIMALS),
                               f"{len(hits)} of {len(known)} records use a {wanted} fuel.",
                               tuple(tp.test_point_id for tp in hits[:MAX_EVIDENCE_POINTS]))


@dataclass(frozen=True)
class DataRichness:
    name: str = "data_richness"
    weight: float = WEIGHT_RICHNESS

    def evaluate(self, inv: Investigation, scenario: HabitatScenario) -> CriterionResult:
        tests = [tp for tp in inv.test_points if tp.record_level == RecordLevel.TEST]
        verified = [tp for tp in tests if tp.provenance_status == ProvenanceStatus.VERIFIED]
        if not tests:
            return CriterionResult(0.0, "No individual test records (only summaries or matrices).")
        value = min(1.0, len(tests) / RICHNESS_FULL_TESTS) * len(verified) / len(tests)
        return CriterionResult(round(value, SCORE_DECIMALS),
                               f"{len(tests)} individual tests, {len(verified)} with verified lineage.")


DEFAULT_CRITERIA: tuple[RelevanceCriterion, ...] = (
    OxygenProximity(), PressureProximity(), PillarMatch(), FuelPhaseMatch(), DataRichness(),
)


class RelevanceRanker:
    """Domain service: same investigations and scenario always give the same order (ties by id)."""

    def __init__(self, criteria: tuple[RelevanceCriterion, ...] = DEFAULT_CRITERIA) -> None:
        if abs(sum(c.weight for c in criteria) - 1.0) > 1e-9:
            raise ValueError("Criterion weights must sum to 1.")
        self._criteria = criteria

    def rank(self, investigations: tuple[Investigation, ...], scenario: HabitatScenario) -> tuple[RankedInvestigation, ...]:
        scored = []
        for inv in investigations:
            parts = []
            for criterion in self._criteria:
                result = criterion.evaluate(inv, scenario)
                parts.append(CriterionScore(criterion.name, criterion.weight, result.value,
                                            round(criterion.weight * result.value, SCORE_DECIMALS * 2),
                                            result.rationale, result.evidence))
            scored.append((inv, ScoreBreakdown(tuple(parts))))
        scored.sort(key=lambda pair: (-pair[1].total, pair[0].id))
        return tuple(RankedInvestigation(inv, i + 1, breakdown) for i, (inv, breakdown) in enumerate(scored))


@dataclass(frozen=True)
class TestedRange:
    low: float
    high: float


def _tested_range(inv: Investigation, field_name: str) -> TestedRange | None:
    rows = _ambient(inv, field_name)
    if not rows:
        return None
    return TestedRange(min(low for _, low, _ in rows), max(high for _, _, high in rows))


def limitations(scenario: HabitatScenario, ranked: tuple[RankedInvestigation, ...]) -> tuple[str, ...]:
    """Limitations are domain facts about the data, never LLM text (SPEC-003 section 4)."""
    notes: list[str] = []
    if scenario.gravity != GravityRegime.MICROGRAVITY and scenario.gravity != GravityRegime.NORMAL:
        notes.append("PSI has no partial-gravity data: microgravity and 1 g bound the interval; E-FIELD only "
                     "emulates partial gravity. LUCI and FM2 are future work.")
    for item in ranked:
        inv = item.investigation
        for label, field_name, target, unit in (("oxygen", "o2_percent", scenario.o2_percent, "%"),
                                                 ("pressure", "pressure_psi", scenario.pressure_psi, " psi")):
            tested = _tested_range(inv, field_name)
            if tested is None:
                notes.append(f"{inv.id}: no ambient {label} reported, so the scenario cannot be compared.")
            elif not tested.low <= target <= tested.high:
                notes.append(f"{inv.id}: scenario {label} {target:g}{unit} is outside the tested range "
                             f"{tested.low:g}-{tested.high:g}{unit}; any conclusion is an extrapolation.")
        if any(tp.o2_basis == O2Basis.OXIDIZER_STREAM for tp in inv.test_points):
            notes.append(f"{inv.id}: some tests report oxygen in the burner (oxidizer) stream, not in the "
                         "surrounding atmosphere; they are not counted as ambient oxygen.")
    return tuple(dict.fromkeys(notes))
