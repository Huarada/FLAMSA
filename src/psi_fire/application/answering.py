"""Answer a habitat-scenario question with validated, cited evidence (SPEC-003).

`AnsweringSteps` holds every node and routing decision once. `AnswerScenarioQuestion` runs them as a plain
loop (reference implementation); `infrastructure.answer_graph` wires the same steps into LangGraph.
"""

from psi_fire.application.answer_types import (
    AnswerResult,
    AnswerState,
    AnswerStatus,
    AttemptRecord,
    FigureTrace,
    NarrationRequest,
    RetrievalSettings,
    TraceEntry,
    ValidationContext,
)
from psi_fire.application.ports import AnswerValidator, Narrator, PassageSearch, SolutionCatalog
from psi_fire.domain.answering import Citation, CitationKind, Draft, IssueCode, ValidationIssue
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import HabitatScenario, RankedInvestigation, RelevanceRanker, limitations

MAX_ATTEMPTS = 2
STRICT_SETTINGS = RetrievalSettings(top_k=5, min_score=0.25, passages_per_investigation=2)
RELAXED_SETTINGS = RetrievalSettings(top_k=6, min_score=0.10, passages_per_investigation=4)

NODE_SEARCH = "search"
NODE_ANSWER = "answer"
NODE_VALIDATE = "validate"
NODE_ADVANCE = "advance"
NODE_FINALIZE = "finalize"


class NarrationError(Exception):
    """The narrator could not produce a structured draft (provider failure, malformed output)."""


def settings_for(attempt: int) -> RetrievalSettings:
    return STRICT_SETTINGS if attempt <= 1 else RELAXED_SETTINGS


def retrieval_query(question: str, scenario: HabitatScenario) -> str:
    """Generic questions ("which studies are relevant?") carry no content words, so add the scenario's own."""
    return (f"{question} oxygen concentration {scenario.o2_percent:g}% pressure {scenario.pressure_psi:g} psi "
            "flame spread burning fire safety microgravity")


def breakdown_text(shortlist: tuple[RankedInvestigation, ...]) -> str:
    """The deterministic fallback: the ranking rendered as plain text, no LLM involved."""
    if not shortlist:
        return "No investigation reached the minimum relevance score for this scenario."
    lines = []
    for item in shortlist:
        parts = "; ".join(f"{s.criterion} {s.value:.2f} x {s.weight:.2f} = {s.contribution:.3f} ({s.rationale})"
                          for s in item.breakdown.scores)
        lines.append(f"{item.rank}. {item.investigation.id}: relevance score {item.score:.3f}. {parts}")
    return "\n".join(lines)


def _sha(inv: Investigation, source_file: str) -> str | None:
    return next((f.sha256 for f in inv.source_files if f.path.endswith(source_file)
                 or source_file.endswith(f.path)), None)


def traceability(draft: Draft, shortlist: tuple[RankedInvestigation, ...]) -> tuple[TraceEntry, ...]:
    by_id = {r.investigation.id: r.investigation for r in shortlist}
    entries = []
    for index, claim in enumerate(draft.claims):
        for citation in claim.citations:
            inv = by_id[citation.investigation_id]
            entries.append(TraceEntry(index, citation, *_source_of(citation, inv), _status_of(citation, inv)))
    return tuple(entries)


PASSAGE_STATUS = "Document passage; the quote matched the retrieved text mechanically and is not human-reviewed"


def _status_of(citation: Citation, inv: Investigation) -> str:
    if citation.kind == CitationKind.RECORD:
        tp = next(tp for tp in inv.test_points if tp.test_point_id == citation.test_point_id)
        return f"Curated experimental record; provenance {tp.provenance_status.value}"
    if citation.kind == CitationKind.METADATA:
        manual = inv.manual_metadata
        if manual is not None and citation.field != "objective":
            return f"Curated metadata; review status {manual.review_status.value}"
        return "Curated study metadata extracted from the archived ISA-Tab record"
    return PASSAGE_STATUS


