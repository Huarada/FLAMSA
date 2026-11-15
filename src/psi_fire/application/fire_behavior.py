"""Source-backed fire-behavior projections over the committed explorer results."""

import hashlib
import json
from dataclasses import asdict, dataclass
from math import isfinite

from psi_fire.application.behavior_statistics import NUMERICAL_LIBRARY_VERSIONS, OxygenSlope, oxygen_slope
from psi_fire.application.chart_data import LUNAR_OXYGEN_MIN, LUNAR_PRESSURE_MAX, scalar
from psi_fire.application.explore import Match
from psi_fire.domain.exploration import ConditionRange
from psi_fire.domain.model import Investigation, O2Basis, TestPoint
from psi_fire.domain.units import ATM_TO_PSI

POLICY_VERSION = "fire-behavior-v1"
MAX_PRESSURE_TOLERANCE = 0.05
COMPARISON_PRESSURE_MAX = 10.5
SIGNED_DIFFERENCE_TOLERANCE = 1e-10


class BehaviorDataError(ValueError):
    """A consumed field does not meet the declared analysis contract."""


@dataclass(frozen=True)
class BehaviorSettings:
    fuels: tuple[str, ...] = ()
    pressure_tolerance_fraction: float = MAX_PRESSURE_TOLERANCE
    diameter: ConditionRange | None = None

    def __post_init__(self) -> None:
        if not isfinite(self.pressure_tolerance_fraction) or not 0 < self.pressure_tolerance_fraction <= MAX_PRESSURE_TOLERANCE:
            raise ValueError("Pressure tolerance must be greater than zero and at most 5% of one atmosphere.")
        if self.diameter and self.diameter.include_missing:
            raise ValueError("Diameter filtering cannot include unreported measurements in a regression.")


@dataclass(frozen=True)
class RecordReference:
    investigation_id: str
    test_point_id: str
    source_file: str
    source_row: str
    provenance_status: str
    provenance_note: str | None


@dataclass(frozen=True)
class ExcludedRecord:
    reference: RecordReference
    reason: str


@dataclass(frozen=True)
class FlexObservation:
    reference: RecordReference
    fuel: str
    diluent: str
    oxygen_percent: float
    k_mm2_s: float
    pressure_psi: float
    diameter_mm: float
    he_percent: float
    co2_percent: float

    @property
    def group(self) -> str:
        return f"{self.fuel} | {self.diluent} | He {self.he_percent}% | CO2 {self.co2_percent}%"


@dataclass(frozen=True)
class FlexGroup:
    label: str
    fuel: str
    diluent: str
    record_ids: tuple[str, ...]
    oxygen_range: tuple[float, float]
    pressure_range: tuple[float, float]
    diameter_range: tuple[float, float]
    he_percent: float
    co2_percent: float
    estimate: OxygenSlope | None
    unavailable_reason: str | None


@dataclass(frozen=True)
class FlexEvidence:
    matched_records: int
    observations: tuple[FlexObservation, ...]
    excluded: tuple[ExcludedRecord, ...]
    groups: tuple[FlexGroup, ...]
    strict_scenario_records: tuple[RecordReference, ...]
    comparison_records: tuple[RecordReference, ...]
    comparison_pressure_range: tuple[float, float] | None


@dataclass(frozen=True)
class GasChange:
    reference: RecordReference
    fuel: str | None
    oxygen_initial_percent: float
    oxygen_final_percent: float
    co2_initial_percent: float
    co2_final_percent: float
    oxygen_consumed_points: float
    co2_increase_points: float
    negative_change: bool


@dataclass(frozen=True)
class BassEvidence:
    matched_records: int
    observations: tuple[GasChange, ...]
    excluded: tuple[ExcludedRecord, ...]


