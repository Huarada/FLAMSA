"""Integration tests on the real knowledgeBase/ sources: the fixtures are the PSI files themselves."""

from pathlib import Path

import pytest

from psi_fire.application.curate_investigations import CurateInvestigations
from psi_fire.domain.model import Investigation
from psi_fire.infrastructure.curated_store import CuratedRepository, CuratedStore
from psi_fire.infrastructure.ingestion.adapters import ADAPTERS
from psi_fire.infrastructure.ingestion.pipeline import CsvInvestigationCurator
from psi_fire.infrastructure.source_registry import SourceRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def curated(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict[str, Investigation]]:
    registry = SourceRegistry(REPO_ROOT / "data" / "sources.json")
    root = tmp_path_factory.mktemp("curated")
    result = CurateInvestigations(CsvInvestigationCurator(registry, REPO_ROOT), CuratedStore(root))(registry.ids())
    return root, {i.id: i for i in result}


def _tp(investigation: Investigation, test_point_id: str):  # type: ignore[no-untyped-def]
    return next(tp for tp in investigation.test_points if tp.test_point_id == test_point_id)


def test_every_registered_investigation_has_an_adapter_and_curates(curated) -> None:  # type: ignore[no-untyped-def]
    _, investigations = curated
    assert set(investigations) == set(ADAPTERS) == set(SourceRegistry(REPO_ROOT / "data" / "sources.json").ids())


def test_flex_units_and_derived_diluent(curated) -> None:  # type: ignore[no-untyped-def]
    flex = curated[1]["FLEX"]
    first = _tp(flex, "1")
    assert first.o2_percent_min == 21.0 and first.o2_percent_raw == "0.21"
    assert first.pressure_psi_min == pytest.approx(757.7 * 0.0193368)
    assert first.diluent == "N2"
    assert flex.source_files[0].encoding == "cp1252"
    assert any(tp.diluent == "He+N2" for tp in flex.test_points)


def test_same_summary_rows_are_expanded_and_inferred(curated) -> None:  # type: ignore[no-untyped-def]
    same = curated[1]["SAME"]
    assert same.test_point_count == 20
    dbp = _tp(same, "8.4")
    assert dbp.fuel_name == "dibutyl phthalate" and dbp.extras["fuel_name_raw"] == "Dibutyl Phthalate"
    assert dbp.fuel_phase == "liquid"
    assert dbp.provenance_status == "inferred" and dbp.flow_speed_cm_s_min == 10.0


def test_acme_bre_excel_percent_artifact(curated) -> None:  # type: ignore[no-untyped-def]
    row = _tp(curated[1]["ACME-BRE"], "r6")
    assert (row.o2_percent_min, row.o2_percent_raw, row.provenance_status) == (34.0, "3400%", "inferred")


def test_cfi_g_inverse_flames_report_oxidizer_stream_o2(curated) -> None:  # type: ignore[no-untyped-def]
    cfig = curated[1]["ACME-CFI-G"]
    assert _tp(cfig, "21196 A2").o2_basis == "oxidizer_stream"
    assert _tp(cfig, "21088A1").o2_basis == "ambient"
    assert max(tp.o2_percent_max or 0 for tp in cfig.test_points) > 40  # highest-O2 microgravity data in PSI


def test_notes_and_continuations_are_not_test_points(curated) -> None:  # type: ignore[no-untyped-def]
    saffire2 = curated[1]["SAFFIRE-II"]
    assert saffire2.test_point_count == 9 and len(saffire2.source_notes) == 6
    efield_row = _tp(curated[1]["ACME-E-FIELD"], "r3")
    assert (efield_row.extras["fuel_concentration_percent_min"], efield_row.extras["fuel_concentration_percent_max"]) == (70.0, 100.0)


def test_ambiguous_value_is_never_guessed(curated) -> None:  # type: ignore[no-untyped-def]
    row = _tp(curated[1]["SAFFIRE-II"], "2-4")
    assert "sample_thickness_mm" not in row.extras and row.extras["sample_thickness_mm_raw"] == "037 mm"


def test_identical_rows_are_kept_and_flagged(curated) -> None:  # type: ignore[no-untyped-def]
    cfi = curated[1]["CFI"]
    assert cfi.test_point_count == 87
    assert _tp(cfi, "r81").provenance_note == "identical to row 24"


def test_repository_round_trip(curated) -> None:  # type: ignore[no-untyped-def]
    root, investigations = curated
    repository = CuratedRepository(root)
    for loaded in repository.all():
        assert loaded == investigations[loaded.id]


def test_dataframe_view_has_all_test_points(curated) -> None:  # type: ignore[no-untyped-def]
    root, investigations = curated
    frame = CuratedRepository(root).to_dataframe()
    assert len(frame) == sum(i.test_point_count for i in investigations.values())
    assert {"investigation_id", "o2_percent_min", "pressure_psi_min", "source_file"} <= set(frame.columns)


def test_output_is_deterministic(curated, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    root, investigations = curated
    store = CuratedStore(tmp_path)
    for investigation in investigations.values():
        store.save(investigation)
    for file in root.rglob("*.*"):
        assert (tmp_path / file.relative_to(root)).read_bytes() == file.read_bytes()
