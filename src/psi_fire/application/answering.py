"""Answer a habitat-scenario question with validated, cited evidence (SPEC-003).

`AnsweringSteps` holds every node and routing decision once. `AnswerScenarioQuestion` runs them as a plain
loop (reference implementation); `infrastructure.answer_graph` wires the same steps into LangGraph.
"""

import re
from math import isclose

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
from psi_fire.application.answer_validation import record_values, unbacked_numbers
from psi_fire.application.ports import AnswerValidator, Narrator, PassageSearch, SolutionCatalog
from psi_fire.domain.answering import (
    NUMBER_ABSOLUTE_TOLERANCE,
    NUMBER_RELATIVE_TOLERANCE,
    Citation,
    CitationKind,
    Draft,
    Figure,
    IssueCode,
    ValidationIssue,
    numbers_in,
)
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


QUESTION_WEIGHT = 3  # stress test: scenario words alone drowned specific questions (hardware hit rate 0.2 -> 0.6)


def retrieval_query(question: str, scenario: HabitatScenario) -> str:
    """Generic questions ("which studies are relevant?") carry no content words, so add the scenario's own,
    but repeat the question so its words still outweigh the added ones."""
    return (f"{' '.join([question] * QUESTION_WEIGHT)} oxygen concentration {scenario.o2_percent:g}% pressure "
            f"{scenario.pressure_psi:g} psi flame spread burning fire safety microgravity")


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
    if citation.kind == CitationKind.BREAKDOWN:
        return "Computed by the application's deterministic ranking; not a source document"
    if citation.kind == CitationKind.RECORD:
        tp = next(tp for tp in inv.test_points if tp.test_point_id == citation.test_point_id)
        return f"Curated experimental record; provenance {tp.provenance_status.value}"
    if citation.kind == CitationKind.METADATA:
        manual = inv.manual_metadata
        return f"Curated metadata; review status {manual.review_status.value}" if manual else "Curated metadata"
    return PASSAGE_STATUS


_JSON_DEBRIS = re.compile(r"""^[\s"'\[\]{},:]+|[\s"'\[\]{},:]+$""")


def clean_identifiers(draft: Draft) -> Draft:
    """Structured output sometimes leaves JSON punctuation inside an id string ("25},{"). Strip only the punctuation
    at its ends; the cleaned id must still exist, so nothing unverified becomes valid."""
    claims = []
    for claim in draft.claims:
        citations = tuple(c.model_copy(update={"test_point_id": _JSON_DEBRIS.sub("", c.test_point_id)})
                          if c.test_point_id else c for c in claim.citations)
        figures = tuple(f.model_copy(update={"test_point_id": _JSON_DEBRIS.sub("", f.test_point_id)})
                        if f.test_point_id else f for f in claim.figures)
        claims.append(claim.model_copy(update={"citations": citations, "figures": figures}))
    return draft.model_copy(update={"claims": tuple(claims)})


def reclassify_breakdown_citations(draft: Draft, shortlist: tuple[RankedInvestigation, ...]) -> Draft:
    """A metadata citation whose field is really a score, rank or criterion of that investigation's breakdown is the
    same mistake every time (the model reaches for the ranking). Re-label it as a breakdown citation; the validator
    still checks the field against the real breakdown, so an invented name stays invalid."""
    ranked = {r.investigation.id: r for r in shortlist}
    claims = []
    for claim in draft.claims:
        citations = []
        for c in claim.citations:
            target = ranked.get(c.investigation_id)
            names = {"score", "rank", *(s.criterion for s in target.breakdown.scores)} if target else set()
            if c.kind == CitationKind.METADATA and c.field in names:
                c = c.model_copy(update={"kind": CitationKind.BREAKDOWN})
            citations.append(c)
        claims.append(claim.model_copy(update={"citations": tuple(citations)}))
    return draft.model_copy(update={"claims": tuple(claims)})


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


def with_declared_figures(draft: Draft, shortlist: tuple[RankedInvestigation, ...],
                          scenario: HabitatScenario, question: str = "") -> Draft:
    """A number in the text that equals a value of a record the claim cites is declared as that record's figure.
    The validator then checks it like any figure; a number matching no cited record stays undeclared and is rejected."""
    ranked = {r.investigation.id: r for r in shortlist}
    scenario_numbers = [scenario.o2_percent, scenario.pressure_psi, *numbers_in(question)]
    claims = []
    for claim in draft.claims:
        cited = [(c.investigation_id, c.test_point_id) for c in claim.citations if c.kind == CitationKind.RECORD]
        added: list[Figure] = []
        for number in unbacked_numbers(claim, ranked, scenario_numbers):
            for inv_id, point_id in cited:
                point = next((tp for tp in ranked[inv_id].investigation.test_points if tp.test_point_id == point_id),
                             None) if inv_id in ranked else None
                match = next(((c, u) for c, v, u in record_values(point) if _same(number, v)), None) if point else None
                if match:
                    added.append(Figure(source="record", investigation_id=inv_id, column=match[0], value=number,
                                        unit=match[1], test_point_id=point_id))
                    break
        claims.append(claim.model_copy(update={"figures": (*claim.figures, *added)}) if added else claim)
    return draft.model_copy(update={"claims": tuple(claims)})


