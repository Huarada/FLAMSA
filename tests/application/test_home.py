import pytest

from psi_fire.application.explore import Snapshot
from psi_fire.application.home import GetHomeSummary
from psi_fire.domain.model import Investigation, TestPoint


def snapshot() -> Snapshot:
    point = TestPoint(investigation_id="FLEX", test_point_id="r2", record_level="test",
                      source_file="fixture.csv", source_row="2", provenance_status="verified")
    inv = Investigation(id="FLEX", psi_id="PSI-69", record_level="test", source_files=(), columns={},
                        test_points=(point,))
    return Snapshot("fixture", (inv,))


def test_home_links_only_loaded_investigations_and_reports_actual_counts() -> None:
    result = GetHomeSummary(snapshot())("flame")
    assert result.related_ids == ("FLEX",)
    assert result.records == 1 and result.investigations == 1 and result.reviewed_metadata == 0


def test_home_does_not_invent_earth_applications_or_accept_unknown_theme() -> None:
    service = GetHomeSummary(snapshot())
    assert not service("earth").related_ids
    with pytest.raises(ValueError):
        service("unsupported")
