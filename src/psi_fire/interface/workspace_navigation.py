"""Native workspace navigation and purpose-specific help."""

import streamlit as st


def open_workspace(destination: str) -> None:
    st.session_state["workspace_navigation"] = destination


def workspace_navigation(current: str) -> None:
    with st.container(horizontal=True, key="header_navigation"):
        st.button("Home", key="nav_home", type="tertiary", on_click=open_workspace, args=("Home",),
                  help="The interactive chamber scene, with a way into each research theme.")
        st.button("Dashboard", key="nav_dashboard", icon=":material/dashboard:", on_click=open_workspace,
                  args=("Dashboard",), help="Filter the investigations and plot any two reported quantities against "
                  "each other. Also shows record counts and the oxygen, pressure and flow ranges that were tested.")
        st.button("Fire behavior", key="nav_fire_behavior", type="primary", icon=":material/local_fire_department:",
                  on_click=open_workspace, args=("Fire behavior",),
                  help="Three studies read against the physics: burning rate versus oxygen (FLEX), oxygen and CO2 "
                  "changes during a burn (BASS-II), and ground versus microgravity outcomes (SAFFIRE-II). "
                  "Fitted slopes come with their intervals and the source rows.")
        st.button("Investigations", key="nav_investigations", type="tertiary", on_click=open_workspace,
                  args=("Investigations",), help="The objective, hardware, sensors and every test record of one "
                  "investigation, with its review status, citations and archived source downloads.")
    st.caption(f"Current view: {current}")
