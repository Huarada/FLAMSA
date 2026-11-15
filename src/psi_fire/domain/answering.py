"""Structured answer types and physical-plausibility rules (SPEC-003). No I/O, no LLM."""

import re
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from psi_fire.domain.model import O2_PERCENT_MAX, O2_PERCENT_MIN


class CitationKind(StrEnum):
    RECORD = "record"      # a curated test point
    METADATA = "metadata"  # a curated investigation field (pillars, hardware, ...)
    PASSAGE = "passage"    # a page of an archived source document


METADATA_FIELDS = ("pillars", "hardware", "gravity_regime", "sensors", "earth_applications", "objective")


class Citation(BaseModel):
    """Flat on purpose: structured-output schemas of LLM providers handle flat models best."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: CitationKind
    investigation_id: str
    test_point_id: str | None = None   # record
    field: str | None = None           # metadata
    source_file: str | None = None     # passage
    locator: str | None = None         # passage, e.g. "p. 12"
    quote: str | None = None           # passage: text copied from the page


class Figure(BaseModel):
    """A number a claim states. `record` figures must lie inside the cited test point's range; `breakdown`
    figures must equal the deterministic score ('score', 'rank' or a criterion name)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: Literal["record", "breakdown"]
    investigation_id: str
    column: str            # record: o2_percent / pressure_psi / ...; breakdown: score / rank / criterion name
    value: float
    unit: str | None = None
    test_point_id: str | None = None


class Claim(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    citations: tuple[Citation, ...] = ()
    figures: tuple[Figure, ...] = ()
    technologies: tuple[str, ...] = ()  # derived technologies mentioned; must come from the solution catalog


class Draft(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    claims: tuple[Claim, ...]


class IssueCode(StrEnum):
    MISSING_CITATION = "missing_citation"
    UNKNOWN_CITATION = "unknown_citation"
    MALFORMED_CITATION = "malformed_citation"
    QUOTE_MISMATCH = "quote_mismatch"
    NUMBER_MISMATCH = "number_mismatch"
    UNDECLARED_NUMBER = "undeclared_number"
    UNBACKED_TECHNOLOGY = "unbacked_technology"
    IMPLAUSIBLE = "implausible"
    EMPTY_DRAFT = "empty_draft"


class ValidationIssue(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: IssueCode
    message: str
    claim_index: int | None = None


NUMBER_RELATIVE_TOLERANCE = 0.01
NUMBER_ABSOLUTE_TOLERANCE = 0.05
SCORE_ABSOLUTE_TOLERANCE = 0.005

_PARTIAL_GRAVITY = re.compile(r"partial[- ]gravity", re.IGNORECASE)
_NEGATION = re.compile(r"\b(no|not|without|lacks?|absent|emulat\w*|future work|unavailable)\b", re.IGNORECASE)
_ID_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b")
_BRACKET = re.compile(r"\[[^\]]*\]")
_NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?")


def numbers_in(text: str) -> tuple[float, ...]:
    """Numbers a reader would take as claimed values: ids such as PSI-26 and [citations] are not claims."""
    cleaned = _ID_TOKEN.sub(" ", _BRACKET.sub(" ", text))
    return tuple(float(token) for token in _NUMBER.findall(cleaned))


def plausibility_issues(claim: Claim, index: int) -> tuple[ValidationIssue, ...]:
    issues = []
    for figure in claim.figures:
        if figure.column == "o2_percent" and not O2_PERCENT_MIN <= figure.value <= O2_PERCENT_MAX:
            issues.append(ValidationIssue(code=IssueCode.IMPLAUSIBLE, claim_index=index,
                                          message=f"Oxygen {figure.value:g}% is outside 0-100%."))
        if figure.column == "pressure_psi" and figure.value < 0:
            issues.append(ValidationIssue(code=IssueCode.IMPLAUSIBLE, claim_index=index,
                                          message=f"Pressure {figure.value:g} psi is negative."))
    if _PARTIAL_GRAVITY.search(claim.text) and not _NEGATION.search(claim.text):
        issues.append(ValidationIssue(code=IssueCode.IMPLAUSIBLE, claim_index=index,
                                      message="PSI has no partial-gravity data; state that it is absent or emulated."))
    return tuple(issues)
