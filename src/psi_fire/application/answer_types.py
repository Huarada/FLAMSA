"""Plain data exchanged by the answering ports (SPEC-003). No I/O, no framework."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, TypedDict

from psi_fire.domain.answering import Citation, Draft, ValidationIssue
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario, RankedInvestigation


@dataclass(frozen=True)
class Passage:
    investigation_id: str
    source_file: str  # repo-relative path under knowledgeBase/
    locator: str      # "p. 12"
    text: str


@dataclass(frozen=True)
class Solution:
    investigation_id: str
    technology: str
    status: Literal["illustrative", "sourced"]  # illustrative entries are never evidence
    source_file: str | None = None
    locator: str | None = None


@dataclass(frozen=True)
class RetrievalSettings:
    top_k: int
    min_score: float
    passages_per_investigation: int


@dataclass(frozen=True)
class NarrationRequest:
    question: str
    scenario: HabitatScenario
    shortlist: tuple[RankedInvestigation, ...]
    passages: tuple[Passage, ...]
    previous_issues: tuple[ValidationIssue, ...]
    attempt: int


@dataclass(frozen=True)
class ValidationContext:
    scenario: HabitatScenario
    shortlist: tuple[RankedInvestigation, ...]
    passages: tuple[Passage, ...]
    question: str = ""  # numbers the user typed in the question are inputs, like the scenario values


class AnswerStatus(StrEnum):
    APPROVED = "approved"
    PARTIAL = "partial"  # some claims passed validation; the others are withheld and never shown (ADR-0145)
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class AttemptRecord:
    attempt: int
    settings: RetrievalSettings
    shortlist_ids: tuple[str, ...]
    passage_count: int
    issues: tuple[ValidationIssue, ...]
    draft: Draft | None = None                # kept so a rejected attempt can be inspected, never shown as an answer
    passages: tuple[Passage, ...] = ()        # what retrieval returned for this attempt


@dataclass(frozen=True)
class TraceEntry:
    """One link of the evidence traceability map: claim -> citation -> archived source."""

    claim_index: int
    citation: Citation
    source_file: str | None
    locator: str | None
    sha256: str | None
    status: str | None = None  # what kind of evidence this is and whether anyone reviewed it; never "verified science"


@dataclass(frozen=True)
class FigureTrace:
    """Where a number a claim states comes from: record, column, unit, raw text and source row."""

    claim_index: int
    investigation_id: str
    test_point_id: str
    column: str
    value: float
    unit: str | None
    raw: str | None
    source_file: str
    source_row: str
    provenance_status: str


@dataclass(frozen=True)
class AnswerResult:
    status: AnswerStatus
    scenario: HabitatScenario
    question: str
    shortlist: tuple[RankedInvestigation, ...]
    draft: Draft | None             # None unless approved: a rejected draft is never shown as an answer
    solutions: tuple[Solution, ...]
    issues: tuple[ValidationIssue, ...]  # reasons of the last attempt (empty when approved)
    limitations: tuple[str, ...]
    breakdown_text: str
    attempts: tuple[AttemptRecord, ...]
    traceability: tuple[TraceEntry, ...]
    figure_traces: tuple[FigureTrace, ...] = ()
    claims_total: int = 0      # claims in the last draft
    claims_withheld: int = 0   # claims removed because they failed validation (partial answers only)


class AnswerState(TypedDict, total=False):
    """Shared by the plain-Python loop and the LangGraph graph so both run the same steps."""

    investigations: tuple[Investigation, ...]
    scenario: HabitatScenario
    question: str
    attempt: int
    settings: RetrievalSettings
    shortlist: tuple[RankedInvestigation, ...]
    passages: tuple[Passage, ...]
    draft: Draft | None
    issues: tuple[ValidationIssue, ...]
    attempts: tuple[AttemptRecord, ...]
    result: AnswerResult
