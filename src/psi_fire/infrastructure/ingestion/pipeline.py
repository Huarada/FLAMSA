"""Ingestion pipeline: raw PSI experimental tables -> validated Investigation aggregates.

read -> map headers -> drop notes / merge continuation rows -> expand summary rows -> parse quantities
-> derive core columns -> validate in the domain model.
"""

import csv
import hashlib
import io
import re
from dataclasses import dataclass, field
from pathlib import Path

from psi_fire.domain.manual import ManualMetadata
from psi_fire.domain.model import (
    CORE_COLUMNS_SET,
    RANGED_CORE_BASES,
    ColumnInfo,
    ExtraValue,
    FuelPhase,
    Investigation,
    ProvenanceStatus,
    SourceFile,
    SourceNote,
    TestPoint,
)
from psi_fire.domain.units import canonical_unit, column_name
from psi_fire.infrastructure.evidence_verifier import EvidenceError, EvidenceVerifier
from psi_fire.infrastructure.ingestion.adapters import ADAPTERS
from psi_fire.infrastructure.ingestion.fuel_names import LABEL_FRACTION_COLUMN, normalize_fuel_label
from psi_fire.infrastructure.ingestion.isa_tab import read_study_metadata
from psi_fire.infrastructure.ingestion.quantity_parser import (
    QuantityParseError,
    format_number,
    is_empty,
    parse_quantity,
)
from psi_fire.infrastructure.ingestion.specs import AdapterSpec, Meta, Num, Skip, TableSpec, Text
from psi_fire.infrastructure.ingestion.text_source import decode
from psi_fire.infrastructure.source_registry import SourceRegistry

ID_COLUMN = "test_point_id"
FUEL_COLUMN = "fuel_name"
FUEL_RAW_COLUMN = "fuel_name_raw"
DILUENT_SPECIES = (("CO2", "co2_percent"), ("He", "he_percent"), ("N2", "n2_percent"))
_SUMMARY_ROW = re.compile(r"^(?P<name>.+?):\s*same conditions as (?P<first>\d+)\s*-\s*(?P<last>\d+)$", re.IGNORECASE)


class CurationError(Exception):
    """A raw table does not match its adapter; fix the adapter, never the raw file."""


def _norm(text: str) -> str:
    return " ".join(text.split())


@dataclass
class _RawRecord:
    rows: list[int]
    cells: dict[str, str]
    status: ProvenanceStatus = ProvenanceStatus.VERIFIED
    notes: list[str] = field(default_factory=list)


