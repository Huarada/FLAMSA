"""SPEC-003 section 4.1: claim-level traceability and source access, with fake narrators (no paid API call)."""

from pathlib import Path

import pytest

from psi_fire.application.answer_types import AnswerStatus, Passage, TraceEntry
from psi_fire.application.answer_validation import RuleBasedValidator
from psi_fire.application.answering import PASSAGE_STATUS, AnsweringSteps, AnswerScenarioQuestion
from psi_fire.application.evidence import InvestigationSources
from psi_fire.application.explore import DatasetError, LoadExplorer
from psi_fire.application.source_access import ResolveCitationSource, SourceDocument, SourceStatus
from psi_fire.domain.answering import Citation, CitationKind, Claim, Draft, Figure
from psi_fire.domain.ranking import LUNAR_BASE, RelevanceRanker
from psi_fire.infrastructure.explorer import FileSnapshotProvider

ROOT = Path(__file__).resolve().parents[2]
PAGE_TEXT = "The flame spread rate increases with oxygen concentration in these tests."


class NoCatalog:
    def lookup(self, investigation_id):
        return ()


class Passages:
    def __init__(self, *passages: Passage) -> None:
        self.passages = passages

    def search(self, query, investigation_ids, per_investigation):
        return tuple(p for p in self.passages if p.investigation_id in investigation_ids)


class FixedNarrator:
    def __init__(self, draft: Draft) -> None:
        self._draft = draft

    def draft(self, request) -> Draft:
        return self._draft


@pytest.fixture(scope="module")
def investigations():
    return LoadExplorer(FileSnapshotProvider(ROOT))().investigations


def answer(investigations, draft: Draft, passages: Passages | None = None):
    catalog = NoCatalog()
    steps = AnsweringSteps(RelevanceRanker(), passages or Passages(), FixedNarrator(draft), RuleBasedValidator(catalog),
                           catalog)
    return AnswerScenarioQuestion(steps)(investigations, LUNAR_BASE, "q")


def top_with_ranged_o2(investigations):
    for item in RelevanceRanker().rank(investigations, LUNAR_BASE)[:5]:
        point = next((t for t in item.investigation.test_points if t.o2_percent_min is not None and t.o2_basis), None)
        if point is not None:
            return item.investigation, point
    pytest.skip("no shortlisted record with oxygen")


def test_every_approved_claim_keeps_investigation_document_locator_status_and_figure_lineage(investigations):
    inv, point = top_with_ranged_o2(investigations)
    value = point.o2_percent_min
    page = Passage(inv.id, "knowledgeBase/fake/report.pdf", "p. 3", PAGE_TEXT)
    record = Citation(kind=CitationKind.RECORD, investigation_id=inv.id, test_point_id=point.test_point_id)
    claim = Claim(text=f"[{inv.id}] was tested at {value:g}% oxygen.", citations=(
        record, Citation(kind=CitationKind.PASSAGE, investigation_id=inv.id, source_file=page.source_file,
                         locator=page.locator, quote=PAGE_TEXT)),
        figures=(Figure(source="record", investigation_id=inv.id, column="o2_percent", value=value, unit="percent",
                        test_point_id=point.test_point_id),))
    result = answer(investigations, Draft(claims=(claim,)), Passages(page))
    assert result.status == AnswerStatus.APPROVED
    by_kind = {e.citation.kind: e for e in result.traceability}
    assert by_kind[CitationKind.RECORD].status.startswith("Curated experimental record")
    assert by_kind[CitationKind.RECORD].source_file == point.source_file
    assert by_kind[CitationKind.PASSAGE].status == PASSAGE_STATUS and "not human-reviewed" in PASSAGE_STATUS
    assert (by_kind[CitationKind.PASSAGE].source_file, by_kind[CitationKind.PASSAGE].locator) == (page.source_file, "p. 3")
    (figure,) = result.figure_traces
    assert (figure.test_point_id, figure.column, figure.unit) == (point.test_point_id, "o2_percent", "percent")
    assert (figure.source_row, figure.raw) == (point.source_row, point.o2_percent_raw)


