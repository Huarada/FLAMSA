"""data/solutions_catalog.json: investigation -> derived technology entries (SPEC-003 section 3.4).

Entries are `illustrative` until they carry an archived source; illustrative entries are labeled in the UI and
never count as evidence (ADR-0112, ADR-0113). A missing file means an empty catalog, never invented entries.
"""

import json
from pathlib import Path

from psi_fire.application.answer_types import Solution


class CatalogError(Exception):
    """A catalog entry breaks the rule that sourced entries need a source."""


class JsonSolutionCatalog:
    def __init__(self, path: Path) -> None:
        raw = json.loads(path.read_text(encoding="utf-8"))["entries"] if path.is_file() else []
        entries = []
        for item in raw:
            entry = Solution(item["investigation_id"], item["technology"], item["status"],
                             item.get("source_file"), item.get("locator"))
            if entry.status == "sourced" and not (entry.source_file and entry.locator):
                raise CatalogError(f"{entry.investigation_id}/{entry.technology}: sourced entries need a source")
            entries.append(entry)
        self._entries = tuple(entries)

    def lookup(self, investigation_id: str) -> tuple[Solution, ...]:
        return tuple(e for e in self._entries if e.investigation_id == investigation_id)
