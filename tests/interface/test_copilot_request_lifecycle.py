"""One submitted request survives reruns, including during cold engine initialization."""

from pathlib import Path
from threading import Event
from unittest.mock import Mock

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from psi_fire.infrastructure.answering_factory import AnsweringPipeline, build_answering_pipeline
from psi_fire.infrastructure.explorer import FileSnapshotProvider

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def ask(app):
    return next(b for b in app.button if b.label == "Ask copilot")


@pytest.fixture
def completed_answer():
    from psi_fire.domain.ranking import LUNAR_BASE

    root = APP.parents[3]
    pipeline = build_answering_pipeline(root, env={})
    return pipeline.answerer(FileSnapshotProvider(root).load().investigations, LUNAR_BASE, "Why?")


def test_first_click_survives_rerun_during_initialization_without_a_second_call(monkeypatch, completed_answer):
    from psi_fire.infrastructure import answering_factory

    monkeypatch.setenv("PSI_LLM_MODEL", "")
    st.cache_resource.clear()
    started, release = Event(), Event()
    answer = Mock(return_value=completed_answer)

    def initialize(root):
        started.set()
        assert release.wait(20)
        return AnsweringPipeline(answer, "Template (cold test)")

    factory = Mock(side_effect=initialize)
    monkeypatch.setattr(answering_factory, "build_answering_pipeline", factory)
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    original_query = app.session_state["applied_query"]
    original_question = app.session_state["copilot_question"]
    from psi_fire.interface import reference_dashboard

    chart_grid = reference_dashboard.chart_grid

    def interrupt_chart_once(*args):
        if st.session_state.pop("interrupt_chart", False):
            st.rerun()
        return chart_grid(*args)

    monkeypatch.setattr(reference_dashboard, "chart_grid", interrupt_chart_once)
    app.session_state["interrupt_chart"] = True
    try:
        ask(app).click().run()
        assert started.wait(5)
        job = app.session_state["copilot_job"]
        assert ask(app).disabled and not app.exception
        next(t for t in app.text_area if t.label == "Ask about this scenario").set_value("A later draft").run()
        app.run()
        assert app.session_state["copilot_job"] is job
        factory.assert_called_once()
        answer.assert_not_called()
    finally:
        release.set()
    job.future.result(timeout=30)
    app.run()
    assert not app.exception
    assert "copilot_job" not in app.session_state
    assert not ask(app).disabled
    assert app.session_state["copilot_result"] is completed_answer
    assert app.session_state["copilot_completed_request"][1] == original_question
    assert app.session_state["copilot_question"] == "A later draft"
    assert app.session_state["applied_query"] == original_query
    assert any("Score breakdown" in e.label for e in app.expander)
    app.run()
    factory.assert_called_once()
    answer.assert_called_once()


def test_submit_callback_reads_current_widget_values(monkeypatch, completed_answer):
    from psi_fire.infrastructure import answering_factory

    monkeypatch.setenv("PSI_LLM_MODEL", "")
    st.cache_resource.clear()
    answer = Mock(return_value=completed_answer)
    monkeypatch.setattr(answering_factory, "build_answering_pipeline",
                        Mock(return_value=AnsweringPipeline(answer, "Template")))
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    next(n for n in app.number_input if n.label == "Oxygen (% of the atmosphere)").set_value(35.0)
    next(n for n in app.number_input if n.label == "Pressure (psi)").set_value(9.0)
    next(t for t in app.text_area if t.label == "Ask about this scenario").set_value("Use the current conditions")
    ask(app).click().run()
    if "copilot_job" in app.session_state:
        app.session_state["copilot_job"].future.result(timeout=30)
        app.run()
    scenario, question = answer.call_args.args[1:]
    assert scenario.o2_percent == 35.0 and scenario.pressure_psi == 9.0
    assert question == "Use the current conditions"
    assert not app.exception


def test_request_failure_preserves_previous_answer_and_allows_explicit_retry(monkeypatch, completed_answer):
    from psi_fire.infrastructure import answering_factory

    monkeypatch.setenv("PSI_LLM_MODEL", "")
    st.cache_resource.clear()
    answer = Mock(side_effect=[RuntimeError("provider-secret-do-not-display"), completed_answer])
    monkeypatch.setattr(answering_factory, "build_answering_pipeline",
                        Mock(return_value=AnsweringPipeline(answer, "Template (retry test)")))
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    app.session_state["copilot_result"] = completed_answer
    app.session_state["copilot_narrator_label"] = "Previous template"
    ask(app).click().run()
    job = app.session_state["copilot_job"] if "copilot_job" in app.session_state else None  # noqa: SIM401 - AppTest has no safe get
    if job:
        with pytest.raises(RuntimeError):
            job.future.result(timeout=30)
        app.run()
    assert not app.exception
    assert "copilot_job" not in app.session_state
    assert app.session_state["copilot_result"] is completed_answer
    assert any("could not finish" in e.value for e in app.error)
    assert not any("provider-secret" in e.value for e in app.error)
    assert not ask(app).disabled
    ask(app).click().run()
    if "copilot_job" in app.session_state:
        app.session_state["copilot_job"].future.result(timeout=30)
        app.run()
    assert not app.error and not app.exception
    assert answer.call_count == 2
