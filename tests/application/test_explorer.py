from pathlib import Path

import pytest

from psi_fire.application.explore import (
    ExplorationQuery,
    ExploreInvestigations,
    InvalidExplorationQuery,
    Snapshot,
    coverage,
)
from psi_fire.domain.exploration import ConditionRange
from psi_fire.domain.model import Investigation, O2Basis, TestPoint


def point(identifier: str, oxygen: float | None, pressure: float | None,
          basis: O2Basis | None = O2Basis.AMBIENT) -> TestPoint:
    return TestPoint(investigation_id="TEST", test_point_id=identifier, record_level="test",
                     o2_percent_min=oxygen, o2_percent_max=oxygen, o2_basis=basis,
                     pressure_psi_min=pressure, pressure_psi_max=pressure,
                     source_file="synthetic.csv", source_row="2", provenance_status="verified")


def explorer(*points: TestPoint) -> ExploreInvestigations:
    inv = Investigation(id="TEST", psi_id="PSI-TEST", record_level="test",
                        source_files=(), columns={}, test_points=points)
    return ExploreInvestigations(Snapshot("fixture", (inv,)))


def test_conditions_must_match_the_same_record() -> None:
    service = explorer(point("a", 30, 14.7), point("b", 21, 10.2))
    assert not service(ExplorationQuery(oxygen=ConditionRange(lower=30), pressure=ConditionRange(upper=10.2)))
    assert service(ExplorationQuery(oxygen=ConditionRange(lower=30)))[0].points[0].test_point_id == "a"


def test_missing_oxygen_does_not_admit_other_basis() -> None:
    service = explorer(point("unknown", None, 10, None),
                       point("oxidizer", 85, 10, O2Basis.OXIDIZER_STREAM), point("ambient", 30, 10))
    matches = service(ExplorationQuery(oxygen=ConditionRange(lower=30, include_missing=True)))
    assert [p.test_point_id for p in matches[0].points] == ["unknown", "ambient"]
    assert coverage(matches[0].points, "o2_percent", O2Basis.AMBIENT)["eligible"] == 1


@pytest.mark.parametrize("low,high", [(None, None), (30, 20), (float("nan"), None), (-1, 2)])
def test_invalid_ranges_fail_without_widgets(low: float | None, high: float | None) -> None:
    with pytest.raises(ValueError):
        ConditionRange(low, high)


def test_unknown_ids_and_out_of_range_oxygen_fail() -> None:
    service = explorer(point("a", 30, 10))
    with pytest.raises(InvalidExplorationQuery):
        service(ExplorationQuery(ids=("UNKNOWN",)))
    with pytest.raises(InvalidExplorationQuery):
        service(ExplorationQuery(oxygen=ConditionRange(lower=101)))


def test_inclusive_boundary_and_review_filter() -> None:
    service = explorer(point("a", 30, 10.2))
    assert service(ExplorationQuery(oxygen=ConditionRange(30, 30), pressure=ConditionRange(10.2, 10.2)))
    assert not service(ExplorationQuery(review="reviewed"))


def test_application_has_no_outer_layer_imports() -> None:
    import ast
    root = Path(__file__).resolve().parents[2] / "src/psi_fire/application"
    for file in root.glob("*.py"):
        imports = [node.module or "" for node in ast.walk(ast.parse(file.read_text(encoding="utf-8")))
                   if isinstance(node, ast.ImportFrom)]
        assert not any("infrastructure" in name or "streamlit" in name or "pandas" in name for name in imports)


def test_standalone_basis_and_numeric_basis_conflicts() -> None:
    service = explorer(point("unknown", None, 10, None), point("ambient", 30, 10),
                       point("oxidizer", 85, 10, O2Basis.OXIDIZER_STREAM))
    assert [p.test_point_id for p in service(ExplorationQuery(bases=("Not reported",)))[0].points] == ["unknown"]
    assert [p.test_point_id for p in service(ExplorationQuery(bases=("ambient", "oxidizer_stream")))[0].points] == [
        "ambient", "oxidizer"
    ]
    with pytest.raises(InvalidExplorationQuery, match="select only"):
        service(ExplorationQuery(bases=("ambient", "oxidizer_stream"), oxygen=ConditionRange(lower=30)))
    with pytest.raises(InvalidExplorationQuery, match="select only"):
        service(ExplorationQuery(bases=("oxidizer_stream",), oxygen=ConditionRange(lower=30)))
    assert service(ExplorationQuery(bases=("ambient",), oxygen=ConditionRange(lower=30)))


def test_reconcile_preserves_valid_filters_and_reports_removed_labels() -> None:
    service = explorer(point("a", 30, 10))
    original = ExplorationQuery(ids=("TEST", "REMOVED"), fuels=("obsolete",), levels=("test",),
                                search="test", pressure=ConditionRange(upper=11))
    query, removed = service.reconcile(original)
    assert query.ids == ("TEST",) and query.fuels == () and query.levels == ("test",)
    assert query.search == original.search and query.pressure == original.pressure
    assert removed == ("ids: REMOVED", "fuel_name: obsolete")
    assert service(query)


def test_missing_metadata_empty_sensor_list_and_not_reported_claim_are_distinct() -> None:
    from psi_fire.domain.manual import ManualMetadata

    inv = Investigation(id="TEST", psi_id="PSI-TEST", record_level="test", source_files=(),
                        columns={}, test_points=(point("a", 30, 10),))
    missing = {"value": None, "status": "not_reported", "note": "Synthetic sources searched."}
    empty = ManualMetadata.model_validate({"investigation_id": "TEST", "review_status": "draft",
                                          "hardware": missing, "gravity_regime": missing, "pillars": missing,
                                          "sensors": []})
    not_reported = ManualMetadata.model_validate({**empty.model_dump(mode="json"), "sensors": [missing]})
    for manual, selection in ((None, "Metadata unavailable"), (empty, "No entries mapped"),
                               (not_reported, "Not reported")):
        service = ExploreInvestigations(Snapshot("fixture", (inv.model_copy(update={"manual_metadata": manual}),)))
        assert service.options()["sensors"] == (selection,)
        assert service(ExplorationQuery(sensors=(selection,)))