def with_figure_citations(draft: Draft, shortlist: tuple[RankedInvestigation, ...]) -> Draft:
    """A record figure that names an existing test point cites it by definition: add that citation.
    The number is still checked against the record, so this only completes traceability, never evidence."""
    known = {(r.investigation.id, tp.test_point_id) for r in shortlist for tp in r.investigation.test_points}
    claims = []
    for claim in draft.claims:
        cited = {(c.investigation_id, c.test_point_id) for c in claim.citations if c.kind == CitationKind.RECORD}
        added = []
        for f in claim.figures:
            key = (f.investigation_id, f.test_point_id)
            if f.source == "record" and key in known and key not in cited:
                added.append(Citation(kind=CitationKind.RECORD, investigation_id=f.investigation_id,
                                      test_point_id=f.test_point_id))
                cited.add(key)
        claims.append(claim.model_copy(update={"citations": (*claim.citations, *added)}) if added else claim)
    return draft.model_copy(update={"claims": tuple(claims)})


def figure_traces(draft: Draft, shortlist: tuple[RankedInvestigation, ...]) -> tuple[FigureTrace, ...]:
    """Record figures only: breakdown figures are computed by the application, not read from a source."""
    by_id = {r.investigation.id: r.investigation for r in shortlist}
    traces = []
    for index, claim in enumerate(draft.claims):
        for figure in claim.figures:
            if figure.source != "record":
                continue
            point = next(tp for tp in by_id[figure.investigation_id].test_points
                         if tp.test_point_id == figure.test_point_id)
            raw = getattr(point, f"{figure.column}_raw", None) or point.extras.get(f"{figure.column}_raw")
            traces.append(FigureTrace(index, point.investigation_id, point.test_point_id, figure.column, figure.value,
                                      figure.unit, None if raw is None else str(raw), point.source_file,
                                      point.source_row, point.provenance_status.value))
    return tuple(traces)


def _source_of(citation: Citation, inv: Investigation) -> tuple[str | None, str | None, str | None]:
    if citation.kind == CitationKind.RECORD:
        tp = next(tp for tp in inv.test_points if tp.test_point_id == citation.test_point_id)
        return tp.source_file, tp.source_row, _sha(inv, tp.source_file)
    if citation.kind == CitationKind.METADATA:
        manual = inv.manual_metadata
        claim = getattr(manual, citation.field or "", None) if manual else None
        evidence = claim.evidence[0] if claim is not None and claim.evidence else None
        if evidence is not None:
            return evidence.source_file, evidence.locator, None
        return inv.study_metadata_source, citation.field, None
    return citation.source_file, citation.locator, None