class CsvInvestigationCurator:
    """Implements the InvestigationCurator port for the PSI 'Experimental table' CSVs."""

    def __init__(
        self,
        registry: SourceRegistry,
        repo_root: Path,
        adapters: dict[str, AdapterSpec] = ADAPTERS,
        manual_dir: Path | None = None,
    ):
        self._registry = registry
        self._root = repo_root
        self._adapters = adapters
        self._manual_dir = manual_dir
        self._verifier = EvidenceVerifier(repo_root)

    def _manual_metadata(self, investigation_id: str) -> ManualMetadata | None:
        """data/manual/<id>.json, with every quote verified against its source file."""
        path = self._manual_dir / f"{investigation_id}.json" if self._manual_dir else None
        if path is None or not path.is_file():
            return None
        manual = ManualMetadata.model_validate_json(path.read_text(encoding="utf-8"))
        if manual.investigation_id != investigation_id:
            raise CurationError(f"{path.name}: investigation_id is {manual.investigation_id!r}")
        for evidence in manual.all_evidence():
            try:
                self._verifier.verify(evidence)
            except EvidenceError as error:
                raise CurationError(f"{path.name}: {error}") from error
        return manual

    def curate(self, investigation_id: str) -> Investigation:
        entry = self._registry.get(investigation_id)
        adapter = self._adapters[investigation_id]
        if {t.file for t in adapter.tables} != set(entry.experimental_tables):
            raise CurationError(f"{investigation_id}: adapter tables differ from data/sources.json")

        source_files, notes, test_points = [], [], []
        columns: dict[str, ColumnInfo] = {}
        for table in adapter.tables:
            path = self._root / entry.raw_dir / table.file
            rel_path = path.relative_to(self._root).as_posix()
            data = path.read_bytes()
            text, encoding = decode(data)
            source_files.append(SourceFile(path=rel_path, sha256=hashlib.sha256(data).hexdigest(), encoding=encoding))
            _merge_columns(columns, _column_dictionary(adapter, table))
            records = self._records(adapter, table, text, rel_path, notes)
            test_points += [_to_test_point(adapter, table, r, rel_path) for r in records]

        used = {k for tp in test_points for k in tp.extras}
        optional = {FUEL_RAW_COLUMN, "fuel_geometry", LABEL_FRACTION_COLUMN}  # listed only when some label yields them
        columns = {k: v for k, v in columns.items()
                   if k in used or (v.kind != "raw" and k not in optional) or k in CORE_COLUMNS_SET}

        study, study_source = {}, None
        if entry.isa_tab_dir:
            isa_path = self._root / entry.raw_dir / entry.isa_tab_dir / "i_Investigation.txt"
            study, study_source = read_study_metadata(isa_path), isa_path.relative_to(self._root).as_posix()

        return Investigation(
            id=investigation_id,
            psi_id=entry.psi_id,
            record_level=adapter.record_level,
            source_files=tuple(source_files),
            study_metadata=study,
            study_metadata_source=study_source,
            source_notes=tuple(notes),
            manual_metadata=self._manual_metadata(investigation_id),
            columns=columns,
            test_points=tuple(test_points),
        )

    def _records(
        self, adapter: AdapterSpec, table: TableSpec, text: str, rel_path: str, notes: list[SourceNote]
    ) -> list[_RawRecord]:
        rows = list(csv.reader(io.StringIO(text, newline="")))
        header = [_norm(h) for h in rows[0]]
        expected = {_norm(c.header) for c in table.columns} | ({adapter.notes_header} if adapter.notes_header else set())
        present = {h for h in header if h}
        if present != expected:
            raise CurationError(
                f"{rel_path}: unmapped headers {sorted(present - expected)}, missing headers {sorted(expected - present)}"
            )

        records: list[_RawRecord] = []
        for row_number, cells in enumerate(rows[1:], start=2):  # spreadsheet numbering: header is row 1
            if any(c.strip() for c in cells[len(header):]):
                raise CurationError(f"{rel_path} row {row_number}: values beyond the last header")
            cells = cells + [""] * (len(header) - len(cells))
            record = {h: c for h, c in zip(header, cells) if h}
            if not any(v.strip() for v in record.values()):
                continue
            if adapter.is_note_row(cells):
                notes.append(SourceNote(source_file=rel_path, source_row=row_number,
                                        text=" ".join(_norm(c) for c in cells if c.strip())))
                continue
            if adapter.notes_header and (note := _norm(record.pop(adapter.notes_header))):
                notes.append(SourceNote(source_file=rel_path, source_row=row_number, text=note))
            if self._is_continuation(adapter, record) and records:
                previous, header_name = records[-1], adapter.continuation_header
                assert header_name is not None
                previous.cells[header_name] = f"{previous.cells[header_name]}; {_norm(record[header_name])}"
                previous.rows.append(row_number)
                previous.status = ProvenanceStatus.INFERRED
                previous.notes.append(f"'{header_name}' extended by continuation row {row_number}")
                continue
            records.append(_RawRecord([row_number], record))
        _flag_identical_rows(records)
        return _expand_summary_rows(records, table)

    @staticmethod
    def _is_continuation(adapter: AdapterSpec, record: dict[str, str]) -> bool:
        name = adapter.continuation_header
        return bool(name and record[name].strip() and not any(v.strip() for k, v in record.items() if k != name))


