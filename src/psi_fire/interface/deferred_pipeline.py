"""Prepare the answering engine on demand, after an explicit question rather than page navigation."""

from collections.abc import Callable
from typing import Protocol

from psi_fire.application.answer_types import AnswerResult
from psi_fire.application.ports import QuestionAnswerer
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario


class PipelineHandle(Protocol):
    @property
    def answerer(self) -> QuestionAnswerer: ...

    @property
    def narrator_label(self) -> str: ...


class DeferredPipeline:
    def __init__(self, factory: Callable[[], PipelineHandle]) -> None:
        self._factory = factory
        self._resolved: PipelineHandle | None = None

    def _get(self) -> PipelineHandle:
        if self._resolved is None:
            self._resolved = self._factory()
        return self._resolved

    @property
    def answerer(self) -> QuestionAnswerer:
        return self._answer

    def _answer(self, investigations: tuple[Investigation, ...], scenario: HabitatScenario,
                question: str) -> AnswerResult:
        return self._get().answerer(investigations, scenario, question)

    @property
    def narrator_label(self) -> str:
        return self._get().narrator_label