class AnsweringSteps:
    def __init__(self, ranker: RelevanceRanker, passages: PassageSearch, narrator: Narrator,
                 validator: AnswerValidator, catalog: SolutionCatalog) -> None:
        self._ranker, self._passages, self._narrator = ranker, passages, narrator
        self._validator, self._catalog = validator, catalog

    def start(self, investigations: tuple[Investigation, ...], scenario: HabitatScenario,
              question: str) -> AnswerState:
        return AnswerState(investigations=investigations, scenario=scenario, question=question, attempt=1,
                           settings=settings_for(1), attempts=(), issues=(), draft=None)

    def retrieve(self, state: AnswerState) -> AnswerState:
        settings = state["settings"]
        ranked = self._ranker.rank(state["investigations"], state["scenario"])
        kept = tuple(r for r in ranked if r.score >= settings.min_score)[: settings.top_k]
        # issues stay: on a retry they are the rejection reasons handed to the narrator
        return AnswerState(shortlist=kept, passages=(), draft=None)

    def route_after_retrieve(self, state: AnswerState) -> str:
        return NODE_SEARCH if state["shortlist"] else NODE_FINALIZE  # empty shortlist: never call the narrator

    def search(self, state: AnswerState) -> AnswerState:
        ids = tuple(r.investigation.id for r in state["shortlist"])
        found = self._passages.search(retrieval_query(state["question"], state["scenario"]), ids,
                                      state["settings"].passages_per_investigation)
        return AnswerState(passages=found)

    def answer(self, state: AnswerState) -> AnswerState:
        request = NarrationRequest(state["question"], state["scenario"], state["shortlist"], state["passages"],
                                   state["issues"], state["attempt"])
        try:
            return AnswerState(draft=self._narrator.draft(request))
        except NarrationError as error:
            return AnswerState(draft=None, issues=(ValidationIssue(code=IssueCode.EMPTY_DRAFT,
                                                                   message=f"Narrator failed: {error}"),))

    def validate(self, state: AnswerState) -> AnswerState:
        draft = state.get("draft")
        if draft is None:
            issues = state["issues"]
        else:
            draft = with_figure_citations(draft, state["shortlist"])
            issues = self._validator.validate(
                draft, ValidationContext(state["scenario"], state["shortlist"], state["passages"]))
        record = AttemptRecord(state["attempt"], state["settings"],
                               tuple(r.investigation.id for r in state["shortlist"]),
                               len(state["passages"]), issues, draft, state["passages"])
        return AnswerState(draft=draft, issues=issues, attempts=(*state["attempts"], record))

    def route_after_validate(self, state: AnswerState) -> str:
        if not state["issues"]:
            return NODE_FINALIZE
        return NODE_ADVANCE if state["attempt"] < MAX_ATTEMPTS else NODE_FINALIZE

    def advance(self, state: AnswerState) -> AnswerState:
        attempt = state["attempt"] + 1
        return AnswerState(attempt=attempt, settings=settings_for(attempt))

    def finalize(self, state: AnswerState) -> AnswerState:
        shortlist, draft, issues = state.get("shortlist", ()), state.get("draft"), state.get("issues", ())
        approved = bool(shortlist) and draft is not None and not issues
        cited = {c.investigation_id for claim in (draft.claims if approved and draft else ()) for c in claim.citations}
        solutions = tuple(s for inv_id in sorted(cited) for s in self._catalog.lookup(inv_id)) if approved else ()
        return AnswerState(result=AnswerResult(
            status=AnswerStatus.APPROVED if approved else AnswerStatus.INSUFFICIENT_EVIDENCE,
            scenario=state["scenario"], question=state["question"], shortlist=shortlist,
            draft=draft if approved else None, solutions=solutions, issues=() if approved else issues,
            limitations=limitations(state["scenario"], shortlist), breakdown_text=breakdown_text(shortlist),
            attempts=state.get("attempts", ()),
            traceability=traceability(draft, shortlist) if approved and draft else (),
            figure_traces=figure_traces(draft, shortlist) if approved and draft else ()))


def merge(state: AnswerState, update: AnswerState) -> AnswerState:
    merged = AnswerState(**state)  # type: ignore[typeddict-item]
    merged.update(update)
    return merged


class AnswerScenarioQuestion:
    """Plain-Python reference loop: retrieve -> search -> answer -> validate -> retry or finalize."""

    def __init__(self, steps: AnsweringSteps) -> None:
        self._steps = steps

    def __call__(self, investigations: tuple[Investigation, ...], scenario: HabitatScenario,
                 question: str) -> AnswerResult:
        steps = self._steps
        state = steps.start(investigations, scenario, question)
        while True:
            state = merge(state, steps.retrieve(state))
            if steps.route_after_retrieve(state) == NODE_FINALIZE:
                break
            state = merge(state, steps.search(state))
            state = merge(state, steps.answer(state))
            state = merge(state, steps.validate(state))
            if steps.route_after_validate(state) == NODE_FINALIZE:
                break
            state = merge(state, steps.advance(state))
        return merge(state, steps.finalize(state))["result"]
