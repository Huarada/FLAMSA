"""Regressions from the Research filters audit: committed scope and visible chart controls."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def widget(app, kind, label):
    return next(item for item in getattr(app, kind) if item.label == label)


def apply(app):
    widget(app, "button", "Apply filters").click().run()
    assert not app.exception


def dashboard(monkeypatch):
    monkeypatch.setenv("PSI_LLM_MODEL", "")
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    app.button(key="nav_dashboard").click().run()
    return app


def test_study_changes_reconcile_chart_scope_and_quantity_labels(monkeypatch):
    app = dashboard(monkeypatch)
    for study in ("FLEX", "BASS-II", "SPICE", "FLEX"):
        widget(app, "multiselect", "Investigation").set_value([study])
        apply(app)
        assert widget(app, "multiselect", "Investigations in comparison charts").value == [study]
        y = widget(app, "selectbox", "Vertical quantity")
        assert y.value
        assert all("· 0 records" not in label for label in y.options)
        assert any("plotted" in c.value for c in app.caption)
    widget(app, "multiselect", "Investigations in comparison charts").set_value([]).run()
    assert not app.exception
    assert any("No investigations selected" in info.value for info in app.info)
    app.run()
    assert widget(app, "multiselect", "Investigations in comparison charts").value == []
    widget(app, "button", "Reset filters").click().run()
    assert len(widget(app, "multiselect", "Investigations in comparison charts").value) == 15
    assert app.session_state["chart_y"] == "burn_time_s"


def test_valid_local_subset_survives_and_stream_basis_follows_research(monkeypatch):
    app = dashboard(monkeypatch)
    widget(app, "multiselect", "Investigations in comparison charts").set_value(["FLEX"]).run()
    widget(app, "multiselect", "Investigation").set_value(["FLEX", "BASS-II"])
    apply(app)
    assert widget(app, "multiselect", "Investigations in comparison charts").value == ["FLEX"]
    widget(app, "button", "Reset filters").click().run()
    widget(app, "multiselect", "Reported oxygen basis").set_value(["oxidizer_stream"])
    apply(app)
    assert app.session_state["chart_basis"] == "oxidizer_stream"
    assert any("154 plotted" in c.value for c in app.caption)
    y = widget(app, "selectbox", "Vertical quantity")
    assert y.value == "burn_time_s"
    assert "Burn time (s) · 154 records" in y.options


def test_inactive_bounds_are_rejected_and_cleared_selects_use_defaults(monkeypatch):
    app = dashboard(monkeypatch)
    baseline = app.session_state["applied_query"]
    for toggle, lower in (("Filter oxygen", "Oxygen minimum (%)"),
                          ("Filter pressure", "Pressure minimum (psi)"),
                          ("Filter flow speed", "Flow minimum (cm/s)")):
        widget(app, "number_input", lower).set_value(90.0)
        apply(app)
        assert app.session_state["applied_query"] == baseline
        assert any(f"Enable {toggle}" in error.value for error in app.error)
        widget(app, "button", "Reset filters").click().run()
    for label in ("Oxygen measurement basis", "Manual review", "Curation notes"):
        widget(app, "selectbox", label).set_value(None)
    apply(app)
    assert not app.error
    assert app.session_state["applied_query"] == baseline


def test_summary_only_and_missing_pressure_explain_their_retained_records(monkeypatch):
    app = dashboard(monkeypatch)
    widget(app, "multiselect", "Investigation").set_value(["FLEX-2"])
    apply(app)
    assert widget(app, "selectbox", "Vertical quantity").disabled
    assert widget(app, "selectbox", "Vertical quantity").options == []
    assert any("daily or matrix summaries" in info.value for info in app.info)
    assert any("8 records remain" in info.value for info in app.info)
    assert any(b.label == "Open retained records" for b in app.button)
    widget(app, "multiselect", "Investigation").set_value(["BASS-II"])
    apply(app)
    assert any("129 records remain" in info.value for info in app.info)
    assert any("127 plotted" in c.value for c in app.caption)
