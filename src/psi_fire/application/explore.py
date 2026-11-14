"""Read-only exploration requests and use cases. No dataframe or UI dependencies."""

from dataclasses import dataclass, replace
from typing import Protocol

from psi_fire.domain.exploration import ConditionRange, conditions_match
from psi_fire.domain.model import Investigation, O2Basis, TestPoint


class DatasetError(ValueError):
    """The requested dataset could not be loaded consistently."""


class InvalidExplorationQuery(ValueError):
    """Invalid filter selections."""


@dataclass(frozen=True)
class Snapshot:
    revision: str
    investigations: tuple[Investigation, ...]


class SnapshotProvider(Protocol):
    def load(self) -> Snapshot: ...


class SnapshotRevisionProvider(Protocol):
    def current_revision(self) -> str: ...


class CheckDatasetFreshness:
    def __init__(self, provider: SnapshotRevisionProvider) -> None:
        self._provider = provider

    def __call__(self, snapshot: Snapshot) -> bool:
        return self._provider.current_revision() == snapshot.revision


@dataclass(frozen=True)
class ExplorationQuery:
    search: str = ""
    ids: tuple[str, ...] = ()
    levels: tuple[str, ...] = ()
    phases: tuple[str, ...] = ()
    fuels: tuple[str, ...] = ()
    directions: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()
    review: str = "all"
    hardware: tuple[str, ...] = ()
    sensors: tuple[str, ...] = ()
    pillars: tuple[str, ...] = ()
    gravity: tuple[str, ...] = ()
    note: str = "any"
    oxygen: ConditionRange | None = None
    basis: O2Basis = O2Basis.AMBIENT
    pressure: ConditionRange | None = None
    flow: ConditionRange | None = None
    bases: tuple[str, ...] = ()


@dataclass(frozen=True)
class Match:
    investigation: Investigation
    points: tuple[TestPoint, ...]


def metadata_values(inv: Investigation, field: str) -> tuple[str, ...]:
    manual = inv.manual_metadata
    if manual is None:
        return ("Metadata unavailable",)
    if field == "sensors":
        return tuple(dict.fromkeys(c.value.instrument if c.value else "Not reported" for c in manual.sensors)) or (
            "No entries mapped",
        )
    claim = getattr(manual, field)
    if claim.value is None:
        return ("Not reported",)
    if isinstance(claim.value, tuple):
        return tuple(str(v) for v in claim.value) or ("No direct pillar",)
    return (str(claim.value),)


def review_state(inv: Investigation) -> str:
    return inv.manual_metadata.review_status.value if inv.manual_metadata else "unavailable"


def coverage(points: tuple[TestPoint, ...], field: str, basis: O2Basis | None = None) -> dict[str, object]:
    eligible = [p for p in points if basis is None or p.o2_basis == basis]
    lows = [getattr(p, field + "_min") for p in eligible if getattr(p, field + "_min") is not None]
    highs = [getattr(p, field + "_max") for p in eligible if getattr(p, field + "_max") is not None]
    return {"reported": len(lows), "eligible": len(eligible), "missing": len(eligible) - len(lows),
            "min": min(lows) if lows else None, "max": max(highs) if highs else None}


class LoadExplorer:
    def __init__(self, provider: SnapshotProvider) -> None:
        self._provider = provider

    def __call__(self) -> Snapshot:
        return self._provider.load()


