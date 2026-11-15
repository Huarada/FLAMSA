"""Deterministic validation of a draft against the retrieved evidence (SPEC-003 section 3.5). No LLM."""

import re
import unicodedata
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
from psi_fire.domain.model import Investigation, TestPoint
from psi_fire.domain.ranking import RankedInvestigation

MIN_QUOTE_CHARS = 20  # shorter strings match too many places to identify a sentence
MIN_SEGMENT_CHARS = 12  # each piece of an ellipsis-joined quote must still identify a place in the passage
_ELLIPSIS = re.compile(r"\s*\.{3}\s*")


def _squeeze(text: str) -> str:
    """Letters and digits only: spacing and punctuation (PDF line breaks, quote marks) are not evidence."""
    return re.sub(r"[\W_]+", "", text)


def quote_in(quote: str, passage: str) -> bool:
    """True if the quote is one span of the passage, or several spans joined by "..." that appear in that order.
    Both arguments are already normalised. Words and numbers must match exactly; only spacing and punctuation are
    ignored. Invented text between the pieces cannot hide inside an ellipsis: every piece must be a real span of
    the same passage."""
    pieces = [s for s in (_squeeze(p) for p in _ELLIPSIS.split(quote)) if s]
    if len(pieces) > 1 and any(len(p) < MIN_SEGMENT_CHARS for p in pieces):
        return False
    squeezed = _squeeze(passage)
    start = 0
    for piece in pieces:
        found = squeezed.find(piece, start)
        if found < 0:
            return False
        start = found + len(piece)
    return bool(pieces)


def available_metadata_fields(inv: Investigation) -> tuple[str, ...]:
    """The metadata fields a claim may cite for this investigation (single source for validator and prompt)."""
    return METADATA_FIELDS if inv.manual_metadata is not None else ()


def _flat(text: str) -> str:
    """Compare quotes the way a reader would: PDF ligatures (fi), soft hyphens, replacement characters and
    letter case are not differences. Words and numbers must still match exactly."""
    cleaned = unicodedata.normalize("NFKC", text).replace("­", "").replace("�", "")
    return " ".join(cleaned.casefold().split())


def _close(a: float, b: float) -> bool:
    return isclose(a, b, rel_tol=NUMBER_RELATIVE_TOLERANCE, abs_tol=NUMBER_ABSOLUTE_TOLERANCE)


RANGED_UNITS = {"o2_percent": "percent", "pressure_psi": "psi", "flow_speed_cm_s": "cm/s"}


def record_values(point: TestPoint) -> list[tuple[str, float, str | None]]:
    """(column, value, unit) for every number a record states: range ends and numeric extra columns."""
    values: list[tuple[str, float, str | None]] = []
    for column, unit in RANGED_UNITS.items():
        for end in ("min", "max"):
            value = getattr(point, f"{column}_{end}")
            if value is not None:
                values.append((column, float(value), unit))
    values += [(c, float(v), None) for c, v in point.extras.items() if isinstance(v, int | float) and not isinstance(v, bool)]
    return values


def _tested_range(points: tuple[TestPoint, ...], column: str) -> list[float]:
    ends = [getattr(p, f"{column}_{end}") for p in points for end in ("min", "max")]
    return [float(v) for v in ends if v is not None]


def system_facts(inv: RankedInvestigation) -> tuple[list[float], list[float]]:
    """Numbers the application itself computed or counted for this investigation: (counts/ranges, scores).
    A claim may state them without declaring a figure; any other digit still needs a source."""
    points = inv.investigation.test_points
    exact = [float(inv.rank), float(len(points)),
             float(sum(p.provenance_status.value == "verified" for p in points))]
    for column in RANGED_UNITS:
        values = _tested_range(points, column)
        exact += [min(values), max(values)] if values else []
    scores = [inv.score] + [v for s in inv.breakdown.scores for v in (s.value, s.weight, s.contribution)]
    return exact, scores


def unbacked_numbers(claim: Claim, ranked: dict[str, RankedInvestigation], input_numbers: list[float]) -> list[float]:
    """Numbers in the text that nothing backs. Backed: a declared figure, a number the user typed (scenario or
    question), a digit group inside a cited passage quote (the quote itself is checked against the document),
    or a system fact of an investigation that the claim cites, declares a figure for, or names in its text."""
    quote_numbers = [n for c in claim.citations if c.kind == CitationKind.PASSAGE and c.quote for n in numbers_in(c.quote)]
    exact = [f.value for f in claim.figures] + input_numbers + quote_numbers
    scores: list[float] = []
    named = {inv_id for inv_id in ranked if inv_id in claim.text}
    for inv_id in {c.investigation_id for c in claim.citations} | {f.investigation_id for f in claim.figures} | named:
        if inv_id in ranked:
            more_exact, more_scores = system_facts(ranked[inv_id])
            exact += more_exact
            scores += more_scores
    return [n for n in numbers_in(claim.text)
            if not any(_close(n, v) for v in exact) and not any(abs(n - v) <= SCORE_ABSOLUTE_TOLERANCE + 1e-9 for v in scores)]


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
        # the scenario's own oxygen and pressure are inputs the user typed, not claims about evidence
        input_numbers = [context.scenario.o2_percent, context.scenario.pressure_psi, *numbers_in(context.question)]
        for number in unbacked_numbers(claim, ranked, input_numbers):
            issues.append(_issue(IssueCode.UNDECLARED_NUMBER,
                                 f"The number {number:g} in the text is not declared as a figure: declare it in "
                                 "figures with its source, or rewrite the sentence without digits.", index))
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
                               f"Metadata field must be one of {METADATA_FIELDS}. To cite a score, rank or criterion "
                               "use kind 'breakdown' instead.", index)]
            if citation.field not in available_metadata_fields(inv):
                allowed = ", ".join(available_metadata_fields(inv)) or "none (cite a record instead)"
                return [_issue(IssueCode.UNKNOWN_CITATION,
                               f"{inv.id} has no '{citation.field}' metadata. Metadata fields you may cite for "
                               f"{inv.id}: {allowed}.", index)]
        elif citation.kind == CitationKind.BREAKDOWN:
            allowed = ("score", "rank", *(s.criterion for s in target.breakdown.scores))
            if citation.field not in allowed:
                return [_issue(IssueCode.UNKNOWN_CITATION,
                               f"{inv.id} ranking has no '{citation.field}'. Breakdown fields you may cite: "
                               f"{', '.join(allowed)}.", index)]
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
        if not any(quote_in(quote, _flat(p.text)) for p in pages):
            return [_issue(IssueCode.QUOTE_MISMATCH,
                           f"The quote {quote[:70]!r} does not appear verbatim in the cited passage "
                           f"({citation.source_file} {citation.locator}); copy one contiguous span exactly (or 'span ... span' "
                           "with each piece copied exactly, in page order).", index)]
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
        if figure.test_point_id is None or point is None:
            return [_issue(IssueCode.UNKNOWN_CITATION,
                           f"Record figure {figure.column} needs the test_point_id of an existing "
                           f"{figure.investigation_id} record.", index)]
        if point.test_point_id not in cited:
            return [_issue(IssueCode.UNKNOWN_CITATION,
                           f"Record figure {figure.column} names test point {point.test_point_id}, but the claim has "
                           "no record citation for it: add that citation or drop the figure.", index)]
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
