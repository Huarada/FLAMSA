import pytest
from pydantic import ValidationError

from psi_fire.domain.model import ColumnInfo, Investigation, TestPoint


def _tp(test_point_id: str = "1", **fields: object) -> TestPoint:
    base = {
        "investigation_id": "X", "test_point_id": test_point_id, "record_level": "test",
        "source_file": "f.csv", "source_row": "2", "provenance_status": "verified",
    }
    return TestPoint.model_validate(base | fields)


def _investigation(*test_points: TestPoint, columns: dict[str, ColumnInfo] | None = None) -> Investigation:
    return Investigation(
        id="X", psi_id="PSI-0", record_level="test", source_files=(), columns=columns or {}, test_points=test_points
    )


def test_o2_outside_physical_range_is_rejected() -> None:
    with pytest.raises(ValidationError, match="outside"):
        _tp(o2_percent_min=21.0, o2_percent_max=3400.0, o2_basis="ambient")


def test_o2_requires_its_basis() -> None:
    with pytest.raises(ValidationError, match="o2_basis"):
        _tp(o2_percent_min=21.0, o2_percent_max=21.0)


def test_range_must_be_ordered_and_complete() -> None:
    with pytest.raises(ValidationError):
        _tp(pressure_psi_min=15.0, pressure_psi_max=14.0)
    with pytest.raises(ValidationError):
        _tp(pressure_psi_min=15.0)


def test_extras_cannot_shadow_core_columns() -> None:
    with pytest.raises(ValidationError, match="shadow"):
        _tp(extras={"fuel_name": "PMMA"})


def test_investigation_rejects_duplicate_ids_and_empty() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        _investigation(_tp("1"), _tp("1"))
    with pytest.raises(ValidationError, match="at least one"):
        _investigation()


def test_variables_are_derived_from_test_points() -> None:
    columns = {
        "burn_time_s": ColumnInfo(kind="quantity", unit="s"),
        "test_date": ColumnInfo(kind="meta"),
    }
    investigation = _investigation(
        _tp("1", fuel_name="PMMA", extras={"burn_time_s": 10.0, "test_date": "a"}),
        _tp("2", fuel_name="PMMA", extras={"burn_time_s": 12.0, "test_date": "b"}),
        columns=columns,
    )
    assert investigation.varied_variables == ["burn_time_s"]
    assert "fuel_name" in investigation.held_constant_variables
    assert "o2_percent" in investigation.unreported_variables  # core condition always assessed
    assert "test_date" not in investigation.varied_variables  # meta columns are bookkeeping
