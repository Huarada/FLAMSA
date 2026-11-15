"""English homepage adapted from the user-supplied React concept."""

import streamlit as st

from psi_fire.application.explore import ExplorationQuery, Snapshot
from psi_fire.application.home import GetHomeSummary
from psi_fire.interface.home_style import hero_image_uri
from psi_fire.interface.research_scene import research_scene

HOME_THEMES = {"1 · Flame behavior": "flame", "2 · Earth applications": "earth",
               "3 · Exploration habitats": "habitats", "4 · Detection and diagnostics": "detection"}


def navigate(page: str, ids: tuple[str, ...] | None = None) -> None:
    st.session_state["workspace_navigation"] = page
    if ids is not None:
        st.session_state["applied_query"] = ExplorationQuery(ids=ids)
        st.session_state["filter_generation"] = st.session_state.get("filter_generation", 0) + 1
        st.session_state.pop("selected_investigation", None)
        if page == "Investigations" and ids:
            st.session_state["selected_investigation"] = ids[0]
        st.session_state.pop("filter_error", None)


def select_scene_topic() -> None:
    selected = st.session_state["home_scene_control"].selected
    for label, topic in HOME_THEMES.items():
        if topic == selected:
            st.session_state["home_theme"] = label
            break


def keep_selected_topic() -> None:
    if st.session_state.get("home_theme") not in HOME_THEMES:
        st.session_state["home_theme"] = next(iter(HOME_THEMES))


def home(snapshot: Snapshot) -> None:
    image_uri = hero_image_uri()
    with st.container(key="home_workspace"):
        home_content(snapshot, image_uri)


def home_content(snapshot: Snapshot, image_uri: str) -> None:
    st.session_state.setdefault("home_theme", next(iter(HOME_THEMES)))
    summary = GetHomeSummary(snapshot)(HOME_THEMES.get(st.session_state["home_theme"], "flame"))
    with st.container(key="home_hero"):
        st.caption("// Intelligence for fire safety")
        st.title("FLAMSA", anchor=False)
        st.subheader("NASA PSI combustion data. Clearer evidence.", anchor=False)
        st.write("Explore NASA PSI combustion research for fire prevention, detection and suppression in crewed "
                 "environments. Compare experimental conditions, identify relevant investigations, and trace "
                 "findings to the original data and sources.")
        st.write("Use Research copilot to rank investigations for selected oxygen and pressure conditions, "
                 "with cited explanations and a transparent score breakdown.")
        st.caption("Select a point in the conceptual chamber or use the research themes below.")

    theme = HOME_THEMES.get(st.session_state["home_theme"], "flame")
    with st.container(border=True, key="home_scene"):
        research_scene(image_uri, theme, select_scene_topic)
    st.toggle("Animate scene", value=True, key="home_motion")
    st.caption("Concept illustration supplied for FLAMSA. Instrument readings and the lunar setting "
               "are part of the artwork, not experimental measurements.")
    selected = st.pills("Explore a research theme", list(HOME_THEMES), default=None, key="home_theme",
                        on_change=keep_selected_topic, label_visibility="collapsed")
    theme = HOME_THEMES.get(selected, "flame")
    summary = GetHomeSummary(snapshot)(theme)
    titles = {"flame": "Flame behavior and experimental conditions",
              "earth": "Curated connections to Earth applications",
              "habitats": "Research for exploration habitats",
              "detection": "Detection, diagnostics and measurement"}
    descriptions = {
        "flame": "Inspect droplet burning and extinction research, reported conditions and source documents. "
                 "Open Fire behavior for the FLEX burning-rate analysis, BASS-II gas changes and SAFFIRE-II "
                 "ground-versus-flight comparison. These analyses describe tested conditions, not a universal predictive model.",
        "earth": "Explore curated Earth-application claims and their supporting sources. "
                 "Check whether each claim is inferred and whether its metadata has been human-reviewed; "
                 "a research connection alone does not establish a proven technology benefit.",
        "habitats": "Explore material and atmosphere studies as starting points for habitat research. "
                    "Lunar or Martian applicability requires explicit assumptions: this dataset does not contain direct partial-gravity measurements.",
        "detection": "Inspect smoke-generation studies and combustion measurement context. "
                     "Read each sensor claim and source before inferring detector performance or suppression effectiveness.",
    }
    with st.container(border=True, key="home_context"):
        st.caption("RESEARCH LENS / " + (selected or next(iter(HOME_THEMES))))
        st.subheader(titles[theme])
        st.write(descriptions[theme])
        st.markdown("**Related investigations in this archive**")
        if summary.related_ids:
            with st.container(horizontal=True):
                for investigation_id in summary.related_ids:
                    st.badge(investigation_id, color="blue")
            st.caption("Topic-based starting points. Review the sources and claim status in the investigation detail.")
            st.button("Open related research", on_click=navigate, args=("Investigations", summary.related_ids),
                      key=f"home_related_{theme}", icon=":material/arrow_forward:", type="primary", width="stretch")
        else:
            st.info("No application claims are mapped for this topic in the current snapshot.")

    with st.container(horizontal=True):
        st.button("Explore the dashboard", type="primary", icon=":material/arrow_forward:",
                  on_click=navigate, args=("Dashboard",), key="home_dashboard")
        st.button("Open Fire behavior", icon=":material/local_fire_department:",
                  on_click=navigate, args=("Fire behavior",), key="home_behavior")
        st.button("Browse investigations", on_click=navigate, args=("Investigations",), key="home_browse")
    with st.container(key="home_metrics"):
        columns = st.columns(2)
        columns[0].metric("Curated investigations", summary.investigations)
        columns[1].metric("Reported records", f"{summary.records:,}")

    st.subheader("From reported measurements to cited explanations")
    columns = st.columns(3)
    for index, (column, title, text) in enumerate(zip(columns, ("Explore conditions", "Inspect the evidence", "Explain relevance"), (
        ("Filter reported oxygen, pressure, fuel and flow. Download matching records as CSV for your own analysis. "
         "Individual tests, daily summaries and planned matrices remain distinct."),
        ("In Investigations, inspect raw values, units, transformations and source locators. "
         "Citations & source downloads keeps archived documents accessible. Draft, inferred and unreported claims remain visible."),
        ("Use the Dashboard's Research copilot to rank the full archive for a habitat scenario. "
         "The application computes the scores; a connected AI model or offline template explains them. "
         "Review the criterion breakdown, citations and limitations; insufficient evidence can prevent an explanation."),
    ), strict=True), start=1):
        with column, st.container(border=True, key=f"home_step_{index}"):
            st.caption(f"0{index}")
            st.markdown(f"**{title}**")
            st.write(text)
    st.caption("Research scope: combustion and fire safety in crewed environments. Rockets and propellants are outside scope. "
               "The PSI archive used here has no direct lunar or Martian partial-gravity measurements. "
               "Record count is not scientific relevance, and a scenario ranking does not certify habitat safety.")