def _flag_identical_rows(records: list[_RawRecord]) -> None:
    """Identical rows are kept (they may be distinct runs with lost telemetry) but flagged for users."""
    first_seen: dict[tuple[str, ...], int] = {}
    for record in records:
        key = tuple(_norm(v) for v in record.cells.values())
        if key in first_seen:
            record.notes.append(f"identical to row {first_seen[key]}")
        else:
            first_seen[key] = record.rows[0]


def _expand_summary_rows(records: list[_RawRecord], table: TableSpec) -> list[_RawRecord]:
    """'Kapton: same conditions as 1-4' becomes one inferred record per referenced sample."""
    id_header = next((_norm(c.header) for c in table.columns if not isinstance(c, Skip) and c.name == ID_COLUMN), None)
    if id_header is None:
        return records
    by_id = {_norm(r.cells[id_header]): r for r in records}
    expanded: list[_RawRecord] = []
    for record in records:
        hit = next(((h, m) for h, v in record.cells.items() if (m := _SUMMARY_ROW.match(_norm(v)))), None)
        if hit is None:
            expanded.append(record)
            continue
        header, match = hit
        summary_id = _norm(record.cells[id_header])
        for reference in range(int(match["first"]), int(match["last"]) + 1):
            source = by_id.get(str(reference))
            if source is None:
                raise CurationError(f"summary row {record.rows[0]} references missing sample {reference}")
            cells = dict(source.cells) | {header: match["name"], id_header: f"{summary_id}.{reference}"}
            expanded.append(_RawRecord(
                record.rows + source.rows, cells, ProvenanceStatus.INFERRED,
                [f"expanded from summary row {record.rows[0]}; conditions copied from row {source.rows[0]}"],
            ))
    return expanded


def _column_dictionary(adapter: AdapterSpec, table: TableSpec) -> dict[str, ColumnInfo]:
    columns: dict[str, ColumnInfo] = {}
    for spec in table.columns:
        match spec:
            case Num(header=header, name=name, unit=unit, ranged=ranged):
                column = column_name(name, canonical_unit(unit))
                info = ColumnInfo(kind="quantity", unit=canonical_unit(unit), source_headers=(header,))
                if ranged or column in RANGED_CORE_BASES:
                    columns[f"{column}_min"] = columns[f"{column}_max"] = info
                else:
                    columns[column] = info
                columns[f"{column}_raw"] = ColumnInfo(kind="raw", source_headers=(header,))
            case Text(header=header, name=name):
                columns[name] = ColumnInfo(kind="text", source_headers=(header,))
                if name == FUEL_COLUMN:
                    columns |= _fuel_columns(header)
            case Meta(header=header, name=name):
                columns[name] = ColumnInfo(kind="meta", source_headers=(header,))
    columns["fuel_phase"] = ColumnInfo(kind="text", derivation=f"adapter: {adapter.fuel_phase.value} unless overridden by fuel name")
    for name, constant in table.constants.items():
        columns[name] = ColumnInfo(kind="text", derivation=f"table constant: {constant.reason}")
    if "diluent" not in columns and any(c in columns for _, c in DILUENT_SPECIES):
        columns["diluent"] = ColumnInfo(kind="text", derivation="species with non-zero initial mole fraction among CO2, He, N2")
    return columns


def _fuel_columns(header: str) -> dict[str, ColumnInfo]:
    source = (header,)
    return {
        FUEL_RAW_COLUMN: ColumnInfo(kind="raw", source_headers=source),
        "fuel_geometry": ColumnInfo(kind="text", source_headers=source, derivation="geometry word literally present in the fuel label"),
        LABEL_FRACTION_COLUMN: ColumnInfo(kind="quantity", unit=canonical_unit("%"), source_headers=source,
                                          derivation="percentage printed in the fuel label ('pure' = 100); not the measured composition"),
    }


