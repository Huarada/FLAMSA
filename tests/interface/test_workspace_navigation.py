from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def test_header_purpose_help_navigation_and_educational_introduction() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    assert not app.exception
    assert not any(button.key == "nav_evidence" for button in app.button)
    dashboard = app.button(key="nav_dashboard")
    behavior = app.button(key="nav_fire_behavior")
    assert "3-step guide" in dashboard.proto.help and "coverage map" in dashboard.proto.help
    assert all(study in behavior.proto.help for study in ("FLEX", "BASS-II", "SAFFIRE-II"))
    assert behavior.proto.type == "primary"
    dashboard.click().run()
    app.multiselect(key="filters_0_ids").set_value(["FLEX", "BASS-II"])
    next(button for button in app.button if button.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    app.button(key="nav_fire_behavior").click().run()
    assert not app.exception and app.session_state["applied_query"] == query
    assert app.session_state["workspace_navigation"] == "Fire behavior"
    assert any("Current view: Fire behavior" in item.value for item in app.caption)
    assert any("From physical laws to traceable evidence" in item.value for item in app.subheader)
    assert any("d-squared model" in item.value for item in app.markdown)
    assert any("percentage points" in item.value for item in app.caption)
    assert any("physical-consistency check" in item.value for item in app.caption)
    app.button(key="nav_investigations").click().run()
    assert not app.exception and app.session_state["applied_query"] == query
    assert app.session_state["workspace_navigation"] == "Investigations"
    assert "Citations & source downloads" in [tab.label for tab in app.tabs]
    assert any(item.label == "Source document" for item in app.selectbox)
    next(button for button in app.button if button.label == "Prepare source download").click().run()
    assert not app.exception
    assert len(app.get("download_button")) == 2
    app.button(key="nav_home").click().run()
    assert not app.exception and app.session_state["applied_query"] == query


def test_existing_evidence_session_redirects_to_investigations_without_losing_query() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    app.multiselect(key="filters_0_ids").set_value(["FLEX"])
    next(button for button in app.button if button.label == "Apply filters").click().run()
    query = app.session_state["applied_query"]
    app.session_state["workspace_navigation"] = "Evidence"
    app.run()
    assert not app.exception
    assert app.session_state["workspace_navigation"] == "Investigations"
    assert app.session_state["applied_query"] == query
    assert any("Current view: Investigations" in caption.value for caption in app.caption)
    assert any(item.label == "Source document" for item in app.selectbox)
