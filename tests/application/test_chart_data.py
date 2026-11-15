from psi_fire.application.chart_data import BuildChartData, PlotExclusion, condition_map, scalar
from psi_fire.application.explore import Match
from psi_fire.domain.model import ColumnInfo, Investigation, O2Basis, TestPoint
from psi_fire.domain.units import Unit


def record(identifier: str, low: float, high: float, phase: str = "test",
           basis: O2Basis = O2Basis.AMBIENT) -> TestPoint:
    return TestPoint(investigation_id="TEST", test_point_id=identifier, record_level=phase,
                     o2_percent_min=low, o2_percent_max=high, o2_basis=basis,
                     source_file="synthetic.csv", source_row="2", provenance_status="verified",
                     extras={"burn_time_s": 10.0})


def test_range_has_no_artificial_midpoint() -> None:
    assert scalar(record("a", 20, 30), "o2_percent") is None
    assert scalar(record("b", 30, 30), "o2_percent") == 30


def test_plot_excludes_ranges_missing_basis_and_daily_records() -> None:
    points = (record("exact", 30, 30), record("range", 20, 30),
              record("stream", 30, 30, basis=O2Basis.OXIDIZER_STREAM), record("day", 30, 30, "test_day"))
    inv = Investigation(id="TEST", psi_id="TEST", record_level="test", source_files=(), test_points=points,
                        columns={"o2_percent_min": ColumnInfo(kind="quantity", unit=Unit.PERCENT),
                                 "o2_percent_max": ColumnInfo(kind="quantity", unit=Unit.PERCENT),
                                 "burn_time_s": ColumnInfo(kind="quantity", unit=Unit.S)})
    result = BuildChartData()((Match(inv, points),), "o2_percent", "burn_time_s", ("TEST",), O2Basis.AMBIENT)
    assert [r["Record"] for r in result.rows] == ["exact"]
    assert result.eligible == 3 and result.excluded == 2 and result.summaries == 1


def test_partners_count_only_plottable_pairs() -> None:
    points = (record("exact", 30, 30), record("range", 20, 30), record("day", 30, 30, "test_day"))
    inv = Investigation(id="TEST", psi_id="TEST", record_level="test", source_files=(), test_points=points,
                        columns={"o2_percent_min": ColumnInfo(kind="quantity", unit=Unit.PERCENT),
                                 "o2_percent_max": ColumnInfo(kind="quantity", unit=Unit.PERCENT),
                                 "burn_time_s": ColumnInfo(kind="quantity", unit=Unit.S)})
    assert BuildChartData().partners((Match(inv, points),), "o2_percent", ("TEST",), O2Basis.AMBIENT) == {"burn_time_s": 1}


def test_exclusion_diagnostics_reconcile_without_double_counting() -> None:
    exact = record("exact", 30, 30)
    points = (exact, record("range", 20, 30), record("day", 30, 30, "test_day"),
              record("stream", 30, 30, basis=O2Basis.OXIDIZER_STREAM),
              exact.model_copy(update={"test_point_id": "missing_y", "extras": {}}),
              exact.model_copy(update={"test_point_id": "missing_both", "o2_percent_min": None,
                                       "o2_percent_max": None, "extras": {}}))
    inv = Investigation(id="TEST", psi_id="TEST", record_level="test", source_files=(), test_points=points,
                        columns={"o2_percent_min": ColumnInfo(kind="quantity", unit=Unit.PERCENT),
                                 "o2_percent_max": ColumnInfo(kind="quantity", unit=Unit.PERCENT),
                                 "burn_time_s": ColumnInfo(kind="quantity", unit=Unit.S)})
    builder = BuildChartData()
    matches = (Match(inv, points),)
    data = builder(matches, "o2_percent", "burn_time_s", ("TEST",), O2Basis.AMBIENT)
    report = builder.coverage(matches, "o2_percent", "burn_time_s", ("TEST",), O2Basis.AMBIENT)[0]
    reasons = dict(report.exclusions)
    assert report.plotted == len(data.rows) == 1
    assert report.records == report.plotted + sum(reasons.values()) == 6
    assert reasons == {PlotExclusion.INTERVAL: 1, PlotExclusion.SUMMARY: 1, PlotExclusion.BASIS: 1,
                       PlotExclusion.Y_MISSING: 1, PlotExclusion.BOTH_MISSING: 1}
    excluded_scope = builder.coverage(matches, "o2_percent", "burn_time_s", (), O2Basis.AMBIENT)[0]
    assert excluded_scope.plotted == 0
    assert excluded_scope.exclusions == ((PlotExclusion.CHART_SCOPE, 6),)


def test_condition_map_counts_the_habitat_scenario_by_oxygen_basis() -> None:
    def at(identifier: str, o2: float, psi: float | None, phase: str = "test",
           basis: O2Basis = O2Basis.AMBIENT) -> TestPoint:
        return record(identifier, o2, o2, phase, basis).model_copy(
            update={"pressure_psi_min": psi, "pressure_psi_max": psi, "extras": {}})
    points = (at("inside", 30, 10.2), at("too_high", 30, 10.3), at("too_lean", 29.9, 8),
              at("stream", 40, 8, basis=O2Basis.OXIDIZER_STREAM), at("no_pressure", 40, None), at("day", 40, 8, "test_day"))
    inv = Investigation(id="TEST", psi_id="TEST", record_level="test", source_files=(), test_points=points, columns={})
    other = Investigation(id="OTHER", psi_id="OTHER", record_level="test", source_files=(),
                          test_points=(at("o2_only", 21, None).model_copy(update={"investigation_id": "OTHER"}),),
                          columns={})
    result = condition_map((Match(inv, points), Match(other, other.test_points)))
    assert [r["Record"] for r in result.rows] == ["inside", "too_high", "too_lean", "stream"]
    assert (result.scenario_ambient, result.scenario_stream) == (1, 1)
    assert (result.tests, result.summaries, result.without_pair) == (6, 1, ("OTHER",))
