"""Build data/rag_index/passages.json from the allowlist in data/rag_corpus.json (generated, never hand-edited).

Run from the repository root:  PYTHONPATH=src python scripts/build_rag_index.py
"""

from pathlib import Path

from psi_fire.infrastructure.passage_index import PdfPassageSearch

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    index = PdfPassageSearch(ROOT, ROOT / "data/rag_corpus.json", ROOT / "data/rag_index/passages.json")
    index.build()
    index.search("oxygen concentration flame spread", ("FLEX",), 1)  # loads the cache and fits the vectorizer
    print(f"skipped: {list(index.skipped)}")
