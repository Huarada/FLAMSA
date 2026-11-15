"""Comparable reported scalar quantities for exploratory charts, without UI dependencies."""

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from psi_fire.application.explore import Match
from psi_fire.domain.model import O2Basis, TestPoint
from psi_fire.domain.ranking import LUNAR_O2_PERCENT, LUNAR_PRESSURE_PSI

# Demonstration habitat scenario (lunar base): at least this O2 percent at or below this pressure in psi.
LUNAR_OXYGEN_MIN = LUNAR_O2_PERCENT
LUNAR_PRESSURE_MAX = LUNAR_PRESSURE_PSI


@dataclass(frozen=True)
class PlotVariable:
    key: str
    unit: str

    @property
    def label(self) -> str:
        names = {"o2_percent": "Oxygen concentration", "pressure_psi": "Pressure",
                 "flow_speed_cm_s": "Flow speed"}
        units = {"percent": "%", "cm_s": "cm/s", "mm2_s": "mm²/s", "mg_s": "mg/s", "k": "K"}
        key = self.key.removesuffix("_" + self.unit) if self.unit else self.key
        name = names.get(self.key, key.replace("_", " ").capitalize())
        return name + (f" ({units.get(self.unit, self.unit)})" if self.unit else "")


@dataclass(frozen=True)
class ChartData:
    rows: tuple[dict[str, str | float], ...]
    eligible: int
    excluded: int
    summaries: int = 0  # daily or matrix records: never observations, so never counted as eligible


class PlotExclusion(StrEnum):
    CHART_SCOPE = "not_selected_for_chart"
    SUMMARY = "summary_record"
    BASIS = "incompatible_or_unknown_oxygen_basis"
    BOTH_MISSING = "both_quantities_missing"
    X_MISSING = "horizontal_quantity_missing"
    Y_MISSING = "vertical_quantity_missing"
    INTERVAL = "interval_instead_of_scalar"
    NONNUMERIC = "not_a_finite_numeric_scalar"


@dataclass(frozen=True)
class InvestigationPlotCoverage:
    investigation_id: str
    records: int
    plotted: int
    exclusions: tuple[tuple[PlotExclusion, int], ...]
    available_quantities: tuple[PlotVariable, ...]
    record_levels: tuple[str, ...]


@dataclass(frozen=True)
class ConditionMap:
    """Individual tests reporting scalar O2 and pressure, and how many fall in the habitat scenario."""

    rows: tuple[dict[str, str | float], ...]
    without_pair: tuple[str, ...]  # investigations in scope with no test reporting both
    tests: int  # individual tests in scope
    summaries: int  # daily or matrix records in scope, never plotted
    scenario_ambient: int  # chamber atmosphere O2: the habitat question
    scenario_stream: int  # inverse flames: O2 is the burner stream, not the atmosphere


def condition_map(matches: tuple[Match, ...]) -> ConditionMap:
    rows: list[dict[str, str | float]] = []
    tests = summaries = ambient = stream = 0
    without: list[str] = []
    for match in matches:
        before = len(rows)
        for point in match.points:
            if point.record_level.value != "test":
                summaries += 1
                continue
            tests += 1
            oxygen, pressure = scalar(point, "o2_percent"), scalar(point, "pressure_psi")
            if oxygen is None or pressure is None:
                continue
            basis = point.o2_basis or O2Basis.AMBIENT
            inside = oxygen >= LUNAR_OXYGEN_MIN and pressure <= LUNAR_PRESSURE_MAX
            ambient += inside and basis == O2Basis.AMBIENT
            stream += inside and basis != O2Basis.AMBIENT
            rows.append({"O2": oxygen, "Pressure": pressure, "Investigation": match.investigation.id,
                         "Record": point.test_point_id, "Fuel": point.fuel_name or "Not reported",
                         "Oxygen basis": "Chamber atmosphere" if basis == O2Basis.AMBIENT else "Burner stream",
                         "Source row": point.source_row})
        if len(rows) == before:
            without.append(match.investigation.id)
    return ConditionMap(tuple(rows), tuple(without), tests, summaries, ambient, stream)


def scalar(point: TestPoint, key: str) -> float | None:
    value = point.value(key)
    if value is None:
        low, high = point.value(key + "_min"), point.value(key + "_max")
        if low != high:
            return None
        value = low
    return float(value) if isinstance(value, (int, float)) and isfinite(value) else None