def test_a_rejected_answer_exposes_no_citations_and_no_figures(investigations):
    ghost = Claim(text="[GHOST] matches.", citations=(
        Citation(kind=CitationKind.RECORD, investigation_id="GHOST", test_point_id="1"),))
    result = answer(investigations, Draft(claims=(ghost,)))
    assert result.status == AnswerStatus.INSUFFICIENT_EVIDENCE
    assert result.traceability == () and result.figure_traces == () and result.breakdown_text and result.limitations


class FakeReader:
    def __init__(self, registered, fail: str | None = None) -> None:
        self.registered, self.fail = registered, fail

    def list_for(self, investigation_id):
        return tuple({"handle": f"h{i}", "path": p, "locator": "", "digest": "abc", "label": "Report"}
                     for i, p in enumerate(self.registered))

    def read(self, investigation_id, handle):
        if self.fail:
            raise DatasetError(self.fail)
        return b"%PDF-fake", "report.pdf", "application/pdf"


def entry(path: str | None) -> TraceEntry:
    citation = Citation(kind=CitationKind.PASSAGE, investigation_id="FLEX", source_file=path, locator="p. 3",
                        quote=PAGE_TEXT)
    return TraceEntry(0, citation, path, "p. 3", None, PASSAGE_STATUS)


def test_registered_source_opens_and_keeps_its_checksum():
    opened = ResolveCitationSource(InvestigationSources(FakeReader(["a/report.pdf"]))).open(entry("a/report.pdf"))
    assert isinstance(opened, SourceDocument) and opened.content.startswith(b"%PDF")
    assert opened.access.digest == "abc" and opened.access.status == SourceStatus.AVAILABLE


@pytest.mark.parametrize("path", [None, "elsewhere/report.pdf", "../../secret.txt", "/etc/passwd"])
def test_a_path_the_model_names_is_never_opened_unless_registered(path):
    opened = ResolveCitationSource(InvestigationSources(FakeReader(["a/report.pdf"]))).open(entry(path))
    assert not isinstance(opened, SourceDocument) and opened.status == SourceStatus.UNREGISTERED and opened.reason


def test_a_registered_but_unreadable_source_is_reported_not_hidden():
    reader = FakeReader(["a/report.pdf"], fail="Source file is unavailable; its citation remains visible.")
    opened = ResolveCitationSource(InvestigationSources(reader)).open(entry("a/report.pdf"))
    assert not isinstance(opened, SourceDocument) and opened.status == SourceStatus.UNAVAILABLE
    assert "unavailable" in (opened.reason or "")


def test_a_record_figure_without_its_citation_is_completed_but_never_trusted(investigations):
    inv, point = top_with_ranged_o2(investigations)
    value = point.o2_percent_min
    meta = Citation(kind=CitationKind.METADATA, investigation_id=inv.id, field="pillars")

    def draft(figure_value: float) -> Draft:
        return Draft(claims=(Claim(text=f"[{inv.id}] was tested at {figure_value:g}% oxygen.", citations=(meta,),
                                   figures=(Figure(source="record", investigation_id=inv.id, column="o2_percent",
                                                   value=figure_value, test_point_id=point.test_point_id),)),))

    good = answer(investigations, draft(value))
    assert good.status == AnswerStatus.APPROVED
    assert any(e.citation.test_point_id == point.test_point_id for e in good.traceability)
    assert answer(investigations, draft(value + 50)).status == AnswerStatus.INSUFFICIENT_EVIDENCE


def test_the_scenarios_own_oxygen_and_pressure_may_appear_in_the_text_but_other_digits_may_not(investigations):
    inv = RelevanceRanker().rank(investigations, LUNAR_BASE)[0].investigation
    cite = (Citation(kind=CitationKind.METADATA, investigation_id=inv.id, field="pillars"),)
    if inv.manual_metadata is None:
        pytest.skip("top investigation has no manual metadata")
    ok = Claim(text=f"[{inv.id}] is closest to {LUNAR_BASE.o2_percent:g}% oxygen at {LUNAR_BASE.pressure_psi:g} psi.",
               citations=cite)
    bad = Claim(text=f"[{inv.id}] burned at 77.7% oxygen.", citations=cite)
    assert answer(investigations, Draft(claims=(ok,))).status == AnswerStatus.APPROVED
    assert answer(investigations, Draft(claims=(bad,))).status == AnswerStatus.INSUFFICIENT_EVIDENCE


