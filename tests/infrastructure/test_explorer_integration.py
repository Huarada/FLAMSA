"""Check explorer projections against the persisted CSV/JSON contracts independently."""

import csv
import json
import shutil
import sqlite3
from pathlib import Path

import pytest

from psi_fire.application.explore import (
    CheckDatasetFreshness,
    ExplorationQuery,
    ExploreInvestigations,
    Snapshot,
)
from psi_fire.domain.exploration import ConditionRange
from psi_fire.domain.manual import ManualMetadata
from psi_fire.infrastructure.explorer import FileSnapshotProvider

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def dataset() -> tuple[Snapshot, list[dict[str, str]], dict[str, dict]]:
    snapshot = FileSnapshotProvider(ROOT).load()
    rows = []
    metadata = {}
    for inv in snapshot.investigations:
        directory = ROOT / "data/curated" / inv.id
        with (directory / "test_points.csv").open(encoding="utf-8", newline="") as stream:
            rows.extend(csv.DictReader(stream))
        metadata[inv.id] = json.loads((directory / "investigation.json").read_text(encoding="utf-8"))
    return snapshot, rows, metadata


def identities(matches) -> set[tuple[str, str]]:
    return {(match.investigation.id, point.test_point_id) for match in matches for point in match.points}


def test_every_persisted_cell_and_record_reaches_the_explorer(dataset) -> None:
    snapshot, rows, metadata = dataset
    points = {(inv.id, point.test_point_id): point for inv in snapshot.investigations for point in inv.test_points}
    assert len(rows) == len(points)
    assert identities(ExploreInvestigations(snapshot)(ExplorationQuery())) == set(points)
    for row in rows:
        point = points[row["investigation_id"], row["test_point_id"]]
        values = point.model_dump(mode="json")
        values.update(point.extras)
        for field, raw in row.items():
            actual = values.get(field)
            assert actual == (None if raw == "" else float(raw) if isinstance(actual, (int, float)) else raw), (
                point.test_point_id, field, raw, actual
            )
    for inv in snapshot.investigations:
        assert inv.columns.keys() == metadata[inv.id]["columns"].keys()
        manual = ROOT / "data/manual" / f"{inv.id}.json"
        if manual.is_file():
            assert ManualMetadata.model_validate_json(manual.read_text(encoding="utf-8")) == inv.manual_metadata


@pytest.mark.parametrize("field,argument", [
    ("investigation_id", "ids"), ("record_level", "levels"), ("fuel_phase", "phases"),
    ("fuel_name", "fuels"), ("flow_direction", "directions"), ("provenance_status", "lineage"),
    ("o2_basis", "bases"),
])
def test_every_row_filter_option_matches_direct_csv_rows(dataset, field: str, argument: str) -> None:
    snapshot, rows, _ = dataset
    service = ExploreInvestigations(snapshot)
    option_key = "ids" if argument == "ids" else field
    expected_values = {row[field] or "Not reported" for row in rows}
    assert set(service.options()[option_key]) == expected_values
    for value in expected_values:
        expected = {(row["investigation_id"], row["test_point_id"]) for row in rows
                    if (row[field] or "Not reported") == value}
        assert identities(service(ExplorationQuery(**{argument: (value,)}))) == expected


@pytest.mark.parametrize("field,argument", [
    ("hardware", "hardware"), ("sensors", "sensors"), ("pillars", "pillars"), ("gravity_regime", "gravity"),
])
def test_every_metadata_option_matches_persisted_claims(dataset, field: str, argument: str) -> None:
    snapshot, rows, documents = dataset
    expected = {}
    for inv_id, document in documents.items():
        manual = document["manual_metadata"]
        if manual is None:
            labels = ["Metadata unavailable"]
        elif field == "sensors":
            labels = [claim["value"]["instrument"] if claim["value"] else "Not reported" for claim in manual[field]]
            labels = labels or ["No entries mapped"]
        else:
            value = manual[field]["value"]
            labels = ["Not reported"] if value is None else (value or ["No direct pillar"]) if isinstance(
                value, list
            ) else [value]
        for label in labels:
            expected.setdefault(label, set()).add(inv_id)
    service = ExploreInvestigations(snapshot)
    assert set(service.options()[field]) == set(expected)
    for label, parents in expected.items():
        expected_rows = {(row["investigation_id"], row["test_point_id"]) for row in rows
                         if row["investigation_id"] in parents}
        assert identities(service(ExplorationQuery(**{argument: (label,)}))) == expected_rows


