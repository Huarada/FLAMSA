"""Narrator that needs no LLM: states the computed ranking with cited, checkable numbers.

It is the default when no model is configured, and it always passes the validator because every figure is
copied from the breakdown or from the cited test point.
"""

from psi_fire.application.answer_types import NarrationRequest
from psi_fire.domain.answering import Citation, CitationKind, Claim, Draft, Figure
from psi_fire.domain.ranking import RankedInvestigation

TEMPLATE_CLAIMS = 3  # investigations described in the template answer


class TemplateNarrator:
    def draft(self, request: NarrationRequest) -> Draft:
        return Draft(claims=tuple(self._claim(item) for item in request.shortlist[:TEMPLATE_CLAIMS]))

    def _claim(self, item: RankedInvestigation) -> Claim:
        inv = item.investigation
        score = round(item.score, 2)
        text = f"[{inv.id}] ranks {item.rank} with relevance score {score:.2f}."
        figures = [Figure(source="breakdown", investigation_id=inv.id, column="rank", value=float(item.rank)),
                   Figure(source="breakdown", investigation_id=inv.id, column="score", value=score)]
        evidence = next((s.evidence for s in item.breakdown.scores
                         if s.criterion == "oxygen_proximity" and s.evidence), ())
        point = next((tp for tp in inv.test_points if evidence and tp.test_point_id == evidence[0]),
                     inv.test_points[0])
        if evidence and point.o2_percent_min is not None and point.pressure_psi_min is not None:
            text += (f" Its closest ambient test reports {point.o2_percent_min:g}% oxygen "
                     f"at {point.pressure_psi_min:g} psi.")
            figures += [Figure(source="record", investigation_id=inv.id, column="o2_percent", unit="percent",
                               value=point.o2_percent_min, test_point_id=point.test_point_id),
                        Figure(source="record", investigation_id=inv.id, column="pressure_psi", unit="psi",
                               value=point.pressure_psi_min, test_point_id=point.test_point_id)]
        citation = Citation(kind=CitationKind.RECORD, investigation_id=inv.id, test_point_id=point.test_point_id)
        return Claim(text=text, citations=(citation,), figures=tuple(figures))