def test_the_isa_tab_objective_is_not_citable_and_missing_metadata_is_rejected_with_the_allowed_fields(investigations):
    inv = next(i for i in investigations if i.manual_metadata is not None)
    objective = Claim(text=f"[{inv.id}] has an objective.", citations=(
        Citation(kind=CitationKind.METADATA, investigation_id=inv.id, field="objective"),))
    (issue, *_) = RuleBasedValidator(NoCatalog()).validate(Draft(claims=(objective,)), _context(inv))
    assert issue.code.value == "malformed_citation" and "pillars" in issue.message
    bare = next((i for i in investigations if i.manual_metadata is None), None)
    if bare is not None:
        claim = Claim(text=f"[{bare.id}] has pillars.", citations=(
            Citation(kind=CitationKind.METADATA, investigation_id=bare.id, field="pillars"),))
        (issue, *_) = RuleBasedValidator(NoCatalog()).validate(Draft(claims=(claim,)), _context(bare))
        assert "Metadata fields you may cite" in issue.message


def _context(inv):
    from psi_fire.application.answer_types import ValidationContext

    ranked = next(r for r in RelevanceRanker().rank((inv,), LUNAR_BASE))
    return ValidationContext(LUNAR_BASE, (ranked,), ())


def _record_claim(inv, point, text: str) -> Claim:
    return Claim(text=text, citations=(Citation(kind=CitationKind.RECORD, investigation_id=inv.id,
                                                test_point_id=point.test_point_id),))


def test_numbers_the_system_itself_computed_need_no_figure_but_other_numbers_do(investigations):
    ranked = RelevanceRanker().rank(investigations, LUNAR_BASE)
    top = ranked[0]
    point = top.investigation.test_points[0]
    count = len(top.investigation.test_points)
    ok = _record_claim(top.investigation, point, f"[{top.investigation.id}] ranks {top.rank} and has {count} tests.")
    wrong = _record_claim(top.investigation, point, f"[{top.investigation.id}] has {count + 1000} tests.")
    assert answer(investigations, Draft(claims=(ok,))).status == AnswerStatus.APPROVED
    assert answer(investigations, Draft(claims=(wrong,))).status == AnswerStatus.INSUFFICIENT_EVIDENCE


def test_a_number_equal_to_a_cited_record_value_is_declared_automatically_and_still_checked(investigations):
    from psi_fire.application.answer_validation import record_values, unbacked_numbers
    from psi_fire.application.answering import with_declared_figures

    ranked = RelevanceRanker().rank(investigations, LUNAR_BASE)[:5]
    by_id = {r.investigation.id: r for r in ranked}
    scenario_numbers = [LUNAR_BASE.o2_percent, LUNAR_BASE.pressure_psi]
    for item in ranked:
        for point in item.investigation.test_points:
            for column, value, _ in record_values(point):
                claim = _record_claim(item.investigation, point, f"[{item.investigation.id}] shows {value:g}.")
                if unbacked_numbers(claim, by_id, scenario_numbers):
                    declared = with_declared_figures(Draft(claims=(claim,)), tuple(ranked), LUNAR_BASE).claims[0]
                    assert declared.figures and declared.figures[0].test_point_id == point.test_point_id
                    result = answer(investigations, Draft(claims=(claim,)))
                    assert result.status == AnswerStatus.APPROVED and result.figure_traces
                    bad = _record_claim(item.investigation, point, f"[{item.investigation.id}] shows 77.7.")
                    assert answer(investigations, Draft(claims=(bad,))).status == AnswerStatus.INSUFFICIENT_EVIDENCE
                    return
    pytest.skip("no record value outside the system facts in the shortlist")
