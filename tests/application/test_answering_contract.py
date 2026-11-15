"""SPEC-003 acceptance AO-01..AO-08 with fakes, run against both orchestration engines."""

from pathlib import Path

import pytest

from psi_fire.application.answer_types import AnswerStatus, NarrationRequest, Passage, Solution
from psi_fire.application.answer_validation import RuleBasedValidator
from psi_fire.application.answering import (
    MAX_ATTEMPTS,
    RELAXED_SETTINGS,
    STRICT_SETTINGS,
    AnsweringSteps,
    AnswerScenarioQuestion,
    NarrationError,
)
from psi_fire.application.explore import LoadExplorer
from psi_fire.application.template_narrator import TemplateNarrator
from psi_fire.domain.answering import Citation, CitationKind, Claim, Draft, Figure, IssueCode
from psi_fire.domain.ranking import LUNAR_BASE, HabitatScenario, RelevanceRanker
from psi_fire.infrastructure.answer_graph import LangGraphAnswerer
from psi_fire.infrastructure.explorer import FileSnapshotProvider

ROOT = Path(__file__).resolve().parents[2]
PAGE_TEXT = "The flame spread rate increases with oxygen concentration in these tests."


@pytest.fixture(scope="module")
def investigations():
    return LoadExplorer(FileSnapshotProvider(ROOT))().investigations


class FakePassages:
    def __init__(self, passages: tuple[Passage, ...] = ()) -> None:
        self.passages, self.calls = passages, 0

    def search(self, query, investigation_ids, per_investigation):
        self.calls += 1
        return tuple(p for p in self.passages if p.investigation_id in investigation_ids)


class Catalog:
    def __init__(self, *entries: Solution) -> None:
        self.entries = entries

    def lookup(self, investigation_id):
        return tuple(e for e in self.entries if e.investigation_id == investigation_id)


class ScriptedNarrator:
    """Returns the scripted drafts in order (the last one repeats); records every request."""

    def __init__(self, *drafts: Draft | Exception) -> None:
        self.drafts, self.requests = drafts, []

    def draft(self, request: NarrationRequest) -> Draft:
        self.requests.append(request)
        item = self.drafts[min(len(self.requests), len(self.drafts)) - 1]
        if isinstance(item, Exception):
            raise item
        return item


def build(engine, narrator, passages=None, catalog=None):
    catalog = catalog or Catalog()
    steps = AnsweringSteps(RelevanceRanker(), passages or FakePassages(), narrator, RuleBasedValidator(catalog), catalog)
    return AnswerScenarioQuestion(steps) if engine == "loop" else LangGraphAnswerer(steps)


engines = pytest.mark.parametrize("engine", ["loop", "graph"])


def valid_claim(result_shortlist, **extra) -> Claim:
    top = result_shortlist[0]
    tp = top.investigation.test_points[0]
    return Claim(text=f"[{top.investigation.id}] is the top match.",
                 citations=(Citation(kind=CitationKind.RECORD, investigation_id=top.investigation.id,
                                     test_point_id=tp.test_point_id),), **extra)


def shortlist_of(investigations, scenario=LUNAR_BASE):
    return RelevanceRanker().rank(investigations, scenario)[: STRICT_SETTINGS.top_k]


def ghost_draft() -> Draft:
    return Draft(claims=(Claim(text="[GHOST] matches.", citations=(
        Citation(kind=CitationKind.RECORD, investigation_id="GHOST", test_point_id="1"),)),))


@engines
def test_ao01_same_input_gives_same_shortlist_and_breakdown(engine, investigations):
    answer = build(engine, TemplateNarrator())
    first, second = (answer(investigations, LUNAR_BASE, "Which study is closest?") for _ in range(2))
    assert [r.investigation.id for r in first.shortlist] == [r.investigation.id for r in second.shortlist]
    assert [r.breakdown for r in first.shortlist] == [r.breakdown for r in second.shortlist]


@engines
def test_ao02_unknown_citation_is_rejected_then_falls_back_to_the_breakdown(engine, investigations):
    narrator = ScriptedNarrator(ghost_draft())
    result = build(engine, narrator)(investigations, LUNAR_BASE, "Which study is closest?")
    assert result.status == AnswerStatus.INSUFFICIENT_EVIDENCE and result.draft is None
    assert len(result.attempts) == MAX_ATTEMPTS == len(narrator.requests)
    assert {i.code for i in result.issues} == {IssueCode.UNKNOWN_CITATION}
    assert result.breakdown_text.startswith("1. ") and result.limitations


@engines
def test_ao03_number_that_differs_from_the_record_is_rejected(engine, investigations):
    top = shortlist_of(investigations)[0]
    tp = next(t for t in top.investigation.test_points if t.o2_percent_min is not None and t.o2_basis)
    wrong = Claim(text=f"[{top.investigation.id}] burns at 99.5% oxygen.", citations=(
        Citation(kind=CitationKind.RECORD, investigation_id=top.investigation.id, test_point_id=tp.test_point_id),),
        figures=(Figure(source="record", investigation_id=top.investigation.id, column="o2_percent",
                        value=99.5, test_point_id=tp.test_point_id),))
    undeclared = Claim(text=f"[{top.investigation.id}] burns at 12.34 psi.", citations=wrong.citations)
    result = build(engine, ScriptedNarrator(Draft(claims=(wrong, undeclared))))(investigations, LUNAR_BASE, "q")
    codes = {i.code for i in result.issues}
    assert IssueCode.NUMBER_MISMATCH in codes and IssueCode.UNDECLARED_NUMBER in codes


