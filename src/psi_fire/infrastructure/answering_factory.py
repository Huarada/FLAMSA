"""Composition of the answering pipeline: the only place that picks the narrator and the orchestration engine."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from psi_fire.application.answer_validation import RuleBasedValidator
from psi_fire.application.answering import AnsweringSteps
from psi_fire.application.ports import Narrator, QuestionAnswerer
from psi_fire.application.template_narrator import TemplateNarrator
from psi_fire.domain.ranking import RelevanceRanker
from psi_fire.infrastructure.answer_graph import LangGraphAnswerer
from psi_fire.infrastructure.langchain_narrator import LangChainNarrator, chat_model_from_env
from psi_fire.infrastructure.passage_index import PdfPassageSearch
from psi_fire.infrastructure.solution_catalog import JsonSolutionCatalog


@dataclass(frozen=True)
class AnsweringPipeline:
    answerer: QuestionAnswerer
    narrator_label: str  # shown in the UI so users know whether a language model wrote the text


def build_answering_pipeline(root: Path, env: Mapping[str, str] = os.environ) -> AnsweringPipeline:
    catalog = JsonSolutionCatalog(root / "data/solutions_catalog.json")
    passages = PdfPassageSearch(root, root / "data/rag_corpus.json", root / "data/rag_index/passages.json")
    narrator: Narrator = TemplateNarrator()
    label = "Template (no language model)"
    try:
        model = chat_model_from_env(env)
    except Exception as error:  # noqa: BLE001 - missing key, missing provider package or bad model name
        model, label = None, f"Template (model unavailable: {type(error).__name__}; check .env)"
    if model is not None:
        narrator = LangChainNarrator.from_chat_model(model, catalog)
        label = f"Language model ({env['PSI_LLM_MODEL']})"
    steps = AnsweringSteps(RelevanceRanker(), passages, narrator, RuleBasedValidator(catalog), catalog)
    return AnsweringPipeline(LangGraphAnswerer(steps), label)
