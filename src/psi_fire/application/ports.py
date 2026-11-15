from typing import Protocol

from psi_fire.application.answer_types import (
    AnswerResult,
    AnswerState,
    NarrationRequest,
    Passage,
    Solution,
    ValidationContext,
)
from psi_fire.domain.answering import Draft, ValidationIssue
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario


class InvestigationCurator(Protocol):
    """Builds a validated Investigation from raw sources."""

    def curate(self, investigation_id: str) -> Investigation: ...


class InvestigationStore(Protocol):
    def save(self, investigation: Investigation) -> None: ...


class InvestigationRepository(Protocol):
    def all(self) -> list[Investigation]: ...

    def get(self, investigation_id: str) -> Investigation: ...


class Narrator(Protocol):
    """Writes the answer as structured claims. The only port that may use an LLM; it never scores."""

    def draft(self, request: NarrationRequest) -> Draft: ...


class PassageSearch(Protocol):
    """Retrieves passages of archived scientific documents (the RAG knowledge base)."""

    def search(self, query: str, investigation_ids: tuple[str, ...], per_investigation: int) -> tuple[Passage, ...]: ...


class SolutionCatalog(Protocol):
    def lookup(self, investigation_id: str) -> tuple[Solution, ...]: ...


class AnswerValidator(Protocol):
    def validate(self, draft: Draft, context: ValidationContext) -> tuple[ValidationIssue, ...]: ...


class QuestionAnswerer(Protocol):
    """Entry point used by the interface; implemented by the plain loop and by the LangGraph graph."""

    def __call__(self, investigations: tuple[Investigation, ...], scenario: HabitatScenario,
                 question: str) -> AnswerResult: ...


__all__ = [
    "AnswerState",
    "AnswerValidator",
    "InvestigationCurator",
    "InvestigationRepository",
    "InvestigationStore",
    "Narrator",
    "PassageSearch",
    "QuestionAnswerer",
    "SolutionCatalog",
]
