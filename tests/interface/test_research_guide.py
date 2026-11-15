from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def test_guide_can_be_hidden_without_changing_research_and_stays_dashboard_only() -> None:
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    app.button(key="nav_dashboard").click().run()
    assert not app.exception
    query = app.session_state["applied_query"]
    conditions = {n.label: n.value for n in app.number_input
                  if n.label in ("Oxygen (% of the atmosphere)", "Pressure (psi)")}
    assert sum(item.value.startswith("**Step ") for item in app.markdown) == 3
    app.toggle(key="research_guide_toggle").set_value(False).run()
    assert not app.exception and not any(item.value.startswith("**Step ") for item in app.markdown)
    assert app.session_state["applied_query"] == query
    assert {n.label: n.value for n in app.number_input if n.label in conditions} == conditions
    app.button(key="nav_home").click().run()
    app.button(key="nav_dashboard").click().run()
    assert not app.toggle(key="research_guide_toggle").value
    app.toggle(key="research_guide_toggle").set_value(True).run()
    assert sum(item.value.startswith("**Step ") for item in app.markdown) == 3
    app.button(key="nav_fire_behavior").click().run()
    assert not app.exception and not any(item.value.startswith("**Step ") for item in app.markdown)
    assert app.session_state["applied_query"] == query
