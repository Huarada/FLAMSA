from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def test_behavior_cards_local_settings_copilot_and_source_navigation_preserve_query() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_fire_behavior").click().run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ["FLEX · Burning rate", "BASS-II · Gas changes", "SAFFIRE-II · Gravity"]
    query = app.session_state["applied_query"]
    assert any("pressure ≤10.2 psi" in item.value for item in app.markdown)
    assert any("Complete and Acceleratory remain source labels" in item.value for item in app.caption)
    slope_frames = [item.value for item in app.dataframe if "Adjusted slope (mm²/s per O₂ point)" in item.value.columns]
    assert len(slope_frames) == 1 and (slope_frames[0]["Fit status"] == "Estimated").any()
    next(s for s in app.selectbox if s.label == "Near-1-atm pressure tolerance (%)").set_value(1).run()
    next(s for s in app.selectbox if s.label == "Initial diameter scope").set_value("2–3 mm").run()
    assert not app.exception and app.session_state["applied_query"] == query
    next(t for t in app.toggle if t.label == "Research copilot").set_value(True).run()
    assert not app.exception and app.session_state["applied_query"] == query
    next(b for b in app.button if b.label == "Open BASS-II source records").click().run()
    assert not app.exception and app.session_state["applied_query"] == query
    assert app.session_state["workspace_navigation"] == "Investigations"
    assert app.session_state["selected_investigation"] == "BASS-II"


def test_behavior_studies_removed_by_research_filters_stay_empty() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_fire_behavior").click().run()
    next(m for m in app.multiselect if m.label == "Investigation").set_value(["BASS-II"])
    next(b for b in app.button if b.label == "Apply filters").click().run()
    assert not app.exception
    assert app.session_state["applied_query"].ids == ("BASS-II",)
    assert any("FLEX is outside" in item.value for item in app.info)
    assert any("SAFFIRE-II has no matching" in item.value for item in app.info)
    assert next(b for b in app.button if b.label == "Open FLEX source records").disabled
    assert next(b for b in app.button if b.label == "Open SAFFIRE-II source records").disabled
    assert not next(b for b in app.button if b.label == "Open BASS-II source records").disabled
