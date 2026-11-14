import json
from dataclasses import asdict
from math import sqrt

import pytest

from psi_fire.application.behavior_statistics import oxygen_slope
from psi_fire.application.explore import Match
from psi_fire.application.fire_behavior import BehaviorDataError, BehaviorSettings, BuildFireBehavior
from psi_fire.domain.model import ColumnInfo, Investigation, TestPoint


def flex_point(identifier: str, oxygen: float, diameter: float = 2, pressure: float | None = 14.7,
               he: float = 0) -> TestPoint:
    return TestPoint(investigation_id="FLEX", test_point_id=identifier, record_level="test", fuel_name="methanol",
                     diluent="N2" if he == 0 else "He+N2", o2_basis="ambient", o2_percent_min=oxygen,
                     o2_percent_max=oxygen, pressure_psi_min=pressure, pressure_psi_max=pressure,
                     source_file="synthetic.csv", source_row=identifier, provenance_status="verified",
                     extras={"burning_rate_constant_mm2_s": .3 + .01 * oxygen, "droplet_initial_diameter_mm": diameter,
                             "he_percent": he, "co2_percent": 0})


def match(study: str, points: tuple[TestPoint, ...]) -> Match:
    units = {"burning_rate_constant_mm2_s": "mm2_s", "droplet_initial_diameter_mm": "mm", "he_percent": "percent",
             "co2_percent": "percent", "pressure_psi_min": "psi", "o2_percent_min": "percent",
             "o2_final_percent": "percent", "co2_initial_percent": "percent", "co2_final_percent": "percent",
             "microgravity_burn_length_mm": "mm", "normal_gravity_burn_length_mm": "mm",
             "microgravity_spread_rate_cm_s": "cm_s", "normal_gravity_spread_rate_cm_s": "cm_s"}
    columns = {key: ColumnInfo(kind="quantity", unit=unit, source_headers=(key,)) for key, unit in units.items()}
    for point in points:
        for key in point.extras:
            if key not in columns:
                columns[key] = ColumnInfo(kind="raw" if key.endswith("_raw") else "text", source_headers=(key,))
    inv = Investigation(id=study, psi_id="synthetic", record_level="test", source_files=(), columns=columns,
                        test_points=points)
    return Match(inv, points)


def test_adjusted_slope_recovers_known_effect_and_analytic_confidence_interval() -> None:
    oxygen, diameter, pressure, response = [], [], [], []
    for x in (15, 20, 25, 30):
        for d in (1, 2, 3):
            for p, sign in ((14.5, -1), (14.8, 1)):
                oxygen.append(x)
                diameter.append(d)
                pressure.append(p)
                response.append(.5 + .02 * (x - 22.5) - .1 * (d - 2) + .3 * (p - 14.65) + .01 * (d - 2) * sign)
    fit, reason = oxygen_slope(tuple(oxygen), tuple(response),
                               (("pressure_psi", tuple(pressure)), ("diameter_mm", tuple(diameter))))
    assert fit is not None and reason is None
    assert fit.slope_mm2_s_per_o2_point == pytest.approx(.02)
    # Orthogonal factorial design: SSE=.0016, df=20, Sxx=750; t(.975,20)=2.085963447.
    expected_margin = 2.085963447 * sqrt((.0016 / 20) / 750)
    assert fit.lower_slope == pytest.approx(.02 - expected_margin)
    assert fit.upper_slope == pytest.approx(.02 + expected_margin)
    assert fit.residual_df == 20
    assert fit.line[0].oxygen_percent == 15 and fit.line[-1].oxygen_percent == 30
    assert all(point.lower_k_mm2_s <= point.expected_k_mm2_s <= point.upper_k_mm2_s for point in fit.line)


def test_adjustment_removes_diameter_confounding_instead_of_reporting_a_pooled_effect() -> None:
    x = (15., 20., 25., 30., 35., 40., 18., 28.)
    d = (1., 1.5, 2.2, 2.6, 3.4, 3.8, 2.5, 1.2)
    y = tuple(.7 + .03 * oxygen - .12 * diameter for oxygen, diameter in zip(x, d, strict=True))
    adjusted, _ = oxygen_slope(x, y, (("diameter_mm", d),))
    pooled, _ = oxygen_slope(x, y, ())
    assert adjusted is not None and pooled is not None
    assert adjusted.slope_mm2_s_per_o2_point == pytest.approx(.03)
    assert abs(pooled.slope_mm2_s_per_o2_point - .03) > .005


@pytest.mark.parametrize("x,controls,fragment", [
    ((1., 2., 3.), (), "observations"),
    ((1., 1., 2., 2., 2., 1.), (), "distinct oxygen"),
    ((1., 2., 3., 4., 5., 6.), (("diameter", (1., 2., 3., 4., 5., 6.)),), "collinear"),
])
def test_unidentifiable_slopes_are_withheld(x, controls, fragment: str) -> None:
    estimate, reason = oxygen_slope(x, tuple(2 * value for value in x), controls)
    assert estimate is None and fragment in reason