def _same(a: float, b: float) -> bool:
    return isclose(a, b, rel_tol=NUMBER_RELATIVE_TOLERANCE, abs_tol=NUMBER_ABSOLUTE_TOLERANCE)


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
    if citation.kind == CitationKind.BREAKDOWN:
        return None, f"ranking: {citation.field}", None  # computed by the application, not read from a document
    if citation.kind == CitationKind.RECORD:
        tp = next(tp for tp in inv.test_points if tp.test_point_id == citation.test_point_id)
        return tp.source_file, tp.source_row, _sha(inv, tp.source_file)
    if citation.kind == CitationKind.METADATA:
        manual = inv.manual_metadata
        value = getattr(manual, citation.field or "", None) if manual else None
        claims = value if isinstance(value, tuple) else (value,)  # sensors and Earth applications are lists of claims
        evidence = next((e for c in claims if c is not None for e in c.evidence), None)
        if evidence is not None:
            return evidence.source_file, evidence.locator, None
        return None, citation.field, None  # no evidence recorded for this field: reported as missing, never guessed
    return citation.source_file, citation.locator, None


TECHNOLOGY_WORDS = ("technolog", "recommend", "implement", "install", "extinguish", "suppression system", "protect")
TECHNOLOGY_NOTICE = ("This copilot does not recommend protection technologies: the curated PSI data describe combustion "
                     "behavior, not evaluations of safety technologies, and the solutions catalog is empty.")


def answer_limitations(scenario: HabitatScenario, shortlist: tuple[RankedInvestigation, ...], question: str,
                       catalog: SolutionCatalog) -> tuple[str, ...]:
    """Domain limitations plus, from the application itself, the honest scope note for technology questions."""
    notes = limitations(scenario, shortlist)
    asks_for_technology = any(w in question.casefold() for w in TECHNOLOGY_WORDS)
    if asks_for_technology and not any(catalog.lookup(r.investigation.id) for r in shortlist):
        notes = (*notes, TECHNOLOGY_NOTICE)
    return notes


MIN_PARTIAL_CLAIMS = 2    # a partial answer needs at least this many validated claims ...
MIN_PARTIAL_SHARE = 0.5   # ... and at least this share of the draft, else the strict fallback applies


def validated_subset(draft: Draft, issues: tuple[ValidationIssue, ...]) -> Draft | None:
    """The claims that raised no issue, if they are enough to stand as a partial answer; otherwise None.
    Issues without a claim index (whole-draft failures) never allow a partial answer."""
    if not draft.claims or any(i.claim_index is None for i in issues):
        return None
    failing = {i.claim_index for i in issues}
    kept = tuple(c for index, c in enumerate(draft.claims) if index not in failing)
    if len(kept) < MIN_PARTIAL_CLAIMS or len(kept) / len(draft.claims) < MIN_PARTIAL_SHARE:
        return None
    return draft.model_copy(update={"claims": kept})


class AnsweringSteps:
    def __init__(self, ranker: RelevanceRanker, passages: PassageSearch, narrator: Narrator,
                 validator: AnswerValidator, catalog: SolutionCatalog, allow_partial: bool = True) -> None:
        self._ranker, self._passages, self._narrator = ranker, passages, narrator
        self._validator, self._catalog = validator, catalog
        self._allow_partial = allow_partial  # False = strict mode: one failing claim rejects the answer

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
            draft = with_declared_figures(with_figure_citations(
                clean_identifiers(reclassify_breakdown_citations(draft, state["shortlist"])), state["shortlist"]),
                                          state["shortlist"], state["scenario"], state["question"])
            issues = self._validator.validate(
                draft, ValidationContext(state["scenario"], state["shortlist"], state["passages"], state["question"]))
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
        total = len(draft.claims) if draft else 0
        shown, status = None, AnswerStatus.INSUFFICIENT_EVIDENCE
        if shortlist and draft is not None and not issues:
            shown, status = draft, AnswerStatus.APPROVED
        elif shortlist and draft is not None and self._allow_partial:
            subset = validated_subset(draft, issues)
            context = ValidationContext(state["scenario"], shortlist, state.get("passages", ()), state["question"])
            if subset is not None and not self._validator.validate(subset, context):  # the kept claims stand alone
                shown, status = subset, AnswerStatus.PARTIAL
        cited = {c.investigation_id for claim in (shown.claims if shown else ()) for c in claim.citations}
        solutions = tuple(s for inv_id in sorted(cited) for s in self._catalog.lookup(inv_id)) if shown else ()
        return AnswerState(result=AnswerResult(
            status=status, scenario=state["scenario"], question=state["question"], shortlist=shortlist,
            draft=shown, solutions=solutions, issues=() if status == AnswerStatus.APPROVED else issues,
            limitations=answer_limitations(state["scenario"], shortlist, state["question"], self._catalog),
            breakdown_text=breakdown_text(shortlist),
            attempts=state.get("attempts", ()),
            traceability=traceability(shown, shortlist) if shown else (),
            figure_traces=figure_traces(shown, shortlist) if shown else (),
            claims_total=total, claims_withheld=total - len(shown.claims) if shown else 0))


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
