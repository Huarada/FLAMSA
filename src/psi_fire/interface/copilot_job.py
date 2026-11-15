"""A per-session background request; workers never read or write Streamlit state."""

from concurrent.futures import Future
from dataclasses import dataclass
from threading import Thread

from psi_fire.application.answer_types import AnswerResult
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario
from psi_fire.interface.deferred_pipeline import PipelineHandle


@dataclass(frozen=True)
class CompletedAnswer:
    result: AnswerResult
    narrator_label: str


@dataclass(frozen=True)
class CopilotJob:
    future: Future[CompletedAnswer]
    scenario: HabitatScenario
    question: str

    @classmethod
    def prepare(cls, scenario: HabitatScenario, question: str) -> "CopilotJob":
        return cls(Future(), scenario, question)

    def start(self, pipeline: PipelineHandle, investigations: tuple[Investigation, ...]) -> None:
        Thread(target=self._run, args=(pipeline, investigations), name="copilot-answer", daemon=True).start()

    def _run(self, pipeline: PipelineHandle, investigations: tuple[Investigation, ...]) -> None:
        if not self.future.set_running_or_notify_cancel():
            return
        try:
            label = pipeline.narrator_label
            result = pipeline.answerer(investigations, self.scenario, self.question)
        except Exception as error:  # noqa: BLE001 - transport the failure to the UI thread without losing the job
            self.future.set_exception(error)
        else:
            self.future.set_result(CompletedAnswer(result, label))
