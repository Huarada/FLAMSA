"""Declarative column specs: each adapter only states how its raw headers map to canonical columns."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from psi_fire.domain.model import FuelPhase, RecordLevel

# (raw cell, whole raw row by normalized header) -> (corrected raw, note) or None.
# Returning the raw unchanged only attaches the note (a flagged conflict); the value stays verified.
Fixup = Callable[[str, Mapping[str, str]], tuple[str, str] | None]


@dataclass(frozen=True)
class Num:
    """Quantity column. `unit` is the source unit assumed when the cell carries none (None = dimensionless)."""

    header: str
    name: str
    unit: str | None
    ranged: bool = False
    fixup: Fixup | None = None


@dataclass(frozen=True)
class Text:
    """Descriptive column that takes part in variable analysis (fuel, outcome, configuration)."""

    header: str
    name: str
    free_text: bool = False  # keeps the source casing; every other Text value is lower-cased


@dataclass(frozen=True)
class Meta:
    """Bookkeeping column (ids, dates, cameras): kept, but excluded from variable analysis."""

    header: str
    name: str


@dataclass(frozen=True)
class Skip:
    """Column intentionally dropped; the reason is mandatory."""

    header: str
    reason: str


ColumnSpec = Num | Text | Meta | Skip


@dataclass(frozen=True)
class Constant:
    value: str
    reason: str


@dataclass(frozen=True)
class TableSpec:
    file: str
    columns: tuple[ColumnSpec, ...]
    constants: dict[str, Constant] = field(default_factory=dict)


def never(_cells: list[str]) -> bool:
    return False


@dataclass(frozen=True)
class AdapterSpec:
    investigation_id: str
    record_level: RecordLevel
    fuel_phase: FuelPhase
    tables: tuple[TableSpec, ...]
    fuel_phase_overrides: dict[str, FuelPhase] = field(default_factory=dict)  # key: lower-case fuel_name
    fuel_aliases: dict[str, str] = field(default_factory=dict)  # normalized fuel_name -> name used by the literature
    is_note_row: Callable[[list[str]], bool] = never
    notes_header: str | None = None          # column holding general notes, moved to source_notes
    continuation_header: str | None = None   # rows filling only this column extend the previous row