@engines
def test_ao04_valid_draft_is_approved_and_every_claim_maps_to_an_archived_source(engine, investigations):
    result = build(engine, TemplateNarrator())(investigations, LUNAR_BASE, "Which study is closest?")
    assert result.status == AnswerStatus.APPROVED and result.draft and not result.issues
    assert {e.claim_index for e in result.traceability} == set(range(len(result.draft.claims)))
    assert all(e.source_file and e.locator for e in result.traceability)


@engines
def test_ao05_retry_relaxes_retrieval_and_hands_the_issues_to_the_narrator(engine, investigations):
    good = Draft(claims=(valid_claim(shortlist_of(investigations)),))
    narrator = ScriptedNarrator(ghost_draft(), good)
    result = build(engine, narrator)(investigations, LUNAR_BASE, "q")
    assert result.status == AnswerStatus.APPROVED
    assert [a.settings for a in result.attempts] == [STRICT_SETTINGS, RELAXED_SETTINGS]
    assert narrator.requests[0].previous_issues == ()
    assert narrator.requests[1].previous_issues and narrator.requests[1].attempt == 2


@engines
def test_ao06_empty_shortlist_never_calls_the_narrator(engine):
    narrator = ScriptedNarrator(ghost_draft())
    result = build(engine, narrator)((), LUNAR_BASE, "q")
    assert result.status == AnswerStatus.INSUFFICIENT_EVIDENCE and narrator.requests == []


@engines
def test_ao07_illustrative_solutions_are_labeled_and_never_replace_a_citation(engine, investigations):
    top = shortlist_of(investigations)[0].investigation.id
    entry = Solution(top, "Example detector", "illustrative")
    catalog = Catalog(entry)
    ok = Draft(claims=(valid_claim(shortlist_of(investigations), technologies=("Example detector",)),))
    approved = build(engine, ScriptedNarrator(ok), catalog=catalog)(investigations, LUNAR_BASE, "q")
    assert approved.status == AnswerStatus.APPROVED and approved.solutions == (entry,)
    unbacked = Draft(claims=(valid_claim(shortlist_of(investigations), technologies=("Made-up gadget",)),))
    uncited = Draft(claims=(Claim(text="A detector helps.", technologies=("Example detector",)),))
    for draft, code in ((unbacked, IssueCode.UNBACKED_TECHNOLOGY), (uncited, IssueCode.MISSING_CITATION)):
        result = build(engine, ScriptedNarrator(draft), catalog=catalog)(investigations, LUNAR_BASE, "q")
        assert code in {i.code for i in result.issues}


@engines
def test_ao08_partial_gravity_limitation_is_added_whatever_the_narrator_writes(engine, investigations):
    result = build(engine, TemplateNarrator())(investigations, LUNAR_BASE, "q")
    assert any("no partial-gravity data" in note for note in result.limitations)
    earth = HabitatScenario("Earth cabin", 21.0, 14.7)
    assert not any("partial-gravity" in n for n in build(engine, TemplateNarrator())(investigations, earth, "q").limitations)


@engines
def test_narrator_failure_is_a_rejection_not_a_crash(engine, investigations):
    result = build(engine, ScriptedNarrator(NarrationError("provider down")))(investigations, LUNAR_BASE, "q")
    assert result.status == AnswerStatus.INSUFFICIENT_EVIDENCE
    assert "provider down" in result.issues[0].message


@engines
def test_passage_quotes_must_come_from_a_passage_retrieved_in_this_attempt(engine, investigations):
    top = shortlist_of(investigations)[0].investigation.id
    page = Passage(top, "knowledgeBase/x.pdf", "p. 3", PAGE_TEXT)

    def draft(quote: str) -> Draft:
        citation = Citation(kind=CitationKind.PASSAGE, investigation_id=top, source_file=page.source_file,
                            locator=page.locator, quote=quote)
        return Draft(claims=(Claim(text=f"[{top}] reports a trend.", citations=(citation,)),))

    good = build(engine, ScriptedNarrator(draft("flame spread rate increases with oxygen")), FakePassages((page,)))
    assert good(investigations, LUNAR_BASE, "q").status == AnswerStatus.APPROVED
    bad = build(engine, ScriptedNarrator(draft("flame spread rate decreases with oxygen")), FakePassages((page,)))
    assert IssueCode.QUOTE_MISMATCH in {i.code for i in bad(investigations, LUNAR_BASE, "q").issues}
    missing = build(engine, ScriptedNarrator(draft("flame spread rate increases with oxygen")), FakePassages())
    assert IssueCode.UNKNOWN_CITATION in {i.code for i in missing(investigations, LUNAR_BASE, "q").issues}


@engines
def test_claiming_partial_gravity_data_is_implausible(engine, investigations):
    claim = valid_claim(shortlist_of(investigations))
    bad = claim.model_copy(update={"text": f"[{claim.citations[0].investigation_id}] provides partial-gravity data."})
    result = build(engine, ScriptedNarrator(Draft(claims=(bad,))))(investigations, LUNAR_BASE, "q")
    assert IssueCode.IMPLAUSIBLE in {i.code for i in result.issues}


def test_ao09_domain_and_application_do_not_import_orchestration_or_llm_libraries():
    banned = ("langchain", "langgraph", "openai", "google.generativeai", "sklearn", "pypdf")
    for layer in ("domain", "application"):
        for path in (ROOT / "src/psi_fire" / layer).glob("*.py"):
            imports = [ln for ln in path.read_text(encoding="utf-8").splitlines()
                       if ln.startswith(("import ", "from "))]
            assert not [ln for ln in imports if any(b in ln for b in banned)], path.name
