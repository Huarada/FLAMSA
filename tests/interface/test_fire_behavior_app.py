from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def test_behavior_cards_local_settings_copilot_and_source_navigation_preserve_query() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_fire_behavior").click().run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ["FLEX · Burning rate", "BASS-II · Gas changes", "SAFFIRE-II · Gravity"]
    assert any("They do not estimate ignition probability" in item.value for item in app.info)
    assert any("Above/below the line is not a risk" in item.value for item in app.warning)
    assert any("do not certify a material as safe" in item.value for item in app.warning)
    gas_frames = [item.value for item in app.dataframe if "Safety-relevant evidence" in item.value.columns
                  and "test_point_id" in item.value.columns]
    assert len(gas_frames) == 1
    assert "Oxygen decrease and CO2 increase measured" in set(gas_frames[0]["Safety-relevant evidence"])
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


@pytest.mark.parametrize("empty_dashboard", [False, True])
def test_behavior_ignores_dashboard_filters_and_restores_them_on_return(empty_dashboard) -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    next(m for m in app.multiselect if m.label == "Investigation").set_value(["BASS-II"])
    if empty_dashboard:
        next(t for t in app.text_input if t.label == "Search investigations").set_value("no-such-investigation")
    next(b for b in app.button if b.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    app.button(key="nav_fire_behavior").click().run()
    assert not app.exception
    assert not any(b.label in ("Apply filters", "Reset filters") for b in app.button)
    assert not any(m.label == "Investigation" for m in app.multiselect)
    assert not any(e.label == "Applied filters and scientific scope" for e in app.expander)
    assert app.get("download_button")[0].proto.label == "Download study records (CSV)"
    for study in ("FLEX", "BASS-II", "SAFFIRE-II"):
        assert not next(b for b in app.button if b.label == f"Open {study} source records").disabled
    assert len(app.tabs) == 3
    next(s for s in app.selectbox if s.label == "Near-1-atm pressure tolerance (%)").set_value(1).run()
    assert not app.exception and app.session_state["applied_query"] == query
    app.button(key="nav_dashboard").click().run()
    assert not app.exception and app.session_state["applied_query"] == query
    assert next(m for m in app.multiselect if m.label == "Investigation").value == ["BASS-II"]
    if empty_dashboard:
        assert any("No records match" in item.value for item in app.info)
