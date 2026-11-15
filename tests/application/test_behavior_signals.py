from dataclasses import replace

import pytest

from psi_fire.application.behavior_signals import flex_signal, gas_signal, length_signal, safety_evidence
from psi_fire.application.behavior_statistics import oxygen_slope
from psi_fire.application.fire_behavior import BuildFireBehavior, FlexGroup, GasChange, RecordReference


def test_flex_evidence_requires_an_identifiable_interval_excluding_zero() -> None:
    estimate, _ = oxygen_slope((15., 20., 25., 30., 35., 40.), (.1, .2, .3, .4, .5, .6), ())
    assert estimate is not None
    group = FlexGroup("fixture", "heptane", "N2", ("test",), (15, 40), (14.7, 14.7), (2, 2),
                      0, 0, estimate, None)
    assert flex_signal(group) == "Higher K associated with higher oxygen"
    # A positive point estimate alone must not create a directional evidence flag.
    uncertain = replace(estimate, lower_slope=-.01, upper_slope=.03)
    assert flex_signal(replace(group, estimate=uncertain)) == "Trend interval includes zero"
    assert flex_signal(replace(group, estimate=replace(estimate, lower_slope=0))) == "Trend interval includes zero"
    negative = replace(estimate, slope_mm2_s_per_o2_point=-.02, lower_slope=-.03, upper_slope=-.01)
    assert flex_signal(replace(group, estimate=negative)) == "Lower K associated with higher oxygen"
    assert flex_signal(replace(group, estimate=None)) == "No identifiable trend"


def test_gas_changes_flag_joint_measured_direction_without_reclassifying_negative_or_zero() -> None:
    reference = RecordReference("BASS-II", "fixture", "source.csv", "2", "verified", None)
    point = GasChange(reference, "pmma", 21, 20, .1, .3, 1, .2, False)
    assert gas_signal(point) == "Oxygen decrease and CO2 increase measured"
    assert gas_signal(replace(point, co2_increase_points=0)) == "No joint oxygen decrease / CO2 increase"
    assert gas_signal(replace(point, oxygen_consumed_points=-.1, negative_change=True)) == (
        "Negative difference; inspect measurements")


@pytest.mark.parametrize(("value", "state", "expected"), [
    (12., "Numeric length; inspect qualifiers", "Positive burned length reported"),
    (None, "Complete (source label)", "Complete burning reported"),
    (0., "Approximately zero", "Zero / near-zero length; not a safety verdict"),
    (0., "Zero length reported", "Zero / near-zero length; not a safety verdict"),
    (None, "Not reported", "Unresolved / missing; inspect source"),
    (None, "Mixed / see source note", "Unresolved / missing; inspect source"),
])
def test_length_evidence_preserves_zero_missing_and_source_categories(value, state, expected) -> None:
    assert length_signal(value, state) == expected


def test_no_records_produces_no_safety_evidence() -> None:
    assert safety_evidence(BuildFireBehavior()("empty", ())) == ()