def _merge_columns(target: dict[str, ColumnInfo], new: dict[str, ColumnInfo]) -> None:
    for name, info in new.items():
        if name in target:
            headers = tuple(dict.fromkeys(target[name].source_headers + info.source_headers))
            info = target[name].model_copy(update={"source_headers": headers})
        target[name] = info


def _fuel_values(raw: str, aliases: dict[str, str]) -> dict[str, ExtraValue]:
    label = normalize_fuel_label(raw)
    name = aliases.get(label.name, label.name) if label.name else None
    values: dict[str, ExtraValue] = {FUEL_COLUMN: name, "fuel_geometry": label.geometry,
                                     LABEL_FRACTION_COLUMN: label.label_fraction_percent}
    if raw != name:
        values[FUEL_RAW_COLUMN] = raw  # data rule 2: the raw label always survives
    return values


def _to_test_point(adapter: AdapterSpec, table: TableSpec, record: _RawRecord, rel_path: str) -> TestPoint:
    values: dict[str, ExtraValue] = {}
    issues, status = list(record.notes), record.status
    for spec in table.columns:
        raw = _norm(record.cells[_norm(spec.header)])
        if isinstance(spec, Skip):
            continue
        if isinstance(spec, Text) and spec.name == FUEL_COLUMN and not is_empty(raw):
            values.update(_fuel_values(raw, adapter.fuel_aliases))
            continue
        if isinstance(spec, Text) and not spec.free_text and not is_empty(raw):
            raw = raw.lower()
        if isinstance(spec, (Text, Meta)):
            values[spec.name] = None if is_empty(raw) else raw
            continue
        column = column_name(spec.name, canonical_unit(spec.unit))
        to_parse = raw
        if spec.fixup and (fixed := spec.fixup(raw, record.cells)):
            to_parse, note = fixed
            issues.append(f"{column}: {note}")
            if to_parse != raw:
                status = ProvenanceStatus.INFERRED
        try:
            quantity = parse_quantity(to_parse, spec.unit)
        except QuantityParseError as error:
            quantity = None
            issues.append(f"{column}: raw value kept, not parsed ({error})")
        if spec.ranged or column in RANGED_CORE_BASES:
            values[f"{column}_min"] = quantity.minimum if quantity else None
            values[f"{column}_max"] = quantity.maximum if quantity else None
            exact = quantity is not None and quantity.part_count == 1 and raw == format_number(quantity.minimum)
        else:
            if quantity is not None and quantity.part_count > 1:
                issues.append(f"{column}: several values in one cell, raw value kept")
                quantity = None
            values[column] = quantity.minimum if quantity else None
            exact = quantity is not None and raw == format_number(quantity.minimum)
        if not exact and not is_empty(raw):
            values[f"{column}_raw"] = raw

    values.update({name: constant.value for name, constant in table.constants.items()})
    if "diluent" not in values and any(c in values for _, c in DILUENT_SPECIES):
        present = [s for s, c in DILUENT_SPECIES if isinstance(values.get(c), float) and values[c] > 0]  # type: ignore[operator]
        values["diluent"] = "+".join(present) or None
    if isinstance(values.get("flow_direction"), str):
        values["flow_direction"] = str(values["flow_direction"]).lower()

    fuel_name = values.get("fuel_name")
    phase: FuelPhase = adapter.fuel_phase_overrides.get(str(fuel_name).lower(), adapter.fuel_phase)
    test_point_id = values.pop(ID_COLUMN, None) or f"r{record.rows[0]}"
    core = {k: values.pop(k) for k in list(values) if k in CORE_COLUMNS_SET}
    return TestPoint(
        investigation_id=adapter.investigation_id,
        test_point_id=str(test_point_id),
        record_level=adapter.record_level,
        fuel_phase=phase,
        source_file=rel_path,
        source_row=";".join(map(str, record.rows)),
        provenance_status=status,
        provenance_note="; ".join(issues) or None,
        extras={k: v for k, v in values.items() if v is not None},  # empty = absent, as in the CSV
        **core,  # type: ignore[arg-type]
    )
