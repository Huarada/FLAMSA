"""Streamlit composition root for the research workspace."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from psi_fire.application.evidence import InvestigationSources
from psi_fire.application.explore import (
    CheckDatasetFreshness,
    DatasetError,
    ExplorationQuery,
    ExploreInvestigations,
    InvalidExplorationQuery,
    LoadExplorer,
    Snapshot,
)
from psi_fire.domain.model import Investigation
from psi_fire.infrastructure.explorer import FileSnapshotProvider, RegisteredSources
from psi_fire.interface.analytics_views import assistant_panel
from psi_fire.interface.explorer_views import applied_filter_summary, catalog, detail, filters
from psi_fire.interface.fire_behavior_views import fire_behavior
from psi_fire.interface.home_view import home
from psi_fire.interface.reference_dashboard import chart_grid, metrics
from psi_fire.interface.workspace_style import apply_style

st.set_page_config(page_title="FLAMSA / Research workspace", page_icon=":material/local_fire_department:", layout="wide")
apply_style()

@st.cache_data(max_entries=2, show_spinner="Validating curated investigations...")
def load_snapshot(root: str, refresh: int) -> tuple[str, tuple[str, ...]]:
    snapshot = LoadExplorer(FileSnapshotProvider(Path(root)))()
    return snapshot.revision, tuple(inv.model_dump_json() for inv in snapshot.investigations)

def open_investigation() -> None:
    st.session_state["workspace_navigation"] = "Investigations"

root = Path(__file__).resolve().parents[3]
if "applied_query" not in st.session_state:
    st.session_state["applied_query"] = ExplorationQuery()
if "refresh" not in st.session_state:
    st.session_state["refresh"] = 0
if "workspace_navigation" not in st.session_state:
    st.session_state["workspace_navigation"] = "Home"

with st.container(key="topbar"):
    brand, navigation, controls = st.columns([1.5, 2, 1])
    brand.image(str(Path(__file__).parent / "assets/flamsa.svg"), width=165)
    brand.caption("NASA PSI / Research workspace")
    page = navigation.segmented_control("Workspace", ["Home", "Dashboard", "Fire behavior", "Investigations", "Evidence"],
        default=None, label_visibility="collapsed", key="workspace_navigation")
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
    snapshot = Snapshot(revision, tuple(Investigation.model_validate_json(value) for value in serialized))
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
        "Evidence": "Find the evidence", "Fire behavior": "Fire behavior & safety evidence"}.get(page, "FLAMSA"))
    title.markdown("**Microgravity combustion · Experimental analysis**")
    title.caption("Explore experimental data. Compare investigations. Find the evidence.")
    show_copilot = actions.toggle("Research copilot", value=False, key="show_copilot")
    export_slot = actions.empty()
explore = ExploreInvestigations(snapshot)
filters(explore.options())
if "candidate_query" in st.session_state:
    candidate = st.session_state.pop("candidate_query")
    try:
        explore(candidate)
        st.session_state["applied_query"] = candidate
        st.session_state.pop("filter_error", None)
    except InvalidExplorationQuery as error:
        st.session_state["filter_error"] = str(error)
if st.session_state.get("filter_error"):
    st.error("Filters were not applied. Results still use the last valid selection. "
             + st.session_state["filter_error"])
query = st.session_state["applied_query"]
matches = explore(query)
applied_filter_summary(query, matches)
export = {"dataset_revision": snapshot.revision, "applied_filters": asdict(query),
    "matching_investigations": [m.investigation.id for m in matches]}
export_slot.download_button("Export view", json.dumps(export, indent=2), file_name="psi-view.json",
    mime="application/json", icon=":material/download:", on_click="ignore", width="stretch")
if not matches:
    st.info("No records match these filters. Broaden the conditions or reset filters above.")
    st.stop()
available_ids = [m.investigation.id for m in matches]
if "selected_investigation" in st.session_state and st.session_state["selected_investigation"] not in available_ids:
    st.session_state.pop("selected_investigation")
    st.info("The previous investigation is outside the results. Select another investigation below.")
if "selected_investigation" not in st.session_state:
    st.session_state["selected_investigation"] = available_ids[0]
selected = st.session_state["selected_investigation"]
st.caption(f"{len(matches)} investigations in view / Dataset {snapshot.revision[:12]} / Applied filters affect all charts")
if page in ("Dashboard", None):
    metrics(matches, len(snapshot.investigations), selected)
    if show_copilot:
        workspace, copilot = st.columns([3.4, 1.15], gap="medium")
        with workspace:
            chart_context = chart_grid(matches, selected)
        with copilot:
            assistant_panel(snapshot.revision, query, matches, chart_context)
    else:
        chart_context = chart_grid(matches, selected)
if page == "Fire behavior":
    chart_context = fire_behavior(matches, snapshot.revision, query)
    if show_copilot:
        assistant_panel(snapshot.revision, query, matches, chart_context)
    with st.expander("Applied filters and scientific scope"):
        st.json(asdict(query), expanded=False)
        st.caption("No direct partial-gravity data or habitat-safety threshold is established by these analyses.")
    st.caption("PSI / Research workspace / Source-backed experimental data / Copilot integration pending")
    st.stop()
with st.container(border=True, key="investigation_preview"):
    picker, summary = st.columns([1, 2])
    selected = picker.selectbox("Open investigation", available_ids, index=None, key="selected_investigation")
    match = next(m for m in matches if m.investigation.id == selected)
    picker.subheader(selected)
    picker.caption(f"{match.investigation.psi_id} / {match.investigation.record_level.value} / "
        f"{len(match.points)} matching / {len(match.investigation.test_points)} total records")
    summary.markdown("**Research objective**")
    objective = match.investigation.study_metadata.get("objective", "Objective not reported in curated metadata.")
    summary.write(objective[:260] + "..." if len(objective) > 260 else objective)
    summary.caption("Open the investigation for the full objective, experimental records and cited evidence.")
    if page in ("Dashboard", None):
        summary.button("Inspect investigation", on_click=open_investigation, icon=":material/arrow_forward:")
if page in ("Investigations", "Evidence"):
    if page == "Investigations":
        with st.expander("Investigation catalog", expanded=False):
            frame = catalog(matches)
            sort = st.selectbox("Catalog order", ["Investigation", "Matching records", "Total records"])
            st.dataframe(frame.sort_values(sort, ascending=sort == "Investigation", kind="stable"), hide_index=True)
    detail(match, InvestigationSources(RegisteredSources(root, snapshot)),
        default_tab="Citations & source downloads" if page == "Evidence" else None)
    if show_copilot:
        assistant_panel(snapshot.revision, query, matches, {"selected_investigation": selected})
with st.expander("Applied filters and scientific scope"):
    st.json(asdict(query), expanded=False)
    st.caption("Ranges describe reported coverage, not safety limits. No partial-gravity measurements are represented; "
        "electrical-field emulation is distinct. View export contains settings, not a training dataset.")
st.caption("PSI / Research workspace / Source-backed experimental data / Copilot integration pending")
