from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from psi_fire.application.explore import DatasetError
from psi_fire.infrastructure.explorer import FileSnapshotProvider

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def finish_copilot(app) -> None:
    if "copilot_job" in app.session_state:
        app.session_state["copilot_job"].future.result(timeout=90)
    app.run()


def test_explorer_navigation_filters_and_reset() -> None:
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.button(key="nav_dashboard").click().run()
    count = len(FileSnapshotProvider(APP.parents[3]).load().investigations)
    assert not app.exception
    assert app.metric[0].value == f"{count} / {count}"
    assert any(b.label == "Ask copilot" for b in app.button)
    app.button(key="nav_investigations").click().run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ["Research & scientific context", "Experimental records & raw values",
                                              "Citations & source downloads"]
    assert any(s.label == "Inspect a record" for s in app.selectbox)
    assert any(s.label == "Source document" for s in app.selectbox)
    assert not any(b.label == "Apply filters" for b in app.button)
    app.button(key="nav_dashboard").click().run()
    next(t for t in app.text_input if t.label == "Search investigations").set_value("no-such-investigation")
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception
    assert any("No records match" in item.value for item in app.info)
    next(b for b in app.button if b.label == "Reset filters").click().run()
    assert not app.exception
    app.button(key="nav_dashboard").click().run()
    assert app.metric[0].value == f"{count} / {count}"


def test_chart_selection_and_connected_assistant() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    assert not app.exception
    query = app.session_state["applied_query"]
    axes = {key: app.session_state[key] for key in ("chart_x", "chart_y", "chart_basis")}
    next(t for t in app.toggle if t.label == "Research copilot").set_value(True).run()
    assert not app.exception
    assert app.session_state["applied_query"] == query
    assert {key: app.session_state[key] for key in axes} == axes
    assert not next(t for t in app.text_area if t.label == "Ask about this scenario").disabled
    selection = next(m for m in app.multiselect if m.label == "Investigations in comparison charts")
    selection.set_value([]).run()
    assert not app.exception
    assert any("No investigations selected" in item.value for item in app.info)
    next(t for t in app.toggle if t.label == "Research copilot").set_value(False).run()
    assert not app.exception
    assert not any(b.label == "Ask copilot" for b in app.button)


def test_english_homepage_and_research_navigation() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    assert not app.exception
    assert app.session_state["workspace_navigation"] == "Home"
    assert any(t.value == "FLAMSA" for t in app.title)
    assert any("Clearer evidence" in item.value for item in app.subheader)
    assert not any(m.label == "Relevance score" for m in app.metric)
    next(b for b in app.button if b.label == "Open related research").click().run()
    assert not app.exception
    assert app.session_state["workspace_navigation"] == "Investigations"
    assert set(app.session_state["applied_query"].ids) <= {"FLEX", "FLEX-2", "CFI"}
    assert next(s for s in app.selectbox if s.label == "Open investigation").value in app.session_state["applied_query"].ids


