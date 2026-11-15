"""Native workspace navigation and purpose-specific help."""

import streamlit as st

from psi_fire.interface.research_guide import track_workspace


def open_workspace(destination: str) -> None:
    st.session_state["workspace_navigation"] = destination


def workspace_navigation(current: str) -> None:
    track_workspace(current)
    with st.container(horizontal=True, gap="medium", key="header_navigation"):
        st.button("Home", key="nav_home", type="tertiary", width="stretch", on_click=open_workspace, args=("Home",),
                  help="The interactive chamber scene, with a way into each research theme.")
        st.button("Dashboard", key="nav_dashboard", icon=":material/dashboard:", width="stretch", on_click=open_workspace,
                  args=("Dashboard",), help="Start the 3-step guide: choose conditions on the coverage map, ask "
                  "Research copilot, then inspect the cited NASA sources. Filter and compare reported measurements.")
        st.button("Fire behavior", key="nav_fire_behavior", type="primary", width="stretch", icon=":material/local_fire_department:",
                  on_click=open_workspace, args=("Fire behavior",),
                  help="Three studies read against the physics: burning rate versus oxygen (FLEX), oxygen and CO2 "
                  "changes during a burn (BASS-II), and ground versus microgravity outcomes (SAFFIRE-II). "
                  "Fitted slopes come with their intervals and the source rows.")
        st.button("Investigations", key="nav_investigations", icon=":material/manage_search:", width="stretch", on_click=open_workspace,
                  args=("Investigations",), help="The objective, hardware, sensors and every test record of one "
                  "investigation, with its review status, citations and archived source downloads.")
    st.caption(f"Current view: {current}")