@dataclass(frozen=True)
class GravityOutcome:
    reference: RecordReference
    fuel: str | None
    thickness_raw: str | None
    oxygen_raw: str | None
    flow_raw: str | None
    flow_direction: str | None
    microgravity_length_mm: float | None
    microgravity_length_raw: str | None
    normal_gravity_length_mm: float | None
    normal_gravity_length_raw: str | None
    microgravity_rate_cm_s: float | None
    microgravity_rate_raw: str | None
    normal_gravity_rate_cm_s: float | None
    normal_gravity_rate_raw: str | None
    microgravity_length_state: str
    normal_gravity_length_state: str


@dataclass(frozen=True)
class SaffireEvidence:
    matched_records: int
    observations: tuple[GravityOutcome, ...]
    excluded: tuple[ExcludedRecord, ...]


@dataclass(frozen=True)
class TableEvidence:
    investigation_id: str
    source_files: tuple[tuple[str, str], ...]
    columns: tuple[tuple[str, str | None, tuple[str, ...]], ...]


@dataclass(frozen=True)
class BehaviorReport:
    dataset_revision: str
    analysis_id: str
    policy_version: str
    settings: BehaviorSettings
    flex: FlexEvidence
    bass: BassEvidence
    saffire: SaffireEvidence
    sources: tuple[TableEvidence, ...]
    numerical_libraries: tuple[tuple[str, str], ...]


def reference(point: TestPoint) -> RecordReference:
    return RecordReference(point.investigation_id, point.test_point_id, point.source_file, point.source_row,
                           point.provenance_status.value, point.provenance_note)


def _raw(point: TestPoint, key: str) -> str | None:
    raw = point.value(key + "_raw")
    if raw is not None:
        return str(raw)
    value = scalar(point, key)
    return f"{value:g}" if value is not None else None


def _require_units(inv: Investigation, columns: tuple[tuple[str, str], ...]) -> None:
    for key, unit in columns:
        info = inv.columns.get(key)
        if info is None or info.kind != "quantity" or info.unit is None or info.unit.value != unit:
            raise BehaviorDataError(f"{inv.id}: {key} requires a documented quantity in {unit}.")


def _length_state(value: float | None, raw: str | None) -> str:
    if value == 0:
        return "Approximately zero" if raw and "~" in raw else "Zero length reported"
    if value is not None:
        return "Numeric length; inspect qualifiers"
    if raw and raw.strip().casefold() == "complete":
        return "Complete (source label)"
    return "Mixed / see source note" if raw else "Not reported"