def test_home_explains_current_capabilities_and_opens_behavior_without_replacing_filters() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    assert any(title.value == "FLAMSA" for title in app.title)
    assert any("NASA PSI combustion data" in item.value for item in app.subheader)
    copy = " ".join(item.value for item in app.markdown)
    assert "prevention, detection and suppression" in copy
    assert "Download matching records as CSV" in copy
    assert "Research copilot" in copy and "The application computes the scores" in copy
    assert "No relevance scores are computed yet" not in copy
    assert "Planned: a deterministic ranking" not in copy
    assert any("no direct lunar or Martian partial-gravity measurements" in c.value for c in app.caption)
    snapshot = app.session_state["last_snapshot"]
    assert not any(m.label == "Human-reviewed metadata" for m in app.metric)
    assert next(m for m in app.metric if m.label == "Curated investigations").value == str(len(snapshot.investigations))
    app.button(key="home_dashboard").click().run()
    app.multiselect(key="filters_0_ids").set_value(["FLEX"])
    next(button for button in app.button if button.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    app.button(key="nav_home").click().run()
    app.button(key="home_behavior").click().run()
    assert not app.exception
    assert app.session_state["workspace_navigation"] == "Fire behavior"
    assert app.session_state["applied_query"] == query
    assert [tab.label for tab in app.tabs] == ["FLEX · Burning rate", "BASS-II · Gas changes", "SAFFIRE-II · Gravity"]


def test_selected_investigations_are_retained_when_profile_quantities_are_missing() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    ids = ["BASS-II", "CFI", "FLEX-2", "FLEX", "BASS", "SAFFIRE-II"]
    next(m for m in app.multiselect if m.label == "Investigation").set_value(ids)
    next(m for m in app.multiselect if m.label == "Record level").set_value(["test", "test_day", "test_matrix"])
    next(m for m in app.multiselect if m.label == "Fuel phase").set_value(["gas", "liquid", "solid"])
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception
    assert set(app.session_state["applied_query"].ids) == set(ids)
    assert any(c.value.endswith("individual tests + 8 daily or matrix summaries") for c in app.caption)
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
    app.button(key="nav_dashboard").click().run()
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
    app.button(key="nav_home").click().run()
    app.button(key="nav_dashboard").click().run()
    assert not app.exception
    assert next(m for m in app.multiselect if m.label == "Investigation").value == ["FLEX"]
    assert next(n for n in app.number_input if n.label == "Oxygen minimum (%)").value == 20.0
    assert next(n for n in app.number_input if n.label == "Oxygen maximum (%)").value == 40.0
    assert next(c for c in app.checkbox if c.label == "Include unreported oxygen").value
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.error and app.session_state["applied_query"] == committed


def test_reload_preserves_query_on_success_and_failure_and_reports_stale_inputs() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
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
    app.button(key="nav_dashboard").click().run()
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
    app.button(key="nav_dashboard").click().run()
    next(m for m in app.multiselect if m.label == "Investigation").set_value(["BASS"])
    next(b for b in app.button if b.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    app.button(key="nav_home").click().run()
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
    assert next(s for s in app.selectbox if s.label == "Open investigation").value in app.session_state["applied_query"].ids


def test_investigations_browses_full_studies_without_changing_empty_dashboard_filters():
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    next(t for t in app.text_input if t.label == "Search investigations").set_value("no-such-investigation")
    next(b for b in app.button if b.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    app.button(key="nav_investigations").click().run()
    assert not app.exception
    assert not any(t.label == "Search investigations" for t in app.text_input)
    assert not any(b.label in ("Apply filters", "Reset filters") for b in app.button)
    picker = next(s for s in app.selectbox if s.label == "Open investigation")
    assert len(picker.options) == 15
    picker.set_value("BASS-II").run()
    assert not app.exception
    assert len(next(s for s in app.selectbox if s.label == "Inspect a record").options) == 129
    assert app.get("download_button")[0].proto.label == "Download investigation records (CSV)"
    assert app.session_state["applied_query"] == query
    app.button(key="nav_dashboard").click().run()
    assert not app.exception
    assert app.session_state["applied_query"] == query
    assert next(t for t in app.text_input if t.label == "Search investigations").value == query.search
    assert any("No records match" in item.value for item in app.info)


def test_copilot_answers_with_validated_citations_and_the_score_breakdown(monkeypatch) -> None:
    monkeypatch.setenv("PSI_LLM_MODEL", "")  # a developer's .env must not turn this offline test into a paid API call
    st.cache_resource.clear()  # the cached pipeline may have been built with that model
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    app.button(key="nav_dashboard").click().run()
    next(t for t in app.toggle if t.label == "Research copilot").set_value(True).run()
    next(b for b in app.button if b.label == "Ask copilot").click().run()
    finish_copilot(app)
    assert not app.exception
    text = " ".join(c.value for c in app.caption)
    assert "no partial-gravity data" in text and "Text written by: Template" in text
    assert "passed citation, number and plausibility checks" in text
    assert any("Score breakdown" in e.label for e in app.expander)
    app.run()  # the chart now highlights the studies of the answer
    assert not app.exception


def test_a_picked_chart_point_fills_the_copilot_inputs(monkeypatch) -> None:
    monkeypatch.setenv("PSI_LLM_MODEL", "")
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    app.button(key="nav_dashboard").click().run()
    # what pick_scenario() writes when the user clicks the coverage chart
    app.session_state["copilot_preset"] = "Custom"
    app.session_state["o2_Custom"] = 33.5
    app.session_state["psi_Custom"] = 8.0
    app.run()
    assert not app.exception
    values = {n.label: n.value for n in app.number_input}
    assert values["Oxygen (% of the atmosphere)"] == 33.5 and values["Pressure (psi)"] == 8.0


def _applied(app):
    return app.session_state["applied_query"] if "applied_query" in app.session_state else None  # noqa: SIM401 - AppTest state has no safe get


def test_view_source_labels_a_study_outside_the_filters_without_touching_them() -> None:
    from psi_fire.interface.copilot_evidence import inspection_scope

    assert inspection_scope(frozenset({"FLEX"}), "FLEX") is None
    label = inspection_scope(frozenset({"FLEX"}), "BASS-II")
    assert label and "BASS-II is outside the dashboard filters" in label and "unchanged" in label


def test_answer_citations_offer_view_source_and_opening_it_keeps_the_answer(monkeypatch) -> None:
    monkeypatch.setenv("PSI_LLM_MODEL", "")
    st.cache_resource.clear()
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    app.button(key="nav_dashboard").click().run()
    next(b for b in app.button if b.label == "Ask copilot").click().run()
    finish_copilot(app)
    buttons = [b for b in app.button if b.label == "View source"]
    assert buttons and not app.exception
    filters_before = _applied(app)
    buttons[0].click().run()
    assert not app.exception
    assert any(b.label == "View source" for b in app.button)  # the answer is still on screen
    after = _applied(app)
    assert after == filters_before


def test_the_page_survives_a_new_session_through_the_url(monkeypatch) -> None:
    monkeypatch.setenv("PSI_LLM_MODEL", "")
    app = AppTest.from_file(str(APP), default_timeout=90)
    app.query_params["page"] = "Dashboard"
    app.run()
    assert app.session_state["workspace_navigation"] == "Dashboard"
    assert app.query_params["page"] == ["Dashboard"] or app.query_params["page"] == "Dashboard"


def test_slope_sentence_states_direction_and_whether_the_interval_includes_zero() -> None:
    from psi_fire.interface.fire_behavior_views import slope_sentence

    up = slope_sentence(0.002, 0.001, 0.003)
    assert "raises K by about 0.0020" in up and "excludes zero" in up and "not a cause" in up
    down = slope_sentence(-0.004, -0.009, 0.001)
    assert "lowers K by about 0.0040" in down and "includes zero" in down


def test_flex_chart_headline_states_the_trend_without_calling_it_a_risk_class() -> None:
    from psi_fire.interface.fire_behavior_views import CHART_SUBTITLE, SIGNAL_LABELS, fuel_headline

    rising = "Higher K associated with higher oxygen"
    assert fuel_headline("heptane", [rising, rising, "Trend interval includes zero"]) == (
        "Heptane: burning rate rises with oxygen in 2 of 3 fitted groups")
    assert "no identifiable trend" in fuel_headline("methanol", [])
    assert set(SIGNAL_LABELS) == {rising, "Lower K associated with higher oxygen", "Trend interval includes zero"}
    assert "not a risk classification" in " ".join(CHART_SUBTITLE)


def test_coverage_bubbles_group_nearby_tests_per_study_and_oxygen_basis() -> None:
    import pandas as pd

    from psi_fire.interface.reference_dashboard import ANSWER_RANK, bubbles_of

    rows = [{"Investigation": "A", "Oxygen basis": "Chamber atmosphere", "O2": o2, "Pressure": psi, "Fuel": "x",
             ANSWER_RANK: "not in answer"}
            for o2, psi in [(21.0, 14.7), (21.2, 14.6), (20.9, 14.7), (30.0, 10.2)]]
    rows.append({**rows[0], "Oxygen basis": "Burner stream"})  # same place, different basis: its own bubble
    result = bubbles_of(pd.DataFrame(rows)).sort_values(["Oxygen basis", "O2"])
    assert sorted(result["n"]) == [1, 1, 3] and result["n"].sum() == 5
    assert result.loc[result["n"] == 3, "psi_min"].iloc[0] == 14.6 and result.loc[result["n"] == 3, "psi_max"].iloc[0] == 14.7


def test_coverage_map_defaults_to_the_habitat_zoom_without_burner_stream_tests(monkeypatch) -> None:
    monkeypatch.setenv("PSI_LLM_MODEL", "")
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    app.button(key="nav_dashboard").click().run()
    assert not app.exception
    labels = {t.label: t.value for t in app.toggle}
    assert labels["Include oxygen measured in the burner stream"] is False and labels["Show all pressures"] is False
    app.toggle(key="coverage_full").set_value(True).run()
    app.toggle(key="coverage_stream").set_value(True).run()
    assert not app.exception


def test_provider_failures_are_reported_as_such_and_not_as_missing_evidence() -> None:
    from psi_fire.domain.answering import IssueCode, ValidationIssue
    from psi_fire.interface.copilot_panel import narrator_failure_message

    def issue(message: str) -> tuple[ValidationIssue, ...]:
        return (ValidationIssue(code=IssueCode.EMPTY_DRAFT, message=message),)

    quota = narrator_failure_message(issue("Narrator failed: RateLimitError: Error code: 429 - {'code': 'insufficient_quota'}"))
    assert quota and "no credits" in quota and "deterministic ranking" in quota
    assert "rate limiting" in narrator_failure_message(issue("Narrator failed: RateLimitError: 429 too many requests"))
    assert "key was rejected" in narrator_failure_message(issue("Narrator failed: AuthenticationError: 401 invalid api key"))
    assert narrator_failure_message(issue("The draft contains no claims.")) is None
    assert narrator_failure_message(()) is None


def test_the_daily_limit_is_shown_counted_and_disables_the_button_when_spent(monkeypatch) -> None:
    monkeypatch.setenv("PSI_LLM_MODEL", "")
    monkeypatch.setenv("PSI_DAILY_MODEL_LIMIT", "1")
    st.cache_resource.clear()
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    app.button(key="nav_dashboard").click().run()
    assert any("Questions left today: 1 of 1" in c.value and "per visitor" in c.value for c in app.caption)
    app.button(key="ask_copilot").click().run()
    assert not app.exception
    assert any("Questions left today: 0 of 1" in c.value for c in app.caption)
    assert app.button(key="ask_copilot").disabled
    st.cache_resource.clear()


def test_the_visitor_is_the_address_google_appended_not_one_the_client_wrote(monkeypatch) -> None:
    from types import SimpleNamespace

    from psi_fire.interface.copilot_panel import visitor_key

    monkeypatch.setattr(st, "context", SimpleNamespace(headers={"X-Forwarded-For": "6.6.6.6, 1.2.3.4, 203.0.113.9"}))
    assert visitor_key() == "203.0.113.9"
    monkeypatch.setattr(st, "context", SimpleNamespace(headers={}))
    assert visitor_key() == "unknown"
