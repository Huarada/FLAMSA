"""Research copilot: asks the answering pipeline (SPEC-003) and shows the validated result next to its evidence."""

import pandas as pd
import streamlit as st

from psi_fire.application.answer_types import AnswerResult, AnswerStatus
from psi_fire.domain.manual import GravityRegime
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import LUNAR_BASE, HabitatScenario
from psi_fire.infrastructure.answering_factory import AnsweringPipeline

EARTH_CABIN = HabitatScenario("Earth cabin", 21.0, 14.7, GravityRegime.NORMAL)
PRESETS = {"Lunar base": LUNAR_BASE, "Earth cabin": EARTH_CABIN}
CUSTOM = "Custom"
DEFAULT_QUESTION = "Which investigations are most relevant to this scenario, and why?"
RESULT_KEY = "copilot_result"


def _scenario() -> HabitatScenario:
    preset = st.selectbox("Habitat scenario", [*PRESETS, CUSTOM], key="copilot_preset")
    base = PRESETS.get(preset, EARTH_CABIN)
    o2 = st.number_input("Oxygen (% of the atmosphere)", 0.0, 100.0, base.o2_percent, 0.5, key=f"o2_{preset}")
    pressure = st.number_input("Pressure (psi)", 0.0, 100.0, base.pressure_psi, 0.1, key=f"psi_{preset}")
    gravity = base.gravity
    if preset == CUSTOM:
        gravity = GravityRegime(st.selectbox("Gravity", [g.value for g in GravityRegime], index=2, key="copilot_g"))
    return HabitatScenario(preset if preset != CUSTOM else "Custom scenario", o2, pressure, gravity)


def _breakdown_table(result: AnswerResult) -> pd.DataFrame:
    return pd.DataFrame([
        {"Rank": r.rank, "Investigation": r.investigation.id, "Score": r.score, "Criterion": s.criterion,
         "Weight": s.weight, "Value": s.value, "Contribution": s.contribution, "Why": s.rationale}
        for r in result.shortlist for s in r.breakdown.scores])


def _render(result: AnswerResult, narrator_label: str) -> None:
    if result.status == AnswerStatus.APPROVED and result.draft:
        st.badge("Validated answer", color="green", icon=":material/verified:")
        st.caption(f"Text written by: {narrator_label}. Ranking and scores are computed by the application, "
                   "not by the model. Every claim below passed citation, number and plausibility checks.")
        for index, claim in enumerate(result.draft.claims):
            st.markdown(claim.text)
            for entry in (e for e in result.traceability if e.claim_index == index):
                c = entry.citation
                where = f"{entry.source_file or 'n/a'} / {entry.locator or 'n/a'}"
                st.caption(f"{c.kind.value}: {c.investigation_id} {c.test_point_id or c.field or ''} → {where}")
        if result.solutions:
            st.markdown("**Derived technologies (catalog)**")
            for s in result.solutions:
                label = "illustrative, not evidence" if s.status == "illustrative" else f"source: {s.source_file}"
                st.caption(f"{s.investigation_id}: {s.technology} ({label})")
    else:
        st.badge("Insufficient evidence", color="orange", icon=":material/rule:")
        st.write("No answer passed validation, so no generated text is shown. The deterministic ranking follows.")
        for issue in result.issues:
            st.caption(f"{issue.code.value}: {issue.message}")
        st.code(result.breakdown_text, language=None)
    if result.shortlist:
        with st.expander("Score breakdown (criterion, weight, value, contribution)", expanded=True):
            st.dataframe(_breakdown_table(result), hide_index=True)
    st.markdown("**Limitations**")
    for note in result.limitations:
        st.caption(note)
    with st.expander("Run trace"):
        for a in result.attempts:
            st.caption(f"Attempt {a.attempt}: top {a.settings.top_k}, minimum score {a.settings.min_score}, "
                       f"{a.passage_count} passages, {len(a.issues)} issues → {', '.join(a.shortlist_ids) or 'none'}")


def copilot(pipeline: AnsweringPipeline, investigations: tuple[Investigation, ...]) -> None:
    scenario = _scenario()
    question = st.text_area("Ask about this scenario", DEFAULT_QUESTION, height=90, key="copilot_question")
    st.caption("The ranking covers all curated investigations, not only the filtered view.")
    if st.button("Ask copilot", icon=":material/auto_awesome:", width="stretch"):
        with st.spinner("Ranking, retrieving passages and validating..."):
            st.session_state[RESULT_KEY] = pipeline.answerer(investigations, scenario, question)
    if RESULT_KEY in st.session_state:
        _render(st.session_state[RESULT_KEY], pipeline.narrator_label)
