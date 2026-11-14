"""Domain model: TestPoint (entity) and Investigation (aggregate root). Pure: no I/O."""

from enum import StrEnum
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from psi_fire.domain.manual import ManualMetadata
from psi_fire.domain.units import Unit


class FuelPhase(StrEnum):
    SOLID = "solid"
    LIQUID = "liquid"
    GAS = "gas"


class RecordLevel(StrEnum):
    TEST = "test"                # one row per ignition/test run
    TEST_DAY = "test_day"        # one row summarizes a day of tests
    TEST_MATRIX = "test_matrix"  # planned condition envelope, not individual runs


class O2Basis(StrEnum):
    AMBIENT = "ambient"                  # O2 in the surrounding atmosphere
    OXIDIZER_STREAM = "oxidizer_stream"  # O2 issued from the burner (inverse flames)


class FlowDirection(StrEnum):
    CONCURRENT = "concurrent"
    OPPOSED = "opposed"
    COFLOW = "coflow"


class ProvenanceStatus(StrEnum):
    VERIFIED = "verified"  # copied/converted from a single source cell
    INFERRED = "inferred"  # reconstructed (summary-row expansion, merged rows, documented fixups)


O2_PERCENT_MIN = 0.0
O2_PERCENT_MAX = 100.0
RANGED_CORE_BASES = ("o2_percent", "pressure_psi", "flow_speed_cm_s")
CORE_DESCRIPTIVE_COLUMNS = ("fuel_name", "fuel_phase", "o2_basis", "diluent", "flow_direction")

ExtraValue = float | str | None


class TestPoint(BaseModel):
    """One normalized row of an experimental table. Mirrors a row of test_points.csv."""

    __test__: ClassVar[bool] = False  # keep pytest from collecting this class
    model_config = ConfigDict(frozen=True, extra="forbid")

    investigation_id: str
    test_point_id: str
    record_level: RecordLevel
    fuel_name: str | None = None
    fuel_phase: FuelPhase | None = None
    o2_basis: O2Basis | None = None
    o2_percent_min: float | None = None
    o2_percent_max: float | None = None
    o2_percent_raw: str | None = None
    pressure_psi_min: float | None = None
    pressure_psi_max: float | None = None
    pressure_psi_raw: str | None = None
    diluent: str | None = None
    flow_speed_cm_s_min: float | None = None
    flow_speed_cm_s_max: float | None = None
    flow_speed_cm_s_raw: str | None = None
    flow_direction: FlowDirection | None = None
    source_file: str
    source_row: str
    provenance_status: ProvenanceStatus
    provenance_note: str | None = None
    extras: dict[str, ExtraValue] = {}

    @model_validator(mode="after")
    def _check_invariants(self) -> "TestPoint":
        for base in RANGED_CORE_BASES:
            low, high = getattr(self, f"{base}_min"), getattr(self, f"{base}_max")
            if (low is None) != (high is None):
                raise ValueError(f"{base}: min and max must both be set or both be empty")
            if low is not None and low > high:
                raise ValueError(f"{base}: min {low} > max {high}")
            if low is not None and base != "o2_percent" and low < 0:
                raise ValueError(f"{base}: negative value {low}")
        if self.o2_percent_min is not None:
            if not (O2_PERCENT_MIN <= self.o2_percent_min and self.o2_percent_max <= O2_PERCENT_MAX):  # type: ignore[operator]
                raise ValueError(f"o2_percent outside [0, 100]: {self.o2_percent_min}..{self.o2_percent_max}")
            if self.o2_basis is None:
                raise ValueError("o2_basis is required when o2_percent is set")
        overlap = CORE_COLUMNS_SET.intersection(self.extras)
        if overlap:
            raise ValueError(f"extras shadow core columns: {sorted(overlap)}")
        return self

    def value(self, column: str) -> ExtraValue:
        if column in CORE_COLUMNS_SET:
            raw = getattr(self, column)
            return raw.value if isinstance(raw, StrEnum) else raw
        return self.extras.get(column)


CORE_COLUMNS: tuple[str, ...] = tuple(name for name in TestPoint.model_fields if name != "extras")
CORE_COLUMNS_SET = frozenset(CORE_COLUMNS)


ColumnKind = Literal["quantity", "text", "meta", "raw"]


class ColumnInfo(BaseModel):
    """Data dictionary entry: where a curated column comes from and how to read it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: ColumnKind  # meta = bookkeeping (dates, ids, cameras); excluded from variable analysis
    unit: Unit | None = None
    source_headers: tuple[str, ...] = ()
    derivation: str | None = None


class SourceFile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    sha256: str
    encoding: str


class SourceNote(BaseModel):
    """Free text found in a source table that is not a test point (footnotes, general notes)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_file: str
    source_row: int
    text: str


class Investigation(BaseModel):
    """Aggregate root. test_points are persisted separately (CSV), never inside investigation.json."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    id: str
    psi_id: str
    record_level: RecordLevel
    source_files: tuple[SourceFile, ...]
    study_metadata: dict[str, str] = {}
    study_metadata_source: str | None = None
    source_notes: tuple[SourceNote, ...] = ()
    manual_metadata: ManualMetadata | None = None  # None until data/manual/<id>.json exists
    columns: dict[str, ColumnInfo]
    test_points: tuple[TestPoint, ...]

    @model_validator(mode="after")
    def _check_invariants(self) -> "Investigation":
        if not self.test_points:
            raise ValueError(f"{self.id}: an investigation needs at least one test point")
        ids = [tp.test_point_id for tp in self.test_points]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"{self.id}: duplicate test_point_id {duplicates}")
        foreign = {tp.investigation_id for tp in self.test_points} - {self.id}
        if foreign:
            raise ValueError(f"{self.id}: test points belong to {sorted(foreign)}")
        unknown = {k for tp in self.test_points for k in tp.extras} - set(self.columns)
        if unknown:
            raise ValueError(f"{self.id}: extras missing from the column dictionary: {sorted(unknown)}")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def test_point_count(self) -> int:
        return len(self.test_points)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def varied_variables(self) -> list[str]:
        return self._variables_with("varied")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def held_constant_variables(self) -> list[str]:
        return self._variables_with("held_constant")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def unreported_variables(self) -> list[str]:
        return self._variables_with("not_reported")

    def _variables_with(self, status: str) -> list[str]:
        return sorted(base for base, s in self._classify_variables().items() if s == status)

    def _classify_variables(self) -> dict[str, str]:
        """How tests of this investigation differ: derived from data, never hand-written."""
        # core conditions are always assessed, so a missing O2/pressure column reads as "not_reported"
        groups: dict[str, list[str]] = {base: [f"{base}_min", f"{base}_max"] for base in RANGED_CORE_BASES}
        groups |= {name: [name] for name in CORE_DESCRIPTIVE_COLUMNS}
        for column, info in self.columns.items():
            if column in CORE_COLUMNS_SET:
                continue
            if info.kind in ("meta", "raw"):
                continue
            base = column.removesuffix("_min").removesuffix("_max")
            groups.setdefault(base, []).append(column)
        result: dict[str, str] = {}
        for base, columns in groups.items():
            empty = tuple(None for _ in columns)
            distinct = {tuple(tp.value(c) for c in columns) for tp in self.test_points} - {empty}
            result[base] = "not_reported" if not distinct else "held_constant" if len(distinct) == 1 else "varied"
        return result