class ExploreInvestigations:
    _FACETS = (("ids", "ids"), ("levels", "record_level"), ("phases", "fuel_phase"),
               ("fuels", "fuel_name"), ("directions", "flow_direction"), ("lineage", "provenance_status"),
               ("hardware", "hardware"), ("sensors", "sensors"), ("pillars", "pillars"),
               ("gravity", "gravity_regime"), ("bases", "o2_basis"))

    def __init__(self, snapshot: Snapshot) -> None:
        self._snapshot = snapshot

    def options(self) -> dict[str, tuple[str, ...]]:
        invs = self._snapshot.investigations
        points = [p for inv in invs for p in inv.test_points]
        options = {field: tuple(sorted({str(getattr(p, field)) if getattr(p, field) is not None
                                       else "Not reported" for p in points}))
                   for field in ("record_level", "fuel_phase", "fuel_name", "flow_direction", "provenance_status",
                                 "o2_basis")}
        options["ids"] = tuple(sorted(inv.id for inv in invs))
        for field in ("hardware", "sensors", "pillars", "gravity_regime"):
            options[field] = tuple(sorted({v for inv in invs for v in metadata_values(inv, field)}))
        return options

    def reconcile(self, query: ExplorationQuery) -> tuple[ExplorationQuery, tuple[str, ...]]:
        """Preserve valid selections when a newly published snapshot removes labels."""
        options = self.options()
        changes: dict[str, tuple[str, ...]] = {}
        removed: list[str] = []
        for attribute, field in self._FACETS:
            selections = getattr(query, attribute)
            changes[attribute] = tuple(value for value in selections if value in options[field])
            removed.extend(f"{field}: {value}" for value in selections if value not in options[field])
        return replace(query, ids=changes["ids"], levels=changes["levels"], phases=changes["phases"],
                       fuels=changes["fuels"], directions=changes["directions"], lineage=changes["lineage"],
                       hardware=changes["hardware"], sensors=changes["sensors"], pillars=changes["pillars"],
                       gravity=changes["gravity"], bases=changes["bases"]), tuple(removed)

    def __call__(self, query: ExplorationQuery) -> tuple[Match, ...]:
        options = self.options()
        for attribute, field in self._FACETS:
            if set(getattr(query, attribute)) - set(options[field]):
                raise InvalidExplorationQuery(f"Unknown selection for {field}.")
        if query.basis not in tuple(O2Basis):
            raise InvalidExplorationQuery("Unknown oxygen measurement basis.")
        if query.oxygen and query.bases and set(query.bases) != {O2Basis(query.basis).value}:
            raise InvalidExplorationQuery(
                "For an oxygen range, select only its measurement basis or clear Reported oxygen basis."
            )
        if query.oxygen and any(v is not None and v > 100 for v in
                                (query.oxygen.lower, query.oxygen.upper)):
            raise InvalidExplorationQuery("Oxygen bounds must be within 0–100 percent.")
        if query.review not in ("all", "draft", "reviewed", "unavailable") or query.note not in (
            "any", "with note", "without note"
        ):
            raise InvalidExplorationQuery("Unknown review or note selection.")
        results = []
        for inv in sorted(self._snapshot.investigations, key=lambda inv: inv.id):
            text = " ".join((inv.id, inv.psi_id, inv.study_metadata.get("study_title", ""),
                             inv.study_metadata.get("objective", "")))
            if query.search.strip().casefold() not in text.casefold() or (query.ids and inv.id not in query.ids):
                continue
            if query.review != "all" and review_state(inv) != query.review:
                continue
            if any(selected and not set(selected).intersection(metadata_values(inv, field)) for selected, field in
                   ((query.hardware, "hardware"), (query.sensors, "sensors"),
                    (query.pillars, "pillars"), (query.gravity, "gravity_regime"))):
                continue
            points = tuple(p for p in inv.test_points if self._matches(p, query))
            if points:
                results.append(Match(inv, points))
        return tuple(results)

    @staticmethod
    def _matches(point: TestPoint, query: ExplorationQuery) -> bool:
        for selected, field in ((query.levels, "record_level"), (query.phases, "fuel_phase"),
                                (query.fuels, "fuel_name"), (query.directions, "flow_direction"),
                                (query.lineage, "provenance_status")):
            value = getattr(point, field)
            if selected and (str(value) if value is not None else "Not reported") not in selected:
                return False
        if not query.oxygen and query.bases:
            basis = point.o2_basis.value if point.o2_basis else "Not reported"
            if basis not in query.bases:
                return False
        if query.note != "any" and bool(point.provenance_note) != (query.note == "with note"):
            return False
        return conditions_match(point, query.oxygen, query.basis, query.pressure, query.flow)