def plot_exclusion(point: TestPoint, x: str, y: str, basis: O2Basis) -> PlotExclusion | None:
    """One primary reason per unplottable record, shared by plotting and diagnostics."""
    if point.record_level.value != "test":
        return PlotExclusion.SUMMARY
    # Missing O2 is explained as missing data below rather than as a fabricated basis mismatch.
    if ((x.startswith("o2_") or y.startswith("o2_")) and point.o2_basis != basis
            and scalar(point, x if x.startswith("o2_") else y) is not None):
        return PlotExclusion.BASIS
    missing = [all(point.value(name) is None for name in (key, key + "_min", key + "_max")) for key in (x, y)]
    if all(missing):
        return PlotExclusion.BOTH_MISSING
    if missing[0]:
        return PlotExclusion.X_MISSING
    if missing[1]:
        return PlotExclusion.Y_MISSING
    if (x.startswith("o2_") or y.startswith("o2_")) and point.o2_basis != basis:
        return PlotExclusion.BASIS
    if scalar(point, x) is None or scalar(point, y) is None:
        if any(point.value(key) is None and point.value(key + "_min") is not None
               and point.value(key + "_max") is not None
               and point.value(key + "_min") != point.value(key + "_max") for key in (x, y)):
            return PlotExclusion.INTERVAL
        return PlotExclusion.NONNUMERIC
    return None


class BuildChartData:
    def variables(self, matches: tuple[Match, ...]) -> tuple[PlotVariable, ...]:
        units: dict[str, set[str]] = {}
        for match in matches:
            for key, info in match.investigation.columns.items():
                if info.kind != "quantity":
                    continue
                if key.endswith("_max"):
                    continue
                base = key.removesuffix("_min")
                unit = info.unit.value if info.unit else ""
                if any(scalar(point, base) is not None for point in match.points):
                    units.setdefault(base, set()).add(unit)
        return tuple(PlotVariable(key, next(iter(values))) for key, values in sorted(units.items())
                     if len(values) == 1)

    def __call__(self, matches: tuple[Match, ...], x: str, y: str,
                 ids: tuple[str, ...], basis: O2Basis) -> ChartData:
        variables = {v.key for v in self.variables(matches)}
        if x not in variables or y not in variables or x == y:
            raise ValueError("Choose two distinct quantities with consistent canonical units.")
        if set(ids) - {m.investigation.id for m in matches}:
            raise ValueError("Chart investigations must belong to the applied filter result.")
        return self._collect(matches, x, y, ids, basis)

    def partners(self, matches: tuple[Match, ...], x: str, ids: tuple[str, ...],
                 basis: O2Basis) -> dict[str, int]:
        """Plottable record count against `x` for every other quantity, so empty axis pairs are never offered."""
        points = [point for match in matches if match.investigation.id in ids for point in match.points
                  if point.record_level.value == "test" and scalar(point, x) is not None
                  and (not x.startswith("o2_") or point.o2_basis == basis)]
        return {v.key: sum(scalar(point, v.key) is not None
                           and (not v.key.startswith("o2_") or point.o2_basis == basis) for point in points)
                for v in self.variables(matches) if v.key != x}

    def coverage(self, matches: tuple[Match, ...], x: str, y: str, ids: tuple[str, ...],
                 basis: O2Basis) -> tuple[InvestigationPlotCoverage, ...]:
        # Validate the request with the same contract used to build the plot.
        self(matches, x, y, ids, basis)
        results = []
        for match in matches:
            exclusions: dict[PlotExclusion, int] = {}
            plotted = 0
            for point in match.points:
                reason = (plot_exclusion(point, x, y, basis) if match.investigation.id in ids
                          else PlotExclusion.CHART_SCOPE)
                if reason is None:
                    plotted += 1
                else:
                    exclusions[reason] = exclusions.get(reason, 0) + 1
            results.append(InvestigationPlotCoverage(match.investigation.id, len(match.points), plotted,
                                                      tuple(exclusions.items()), self.variables((match,)),
                                                      tuple(sorted({p.record_level.value for p in match.points}))))
        return tuple(results)

    @staticmethod
    def _collect(matches: tuple[Match, ...], x: str, y: str, ids: tuple[str, ...], basis: O2Basis) -> ChartData:
        rows: list[dict[str, str | float]] = []
        eligible = summaries = 0
        for match in matches:
            if match.investigation.id not in ids:
                continue
            for point in match.points:
                # Planned envelopes and daily summaries are not individual observations.
                reason = plot_exclusion(point, x, y, basis)
                if reason is PlotExclusion.SUMMARY:
                    summaries += 1
                    continue
                eligible += 1
                if reason is not None:
                    continue
                a, b = scalar(point, x), scalar(point, y)
                assert a is not None and b is not None
                rows.append({"x": a, "y": b, "Investigation": match.investigation.id,
                             "Record": point.test_point_id, "Fuel": point.fuel_name or "Not reported",
                             "Flow direction": str(point.flow_direction or "Not reported"),
                             "Oxygen basis": str(point.o2_basis or "Not reported"),
                             "Lineage": point.provenance_status.value,
                             "Source row": point.source_row})
        return ChartData(tuple(rows), eligible, eligible - len(rows), summaries)
