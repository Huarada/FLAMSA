"""Performance changes must preserve plotted counts and revision/filter cache boundaries."""

from pathlib import Path
from unittest.mock import patch

import pytest

from psi_fire.application.chart_data import BuildChartData
from psi_fire.application.explore import ExplorationQuery, ExploreInvestigations
from psi_fire.domain.model import O2Basis
from psi_fire.infrastructure.explorer import FileSnapshotProvider
from psi_fire.interface.dashboard_cache import comparison_projection, partner_counts, record_scope
from psi_fire.interface.reference_dashboard import MAX_PICK_GRID_POINTS, pick_grid

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("x", ["o2_percent", "pressure_psi", "burn_time_s", "co2_initial_percent"])
@pytest.mark.parametrize("basis", list(O2Basis))
def test_count_only_axis_options_equal_actual_plot_eligibility(x: str, basis: O2Basis) -> None:
    snapshot = FileSnapshotProvider(ROOT).load()
    matches = ExploreInvestigations(snapshot)(ExplorationQuery())
    builder = BuildChartData()
    ids = tuple(match.investigation.id for match in matches)
    counts = builder.partners(matches, x, ids, basis)
    assert counts == {key: len(builder(matches, x, key, ids, basis).rows) for key in counts}
    with patch.object(builder, "_collect", side_effect=AssertionError("Counting must not allocate plot rows")):
        assert builder.partners(matches, x, ids, basis) == counts


def test_projection_cache_separates_revision_records_scope_axes_and_basis() -> None:
    snapshot = FileSnapshotProvider(ROOT).load()
    explore = ExploreInvestigations(snapshot)
    matches = explore(ExplorationQuery(ids=("FLEX", "BASS-II")))
    flex = explore(ExplorationQuery(ids=("FLEX",)))
    ids = ("FLEX", "BASS-II")
    partner_counts.clear()
    comparison_projection.clear()
    counts = partner_counts(snapshot.revision, record_scope(matches), "o2_percent", ids, O2Basis.AMBIENT, matches)
    with patch.object(BuildChartData, "partners", side_effect=AssertionError("Expected cache hit")):
        assert partner_counts(snapshot.revision, record_scope(matches), "o2_percent", ids, O2Basis.AMBIENT, matches) == counts
    with patch.object(BuildChartData, "partners", wraps=BuildChartData().partners) as compute:
        for revision, points, axes, selected, basis in (
            ("new-revision", matches, "o2_percent", ids, O2Basis.AMBIENT),
            (snapshot.revision, flex, "o2_percent", ("FLEX",), O2Basis.AMBIENT),
            (snapshot.revision, matches, "burn_time_s", ids, O2Basis.AMBIENT),
            (snapshot.revision, matches, "o2_percent", ("FLEX",), O2Basis.AMBIENT),
            (snapshot.revision, matches, "o2_percent", ids, O2Basis.OXIDIZER_STREAM),
        ):
            partner_counts(revision, record_scope(points), axes, selected, basis, points)
        assert compute.call_count == 5
    data, reports = comparison_projection(snapshot.revision, record_scope(matches), "o2_percent", "burn_time_s",
                                          ids, O2Basis.AMBIENT, matches)
    assert len(data.rows) == sum(report.plotted for report in reports)
    data.rows[0]["x"] = -999
    again, _ = comparison_projection(snapshot.revision, record_scope(matches), "o2_percent", "burn_time_s",
                                     ids, O2Basis.AMBIENT, matches)
    assert again.rows[0]["x"] != -999


@pytest.mark.parametrize(("right", "pressure"), [(88, 73.5), (35, 15), (103, 100)])
def test_scenario_picker_has_a_bounded_interaction_mesh(right: float, pressure: float) -> None:
    grid = pick_grid(right, pressure)
    assert 0 < len(grid) <= MAX_PICK_GRID_POINTS
    assert grid.o2.min() == 10 and grid.psi.min() == 0
    assert grid.o2.max() <= right and grid.psi.max() >= pressure
