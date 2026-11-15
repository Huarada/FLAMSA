import json
from pathlib import Path

import pytest
from langchain_core.runnables import RunnableLambda

from psi_fire.application.answer_types import AnswerStatus, NarrationRequest, Passage
from psi_fire.application.answering import NarrationError
from psi_fire.application.explore import LoadExplorer
from psi_fire.domain.answering import Citation, CitationKind, Claim, Draft
from psi_fire.domain.ranking import LUNAR_BASE, RelevanceRanker
from psi_fire.infrastructure.answering_factory import build_answering_pipeline
from psi_fire.infrastructure.explorer import FileSnapshotProvider
from psi_fire.infrastructure.langchain_narrator import LangChainNarrator, chat_model_from_env, request_payload
from psi_fire.infrastructure.passage_index import (
    MAX_CHUNK_CHARS,
    CorpusError,
    PdfPassageSearch,
    _chunks,
    _clean,
    _fingerprint,
)
from psi_fire.infrastructure.solution_catalog import CatalogError, JsonSolutionCatalog

ROOT = Path(__file__).resolve().parents[2]


def test_chunks_respect_the_size_limit_and_drop_running_headers():
    page = "12\n" + "\n".join(f"Line {i} of the page that describes flame spread over thin fuels." for i in range(60))
    chunks = _chunks(page)
    assert len(chunks) > 1 and all(80 <= len(c) <= MAX_CHUNK_CHARS for c in chunks)
    assert _chunks("12\nFig. 3") == []


def test_clean_removes_lone_surrogates():
    assert _clean("a\ud835b") == "ab"


def make_index(tmp_path: Path, passages: list[Passage]) -> PdfPassageSearch:
    (tmp_path / "knowledgeBase").mkdir()
    pdf = tmp_path / "knowledgeBase/a.pdf"
    pdf.write_bytes(b"x")
    manifest = tmp_path / "corpus.json"
    manifest.write_text(json.dumps({"documents": [
        {"investigation_id": "FLEX", "source_file": "knowledgeBase/a.pdf", "kind": "report"}]}), encoding="utf-8")
    cache = tmp_path / "idx/passages.json"
    cache.parent.mkdir()
    cache.write_text(json.dumps({"fingerprint": _fingerprint(manifest.read_text(encoding="utf-8"), [pdf]),
                                 "skipped": [], "passages": [p.__dict__ for p in passages]}), encoding="utf-8")
    return PdfPassageSearch(tmp_path, manifest, cache)


def test_search_returns_the_best_pages_per_investigation_deterministically(tmp_path):
    texts = ["droplet burning rate constant versus oxygen concentration", "calibration of the camera lens",
             "oxygen concentration changes the droplet burning rate", "wiring harness inspection notes"]
    passages = [Passage("FLEX", "knowledgeBase/a.pdf", f"p. {n}", t) for n, t in enumerate(texts, 1)]
    passages.append(Passage("BASS", "knowledgeBase/a.pdf", "p. 9", "oxygen concentration droplet burning rate"))
    index = make_index(tmp_path, passages)
    found = index.search("oxygen droplet burning rate", ("FLEX",), 2)
    assert {p.locator for p in found} == {"p. 1", "p. 3"} and all(p.investigation_id == "FLEX" for p in found)
    assert found[0].locator == "p. 3"  # contains every query term, so it outranks p. 1
    assert index.search("oxygen droplet burning rate", ("FLEX",), 2) == found
    assert index.search("   ", ("FLEX",), 2) == () and index.search("zzzz qqqq", ("FLEX",), 2) == ()


def test_corpus_may_only_list_knowledgebase_files(tmp_path):
    manifest = tmp_path / "corpus.json"
    manifest.write_text(json.dumps({"documents": [
        {"investigation_id": "X", "source_file": "docs/x.pdf", "kind": "k"}]}), encoding="utf-8")
    with pytest.raises(CorpusError):
        PdfPassageSearch(tmp_path, manifest, tmp_path / "c.json").documents()


