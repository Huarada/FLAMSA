import csv
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from psi_fire.application.explore import ExplorationQuery, ExploreInvestigations
from psi_fire.application.fire_behavior import BuildFireBehavior
from psi_fire.infrastructure.explorer import FileSnapshotProvider

ROOT = Path(__file__).resolve().parents[2]


def test_actual_evidence_reconciles_csv_measurements_sources_and_scenario_counts() -> None:
    snapshot = FileSnapshotProvider(ROOT).load()
    matches = ExploreInvestigations(snapshot)(ExplorationQuery())
    report = BuildFireBehavior()(snapshot.revision, matches)
    for study, evidence in (("FLEX", report.flex), ("BASS-II", report.bass), ("SAFFIRE-II", report.saffire)):
        with (ROOT / "data/curated" / study / "test_points.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        expected = {row["test_point_id"]: row for row in rows}
        assert evidence.matched_records == len(rows)
        assert len(evidence.observations) + len(evidence.excluded) == len(rows)
        assert {point.reference.test_point_id for point in evidence.observations}.union(
            item.reference.test_point_id for item in evidence.excluded
        ) == set(expected)
        for point in evidence.observations:
            row = expected[point.reference.test_point_id]
            assert (point.reference.source_file, point.reference.source_row) == (row["source_file"], row["source_row"])
        if study == "FLEX":
            expected_strict = {row["test_point_id"] for row in rows if row["o2_percent_min"] and row["pressure_psi_max"]
                               and float(row["o2_percent_min"]) >= 30 and float(row["pressure_psi_max"]) <= 10.2}
            expected_nearby = {row["test_point_id"] for row in rows if row["o2_percent_min"] and row["pressure_psi_max"]
                               and float(row["o2_percent_min"]) >= 30 and float(row["pressure_psi_max"]) <= 10.5}
            assert {point.test_point_id for point in report.flex.strict_scenario_records} == expected_strict
            assert {point.test_point_id for point in report.flex.comparison_records} == expected_nearby
            for point in report.flex.observations:
                assert point.k_mm2_s == float(expected[point.reference.test_point_id]["burning_rate_constant_mm2_s"])
            for group in report.flex.groups:
                raw_members = [expected[identifier] for identifier in group.record_ids]
                assert len({row["fuel_name"] for row in raw_members}) == 1
                assert len({row["he_percent"] for row in raw_members}) == 1
                assert len({row["co2_percent"] for row in raw_members}) == 1
        elif study == "BASS-II":
            for point in report.bass.observations:
                row = expected[point.reference.test_point_id]
                assert point.oxygen_consumed_points == pytest.approx(float(row["o2_percent_min"]) - float(row["o2_final_percent"]))
                assert point.co2_increase_points == pytest.approx(float(row["co2_final_percent"]) - float(row["co2_initial_percent"]))
        else:
            for point in report.saffire.observations:
                row = expected[point.reference.test_point_id]
                if row["normal_gravity_burn_length_mm_raw"] == "Complete":
                    assert point.normal_gravity_length_mm is None
                    assert point.normal_gravity_length_raw == "Complete"
    payload = json.loads(json.dumps(asdict(report), allow_nan=False))
    assert payload["dataset_revision"] == snapshot.revision
    assert all(source["source_files"] for source in payload["sources"])
    assert BuildFireBehavior()(snapshot.revision, tuple(reversed(matches))).analysis_id == report.analysis_id
