from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from psi_fire.application.explore import DatasetError
from psi_fire.infrastructure.explorer import FileSnapshotProvider

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def test_explorer_navigation_filters_and_reset() -> None:
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    count = len(FileSnapshotProvider(APP.parents[3]).load().investigations)
    assert not app.exception
    assert app.metric[0].value == f"{count} / {count}"
    assert not any(b.label == "Ask copilot" for b in app.button)
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Investigations").run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ["Research & scientific context", "Experimental records & raw values",
                                              "Citations & source downloads"]
    assert any(s.label == "Inspect a record" for s in app.selectbox)
    assert any(s.label == "Source document" for s in app.selectbox)
    next(t for t in app.text_input if t.label == "Search investigations").set_value("no-such-investigation")
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception
    assert any("No records match" in item.value for item in app.info)
    next(b for b in app.button if b.label == "Reset filters").click().run()
    assert not app.exception
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    assert app.metric[0].value == f"{count} / {count}"


def test_chart_selection_and_disabled_assistant() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    assert not app.exception
    query = app.session_state["applied_query"]
    axes = {key: app.session_state[key] for key in ("chart_x", "chart_y", "chart_basis")}
    next(t for t in app.toggle if t.label == "Research copilot").set_value(True).run()
    assert not app.exception
    assert app.session_state["applied_query"] == query
    assert {key: app.session_state[key] for key in axes} == axes
    assert next(t for t in app.text_area if t.label == "Ask about this dashboard").disabled
    selection = next(m for m in app.multiselect if m.label == "Investigations in comparison charts")
    selection.set_value([]).run()
    assert not app.exception
    assert any("No compatible scalar pairs" in item.value for item in app.info)
    next(t for t in app.toggle if t.label == "Research copilot").set_value(False).run()
    assert not app.exception
    assert not any(b.label == "Ask copilot" for b in app.button)


def test_english_homepage_and_research_navigation() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    assert not app.exception
    assert next(s for s in app.segmented_control if s.label == "Workspace").value == "Home"
    assert any("Clearer evidence" in t.value for t in app.title)
    assert not any(m.label == "Relevance score" for m in app.metric)
    next(b for b in app.button if b.label == "Open related research").click().run()
    assert not app.exception
    assert next(s for s in app.segmented_control if s.label == "Workspace").value == "Investigations"
    assert set(app.session_state["applied_query"].ids) <= {"FLEX", "FLEX-2", "CFI"}
    assert next(m for m in app.multiselect if m.label == "Investigation").value == list(
        app.session_state["applied_query"].ids
    )


def test_selected_investigations_are_retained_when_profile_quantities_are_missing() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    ids = ["BASS-II", "CFI", "FLEX-2", "FLEX", "BASS", "SAFFIRE-II"]
    next(m for m in app.multiselect if m.label == "Investigation").set_value(ids)
    next(m for m in app.multiselect if m.label == "Record level").set_value(["test", "test_day", "test_matrix"])
    next(m for m in app.multiselect if m.label == "Fuel phase").set_value(["gas", "liquid", "solid"])
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception
    assert set(app.session_state["applied_query"].ids) == set(ids)
    assert any(c.value == "test · test_matrix" for c in app.caption)
    assert any("Showing 2 of 6 chart-selected investigations" in item.value for item in app.info)
    tables = [frame.value for frame in app.dataframe if "Primary reasons for omitted records" in frame.value.columns]
    assert len(tables) == 1
    availability = tables[0].set_index("Investigation")
    assert set(availability.index) == set(ids)
    assert availability.loc["BASS", "Plotted records"] == 0
    assert "not reported" in availability.loc["BASS-II", "Primary reasons for omitted records"]
    assert "summaries" in availability.loc["FLEX-2", "Primary reasons for omitted records"]
    original_query = app.session_state["applied_query"]
    next(s for s in app.selectbox if s.label == "Inspect retained investigation").set_value("BASS-II").run()
    next(b for b in app.button if b.label == "Open retained records").click().run()
    assert not app.exception
    assert app.session_state["workspace_navigation"] == "Investigations"
    assert app.session_state["selected_investigation"] == "BASS-II"
    assert app.session_state["applied_query"] == original_query


