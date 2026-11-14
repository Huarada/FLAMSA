"""Second opinion on PDF quotes: `pdftotext -layout` keeps the lines as a reader sees them.

`pypdf` sometimes returns a whole paragraph as one "line", so the verifier alone cannot guarantee that a quote
fits on one visible line. Skipped when poppler's `pdftotext` is not installed.
"""

import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest

from psi_fire.domain.manual import ManualMetadata
from psi_fire.infrastructure.evidence_verifier import collapse

REPO_ROOT = Path(__file__).resolve().parents[2]
PDFTOTEXT = shutil.which("pdftotext")
CASES = [
    (path.stem, e)
    for path in sorted((REPO_ROOT / "data" / "manual").glob("*.json"))
    for e in ManualMetadata.model_validate_json(path.read_text(encoding="utf-8")).all_evidence()
    if e.source_file.lower().endswith(".pdf")
]


@lru_cache(maxsize=32)
def _visual_lines(pdf: Path, page: int) -> list[str]:
    result = subprocess.run(
        [PDFTOTEXT, "-f", str(page), "-l", str(page), "-layout", "-enc", "UTF-8", str(pdf), "-"],
        capture_output=True, check=True,
    )
    return [collapse(line) for line in result.stdout.decode("utf-8", "replace").split("\n")]


@pytest.mark.skipif(PDFTOTEXT is None, reason="pdftotext (poppler) is not installed")
@pytest.mark.parametrize(("investigation", "evidence"), CASES, ids=lambda v: v if isinstance(v, str) else v.quote[:40])
def test_pdf_quote_is_on_one_visible_line(investigation: str, evidence) -> None:  # type: ignore[no-untyped-def]
    page = int(evidence.locator.split()[-1])
    lines = _visual_lines(REPO_ROOT / evidence.source_file, page)
    assert any(collapse(evidence.quote) in line for line in lines), (
        f"{investigation}: not on one visible line of p. {page}: {evidence.quote!r}"
    )
