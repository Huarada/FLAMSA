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


def test_report_pdfs_cited_by_passages_are_registered_pinned_and_readable():
    from psi_fire.application.answer_types import TraceEntry
    from psi_fire.application.evidence import InvestigationSources
    from psi_fire.application.source_access import ResolveCitationSource, SourceDocument
    from psi_fire.domain.answering import Citation, CitationKind

    sources = InvestigationSources(RegisteredSources(ROOT, FileSnapshotProvider(ROOT).load()))
    report = next(s for s in sources("FLEX") if s["path"].endswith(".pdf"))
    assert len(report["digest"]) == 64
    citation = Citation(kind=CitationKind.PASSAGE, investigation_id="FLEX", source_file=report["path"],
                        locator="p. 1", quote="x" * 25)
    opened = ResolveCitationSource(sources).open(TraceEntry(0, citation, report["path"], "p. 1", None))
    assert isinstance(opened, SourceDocument) and opened.content.startswith(b"%PDF")


def test_a_missing_report_pdf_is_listed_unpinned_and_reported_unavailable(tmp_path):
    from psi_fire.application.answer_types import TraceEntry
    from psi_fire.application.evidence import InvestigationSources
    from psi_fire.application.explore import Snapshot
    from psi_fire.application.source_access import ResolveCitationSource, SourceStatus
    from psi_fire.domain.answering import Citation, CitationKind
    from psi_fire.domain.model import Investigation, TestPoint

    (tmp_path / "data").mkdir()
    (tmp_path / "data/sources.json").write_text(json.dumps({"investigations": [{"raw_dir": "raw"}]}))
    (tmp_path / "data/rag_corpus.json").write_text(json.dumps({"documents": [
        {"investigation_id": "TEST", "source_file": "raw/missing.pdf", "kind": "Final report"}]}))
    point = TestPoint(investigation_id="TEST", test_point_id="a", record_level="test", source_file="raw/test.csv",
                      source_row="2", provenance_status="verified")
    inv = Investigation(id="TEST", psi_id="TEST", record_level="test", columns={}, test_points=(point,),
                        source_files=())
    sources = InvestigationSources(RegisteredSources(tmp_path, Snapshot("fixture", (inv,))))
    (entry,) = [s for s in sources("TEST") if s["path"] == "raw/missing.pdf"]
    assert entry["digest"] == ""
    citation = Citation(kind=CitationKind.PASSAGE, investigation_id="TEST", source_file="raw/missing.pdf",
                        locator="p. 1", quote="x" * 25)
    opened = ResolveCitationSource(sources).open(TraceEntry(0, citation, "raw/missing.pdf", "p. 1", None))
    assert opened.status == SourceStatus.UNAVAILABLE