def test_filters_rehydrate_after_home_and_invalid_drafts_do_not_replace_results() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    next(m for m in app.multiselect if m.label == "Investigation").set_value(["FLEX"])
    next(c for c in app.checkbox if c.label == "Filter oxygen").check()
    next(n for n in app.number_input if n.label == "Oxygen minimum (%)").set_value(20.0)
    next(n for n in app.number_input if n.label == "Oxygen maximum (%)").set_value(40.0)
    next(c for c in app.checkbox if c.label == "Include unreported oxygen").check()
    next(b for b in app.button if b.label == "Apply filters").click().run()
    committed = app.session_state["applied_query"]
    metrics = [m.value for m in app.metric]
    assert any("without reported oxygen" in c.value for c in app.caption)
    next(m for m in app.multiselect if m.label == "Investigation").set_value(["CFI"]).run()
    assert app.session_state["applied_query"] == committed
    assert [m.value for m in app.metric] == metrics
    next(n for n in app.number_input if n.label == "Oxygen minimum (%)").set_value(50.0)
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception
    assert app.session_state["applied_query"] == committed
    assert [m.value for m in app.metric] == metrics
    assert any("Filters were not applied" in item.value for item in app.error)
    assert any("Applied filters · Investigation: FLEX" in c.value for c in app.caption)
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Home").run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    assert not app.exception
    assert next(m for m in app.multiselect if m.label == "Investigation").value == ["FLEX"]
    assert next(n for n in app.number_input if n.label == "Oxygen minimum (%)").value == 20.0
    assert next(n for n in app.number_input if n.label == "Oxygen maximum (%)").value == 40.0
    assert next(c for c in app.checkbox if c.label == "Include unreported oxygen").value
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.error and app.session_state["applied_query"] == committed


def test_reload_preserves_query_on_success_and_failure_and_reports_stale_inputs() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    next(m for m in app.multiselect if m.label == "Investigation").set_value(["FLEX", "BASS-II"])
    next(b for b in app.button if b.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    metrics = [m.value for m in app.metric]
    with patch.object(FileSnapshotProvider, "current_revision", return_value="new-publication"):
        app.run()
    assert any("Curated files changed" in item.value for item in app.warning)
    next(c for c in app.checkbox if c.label == "Curation is complete and idle").check().run()
    next(b for b in app.button if b.label == "Reload dataset").click().run()
    assert not app.exception
    assert app.session_state["applied_query"] == query
    assert next(m for m in app.multiselect if m.label == "Investigation").value == list(query.ids)
    assert [m.value for m in app.metric] == metrics
    st.cache_data.clear()
    with patch.object(FileSnapshotProvider, "load", side_effect=DatasetError("Incomplete publication")):
        next(b for b in app.button if b.label == "Reload dataset").click().run()
    assert not app.exception
    assert any("Reload failed" in item.value for item in app.warning)
    assert app.session_state["applied_query"] == query
    assert [m.value for m in app.metric] == metrics


def test_standalone_basis_submission_and_conflict_keep_the_committed_scope() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    next(m for m in app.multiselect if m.label == "Reported oxygen basis").set_value(["oxidizer_stream"])
    next(b for b in app.button if b.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    assert query.bases == ("oxidizer_stream",) and query.oxygen is None
    assert app.metric[0].value.startswith("1 /")
    next(c for c in app.checkbox if c.label == "Filter oxygen").check()
    next(n for n in app.number_input if n.label == "Oxygen minimum (%)").set_value(20.0)
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception
    assert app.session_state["applied_query"] == query
    assert any("select only its measurement basis" in item.value for item in app.error)
    next(s for s in app.selectbox if s.label == "Oxygen measurement basis").set_value("oxidizer_stream")
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception and not app.error
    assert app.session_state["applied_query"].oxygen.lower == 20.0


def test_home_topics_preserve_applied_filters_until_opening_related_research() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Dashboard").run()
    next(m for m in app.multiselect if m.label == "Investigation").set_value(["BASS"])
    next(b for b in app.button if b.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    next(s for s in app.segmented_control if s.label == "Workspace").set_value("Home").run()
    counts = [metric.value for metric in app.metric]
    next(p for p in app.pills if p.label == "Explore a research theme").set_value(
        "4 · Detection and diagnostics"
    ).run()
    assert not app.exception
    assert app.session_state["applied_query"] == query
    assert [metric.value for metric in app.metric] == counts
    assert any("Detection, diagnostics and measurement" in header.value for header in app.subheader)
    assert any("Concept illustration supplied for FLAMSA" in caption.value for caption in app.caption)
    next(b for b in app.button if b.label == "Open related research").click().run()
    assert not app.exception
    assert set(app.session_state["applied_query"].ids) == {"SAME", "SAME-R", "ACME-CFI-G", "SPICE"}
    assert next(m for m in app.multiselect if m.label == "Investigation").value == list(
        app.session_state["applied_query"].ids
    )
