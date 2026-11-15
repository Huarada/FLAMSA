"""Deterministic validation of a draft against the retrieved evidence (SPEC-003 section 3.5). No LLM."""

from math import isclose

from psi_fire.application.answer_types import ValidationContext
from psi_fire.application.ports import SolutionCatalog
from psi_fire.domain.answering import (
    METADATA_FIELDS,
    NUMBER_ABSOLUTE_TOLERANCE,
    NUMBER_RELATIVE_TOLERANCE,
    SCORE_ABSOLUTE_TOLERANCE,
    Citation,
    CitationKind,
    Claim,
    Draft,
    Figure,
    IssueCode,
    ValidationIssue,
    numbers_in,
    plausibility_issues,
)
from psi_fire.domain.model import TestPoint
from psi_fire.domain.ranking import RankedInvestigation

MIN_QUOTE_CHARS = 20  # shorter strings match too many places to identify a sentence


def _flat(text: str) -> str:
    return " ".join(text.replace("­", "").split())


def _close(a: float, b: float) -> bool:
    return isclose(a, b, rel_tol=NUMBER_RELATIVE_TOLERANCE, abs_tol=NUMBER_ABSOLUTE_TOLERANCE)


def _issue(code: IssueCode, message: str, index: int) -> ValidationIssue:
    return ValidationIssue(code=code, message=message, claim_index=index)


def record_range(point: TestPoint, column: str) -> tuple[float, float] | None:
    if hasattr(point, f"{column}_min"):
        low, high = getattr(point, f"{column}_min"), getattr(point, f"{column}_max")
        return None if low is None else (low, high)
    value = point.value(column)
    return (float(value), float(value)) if isinstance(value, int | float) else None


