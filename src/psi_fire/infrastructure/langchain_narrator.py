"""Narrator backed by a LangChain chat model with structured output (SPEC-003 section 3.2).

The model receives the computed ranking, curated records and retrieved passages, and must answer with a `Draft`.
Whatever it writes is checked by the deterministic validator; it never computes or alters a score.
"""

import json
import os
from collections.abc import Mapping

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from psi_fire.application.answer_types import NarrationRequest
from psi_fire.application.answer_validation import available_metadata_fields
from psi_fire.application.answering import NarrationError
from psi_fire.application.ports import SolutionCatalog
from psi_fire.domain.answering import METADATA_FIELDS, Draft
from psi_fire.domain.ranking import RankedInvestigation

LLM_ENV = "PSI_LLM_MODEL"  # e.g. "openai:gpt-4.1-mini" or "google_genai:gemini-2.5-flash"
MAX_RECORDS_PER_INVESTIGATION = 6
MAX_PASSAGE_CHARS = 1200

SYSTEM_PROMPT = """You explain which NASA PSI combustion investigations are relevant to a habitat scenario.
Answer ONLY with the structured Draft. Rules, all machine-checked (a violation rejects the draft):
1. Every claim needs at least one citation, and cites only what you were given:
   - kind "record": investigation_id + test_point_id copied exactly from the provided records (the id string only,
     with no brackets, braces or commas);
   - kind "metadata": investigation_id + field, ONLY from that investigation's `metadata_fields_available` list
     (a field in `metadata_fields_NEVER_cite` does not exist for it; use a record citation instead);
   - kind "breakdown": investigation_id + field = "score", "rank" or a criterion name from that investigation's
     `criteria` list. Use it whenever you refer to the ranking or a criterion; never put a criterion name in a metadata field;
   - kind "passage": investigation_id + source_file + locator + a quote of 20-200 characters copied character for character as ONE contiguous span of the provided passage.
     Do not paraphrase, merge sentences or fix wording. If you need two separate spans of the SAME passage, join them
     with " ... " and copy each piece exactly, in page order. If no passage supports a claim, cite records or metadata instead.
2. Every number in a claim's text must also be declared in `figures`:
   - source "record": the value lies in the cited test point's range (column o2_percent, pressure_psi, ...); set
     test_point_id AND add a kind "record" citation for that same test point to the SAME claim;
   - source "breakdown": column "score", "rank" or a criterion name, copied from the provided ranking.
   The scenario's own oxygen and pressure values may be written without declaring them.
   Never compute, round differently, or change a score or rank. Never write a number you did not declare.
   Prefer wording without digits ("a higher-oxygen test", "close to the scenario"); every digit you write, including
   in ranges and counts, must be a declared figure, and a record figure must carry its test_point_id.
3. Name a derived technology in `technologies` only if it appears in the provided solutions for a cited investigation.
   If the question asks which technology to use and no solutions are provided, do NOT recommend or name any:
   state that the curated PSI data contains no technology recommendations, and describe instead what the cited
   records and passages show about burning behavior at the scenario's oxygen and pressure.
4. PSI has no partial-gravity data; if you mention partial gravity, say so (E-FIELD only emulates it).
5. Do not restate the limitations list; it is shown separately. Be concise: at most one claim per investigation.
Refer to investigations as [ID]. If previous_issues is not empty, fix exactly those problems."""


def _record(inv: RankedInvestigation, evidence_ids: set[str]) -> list[dict[str, object]]:
    points = [tp for tp in inv.investigation.test_points if tp.test_point_id in evidence_ids]
    points += [tp for tp in inv.investigation.test_points if tp.test_point_id not in evidence_ids]
    return [{"test_point_id": tp.test_point_id, "fuel": tp.fuel_name, "o2_percent": [tp.o2_percent_min, tp.o2_percent_max],
             "o2_basis": tp.o2_basis, "pressure_psi": [tp.pressure_psi_min, tp.pressure_psi_max],
             "record_level": tp.record_level} for tp in points[:MAX_RECORDS_PER_INVESTIGATION]]


def available_metadata(item: RankedInvestigation) -> list[str]:
    return list(available_metadata_fields(item.investigation))


def missing_metadata(item: RankedInvestigation) -> list[str]:
    return [f for f in METADATA_FIELDS if f not in available_metadata(item)]


def request_payload(request: NarrationRequest, catalog: SolutionCatalog) -> dict[str, object]:
    ranking = []
    for item in request.shortlist:
        evidence = {e for s in item.breakdown.scores for e in s.evidence}
        ranking.append({
            "investigation_id": item.investigation.id, "rank": item.rank, "score": item.score,
            "metadata_fields_available": available_metadata(item),
            "metadata_fields_NEVER_cite": missing_metadata(item),
            "criteria": [{"criterion": s.criterion, "value": s.value, "contribution": s.contribution,
                          "rationale": s.rationale} for s in item.breakdown.scores],
            "records": _record(item, evidence),
            "solutions": [{"technology": s.technology, "status": s.status}
                          for s in catalog.lookup(item.investigation.id)],
        })
    return {
        "question": request.question,
        "scenario": {"name": request.scenario.name, "o2_percent": request.scenario.o2_percent,
                     "pressure_psi": request.scenario.pressure_psi, "gravity": request.scenario.gravity},
        "ranking": ranking,
        "passages": [{"investigation_id": p.investigation_id, "source_file": p.source_file, "locator": p.locator,
                      "text": p.text[:MAX_PASSAGE_CHARS]} for p in request.passages],
        "previous_issues": [{"code": i.code, "message": i.message, "claim_index": i.claim_index}
                            for i in request.previous_issues],
    }


class LangChainNarrator:
    def __init__(self, chain: Runnable[list[BaseMessage], Draft], catalog: SolutionCatalog) -> None:
        self._chain, self._catalog = chain, catalog

    @classmethod
    def from_chat_model(cls, model: object, catalog: SolutionCatalog) -> "LangChainNarrator":
        chain = model.with_structured_output(Draft)  # type: ignore[attr-defined]
        return cls(chain, catalog)

    def draft(self, request: NarrationRequest) -> Draft:
        payload = json.dumps(request_payload(request, self._catalog), default=str, ensure_ascii=False)
        messages: list[BaseMessage] = [SystemMessage(SYSTEM_PROMPT), HumanMessage(payload)]
        try:
            result = self._chain.invoke(messages)
        except Exception as error:
            raise NarrationError(f"{type(error).__name__}: {error}") from error
        if not isinstance(result, Draft):
            raise NarrationError("The model did not return a Draft.")
        return result


def chat_model_from_env(env: Mapping[str, str] = os.environ) -> object | None:
    """None when PSI_LLM_MODEL is unset: the interface then uses the template narrator."""
    spec = env.get(LLM_ENV, "").strip()
    if not spec:
        return None
    from langchain.chat_models import init_chat_model

    return init_chat_model(spec, temperature=0)
