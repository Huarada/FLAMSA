"""Passage retrieval over the allowlisted scientific PDFs (the RAG knowledge base).

Lexical TF-IDF over page chunks: deterministic, offline and with exact page locators, so every cited quote can be
checked against the archived page. Embedding or graph retrieval can replace it behind `PassageSearch` (SPEC-003).
"""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from psi_fire.application.answer_types import Passage

MAX_CHUNK_CHARS = 1200
MIN_CHUNK_CHARS = 80  # page numbers and running headers are not passages
INDEX_FORMAT = 1


class CorpusError(Exception):
    """The corpus manifest is malformed or points outside knowledgeBase/."""


def _clean(text: str) -> str:
    """pypdf can emit lone surrogates from broken font maps; they cannot be stored or quoted."""
    return text.encode("utf-8", "ignore").decode("utf-8")


def _chunks(page_text: str) -> list[str]:
    chunks, current = [], ""
    for line in (ln.strip() for ln in _clean(page_text).split("\n")):
        if not line:
            continue
        if current and len(current) + len(line) + 1 > MAX_CHUNK_CHARS:
            chunks.append(current)
            current = ""
        current = f"{current} {line}".strip()
    if current:
        chunks.append(current)
    return [c for c in chunks if len(c) >= MIN_CHUNK_CHARS]


def _fingerprint(manifest_text: str, files: list[Path]) -> str:
    digest = hashlib.sha256(manifest_text.encode("utf-8"))
    for path in files:
        digest.update(f"{path.name}:{path.stat().st_size}".encode())
    digest.update(str(INDEX_FORMAT).encode())
    return digest.hexdigest()


class PdfPassageSearch:
    def __init__(self, repo_root: Path, manifest_path: Path, cache_path: Path) -> None:
        self._root, self._manifest, self._cache = repo_root, manifest_path, cache_path
        self._passages: tuple[Passage, ...] | None = None
        self._matrix = None
        self._vectorizer = None
        self.skipped: tuple[str, ...] = ()

    def documents(self) -> list[dict[str, str]]:
        documents = json.loads(self._manifest.read_text(encoding="utf-8"))["documents"]
        for doc in documents:
            if not doc["source_file"].startswith("knowledgeBase/"):
                raise CorpusError(f"{doc['source_file']}: the corpus may only list knowledgeBase/ files")
        return documents

    def build(self) -> None:
        """Extract, chunk and cache every allowlisted page; rerun only when the corpus changes."""
        from pypdf import PdfReader
        from pypdf.errors import PyPdfError

        manifest_text = self._manifest.read_text(encoding="utf-8")
        docs = self.documents()
        files = [self._root / d["source_file"] for d in docs]
        missing = [str(f) for f in files if not f.is_file()]
        if missing:
            raise CorpusError(f"Corpus files not found: {missing}")
        passages, skipped = [], []
        for doc, path in zip(docs, files, strict=True):
            try:
                reader = PdfReader(str(path))
                pages = [(number, page.extract_text() or "") for number, page in enumerate(reader.pages, start=1)]
            except (PyPdfError, ValueError, OSError) as error:
                skipped.append(f"{doc['source_file']}: {error}")
                continue
            for number, text in pages:
                passages += [Passage(doc["investigation_id"], doc["source_file"], f"p. {number}", chunk)
                             for chunk in _chunks(text)]
        payload = {"fingerprint": _fingerprint(manifest_text, files), "skipped": skipped,
                   "passages": [asdict(p) for p in passages]}
        self._cache.parent.mkdir(parents=True, exist_ok=True)
        partial = self._cache.with_suffix(".tmp")  # a failed write must never leave a truncated cache
        partial.write_text(json.dumps(payload, ensure_ascii=False, indent=0), encoding="utf-8")
        partial.replace(self._cache)

    def _load(self) -> tuple[Passage, ...]:
        if self._passages is not None:
            return self._passages
        docs = self.documents()
        wanted = _fingerprint(self._manifest.read_text(encoding="utf-8"), [self._root / d["source_file"] for d in docs])
        if not self._cache.is_file() or json.loads(self._cache.read_text(encoding="utf-8")).get("fingerprint") != wanted:
            self.build()
        payload = json.loads(self._cache.read_text(encoding="utf-8"))
        self.skipped = tuple(payload["skipped"])
        self._passages = tuple(Passage(**p) for p in payload["passages"])
        if self._passages:
            from sklearn.feature_extraction.text import TfidfVectorizer

            self._vectorizer = TfidfVectorizer(sublinear_tf=True, stop_words="english", ngram_range=(1, 2))
            self._matrix = self._vectorizer.fit_transform(p.text for p in self._passages)
        return self._passages

    def passages_of(self, investigation_id: str) -> tuple[Passage, ...]:
        """Every indexed passage of one investigation (diagnostics: was the text there but not retrieved?)."""
        return tuple(p for p in self._load() if p.investigation_id == investigation_id)

    def search(self, query: str, investigation_ids: tuple[str, ...], per_investigation: int) -> tuple[Passage, ...]:
        passages = self._load()
        if not passages or self._vectorizer is None or not query.strip():
            return ()
        scores = (self._matrix @ self._vectorizer.transform([query]).T).toarray().ravel()
        found: list[Passage] = []
        for inv_id in investigation_ids:
            ranked = sorted((i for i, p in enumerate(passages) if p.investigation_id == inv_id and scores[i] > 0),
                            key=lambda i: (-scores[i], i))  # index breaks ties deterministically
            found += [passages[i] for i in ranked[:per_investigation]]
        return tuple(found)
