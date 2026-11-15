from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, sentinel

from streamlit.testing.v1 import AppTest

from psi_fire.domain.ranking import LUNAR_BASE
from psi_fire.interface.deferred_pipeline import DeferredPipeline


def test_question_initializes_once_and_preserves_the_real_answer_and_label() -> None:
    answer = Mock(return_value=sentinel.result)
    factory = Mock(return_value=SimpleNamespace(answerer=answer, narrator_label="Template"))
    deferred = DeferredPipeline(factory)
    call = deferred.answerer
    factory.assert_not_called()
    assert call((), LUNAR_BASE, "Why?") is sentinel.result
    assert deferred.narrator_label == "Template"
    factory.assert_called_once()
    answer.assert_called_once_with((), LUNAR_BASE, "Why?")


def test_browsing_does_not_initialize_answering_engine(monkeypatch) -> None:
    import streamlit as st

    from psi_fire.infrastructure import answering_factory

    st.cache_resource.clear()
    factory = Mock(side_effect=AssertionError("Browsing must not initialize the answering engine"))
    monkeypatch.setattr(answering_factory, "build_answering_pipeline", factory)
    app_path = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"
    app = AppTest.from_file(str(app_path), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    app.run()
    assert not app.exception
    assert any(button.label == "Ask copilot" for button in app.button)
    factory.assert_not_called()
