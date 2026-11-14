"""English homepage adapted from the user-supplied React concept."""

import streamlit as st

from psi_fire.application.explore import ExplorationQuery, Snapshot
from psi_fire.application.home import GetHomeSummary
from psi_fire.interface.home_style import apply_home_style, hero_image_uri
from psi_fire.interface.research_scene import research_scene

HOME_THEMES = {"1 · Flame behavior": "flame", "2 · Earth applications": "earth",
               "3 · Exploration habitats": "habitats", "4 · Detection and diagnostics": "detection"}


def navigate(page: str, ids: tuple[str, ...] | None = None) -> None:
    st.session_state["workspace_navigation"] = page
    if ids is not None:
        st.session_state["applied_query"] = ExplorationQuery(ids=ids)
        st.session_state["filter_generation"] = st.session_state.get("filter_generation", 0) + 1
        st.session_state.pop("selected_investigation", None)
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
    apply_home_style(image_uri)
    with st.container(key="home_workspace"):
        home_content(snapshot, image_uri)


def home_content(snapshot: Snapshot, image_uri: str) -> None:
    st.session_state.setdefault("home_theme", next(iter(HOME_THEMES)))
    summary = GetHomeSummary(snapshot)(HOME_THEMES.get(st.session_state["home_theme"], "flame"))
    with st.container(key="home_hero"):
        st.caption("// Intelligence for fire safety")
        st.title("ISS combustion data, :orange[Clearer evidence.]")
        st.write("Explore the interactive chamber: select a point to discover combustion research "
                 "for spacecraft, stations, habitats and rovers.")

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
              "earth": "Documented applications on Earth",
              "habitats": "Research for exploration habitats",
              "detection": "Detection, diagnostics and measurement"}
    descriptions = {
        "flame": "Inspect droplet-combustion records, reported conditions and source documents. "
                 "Compare available quantities without turning sparse coverage into a predictive model.",
        "earth": "Find Earth-application claims that have actually been curated. "
                 "Each application retains its evidence and review status; shared hardware alone does not establish a benefit.",
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
        st.button("Browse investigations", on_click=navigate, args=("Investigations",), key="home_browse")
    with st.container(key="home_metrics"):
        columns = st.columns(3)
        columns[0].metric("Curated investigations", summary.investigations)
        columns[1].metric("Reported records", f"{summary.records:,}")
        columns[2].metric("Human-reviewed metadata", f"{summary.reviewed_metadata} / {summary.investigations}")

    st.subheader("From records to traceable decisions")
    columns = st.columns(3)
    for index, (column, title, text) in enumerate(zip(columns, ("Explore conditions", "Inspect the evidence", "Explain relevance"), (
        "Filter reported oxygen, pressure, fuel and flow. Keep experimental tests, daily summaries and planned matrices distinct.",
        "Open raw values, transformations, exact quotes and source locators. Draft, inferred and unreported claims remain visible.",
        "Planned: a deterministic ranking with a visible criterion breakdown and validated citations. No relevance scores are computed yet.",
    ), strict=True), start=1):
        with column, st.container(border=True, key=f"home_step_{index}"):
            st.caption(f"0{index}")
            st.markdown(f"**{title}**")
            st.write(text)
    st.caption("Research scope: combustion and fire safety in crewed environments. Rockets and propellants are outside scope. "
               "Record count is not scientific relevance; this explorer does not certify habitat safety.")
