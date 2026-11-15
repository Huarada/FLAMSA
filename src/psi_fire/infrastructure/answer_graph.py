"""LangGraph wiring of the answering steps (SPEC-003 section 2). Nodes and routing come from `AnsweringSteps`."""

from langgraph.graph import END, START, StateGraph

from psi_fire.application.answer_types import AnswerResult, AnswerState
from psi_fire.application.answering import (
    NODE_ADVANCE,
    NODE_ANSWER,
    NODE_FINALIZE,
    NODE_SEARCH,
    NODE_VALIDATE,
    AnsweringSteps,
)
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario

NODE_RETRIEVE = "retrieve"


def build_graph(steps: AnsweringSteps):  # type: ignore[no-untyped-def]
    graph = StateGraph(AnswerState)
    graph.add_node(NODE_RETRIEVE, steps.retrieve)
    graph.add_node(NODE_SEARCH, steps.search)
    graph.add_node(NODE_ANSWER, steps.answer)
    graph.add_node(NODE_VALIDATE, steps.validate)
    graph.add_node(NODE_ADVANCE, steps.advance)
    graph.add_node(NODE_FINALIZE, steps.finalize)
    graph.add_edge(START, NODE_RETRIEVE)
    graph.add_conditional_edges(NODE_RETRIEVE, steps.route_after_retrieve,
                                {NODE_SEARCH: NODE_SEARCH, NODE_FINALIZE: NODE_FINALIZE})
    graph.add_edge(NODE_SEARCH, NODE_ANSWER)
    graph.add_edge(NODE_ANSWER, NODE_VALIDATE)
    graph.add_conditional_edges(NODE_VALIDATE, steps.route_after_validate,
                                {NODE_ADVANCE: NODE_ADVANCE, NODE_FINALIZE: NODE_FINALIZE})
    graph.add_edge(NODE_ADVANCE, NODE_RETRIEVE)
    graph.add_edge(NODE_FINALIZE, END)
    return graph.compile()


class LangGraphAnswerer:
    """Same contract as `AnswerScenarioQuestion`; differs only in who drives the steps."""

    def __init__(self, steps: AnsweringSteps) -> None:
        self._steps = steps
        self._graph = build_graph(steps)

    def __call__(self, investigations: tuple[Investigation, ...], scenario: HabitatScenario,
                 question: str) -> AnswerResult:
        final = self._graph.invoke(self._steps.start(investigations, scenario, question))
        result: AnswerResult = final["result"]
        return result
