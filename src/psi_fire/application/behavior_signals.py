"""Deterministic evidence labels, never ignition probabilities or safety thresholds."""

from dataclasses import dataclass

from psi_fire.application.fire_behavior import BehaviorReport, FlexGroup, GasChange


def flex_signal(group: FlexGroup) -> str:
    fit = group.estimate
    if fit is None:
        return "No identifiable trend"
    if fit.lower_slope > 0:
        return "Higher K associated with higher oxygen"
    if fit.upper_slope < 0:
        return "Lower K associated with higher oxygen"
    return "Trend interval includes zero"


def gas_signal(point: GasChange) -> str:
    if point.negative_change:
        return "Negative difference; inspect measurements"
    if point.oxygen_consumed_points > 0 and point.co2_increase_points > 0:
        return "Oxygen decrease and CO2 increase measured"
    return "No joint oxygen decrease / CO2 increase"


def length_signal(value: float | None, state: str) -> str:
    if state == "Complete (source label)":
        return "Complete burning reported"
    if value is not None and value > 0:
        return "Positive burned length reported"
    if state in ("Approximately zero", "Zero length reported"):
        return "Zero / near-zero length; not a safety verdict"
    return "Unresolved / missing; inspect source"


@dataclass(frozen=True)
class SafetyEvidence:
    investigation_id: str
    record_ids: tuple[str, ...]
    condition: str
    signal: str


def safety_evidence(report: BehaviorReport) -> tuple[SafetyEvidence, ...]:
    """Export the same labels as the charts, with identities into the source-backed report."""
    return (
        *(SafetyEvidence("FLEX", group.record_ids, group.label, flex_signal(group)) for group in report.flex.groups),
        *(SafetyEvidence("BASS-II", (point.reference.test_point_id,), "Before / after burn", gas_signal(point))
          for point in report.bass.observations),
        *(SafetyEvidence("SAFFIRE-II", (point.reference.test_point_id,), condition, length_signal(value, state))
          for point in report.saffire.observations
          for condition, value, state in (
              ("Microgravity", point.microgravity_length_mm, point.microgravity_length_state),
              ("1 g", point.normal_gravity_length_mm, point.normal_gravity_length_state))),
    )
