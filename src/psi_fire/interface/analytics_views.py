"""Business-intelligence chart workspace and explicit future-assistant surface."""

from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from psi_fire.application.evidence import InvestigationSources
from psi_fire.application.explore import ExplorationQuery, Match
from psi_fire.application.quota import DailyQuota
from psi_fire.application.source_access import ResolveCitationSource
from psi_fire.domain.model import Investigation
from psi_fire.interface.copilot_evidence import EvidenceContext
from psi_fire.interface.copilot_panel import copilot
from psi_fire.interface.deferred_pipeline import PipelineHandle


def assistant_panel(revision: str, query: ExplorationQuery, matches: tuple[Match, ...],
                    chart_context: dict[str, object], pipeline: PipelineHandle | None = None,
                    investigations: tuple[Investigation, ...] = (),
                    sources: InvestigationSources | None = None, quota: DailyQuota | None = None) -> None:
    with st.container(border=True, key="copilot_panel"):
        st.subheader("Research copilot", anchor="research-copilot")
        if pipeline is not None:
            visible = frozenset(m.investigation.id for m in matches)
            copilot(pipeline, investigations,
                    EvidenceContext(ResolveCitationSource(sources) if sources else None, visible), quota)
            return
        st.badge("Not connected", color="gray")
        st.write("A workspace for asking questions about these charts and proposing dashboard changes.")
        st.caption("The answering pipeline was not provided to this view.")
        st.text_area("Ask about this dashboard", placeholder="Compare burn duration at different oxygen levels…",
                     disabled=True, height=100)
        st.button("Ask copilot", disabled=True, icon=":material/auto_awesome:", width="stretch")
        st.caption("No AI model or action executor is connected. Questions are not sent, and this panel does not "
                   "generate answers or change filters.")
        with st.expander("Planned dashboard actions"):
            st.write("• Propose investigation and condition filters\n"
                     "• Suggest chart quantities and comparison series\n"
                     "• Explain observed patterns with cited records\n"
                     "• Open the evidence supporting a claim")
            st.caption("Future changes will pass through validated application commands. "
                       "The model will not edit scientific data or calculate ranking scores.")
        with st.expander("Context available for future integration"):
            st.json({"dataset_revision": revision, "applied_filters": asdict(query),
                     "matching_investigations": [m.investigation.id for m in matches],
                     "comparison_chart": chart_context}, expanded=False)