def test_multiselect_union_and_cross_filter_intersection_against_csv(dataset) -> None:
    snapshot, rows, _ = dataset
    query = ExplorationQuery(ids=("SAME", "SAME-R"), fuels=("teflon", "silicone rubber"),
                             lineage=("verified", "inferred"), note="with note")
    expected = {(row["investigation_id"], row["test_point_id"]) for row in rows
                if row["investigation_id"] in {"SAME", "SAME-R"}
                and row["fuel_name"] in {"teflon", "silicone rubber"} and row["provenance_note"]}
    assert expected
    assert identities(ExploreInvestigations(snapshot)(query)) == expected


def test_numeric_conditions_against_independent_sql_over_persisted_rows(dataset) -> None:
    snapshot, rows, _ = dataset
    cases = (
        (ExplorationQuery(oxygen=ConditionRange(lower=30), pressure=ConditionRange(upper=10.2)),
         "basis = 'ambient' AND oh >= 30 AND pl <= 10.2"),
        (ExplorationQuery(pressure=ConditionRange(upper=10.2, include_missing=True)),
         "pl <= 10.2 OR pl IS NULL"),
        (ExplorationQuery(flow=ConditionRange(10, 30)), "fh >= 10 AND fl <= 30"),
    )
    with sqlite3.connect(":memory:") as database:
        database.execute("CREATE TABLE points (inv TEXT, id TEXT, basis TEXT, ol REAL, oh REAL, "
                         "pl REAL, ph REAL, fl REAL, fh REAL)")
        fields = ("o2_percent_min", "o2_percent_max", "pressure_psi_min", "pressure_psi_max",
                  "flow_speed_cm_s_min", "flow_speed_cm_s_max")
        database.executemany("INSERT INTO points VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            (row["investigation_id"], row["test_point_id"], row["o2_basis"] or None,
             *(float(row[key]) if row[key] else None for key in fields)) for row in rows
        ])
        for query, predicate in cases:
            expected = set(database.execute("SELECT inv, id FROM points WHERE " + predicate))
            assert identities(ExploreInvestigations(snapshot)(query)) == expected


def test_freshness_detects_new_curated_bytes_without_mutating_loaded_snapshot(tmp_path: Path, dataset) -> None:
    snapshot, _, _ = dataset
    inv_id = snapshot.investigations[0].id
    directory = tmp_path / "data/curated" / inv_id
    directory.mkdir(parents=True)
    for name in ("test_points.csv", "investigation.json"):
        shutil.copyfile(ROOT / "data/curated" / inv_id / name, directory / name)
    shutil.copyfile(ROOT / "data/sources.json", tmp_path / "data/sources.json")
    provider = FileSnapshotProvider(tmp_path)
    loaded = provider.load()
    assert CheckDatasetFreshness(provider)(loaded)
    path = directory / "test_points.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        headers, rows = reader.fieldnames, list(reader)
    original_fuel = loaded.investigations[0].test_points[0].fuel_name
    rows[0]["fuel_name"] = "audit-material"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    assert not CheckDatasetFreshness(provider)(loaded)
    assert loaded.investigations[0].test_points[0].fuel_name == original_fuel
    reloaded = provider.load()
    assert "audit-material" in ExploreInvestigations(reloaded).options()["fuel_name"]
    assert reloaded.revision != loaded.revision
