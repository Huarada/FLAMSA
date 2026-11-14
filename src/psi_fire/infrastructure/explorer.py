"""Validated snapshot and registered evidence access adapters."""

import csv
import hashlib
import json
import mimetypes
from math import isfinite
from pathlib import Path

from pydantic import ValidationError

from psi_fire.application.explore import DatasetError, Snapshot
from psi_fire.domain.model import CORE_COLUMNS, Investigation
from psi_fire.infrastructure.curated_store import CuratedRepository


class FileSnapshotProvider:
    def __init__(self, root: Path) -> None:
        self._root = root

    def load(self) -> Snapshot:
        try:
            directories, paths = self._input_paths()
            for directory in directories:
                with (directory / "test_points.csv").open(encoding="utf-8", newline="") as stream:
                    headers = next(csv.reader(stream))
                if len(headers) != len(set(headers)) or not set(CORE_COLUMNS).issubset(headers):
                    raise DatasetError(f"{directory.name}: duplicate or missing core columns.")
            before = self._revision(paths)
            investigations = tuple(CuratedRepository(self._root / "data/curated").all())
            for directory, inv in zip(directories, investigations, strict=True):
                self._validate(directory.name, inv)
            if before != self._revision(paths):
                raise DatasetError("Dataset changed while loading. Wait for curation to finish, then reload.")
            return Snapshot(before, investigations)
        except DatasetError:
            raise
        except (OSError, ValidationError, ValueError, KeyError, csv.Error, StopIteration) as error:
            raise DatasetError("Dataset cannot be loaded. Check curated file pairs and schema validation.") from error

    def current_revision(self) -> str:
        try:
            _, paths = self._input_paths()
            return self._revision(paths)
        except OSError as error:
            raise DatasetError("Cannot check the current curated dataset revision.") from error

    def _input_paths(self) -> tuple[list[Path], list[Path]]:
        directories = sorted(p for p in (self._root / "data/curated").iterdir()
                             if p.is_dir() and not p.name.startswith("."))
        if not directories:
            raise DatasetError("No curated investigations available.")
        paths = [self._root / "data/sources.json"]
        for directory in directories:
            for name in ("investigation.json", "test_points.csv"):
                path = directory / name
                if not path.is_file():
                    raise DatasetError(f"{directory.name}: incomplete curated pair ({name} missing).")
                paths.append(path)
        return directories, paths

    @staticmethod
    def _revision(paths: list[Path]) -> str:
        digest = hashlib.sha256()
        for path in paths:
            digest.update(path.name.encode())
            digest.update(path.read_bytes())
        return digest.hexdigest()

    @staticmethod
    def _validate(directory_id: str, inv: Investigation) -> None:
        if directory_id != inv.id or (inv.manual_metadata and inv.manual_metadata.investigation_id != inv.id):
            raise DatasetError(f"{directory_id}: investigation/manual metadata identity mismatch.")
        for point in inv.test_points:
            if point.record_level != inv.record_level:
                raise DatasetError(f"{inv.id}: inconsistent record granularity.")
            for field in ("o2_percent_min", "o2_percent_max", "pressure_psi_min", "pressure_psi_max",
                          "flow_speed_cm_s_min", "flow_speed_cm_s_max"):
                value = getattr(point, field)
                if value is not None and not isfinite(value):
                    raise DatasetError(f"{inv.id}: nonfinite condition in {point.test_point_id}.")
            if any(isinstance(value, float) and not isfinite(value) for value in point.extras.values()):
                raise DatasetError(f"{inv.id}: nonfinite quantity in {point.test_point_id}.")


class RegisteredSources:
    def __init__(self, root: Path, snapshot: Snapshot) -> None:
        self._root = root.resolve()
        self._registry = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))
        self._snapshot = snapshot

    def list_for(self, investigation_id: str) -> tuple[dict[str, str], ...]:
        inv = next(i for i in self._snapshot.investigations if i.id == investigation_id)
        sources: dict[str, dict[str, str]] = {}

        def add(path: str, locator: str = "", digest: str = "", label: str = "Cited source") -> None:
            handle = hashlib.sha256((investigation_id + path).encode()).hexdigest()
            sources[handle] = {"handle": handle, "path": path, "locator": locator,
                               "digest": digest, "label": label}

        for source in inv.source_files:
            add(source.path, digest=source.sha256)
        if inv.study_metadata_source:
            add(inv.study_metadata_source, "ISA-Tab study record")
        if inv.manual_metadata:
            for evidence in inv.manual_metadata.all_evidence():
                if not any(s["path"] == evidence.source_file for s in sources.values()):
                    add(evidence.source_file, evidence.locator)
        for source in self._registry.get("external_sources", []):
            if investigation_id not in source["investigation_ids"]:
                continue
            capture_root = self._root / source["captures_dir"]
            metadata_paths = sorted(capture_root.glob("*/metadata.json"))
            if not metadata_paths:
                continue
            latest = json.loads(metadata_paths[-1].read_text(encoding="utf-8"))
            label = f"{source['id']} · latest attempt: {latest['status']}"
            for meta_path in reversed(metadata_paths):
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                if meta["status"] == "captured":
                    for name, artifact in meta["artifacts"].items():
                        path = (meta_path.parent / name).relative_to(self._root).as_posix()
                        add(path, meta.get("captured_at_utc", ""), artifact["sha256"], label)
                    break
            else:
                add(metadata_paths[-1].relative_to(self._root).as_posix(), label=label)
        return tuple(sources.values())

    def read(self, investigation_id: str, handle: str) -> tuple[bytes, str, str]:
        matches = [s for s in self.list_for(investigation_id) if s["handle"] == handle]
        if not matches:
            raise DatasetError("Source is not registered for this investigation.")
        source = matches[0]
        path = (self._root / source["path"]).resolve()
        roots = [self._root / i["raw_dir"] for i in self._registry["investigations"]]
        roots += [self._root / s["captures_dir"] for s in self._registry.get("external_sources", [])]
        if not any(path.is_relative_to(base.resolve()) for base in roots):
            raise DatasetError("Source is outside approved data roots.")
        try:
            content = path.read_bytes()
        except OSError as error:
            raise DatasetError("Source file is unavailable; its citation remains visible.") from error
        if source["digest"] and hashlib.sha256(content).hexdigest() != source["digest"]:
            raise DatasetError("Source changed: its checksum no longer matches the archived version.")
        return content, path.name, mimetypes.guess_type(path.name)[0] or "application/octet-stream"
