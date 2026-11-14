"""Fuel labels and categorical casing are standardized without losing the raw value (ADR-0060/0061)."""

from pathlib import Path

import pytest

from psi_fire.application.curate_investigations import CurateInvestigations
from psi_fire.domain.model import Investigation
from psi_fire.infrastructure.curated_store import CuratedStore
from psi_fire.infrastructure.ingestion.fuel_names import FuelLabel, normalize_fuel_label
from psi_fire.infrastructure.ingestion.pipeline import CsvInvestigationCurator
from psi_fire.infrastructure.source_registry import SourceRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(("raw", "expected"), [
    ("100%C2H4", FuelLabel("ethylene", None, 100.0)),
    ("75 % Propylene", FuelLabel("propylene", None, 75.0)),
    ("40% CH4 (balance N2) including 2 pyrometry calibration tests", FuelLabel("methane", None, 40.0)),
    ("Methanol", FuelLabel("methanol", None, None)),
    ("Cotton-Fiberglass (SIBAL)", FuelLabel("sibal", None, None)),
    ("PMMA & Nomex", FuelLabel("pmma+nomex", None, None)),
    ("parrafin wax slab", FuelLabel("paraffin wax", "slab", None)),
    ("flat wax slab", FuelLabel("wax", "slab", None)),
    ("1/2\" clear PMMA rod", FuelLabel("pmma", "rod", None)),
    ("IsoOctane (pure)", FuelLabel("iso-octane", None, 100.0)),
    ("Heptane (50%) IsoOctane (50%) (mixture)", FuelLabel("heptane+iso-octane", None, None)),
    ("[.60]/[.40] C12H26/iso-dodecane", FuelLabel("n-dodecane+iso-dodecane", None, None)),
])
def test_label_is_reduced_to_what_it_states(raw: str, expected: FuelLabel) -> None:
    assert normalize_fuel_label(raw) == expected


@pytest.mark.parametrize("raw", ['1/4" clear rod', "2 cm sphere", "SOOT Cleaning"])
def test_material_is_never_guessed(raw: str) -> None:
    assert normalize_fuel_label(raw).name is None


@pytest.fixture(scope="module")
def curated(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Investigation]:
    registry = SourceRegistry(REPO_ROOT / "data" / "sources.json")
    root = tmp_path_factory.mktemp("standardized")
    result = CurateInvestigations(CsvInvestigationCurator(registry, REPO_ROOT), CuratedStore(root))(registry.ids())
    return {i.id: i for i in result}


def test_categorical_values_have_a_single_casing(curated: dict[str, Investigation]) -> None:
    cfig = curated["ACME-CFI-G"]
    for column in ("flame_configuration", "hot_ignition", "flame_color"):
        values = {str(tp.extras[column]) for tp in cfig.test_points if column in tp.extras}
        assert values == {v.lower() for v in values}, column
    assert {tp.extras["flame_configuration"] for tp in cfig.test_points} == {"normal", "inverse"}


def test_every_fuel_name_is_lower_case_and_raw_label_is_kept(curated: dict[str, Investigation]) -> None:
    unlabeled = []
    for investigation in curated.values():
        for point in investigation.test_points:
            assert point.fuel_name is None or point.fuel_name == point.fuel_name.lower()
            if point.fuel_name is None and "fuel_name_raw" not in point.extras:
                unlabeled.append(investigation.id)
    assert set(unlabeled) == {"SAFFIRE-II"}  # the two rows whose source cell is empty


def test_flex_zero_pressure_is_missing_not_zero(curated: dict[str, Investigation]) -> None:
    flex = curated["FLEX"]
    point = next(tp for tp in flex.test_points if tp.test_point_id == "114")
    assert point.pressure_psi_min is None and point.pressure_psi_raw == "0"
    assert point.provenance_status == "inferred"
    assert all((tp.pressure_psi_min or 1) > 0 for tp in flex.test_points)


def test_same_r_silicone_uses_the_literature_name(curated: dict[str, Investigation]) -> None:
    same_r = {tp.fuel_name for tp in curated["SAME-R"].test_points}
    assert "silicone rubber" in same_r and "silicone" not in same_r
    assert {tp.fuel_name for tp in curated["SAME"].test_points} >= {"silicone rubber"}
    row = next(tp for tp in curated["SAME-R"].test_points if tp.fuel_name == "silicone rubber")
    assert row.extras["fuel_name_raw"] == "Silicone"
