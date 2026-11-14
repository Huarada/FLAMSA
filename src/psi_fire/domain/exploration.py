"""Scientific condition matching, independent of persistence and presentation."""

from dataclasses import dataclass
from math import isfinite

from psi_fire.domain.model import O2Basis, TestPoint


@dataclass(frozen=True)
class ConditionRange:
    lower: float | None = None
    upper: float | None = None
    include_missing: bool = False

    def __post_init__(self) -> None:
        values = [v for v in (self.lower, self.upper) if v is not None]
        if not values or any(not isfinite(v) or v < 0 for v in values):
            raise ValueError("Supply at least one finite, nonnegative bound.")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("Minimum must not exceed maximum.")

    def matches(self, lower: float | None, upper: float | None) -> bool:
        if lower is None or upper is None:
            return self.include_missing
        return (self.lower is None or upper >= self.lower) and (self.upper is None or lower <= self.upper)


def conditions_match(
    point: TestPoint,
    oxygen: ConditionRange | None,
    basis: O2Basis,
    pressure: ConditionRange | None,
    flow: ConditionRange | None,
) -> bool:
    if oxygen is not None:
        if point.o2_basis is not None and point.o2_basis != basis:
            return False
        if point.o2_percent_min is not None and point.o2_basis != basis:
            return False
        if not oxygen.matches(point.o2_percent_min, point.o2_percent_max):
            return False
    return (
        (pressure is None or pressure.matches(point.pressure_psi_min, point.pressure_psi_max))
        and (flow is None or flow.matches(point.flow_speed_cm_s_min, point.flow_speed_cm_s_max))
    )
