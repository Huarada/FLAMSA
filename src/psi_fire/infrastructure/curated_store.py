"""data/curated/<investigation_id>/{investigation.json, test_points.csv}: writer and repository (ADR-0007)."""

import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

from psi_fire.domain.model import CORE_COLUMNS, CORE_COLUMNS_SET, ExtraValue, Investigation, TestPoint
from psi_fire.infrastructure.ingestion.quantity_parser import format_number

if TYPE_CHECKING:
    import pandas as pd

INVESTIGATION_FILE = "investigation.json"
TEST_POINTS_FILE = "test_points.csv"
_COMPUTED_FIELDS = ("test_point_count", "varied_variables", "held_constant_variables", "unreported_variables")


def _csv_columns(investigation: Investigation) -> list[str]:
    return [*CORE_COLUMNS, *(c for c in investigation.columns if c not in CORE_COLUMNS_SET)]


def _cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return format_number(value)
    return str(getattr(value, "value", value))


class CuratedStore:
    """Implements InvestigationStore. Output is deterministic: same input, byte-identical files."""

    def __init__(self, curated_root: Path) -> None:
        self._root = curated_root

    def save(self, investigation: Investigation) -> None:
        folder = self._root / investigation.id
        folder.mkdir(parents=True, exist_ok=True)
        document = investigation.model_dump(mode="json", exclude={"test_points"})
        (folder / INVESTIGATION_FILE).write_text(
            json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        columns = _csv_columns(investigation)
        with (folder / TEST_POINTS_FILE).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(columns)
            for tp in investigation.test_points:
                writer.writerow(_cell(tp.value(c)) for c in columns)


class CuratedRepository:
    """Implements InvestigationRepository over data/curated/. One source, many views (ADR-0007)."""

    def __init__(self, curated_root: Path) -> None:
        self._root = curated_root

    def ids(self) -> list[str]:
        return sorted(p.name for p in self._root.iterdir() if (p / INVESTIGATION_FILE).is_file())

    def all(self) -> list[Investigation]:
        return [self.get(i) for i in self.ids()]

    def get(self, investigation_id: str) -> Investigation:
        folder = self._root / investigation_id
        if not (folder / INVESTIGATION_FILE).is_file() or not (folder / TEST_POINTS_FILE).is_file():
            raise FileNotFoundError(f"{folder} must contain {INVESTIGATION_FILE} and {TEST_POINTS_FILE}")
        document = json.loads((folder / INVESTIGATION_FILE).read_text(encoding="utf-8"))
        for name in _COMPUTED_FIELDS:
            document.pop(name, None)
        quantity_columns = {name for name, info in document["columns"].items() if info["kind"] == "quantity"}
        with (folder / TEST_POINTS_FILE).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        document["test_points"] = [_test_point(row, quantity_columns) for row in rows]
        return Investigation.model_validate(document)

    def to_dataframe(self) -> "pd.DataFrame":
        """All test points of all investigations in one tidy frame (Streamlit, model training)."""
        import pandas as pd

        frames = [pd.read_csv(self._root / i / TEST_POINTS_FILE, dtype={"test_point_id": str}) for i in self.ids()]
        return pd.concat(frames, ignore_index=True, sort=False)


def _test_point(row: dict[str, str], quantity_columns: set[str]) -> TestPoint:
    core = {k: (v or None) for k, v in row.items() if k in CORE_COLUMNS_SET}
    extras: dict[str, ExtraValue] = {}
    for key, raw in row.items():
        if key in CORE_COLUMNS_SET or raw == "":
            continue
        extras[key] = float(raw) if key in quantity_columns else raw
    return TestPoint.model_validate({**core, "extras": extras})
