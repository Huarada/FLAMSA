"""Streamlit composition root for the research workspace."""

import sys
from dataclasses import asdict
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from psi_fire.application.evidence import InvestigationSources
from psi_fire.application.explore import (
    CheckDatasetFreshness,
    DatasetError,
    ExplorationQuery,
    ExploreInvestigations,
    InvalidExplorationQuery,
    LoadExplorer,
    Match,
    Snapshot,
)
from psi_fire.domain.model import Investigation
from psi_fire.infrastructure.explorer import FileSnapshotProvider, RegisteredSources
from psi_fire.interface.analytics_views import assistant_panel
from psi_fire.interface.behavior_introduction import behavior_introduction
from psi_fire.interface.dashboard_cache import RecordScope, record_scope
from psi_fire.interface.deferred_pipeline import DeferredPipeline
from psi_fire.interface.explorer_views import applied_filter_summary, catalog, detail, filters
from psi_fire.interface.home_style import apply_home_style, hero_image_uri
from psi_fire.interface.home_view import home
from psi_fire.interface.reference_dashboard import chart_grid, filtered_records_csv, metrics
from psi_fire.interface.workspace_navigation import workspace_navigation
from psi_fire.interface.workspace_style import apply_style

st.set_page_config(page_title="FLAMSA / Research workspace", page_icon=":material/local_fire_department:", layout="wide")
apply_style()

@st.cache_data(max_entries=2, show_spinner="Validating curated investigations...")
def load_snapshot(root: str, refresh: int) -> tuple[str, tuple[str, ...]]:
    snapshot = LoadExplorer(FileSnapshotProvider(Path(root)))()
    return snapshot.revision, tuple(inv.model_dump_json() for inv in snapshot.investigations)

@st.cache_resource(show_spinner=False)
def answering_pipeline(root: str):
    from psi_fire.infrastructure.answering_factory import build_answering_pipeline

    return build_answering_pipeline(Path(root))


@st.cache_data(max_entries=8, show_spinner=False)
def export_records(revision: str, scope: RecordScope, _matches: tuple[Match, ...]) -> str:
    return filtered_records_csv(_matches)

WORKSPACE_PAGES = ("Home", "Dashboard", "Fire behavior", "Investigations", "Evidence")  # Evidence: legacy link
root = Path(__file__).resolve().parents[3]
load_dotenv(root / ".env")  # keys and PSI_LLM_MODEL; real environment variables take precedence
if "applied_query" not in st.session_state:
    st.session_state["applied_query"] = ExplorationQuery()
if "refresh" not in st.session_state:
    st.session_state["refresh"] = 0
if "workspace_navigation" not in st.session_state:  # a reload or reconnect keeps the page through the URL
    requested = st.query_params.get("page", "Home")
    st.session_state["workspace_navigation"] = requested if requested in WORKSPACE_PAGES else "Home"
legacy_evidence = st.session_state["workspace_navigation"] == "Evidence"
if legacy_evidence:
    st.session_state["workspace_navigation"] = "Investigations"

home_style_slot = st.empty()
if st.session_state["workspace_navigation"] == "Home":
    with home_style_slot.container():
        apply_home_style(hero_image_uri())
else:
    home_style_slot.empty()

with st.container(key="topbar"):
    brand, navigation, controls = st.columns([1.1, 3.9, 1], vertical_alignment="center")
    brand.image(str(Path(__file__).parent / "assets/flamsa.svg"), width=165)
    brand.caption("NASA PSI / Research workspace")
    page = st.session_state["workspace_navigation"]
    st.query_params["page"] = page
    with navigation:
        workspace_navigation(page)
    with controls.popover("Dataset controls", icon=":material/database:", width="stretch"):
        st.caption("Reload only after curation is complete. Browsing uses an in-memory snapshot.")
        st.caption("Charts consume curated CSV + JSON. Excel/source and manual-metadata edits must be curated first.")
        dataset_status = st.empty()
        ready = st.checkbox("Curation is complete and idle", key="curation_idle")
        if st.button("Reload dataset", disabled=not ready, icon=":material/refresh:"):
            st.session_state["refresh"] += 1
            st.session_state["reload_pending"] = True
            st.rerun()

