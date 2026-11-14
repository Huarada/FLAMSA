"""Evidence is checked against the real knowledgeBase/ files: a quote that is not in its source fails curation."""

from pathlib import Path

import pytest

from psi_fire.domain.manual import Evidence, ManualMetadata
from psi_fire.infrastructure.evidence_verifier import EvidenceError, EvidenceVerifier, collapse

REPO_ROOT = Path(__file__).resolve().parents[2]
MANUAL_DIR = REPO_ROOT / "data" / "manual"
ISA = "knowledgeBase/Flammable/SAFFIRE3/PSI-100_metadata_PSI-168_SAFFIRE-III/i_Investigation.txt"
PDF = "knowledgeBase/Flammable/SAFFIRE3/SAFFIRE-III Operations.pdf"
ACME = "knowledgeBase/ACME/CFI-G/PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf"
DOCX = "knowledgeBase/Flammable/SAFFIRE3/SAFFIRE-I and SAFFIRE-III DoD.docx"
verifier = EvidenceVerifier(REPO_ROOT)


def _evidence(source_file: str, locator: str, quote: str) -> Evidence:
    return Evidence(source_file=source_file, locator=locator, quote=quote)


@pytest.mark.parametrize(
    ("source_file", "locator", "quote"),
    [
        (ISA, "Comment[Approach]", "two radiometers recorded flame radiation"),
        (ISA, "Comment[Objective]", "NASA’s normal gravity material flammability screening test"),  # curly apostrophe
        (PDF, "p. 1", "Saffire-III mission operations begin when Cygnus unberths from the ISS."),
        (DOCX, "para 1", "determine how rapidly a large-scale fire grows in low-gravity"),
        (ACME, "p. 23", "intensified video camera, radiometers, and thermocouples."),  # one printed line
    ],
)
def test_real_quotes_are_found(source_file: str, locator: str, quote: str) -> None:
    verifier.verify(_evidence(source_file, locator, quote))


def test_invented_quote_is_rejected() -> None:
    with pytest.raises(EvidenceError, match="not found"):
        verifier.verify(_evidence(ISA, "Comment[Approach]", "three radiometers recorded flame radiation"))


def test_quote_on_the_wrong_page_or_paragraph_is_rejected() -> None:
    with pytest.raises(EvidenceError, match="not found"):
        verifier.verify(_evidence(DOCX, "para 3", "determine how rapidly a large-scale fire grows in low-gravity"))
    with pytest.raises(EvidenceError, match="out of range"):
        verifier.verify(_evidence(PDF, "p. 99", "Saffire-III mission operations begin"))


def test_quote_wrapped_over_two_printed_lines_is_rejected() -> None:
    # p. 23 prints "...The diagnostics included an" / "intensified video camera...": Ctrl+F cannot find it
    with pytest.raises(EvidenceError, match="spans a line break"):
        verifier.verify(_evidence(ACME, "p. 23", "The diagnostics included an intensified video camera, radiometers, and thermocouples."))


def test_quote_must_match_characters_not_only_words() -> None:
    with pytest.raises(EvidenceError, match="not found"):  # the source has a curly apostrophe
        verifier.verify(_evidence(ISA, "Comment[Objective]", "NASA's normal gravity material flammability screening test"))


def test_pdf_and_docx_evidence_need_a_page_or_paragraph_locator() -> None:
    with pytest.raises(EvidenceError, match="locator must look like"):
        verifier.verify(_evidence(PDF, "Operations", "Saffire-III mission operations begin when Cygnus unberths"))
    with pytest.raises(EvidenceError, match="locator must look like"):
        verifier.verify(_evidence(DOCX, "intro", "determine how rapidly a large-scale fire grows in low-gravity"))


def test_missing_file_and_foreign_paths_are_rejected() -> None:
    with pytest.raises(EvidenceError, match="not found"):
        verifier.verify(_evidence("knowledgeBase/nope.pdf", "p. 1", "any quote long enough here"))
    with pytest.raises(EvidenceError, match="must live under"):
        verifier.verify(_evidence("docs/ADR.md", "line 1", "Continuous decision log of the project"))
    with pytest.raises(EvidenceError, match="shorter than"):
        verifier.verify(_evidence(ISA, "Comment[Approach]", "flame images"))


def test_collapse_ignores_only_whitespace() -> None:
    assert collapse("fire\n  grows   fast") == "fire grows fast"
    assert collapse("a ‘b’ – c") == "a ‘b’ – c"  # typography is NOT folded: 1:1


@pytest.mark.parametrize("path", sorted(MANUAL_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_every_manual_file_is_valid_and_all_its_evidence_exists(path: Path) -> None:
    manual = ManualMetadata.model_validate_json(path.read_text(encoding="utf-8"))
    assert manual.investigation_id == path.stem
    for evidence in manual.all_evidence():
        verifier.verify(evidence)
