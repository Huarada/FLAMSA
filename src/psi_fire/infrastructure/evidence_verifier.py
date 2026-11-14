"""Checks that every Evidence quote is a 1:1 transcription a human can find with Ctrl+F.

A quote must sit inside ONE printed line (PDF page / text file) or ONE paragraph (DOCX), with its characters
unchanged: only runs of whitespace (and soft hyphens) are ignored. A sentence that wraps onto two lines is quoted by the part
on one line. Quotes are matched against the text `pypdf` extracts; if that differs from what you see on the
page (e.g. "o nly", "high -definition"), choose another span of the line.
"""

import html
import re
import zipfile
from functools import lru_cache
from pathlib import Path

from psi_fire.domain.manual import Evidence
from psi_fire.infrastructure.ingestion.text_source import decode

ALLOWED_ROOTS = ("knowledgeBase/", "data/external/")  # evidence may only cite raw or captured sources
MIN_QUOTE_CHARS = 20  # shorter strings match too many places to identify a sentence
_PAGE = re.compile(r"^p\.\s*(\d+)$")
_PARAGRAPH = re.compile(r"^para\s*(\d+)$")


class EvidenceError(Exception):
    """An evidence entry does not match its source; fix the manual file, never the source."""


def collapse(text: str) -> str:
    """Whitespace runs (and soft hyphens) are the only differences ignored between a quote and its source."""
    return " ".join(text.replace("­", "").split())


class EvidenceVerifier:
    def __init__(self, repo_root: Path) -> None:
        self._root = repo_root

    def verify(self, evidence: Evidence) -> None:
        where = f"{evidence.source_file} [{evidence.locator}]"
        if not evidence.source_file.startswith(ALLOWED_ROOTS):
            raise EvidenceError(f"{evidence.source_file}: evidence must live under {ALLOWED_ROOTS}")
        path = self._root / evidence.source_file
        if not path.is_file():
            raise EvidenceError(f"{evidence.source_file}: file not found")
        quote = collapse(evidence.quote)
        if len(quote) < MIN_QUOTE_CHARS:
            raise EvidenceError(f"{where}: quote shorter than {MIN_QUOTE_CHARS} characters")
        units = self._units(path, evidence.locator)
        if any(quote in collapse(unit) for unit in units):
            return
        if quote in collapse(" ".join(units)):
            raise EvidenceError(f"{where}: quote spans a line break; quote the part inside one printed line")
        raise EvidenceError(f"{where}: quote not found as typed: {evidence.quote[:80]!r}")

    def _units(self, path: Path, locator: str) -> list[str]:
        """The searchable units: lines of a PDF page, one DOCX paragraph, or lines of a text file."""
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            pages = _pdf_pages(path)
            match = _PAGE.match(locator.strip())
            if not match:
                raise EvidenceError(f"{path.name}: a PDF locator must look like 'p. 12', got {locator!r}")
            number = int(match[1])
            if not 1 <= number <= len(pages):
                raise EvidenceError(f"{path.name}: page {number} out of range (1..{len(pages)})")
            return pages[number - 1].split("\n")
        if suffix == ".docx":
            paragraphs = _docx_paragraphs(path)
            match = _PARAGRAPH.match(locator.strip())
            if not match:
                raise EvidenceError(f"{path.name}: a DOCX locator must look like 'para 3', got {locator!r}")
            number = int(match[1])
            if not 1 <= number <= len(paragraphs):
                raise EvidenceError(f"{path.name}: paragraph {number} out of range (1..{len(paragraphs)})")
            return [paragraphs[number - 1]]
        return decode(path.read_bytes())[0].split("\n")


@lru_cache(maxsize=64)
def _pdf_pages(path: Path) -> tuple[str, ...]:
    from pypdf import PdfReader  # optional dependency: only needed when evidence cites a PDF

    return tuple(page.extract_text() or "" for page in PdfReader(str(path)).pages)


@lru_cache(maxsize=64)
def _docx_paragraphs(path: Path) -> tuple[str, ...]:
    """Paragraph numbering counts every <w:p>, tables included: the same numbering a reviewer sees in the extract."""
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    paragraphs = re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.DOTALL)
    # `<w:t>` or `<w:t xml:space=...>` only: a bare `<w:t[^>]*>` would also match <w:tab/>, <w:tc>, <w:tbl>
    return tuple(html.unescape("".join(re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", p, flags=re.DOTALL))) for p in paragraphs)