try:
    revision, serialized = load_snapshot(str(root), st.session_state["refresh"])
    previous = st.session_state.get("last_snapshot")
    snapshot = (previous if previous is not None and previous.revision == revision
                else Snapshot(revision, tuple(Investigation.model_validate_json(value) for value in serialized)))
    st.session_state["last_snapshot"] = snapshot
    if st.session_state.pop("reload_pending", False):
        query, removed = ExploreInvestigations(snapshot).reconcile(st.session_state["applied_query"])
        st.session_state["applied_query"] = query
        st.session_state["filter_generation"] = st.session_state.get("filter_generation", 0) + 1
        st.session_state.pop("filter_error", None)
        if removed:
            st.warning("Dataset reloaded. Removed unavailable selections: " + "; ".join(removed)
                       + ". Remaining filters were preserved; review the resulting scope.")
        else:
            st.info("Dataset reloaded. Applied filters were preserved.")
except DatasetError as error:
    st.session_state.pop("reload_pending", None)
    st.error(str(error))
    if "last_snapshot" not in st.session_state:
        st.stop()
    snapshot = st.session_state["last_snapshot"]
    st.warning("Showing the previous snapshot. Reload failed; these results are stale.")

dataset_status.caption(f"Loaded: {len(snapshot.investigations)} investigations / "
                       f"{sum(len(inv.test_points) for inv in snapshot.investigations):,} records / "
                       f"revision {snapshot.revision[:12]}")
try:
    if not CheckDatasetFreshness(FileSnapshotProvider(root))(snapshot):
        st.warning("Curated files changed since this snapshot was loaded. Results still use the loaded revision. "
                   "After curation is complete, use Dataset controls → Reload dataset.")
except DatasetError as error:
    st.warning(f"Dataset freshness could not be checked: {error} Results use the loaded snapshot.")

if page in ("Home", None):
    home(snapshot)
    st.stop()

with st.container(key="hero"):
    title, actions = st.columns([3, 1])
    title.title({"Dashboard": "FLAMSA", "Investigations": "Explore investigations",
        "Fire behavior": "Fire behavior & safety evidence"}.get(page, "FLAMSA"))
    title.markdown("**Microgravity combustion · Experimental analysis**")
    title.caption("Explore experimental data. Compare investigations. Find the evidence.")
    show_copilot = actions.toggle("Research copilot", value=True, key="show_copilot",
                              help="Side panel that explains which studies fit a habitat condition, with citations.")
    export_slot = actions.empty()
if page == "Fire behavior":
    behavior_introduction()
explore = ExploreInvestigations(snapshot)
sources = InvestigationSources(RegisteredSources(root, snapshot))
if page == "Dashboard":
    filters(explore.options())
if page == "Dashboard" and "candidate_query" in st.session_state:
    candidate = st.session_state.pop("candidate_query")
    try:
        explore(candidate)
        st.session_state["applied_query"] = candidate
        st.session_state.pop("filter_error", None)
    except InvalidExplorationQuery as error:
        st.session_state["filter_error"] = str(error)
if page == "Dashboard" and st.session_state.get("filter_error"):
    st.error("Filters were not applied. Results still use the last valid selection. "
             + st.session_state["filter_error"])
query = st.session_state["applied_query"]
view_query = (ExplorationQuery() if page == "Investigations" else
              ExplorationQuery(ids=("FLEX", "BASS-II", "SAFFIRE-II")) if page == "Fire behavior" else query)
matches = explore(view_query)
if page == "Dashboard":
    applied_filter_summary(query, matches)
    export_slot.download_button("Download filtered records (CSV)", export_records(snapshot.revision, record_scope(matches), matches),
        file_name=f"flamsa-records-{snapshot.revision[:12]}.csv", mime="text/csv", icon=":material/download:",
        on_click="ignore", width="stretch", help="Every record that passes the filters, with all curated columns, "
        "the raw source values and provenance. Same columns as data/curated; the file name carries the dataset revision.")
elif page == "Fire behavior":
    export_slot.download_button("Download study records (CSV)",
        export_records(snapshot.revision, record_scope(matches), matches),
        file_name=f"flamsa-fire-behavior-records-{snapshot.revision[:12]}.csv", mime="text/csv",
        icon=":material/download:", on_click="ignore", width="stretch",
        help="Complete FLEX, BASS-II and SAFFIRE-II source records, including raw values and provenance. "
             "Local analysis settings govern the charts and analysis JSON.")