class RuleBasedValidator:
    def __init__(self, catalog: SolutionCatalog) -> None:
        self._catalog = catalog

    def validate(self, draft: Draft, context: ValidationContext) -> tuple[ValidationIssue, ...]:
        if not draft.claims:
            return (ValidationIssue(code=IssueCode.EMPTY_DRAFT, message="The draft contains no claims."),)
        ranked = {r.investigation.id: r for r in context.shortlist}
        issues: list[ValidationIssue] = []
        for index, claim in enumerate(draft.claims):
            issues.extend(self._claim_issues(claim, index, ranked, context))
        return tuple(issues)

    def _claim_issues(self, claim: Claim, index: int, ranked: dict[str, RankedInvestigation],
                      context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not claim.citations:
            issues.append(_issue(IssueCode.MISSING_CITATION, "Every claim needs at least one citation.", index))
        for citation in claim.citations:
            issues.extend(self._citation_issues(citation, index, ranked, context))
        for figure in claim.figures:
            issues.extend(self._figure_issues(figure, claim, index, ranked))
        declared = [f.value for f in claim.figures]
        for number in numbers_in(claim.text):
            if not any(_close(number, value) for value in declared):
                issues.append(_issue(IssueCode.UNDECLARED_NUMBER,
                                     f"The number {number:g} in the text is not declared as a figure.", index))
        cited = {c.investigation_id for c in claim.citations}
        offered = {s.technology.casefold() for inv_id in cited for s in self._catalog.lookup(inv_id)}
        for technology in claim.technologies:
            if technology.casefold() not in offered:
                issues.append(_issue(IssueCode.UNBACKED_TECHNOLOGY,
                                     f"'{technology}' is not a catalog entry for the cited investigations.", index))
        issues.extend(plausibility_issues(claim, index))
        return issues

    def _citation_issues(self, citation: Citation, index: int, ranked: dict[str, RankedInvestigation],
                         context: ValidationContext) -> list[ValidationIssue]:
        target = ranked.get(citation.investigation_id)
        if target is None:
            return [_issue(IssueCode.UNKNOWN_CITATION,
                           f"{citation.investigation_id} is not in the retrieved shortlist.", index)]
        inv = target.investigation
        if citation.kind == CitationKind.RECORD:
            if citation.test_point_id is None:
                return [_issue(IssueCode.MALFORMED_CITATION, "A record citation needs test_point_id.", index)]
            if not any(tp.test_point_id == citation.test_point_id for tp in inv.test_points):
                return [_issue(IssueCode.UNKNOWN_CITATION,
                               f"{inv.id} has no test point {citation.test_point_id}.", index)]
        elif citation.kind == CitationKind.METADATA:
            if citation.field not in METADATA_FIELDS:
                return [_issue(IssueCode.MALFORMED_CITATION,
                               f"Metadata field must be one of {METADATA_FIELDS}.", index)]
            if citation.field != "objective" and inv.manual_metadata is None:
                return [_issue(IssueCode.UNKNOWN_CITATION, f"{inv.id} has no curated metadata.", index)]
            if citation.field == "objective" and "objective" not in inv.study_metadata:
                return [_issue(IssueCode.UNKNOWN_CITATION, f"{inv.id} reports no objective.", index)]
        else:
            return self._passage_issues(citation, index, context)
        return []

    def _passage_issues(self, citation: Citation, index: int, context: ValidationContext) -> list[ValidationIssue]:
        quote = _flat(citation.quote or "")
        if citation.source_file is None or citation.locator is None or len(quote) < MIN_QUOTE_CHARS:
            return [_issue(IssueCode.MALFORMED_CITATION,
                           f"A passage citation needs source_file, locator and a quote of at least "
                           f"{MIN_QUOTE_CHARS} characters.", index)]
        pages = [p for p in context.passages if (p.investigation_id, p.source_file, p.locator) ==
                 (citation.investigation_id, citation.source_file, citation.locator)]
        if not pages:
            return [_issue(IssueCode.UNKNOWN_CITATION, "The cited passage was not retrieved in this attempt.", index)]
        if not any(quote in _flat(p.text) for p in pages):
            return [_issue(IssueCode.QUOTE_MISMATCH, "The quote does not appear in the cited passage.", index)]
        return []

    def _figure_issues(self, figure: Figure, claim: Claim, index: int,
                       ranked: dict[str, RankedInvestigation]) -> list[ValidationIssue]:
        target = ranked.get(figure.investigation_id)
        if target is None:
            return [_issue(IssueCode.UNKNOWN_CITATION,
                           f"Figure refers to {figure.investigation_id}, which is not in the shortlist.", index)]
        if figure.source == "breakdown":
            return self._breakdown_issues(figure, target, index)
        cited = {c.test_point_id for c in claim.citations if c.kind == CitationKind.RECORD}
        point = next((tp for tp in target.investigation.test_points if tp.test_point_id == figure.test_point_id), None)
        if point is None or point.test_point_id not in cited:
            return [_issue(IssueCode.UNKNOWN_CITATION,
                           "A record figure must name a test point that the claim cites.", index)]
        bounds = record_range(point, figure.column)
        if bounds is None:
            return [_issue(IssueCode.NUMBER_MISMATCH,
                           f"{point.investigation_id}/{point.test_point_id} does not report {figure.column}.", index)]
        low, high = bounds
        if not (low <= figure.value <= high or _close(figure.value, low) or _close(figure.value, high)):
            return [_issue(IssueCode.NUMBER_MISMATCH,
                           f"{figure.column} {figure.value:g} differs from the record ({low:g}-{high:g}).", index)]
        return []

    def _breakdown_issues(self, figure: Figure, target: RankedInvestigation, index: int) -> list[ValidationIssue]:
        if figure.column == "rank":
            actual = [float(target.rank)]
        elif figure.column == "score":
            actual = [target.score]
        else:
            matches = [s for s in target.breakdown.scores if s.criterion == figure.column]
            actual = [v for s in matches for v in (s.value, s.contribution)]
        if not any(abs(figure.value - value) <= SCORE_ABSOLUTE_TOLERANCE + 1e-9 for value in actual):
            return [_issue(IssueCode.NUMBER_MISMATCH,
                           f"{figure.column}={figure.value:g} does not match the computed breakdown.", index)]
        return []