def test_the_committed_corpus_lists_only_existing_knowledgebase_pdfs():
    docs = PdfPassageSearch(ROOT, ROOT / "data/rag_corpus.json", ROOT / "x").documents()
    assert docs and all((ROOT / d["source_file"]).is_file() and d["source_file"].endswith(".pdf") for d in docs)
    assert not [d for d in docs if "rawing" in d["source_file"] or d["source_file"].endswith(".txt")]


def test_catalog_requires_a_source_for_sourced_entries(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"entries": [
        {"investigation_id": "FLEX", "technology": "T", "status": "sourced"}]}), encoding="utf-8")
    with pytest.raises(CatalogError):
        JsonSolutionCatalog(path)
    assert JsonSolutionCatalog(tmp_path / "missing.json").lookup("FLEX") == ()
    assert JsonSolutionCatalog(ROOT / "data/solutions_catalog.json").lookup("FLEX") == ()


@pytest.fixture(scope="module")
def investigations():
    return LoadExplorer(FileSnapshotProvider(ROOT))().investigations


def request_for(investigations) -> NarrationRequest:
    shortlist = RelevanceRanker().rank(investigations, LUNAR_BASE)[:2]
    return NarrationRequest("What is closest?", LUNAR_BASE, shortlist, (), (), 1)


def test_langchain_narrator_sends_the_ranking_and_returns_the_structured_draft(investigations):
    seen = []
    top = RelevanceRanker().rank(investigations, LUNAR_BASE)[0].investigation
    draft = Draft(claims=(Claim(text=f"[{top.id}] x", citations=(
        Citation(kind=CitationKind.METADATA, investigation_id=top.id, field="pillars"),)),))
    narrator = LangChainNarrator(RunnableLambda(lambda messages: seen.append(messages) or draft),
                                 JsonSolutionCatalog(ROOT / "data/solutions_catalog.json"))
    assert narrator.draft(request_for(investigations)) == draft
    system, human = seen[0]
    assert "machine-checked" in system.content and top.id in human.content and "criteria" in human.content


def test_langchain_narrator_turns_provider_failures_into_narration_errors(investigations):
    def boom(_):
        raise RuntimeError("rate limited")

    narrator = LangChainNarrator(RunnableLambda(boom), JsonSolutionCatalog(ROOT / "data/solutions_catalog.json"))
    with pytest.raises(NarrationError, match="rate limited"):
        narrator.draft(request_for(investigations))
    not_a_draft = LangChainNarrator(RunnableLambda(lambda _: "text"), JsonSolutionCatalog(ROOT / "x.json"))
    with pytest.raises(NarrationError):
        not_a_draft.draft(request_for(investigations))


def test_request_payload_never_lets_the_model_rescore(investigations):
    payload = request_payload(request_for(investigations), JsonSolutionCatalog(ROOT / "x.json"))
    scores = [r["score"] for r in payload["ranking"]]
    assert scores == sorted(scores, reverse=True) and payload["ranking"][0]["rank"] == 1


def test_no_model_configured_means_the_template_narrator():
    assert chat_model_from_env({}) is None
    assert "Template" in build_answering_pipeline(ROOT, {}).narrator_label


def test_end_to_end_with_the_real_corpus_and_the_langgraph_engine(investigations):
    pipeline = build_answering_pipeline(ROOT, {})
    result = pipeline.answerer(investigations, LUNAR_BASE, "How does oxygen concentration affect flame spread?")
    assert result.status == AnswerStatus.APPROVED
    assert result.traceability and all(e.source_file for e in result.traceability)
    index = PdfPassageSearch(ROOT, ROOT / "data/rag_corpus.json", ROOT / "data/rag_index/passages.json")
    found = index.search("oxygen concentration flame spread", ("FLEX", "BASS-II"), 2)
    assert {p.investigation_id for p in found} == {"FLEX", "BASS-II"}
    assert all((ROOT / p.source_file).is_file() and p.locator.startswith("p. ") for p in found)


def test_an_unusable_model_setting_falls_back_to_the_template_and_says_so():
    pipeline = build_answering_pipeline(ROOT, {"PSI_LLM_MODEL": "openai:gpt-4.1-mini", "OPENAI_API_KEY": ""})
    assert pipeline.narrator_label.startswith("Template (model unavailable")