if not matches:
    st.info("No records match these filters. Broaden the conditions or reset filters above.")
    st.stop()
available_ids = [m.investigation.id for m in matches]
if "selected_investigation" in st.session_state and st.session_state["selected_investigation"] not in available_ids:
    st.session_state.pop("selected_investigation")
    st.info("The previous investigation is outside the results. Select another investigation below.")
if "selected_investigation" not in st.session_state:
    st.session_state["selected_investigation"] = available_ids[0]
if page == "Investigations":
    st.caption("Browse full investigations. Dashboard filters are preserved and do not restrict this view.")
elif page == "Dashboard":
    st.caption(f"{len(matches)} investigations in view / Dataset {snapshot.revision[:12]} / Applied filters affect all charts")
if page in ("Dashboard", None):
    metrics(matches, len(snapshot.investigations))
    if show_copilot:
        workspace, copilot = st.columns([3.1, 1.35], gap="medium")
        with workspace:
            chart_context = chart_grid(matches, snapshot.revision)
        with copilot:
            pipeline = DeferredPipeline(lambda: answering_pipeline(str(root)))
            assistant_panel(snapshot.revision, query, matches, chart_context, pipeline, snapshot.investigations, sources)
    else:
        chart_context = chart_grid(matches, snapshot.revision)
if page == "Fire behavior":
    from psi_fire.interface.fire_behavior_views import fire_behavior

    chart_context = fire_behavior(matches, snapshot.revision, view_query)
    if show_copilot:
        pipeline = DeferredPipeline(lambda: answering_pipeline(str(root)))
        assistant_panel(snapshot.revision, view_query, matches, chart_context, pipeline, snapshot.investigations, sources)
    with st.expander("Scientific scope"):
        st.caption("No direct partial-gravity data or habitat-safety threshold is established by these analyses.")
    st.caption("PSI / Research workspace / Source-backed experimental data / Research copilot: validated answers only")
    st.stop()
if page == "Investigations":
    with st.container(border=True, key="investigation_preview"):
        picker, summary = st.columns([1, 2])
        selected = picker.selectbox("Open investigation", available_ids, index=None, key="selected_investigation")
        match = next(m for m in matches if m.investigation.id == selected)
        export_slot.download_button("Download investigation records (CSV)",
            export_records(snapshot.revision, record_scope((match,)), (match,)),
            file_name=f"flamsa-{selected}-{snapshot.revision[:12]}.csv", mime="text/csv",
            icon=":material/download:", on_click="ignore", width="stretch",
            help="All records of the selected investigation, including raw values and provenance.")
        picker.subheader(selected)
        picker.caption(f"{match.investigation.psi_id} / {match.investigation.record_level.value} / "
            f"{len(match.points)} reported records")
        summary.markdown("**Research objective**")
        objective = match.investigation.study_metadata.get("objective", "Objective not reported in curated metadata.")
        summary.write(objective[:260] + "..." if len(objective) > 260 else objective)
        summary.caption("The full objective, records and cited evidence are below.")
    with st.expander("Investigation catalog", expanded=False):
        frame = catalog(matches)
        sort = st.selectbox("Catalog order", ["Investigation", "Matching records", "Total records"])
        st.dataframe(frame.sort_values(sort, ascending=sort == "Investigation", kind="stable"), hide_index=True)
    detail(match, sources,
        default_tab="Citations & source downloads" if legacy_evidence else None)
    if show_copilot:
        pipeline = DeferredPipeline(lambda: answering_pipeline(str(root)))
        assistant_panel(snapshot.revision, view_query, matches, {"selected_investigation": selected}, pipeline,
                        snapshot.investigations, sources)
with st.expander("Scientific scope" if page == "Investigations" else "Applied filters and scientific scope"):
    if page != "Investigations":
        st.json(asdict(query), expanded=False)
    st.caption("Ranges describe reported coverage, not safety limits. No partial-gravity measurements are represented; "
        "electrical-field emulation is distinct. "
        + ("The CSV download holds the selected investigation's full records, not a fitted model."
           if page == "Investigations" else "The CSV download holds the filtered records, not a fitted model."))
st.caption("PSI / Research workspace / Source-backed experimental data / Research copilot: validated answers only")
