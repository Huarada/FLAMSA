import json
from pathlib import Path

import pytest

from psi_fire.application.explore import DatasetError
from psi_fire.infrastructure.explorer import FileSnapshotProvider, RegisteredSources

ROOT = Path(__file__).resolve().parents[2]


def test_current_dataset_and_source_download() -> None:
    snapshot = FileSnapshotProvider(ROOT).load()
    assert snapshot.investigations
    service = RegisteredSources(ROOT, snapshot)
    inv = snapshot.investigations[0]
    entry = service.list_for(inv.id)[0]
    content, filename, _ = service.read(inv.id, entry["handle"])
    assert content and filename.endswith(".csv")
    with pytest.raises(DatasetError):
        service.read(inv.id, "not-registered")


def test_csv_only_directory_is_rejected(tmp_path: Path) -> None:
    orphan = tmp_path / "data/curated/ORPHAN"
    orphan.mkdir(parents=True)
    (orphan / "test_points.csv").write_text("investigation_id\nORPHAN\n", encoding="utf-8")
    with pytest.raises(DatasetError, match="incomplete curated pair"):
        FileSnapshotProvider(tmp_path).load()


def test_parent_identity_checked_without_changing_domain() -> None:
    snapshot = FileSnapshotProvider(ROOT).load()
    original = next(i for i in snapshot.investigations if i.manual_metadata)
    payload = json.loads(original.model_dump_json())
    payload["manual_metadata"]["investigation_id"] = "WRONG"
    mismatch = type(original).model_validate(payload)
    with pytest.raises(DatasetError, match="identity mismatch"):
        FileSnapshotProvider._validate(mismatch.id, mismatch)


def test_source_changed_is_rejected(tmp_path: Path) -> None:
    import hashlib

    from psi_fire.application.explore import Snapshot
    from psi_fire.domain.model import Investigation, SourceFile, TestPoint
    raw = tmp_path / "raw"
    raw.mkdir()
    source = raw / "test.csv"
    source.write_text("changed", encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "data/sources.json").write_text(json.dumps({"investigations": [{"raw_dir": "raw"}]}))
    point = TestPoint(investigation_id="TEST", test_point_id="a", record_level="test", source_file="raw/test.csv",
                      source_row="2", provenance_status="verified")
    inv = Investigation(id="TEST", psi_id="TEST", record_level="test", columns={}, test_points=(point,),
                        source_files=(SourceFile(path="raw/test.csv", sha256=hashlib.sha256(b"original").hexdigest(),
                                                 encoding="utf-8"),))
    service = RegisteredSources(tmp_path, Snapshot("fixture", (inv,)))
    with pytest.raises(DatasetError, match="checksum"):
        service.read("TEST", service.list_for("TEST")[0]["handle"])