def test_blend_strata_pressure_and_missingness_never_mix_into_a_fit() -> None:
    points = tuple(flex_point(str(index), oxygen, he=helium) for index, (oxygen, helium) in enumerate(
        [(oxygen, helium) for helium in (15., 15.00000001) for oxygen in (15., 20., 25., 30., 35., 40.)]
    )) + (flex_point("low-pressure", 35, pressure=10.2), flex_point("missing-pressure", 35, pressure=None))
    evidence = BuildFireBehavior()("fixture", (match("FLEX", points),)).flex
    assert len(evidence.groups) == 2
    assert all(len(group.record_ids) == 6 for group in evidence.groups)
    assert all(group.estimate is not None for group in evidence.groups)
    assert {item.reference.test_point_id for item in evidence.excluded} == {"low-pressure", "missing-pressure"}
    assert len(evidence.observations) + len(evidence.excluded) == evidence.matched_records


def test_strict_and_approximate_lower_pressure_scenarios_use_exact_values() -> None:
    points = (flex_point("strict", 30, pressure=10.2), flex_point("nearby", 30, pressure=10.35),
              flex_point("outside", 30, pressure=10.51))
    report = BuildFireBehavior()("fixture", (match("FLEX", points),))
    assert [item.test_point_id for item in report.flex.strict_scenario_records] == ["strict"]
    assert {item.test_point_id for item in report.flex.comparison_records} == {"strict", "nearby"}
    assert not report.flex.observations


def test_bass_differences_keep_negative_sign_and_reject_incomplete_pairs() -> None:
    def point(identifier, final, co2_final):
        return TestPoint(investigation_id="BASS-II", test_point_id=identifier, record_level="test", o2_basis="ambient",
                         o2_percent_min=21, o2_percent_max=21, source_file="synthetic.csv", source_row=identifier,
                         provenance_status="verified", extras={"o2_final_percent": final, "co2_initial_percent": .4,
                                                                "co2_final_percent": co2_final})
    points = (point("burn", 20.7, .8), point("negative", 21.1, .39), point("missing", 20.8, None))
    evidence = BuildFireBehavior()("fixture", (match("BASS-II", points),)).bass
    burn, negative = evidence.observations
    assert burn.oxygen_consumed_points == pytest.approx(.3) and burn.co2_increase_points == pytest.approx(.4)
    assert negative.negative_change and negative.oxygen_consumed_points == pytest.approx(-.1)
    assert negative.co2_increase_points == pytest.approx(-.01)
    assert len(evidence.excluded) == 1 and evidence.excluded[0].reference.test_point_id == "missing"


def test_saffire_complete_acceleratory_and_missing_rates_are_not_numeric_observations() -> None:
    point = TestPoint(investigation_id="SAFFIRE-II", test_point_id="2-1", record_level="test", fuel_name="silicone",
                      source_file="synthetic.csv", source_row="2", provenance_status="verified",
                      extras={"microgravity_burn_length_mm": 0., "microgravity_burn_length_mm_raw": "~ 0",
                              "normal_gravity_burn_length_mm_raw": "Complete",
                              "normal_gravity_spread_rate_cm_s_raw": "Acceleratory"})
    result = BuildFireBehavior()("fixture", (match("SAFFIRE-II", (point,)),)).saffire.observations[0]
    assert result.microgravity_length_mm == 0 and result.microgravity_length_raw == "~ 0"
    assert result.normal_gravity_length_mm is None and result.normal_gravity_length_raw == "Complete"
    assert result.microgravity_rate_cm_s is None and result.normal_gravity_rate_cm_s is None
    assert result.normal_gravity_rate_raw == "Acceleratory"
    assert result.microgravity_length_state == "Approximately zero"


def test_analysis_identity_export_and_units_are_reproducible_and_fail_closed() -> None:
    points = tuple(flex_point(str(index), oxygen) for index, oxygen in enumerate((15., 20., 25., 30., 35., 40.)))
    source = match("FLEX", points)
    service = BuildFireBehavior()
    report = service("fixture", (source,))
    reversed_report = service("fixture", (Match(source.investigation, tuple(reversed(points))),))
    assert report.analysis_id == reversed_report.analysis_id
    payload = json.loads(json.dumps(asdict(report), allow_nan=False))
    assert payload["flex"]["observations"][0]["reference"]["source_file"] == "synthetic.csv"
    assert service("other-revision", (source,)).analysis_id != report.analysis_id
    columns = {**source.investigation.columns, "burning_rate_constant_mm2_s": ColumnInfo(kind="quantity", unit="mm")}
    wrong = source.investigation.model_copy(update={"columns": columns})
    with pytest.raises(BehaviorDataError, match="mm2_s"):
        service("fixture", (Match(wrong, points),))
    with pytest.raises(ValueError, match="5%"):
        BehaviorSettings(pressure_tolerance_fraction=.1)


def test_absent_studies_remain_empty_and_no_data_is_injected() -> None:
    report = BuildFireBehavior()("fixture", ())
    assert not report.flex.observations and not report.bass.observations and not report.saffire.observations
    assert not report.sources
