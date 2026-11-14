"""Grounded homepage projections; thematic navigation is not a relevance ranking."""

from dataclasses import dataclass

from psi_fire.application.explore import Snapshot


@dataclass(frozen=True)
class HomeSummary:
    investigations: int
    records: int
    reviewed_metadata: int
    related_ids: tuple[str, ...]


class GetHomeSummary:
    def __init__(self, snapshot: Snapshot) -> None:
        self._snapshot = snapshot

    def __call__(self, theme: str) -> HomeSummary:
        invs = self._snapshot.investigations
        starting_points = {
            "flame": ("FLEX", "FLEX-2", "CFI"),
            "habitats": ("BASS", "BASS-II", "SAFFIRE-I", "SAFFIRE-II", "SAFFIRE-III", "ACME-BRE"),
            "detection": ("SAME", "SAME-R", "ACME-CFI-G", "SPICE"),
        }
        if theme == "earth":
            candidates = tuple(inv.id for inv in invs if inv.manual_metadata and any(
                claim.value is not None for claim in inv.manual_metadata.earth_applications))
        elif theme in starting_points:
            candidates = starting_points[theme]
        else:
            raise ValueError("Unknown homepage research theme.")
        available = {inv.id for inv in invs}
        return HomeSummary(len(invs), sum(len(inv.test_points) for inv in invs),
                           sum(inv.manual_metadata is not None and inv.manual_metadata.review_status.value == "reviewed"
                               for inv in invs), tuple(key for key in candidates if key in available))