class BuildFireBehavior:
    def __call__(self, revision: str, matches: tuple[Match, ...],
                 settings: BehaviorSettings | None = None) -> BehaviorReport:
        settings = settings or BehaviorSettings()
        indexed = {match.investigation.id: match for match in matches}
        target_ids = ("FLEX", "BASS-II", "SAFFIRE-II")
        for inv_id in target_ids:
            if inv_id in indexed:
                self._validate(indexed[inv_id].investigation)
        flex = self._flex(indexed.get("FLEX"), settings)
        bass = self._bass(indexed.get("BASS-II"))
        saffire = self._saffire(indexed.get("SAFFIRE-II"))
        sources = tuple(TableEvidence(inv_id,
                                     tuple((source.path, source.sha256) for source in indexed[inv_id].investigation.source_files),
                                     tuple((key, info.unit.value if info.unit else None, info.source_headers)
                                           for key, info in sorted(indexed[inv_id].investigation.columns.items())))
                        for inv_id in target_ids if inv_id in indexed)
        identity = json.dumps({"revision": revision, "policy": POLICY_VERSION, "settings": asdict(settings),
                               "flex": asdict(flex), "bass": asdict(bass), "saffire": asdict(saffire),
                               "sources": [asdict(source) for source in sources],
                               "numerical_libraries": NUMERICAL_LIBRARY_VERSIONS}, sort_keys=True, allow_nan=False)
        return BehaviorReport(revision, hashlib.sha256(identity.encode()).hexdigest(), POLICY_VERSION,
                              settings, flex, bass, saffire, sources, NUMERICAL_LIBRARY_VERSIONS)

    @staticmethod
    def _validate(inv: Investigation) -> None:
        required = {
            "FLEX": (("burning_rate_constant_mm2_s", "mm2_s"), ("droplet_initial_diameter_mm", "mm"),
                     ("he_percent", "percent"), ("co2_percent", "percent"), ("pressure_psi_min", "psi"),
                     ("o2_percent_min", "percent")),
            "BASS-II": (("o2_final_percent", "percent"), ("co2_initial_percent", "percent"),
                        ("co2_final_percent", "percent"), ("o2_percent_min", "percent")),
            "SAFFIRE-II": (("microgravity_burn_length_mm", "mm"), ("normal_gravity_burn_length_mm", "mm"),
                           ("microgravity_spread_rate_cm_s", "cm_s"), ("normal_gravity_spread_rate_cm_s", "cm_s")),
        }
        _require_units(inv, required[inv.id])

    @staticmethod
    def _flex(match: Match | None, settings: BehaviorSettings) -> FlexEvidence:
        points = sorted(match.points, key=lambda point: point.test_point_id) if match else []
        fuels = {point.fuel_name for point in points}
        if set(settings.fuels) - fuels:
            raise ValueError("Unknown FLEX fuel in this research-filter scope.")
        observed: list[FlexObservation] = []
        excluded = []
        strict, comparison, pressures = [], [], []
        for point in points:
            ref = reference(point)
            oxygen, pressure = scalar(point, "o2_percent"), scalar(point, "pressure_psi")
            if (point.record_level.value == "test" and point.o2_basis == O2Basis.AMBIENT
                    and oxygen is not None and pressure is not None and oxygen >= LUNAR_OXYGEN_MIN):
                if pressure <= LUNAR_PRESSURE_MAX:
                    strict.append(ref)
                if pressure <= COMPARISON_PRESSURE_MAX:
                    comparison.append(ref)
                    pressures.append(pressure)
            keys = ("burning_rate_constant_mm2_s", "droplet_initial_diameter_mm", "he_percent", "co2_percent")
            values = tuple(scalar(point, key) for key in keys)
            reason = None
            if point.record_level.value != "test":
                reason = "Not an individual test"
            elif settings.fuels and point.fuel_name not in settings.fuels:
                reason = "Not selected in FLEX fuel settings"
            elif point.o2_basis != O2Basis.AMBIENT:
                reason = "Ambient oxygen basis not reported"
            elif oxygen is None or pressure is None or any(value is None for value in values):
                reason = "Missing or non-scalar oxygen, pressure, K, diameter or blend fraction"
            elif not point.fuel_name or not point.diluent:
                reason = "Fuel or diluent not reported"
            elif abs(pressure - ATM_TO_PSI) > ATM_TO_PSI * settings.pressure_tolerance_fraction:
                reason = "Outside the near-1-atm pressure band"
            if reason is not None:
                excluded.append(ExcludedRecord(ref, reason))
                continue
            assert oxygen is not None and pressure is not None and all(value is not None for value in values)
            k, diameter, helium, carbon_dioxide = (float(value) for value in values)  # type: ignore[arg-type]
            if k <= 0 or diameter <= 0 or not 0 <= helium <= 100 or not 0 <= carbon_dioxide <= 100:
                excluded.append(ExcludedRecord(ref, "Nonphysical K, diameter or blend fraction"))
            elif settings.diameter and not settings.diameter.matches(diameter, diameter):
                excluded.append(ExcludedRecord(ref, "Outside the selected initial-diameter interval"))
            else:
                observed.append(FlexObservation(ref, str(point.fuel_name), str(point.diluent), oxygen, k, pressure,
                                                diameter, helium, carbon_dioxide))
        groups = []
        for label in sorted({point.group for point in observed}):
            members = [point for point in observed if point.group == label]
            first = members[0]
            oxygen_values = tuple(point.oxygen_percent for point in members)
            pressure_values = tuple(point.pressure_psi for point in members)
            diameter_values = tuple(point.diameter_mm for point in members)
            estimate, reason = oxygen_slope(oxygen_values, tuple(point.k_mm2_s for point in members),
                                             (("pressure_psi", pressure_values), ("diameter_mm", diameter_values)))
            groups.append(FlexGroup(label, first.fuel, first.diluent,
                                    tuple(point.reference.test_point_id for point in members),
                                    (min(oxygen_values), max(oxygen_values)), (min(pressure_values), max(pressure_values)),
                                    (min(diameter_values), max(diameter_values)), first.he_percent, first.co2_percent,
                                    estimate, reason))
        return FlexEvidence(len(points), tuple(observed), tuple(excluded), tuple(groups), tuple(strict), tuple(comparison),
                            (min(pressures), max(pressures)) if pressures else None)

    @staticmethod
    def _bass(match: Match | None) -> BassEvidence:
        points = sorted(match.points, key=lambda point: point.test_point_id) if match else []
        observed, excluded = [], []
        for point in points:
            ref = reference(point)
            values = tuple(scalar(point, key) for key in ("o2_percent", "o2_final_percent",
                                                         "co2_initial_percent", "co2_final_percent"))
            if point.record_level.value != "test" or point.o2_basis != O2Basis.AMBIENT:
                excluded.append(ExcludedRecord(ref, "Not an individual ambient-oxygen test"))
            elif any(value is None for value in values):
                excluded.append(ExcludedRecord(ref, "Missing or non-scalar initial/final oxygen or CO2"))
            elif any(value is not None and not 0 <= value <= 100 for value in values):
                excluded.append(ExcludedRecord(ref, "Concentration outside 0–100 percent"))
            else:
                initial, final, co2_initial, co2_final = (float(value) for value in values)  # type: ignore[arg-type]
                oxygen_delta, co2_delta = initial - final, co2_final - co2_initial
                observed.append(GasChange(ref, point.fuel_name, initial, final, co2_initial, co2_final,
                                           oxygen_delta, co2_delta, oxygen_delta < -SIGNED_DIFFERENCE_TOLERANCE
                                           or co2_delta < -SIGNED_DIFFERENCE_TOLERANCE))
        return BassEvidence(len(points), tuple(observed), tuple(excluded))

    @staticmethod
    def _saffire(match: Match | None) -> SaffireEvidence:
        points = sorted(match.points, key=lambda point: point.test_point_id) if match else []
        observed, excluded = [], []
        for point in points:
            if point.record_level.value != "test":
                excluded.append(ExcludedRecord(reference(point), "Not an individual test"))
                continue
            observed.append(GravityOutcome(reference(point), point.fuel_name, _raw(point, "sample_thickness_mm"),
                                             point.o2_percent_raw or _raw(point, "o2_percent"),
                                             point.flow_speed_cm_s_raw or _raw(point, "flow_speed_cm_s"),
                                             point.flow_direction.value if point.flow_direction else None,
                                             scalar(point, "microgravity_burn_length_mm"),
                                             _raw(point, "microgravity_burn_length_mm"),
                                             scalar(point, "normal_gravity_burn_length_mm"),
                                             _raw(point, "normal_gravity_burn_length_mm"),
                                             scalar(point, "microgravity_spread_rate_cm_s"),
                                             _raw(point, "microgravity_spread_rate_cm_s"),
                                             scalar(point, "normal_gravity_spread_rate_cm_s"),
                                             _raw(point, "normal_gravity_spread_rate_cm_s"),
                                             _length_state(scalar(point, "microgravity_burn_length_mm"),
                                                           _raw(point, "microgravity_burn_length_mm")),
                                             _length_state(scalar(point, "normal_gravity_burn_length_mm"),
                                                           _raw(point, "normal_gravity_burn_length_mm"))))
        return SaffireEvidence(len(points), tuple(observed), tuple(excluded))
