"""data/sources.json: the only place where raw knowledgeBase/ paths live (ADR-0008)."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceEntry:
    id: str
    psi_id: str
    raw_dir: str
    experimental_tables: tuple[str, ...]
    isa_tab_dir: str | None


class SourceRegistry:
    def __init__(self, registry_path: Path) -> None:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
        self._entries = {
            e["id"]: SourceEntry(e["id"], e["psi_id"], e["raw_dir"], tuple(e["experimental_tables"]), e["isa_tab_dir"])
            for e in raw["investigations"]
        }

    def ids(self) -> list[str]:
        return list(self._entries)

    def get(self, investigation_id: str) -> SourceEntry:
        try:
            return self._entries[investigation_id]
        except KeyError:
            raise KeyError(f"{investigation_id!r} is not registered in data/sources.json") from None
