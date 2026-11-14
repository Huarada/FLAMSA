"""Business-intelligence chart workspace and explicit future-assistant surface."""

from dataclasses import asdict

import streamlit as st

from psi_fire.application.explore import ExplorationQuery, Match


def assistant_panel(revision: str, query: ExplorationQuery, matches: tuple[Match, ...],
                    chart_context: dict[str, object]) -> None:
    with st.container(border=True, key="copilot_panel"):
        st.markdown("### Research copilot")
        st.badge("Not connected", color="gray")
        st.write("A workspace for asking questions about these charts and proposing dashboard changes.")
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
