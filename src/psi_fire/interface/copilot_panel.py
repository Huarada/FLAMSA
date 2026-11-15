"""Research copilot: asks the answering pipeline (SPEC-003) and shows the validated result next to its evidence."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from psi_fire.application.answer_types import AnswerResult, AnswerStatus
from psi_fire.application.quota import DailyQuota, QuotaVerdict
from psi_fire.domain.answering import CitationKind, IssueCode, ValidationIssue
from psi_fire.domain.manual import GravityRegime
from psi_fire.domain.model import Investigation
from psi_fire.domain.ranking import LUNAR_BASE, HabitatScenario
from psi_fire.interface.copilot_evidence import EvidenceContext, render_citation, render_figures
from psi_fire.interface.copilot_job import CopilotJob
from psi_fire.interface.deferred_pipeline import PipelineHandle
from psi_fire.interface.research_guide import question_step, response_step

EARTH_CABIN = HabitatScenario("Earth cabin", 21.0, 14.7, GravityRegime.NORMAL)
PRESETS = {"Lunar base": LUNAR_BASE, "Earth cabin": EARTH_CABIN}
CUSTOM = "Custom"
DEFAULT_QUESTION = "Which investigations are most relevant to this scenario, and why?"
RESULT_KEY = "copilot_result"
JOB_KEY = "copilot_job"
LABEL_KEY = "copilot_narrator_label"
REQUEST_KEY = "copilot_completed_request"


def scenario_point() -> tuple[float, float]:
    """Oxygen and pressure currently set in the copilot; the coverage chart draws its marker here."""
    preset = st.session_state.get("copilot_preset", "Lunar base")
    base = PRESETS.get(preset, EARTH_CABIN)
    return (float(st.session_state.get(f"o2_{preset}", base.o2_percent)),
            float(st.session_state.get(f"psi_{preset}", base.pressure_psi)))


def pick_scenario(o2_percent: float, pressure_psi: float) -> None:
    """Called before the copilot widgets are created in the same run, so Streamlit accepts the new values."""
    st.session_state["copilot_preset"] = CUSTOM
    st.session_state[f"o2_{CUSTOM}"] = o2_percent
    st.session_state[f"psi_{CUSTOM}"] = pressure_psi


def _scenario() -> HabitatScenario:
    st.caption("Set the conditions, ask a question, then check the sources.")
    preset = st.selectbox("Habitat scenario", [*PRESETS, CUSTOM], key="copilot_preset",
                          help="Lunar base: 30% O₂, 10.2 psi. Earth cabin: 21% O₂, 14.7 psi. Clicking the chart "
                               "switches to Custom.")
    base = PRESETS.get(preset, EARTH_CABIN)
    st.session_state.setdefault(f"o2_{preset}", base.o2_percent)  # state, not value=, so chart picks raise no warning
    st.session_state.setdefault(f"psi_{preset}", base.pressure_psi)
    o2 = st.number_input("Oxygen (% of the atmosphere)", 0.0, 100.0, step=0.5, key=f"o2_{preset}",
                         help="Share of oxygen in the habitat air. Moves the dark-cyan marker on the chart.")
    pressure = st.number_input("Pressure (psi)", 0.0, 100.0, step=0.1, key=f"psi_{preset}",
                               help="Total cabin pressure. Sea level is 14.7 psi.")
    gravity = base.gravity
    if preset == CUSTOM:
        gravity = GravityRegime(st.selectbox("Gravity", [g.value for g in GravityRegime], index=2, key="copilot_g"))
    return HabitatScenario(preset if preset != CUSTOM else "Custom scenario", o2, pressure, gravity)


USER_QUOTA_MESSAGE = ("You have used your {limit} copilot questions for today. The count resets at 00:00 UTC and "
                      "whenever the application is released again. Your previous answer, the chart and the filters "
                      "are unchanged.")
GLOBAL_QUOTA_MESSAGE = ("The copilot reached its daily limit for all visitors. It resets at 00:00 UTC and whenever the "
                        "application is released again. Your previous answer, the chart and the filters are unchanged.")


def visitor_key() -> str:
    """The visitor's network address as Cloud Run reports it. The last X-Forwarded-For entry is the one Google's
    front end appended; earlier entries can be written by the client, so they are ignored. Without the header
    (local run) every visitor shares one bucket, which is harmless because local runs set no limit."""
    forwarded = st.context.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[-1].strip() or "unknown"


def _submit(pipeline: PipelineHandle, investigations: tuple[Investigation, ...],
            quota: DailyQuota | None = None) -> None:
    """Capture the click before charts render: a queued rerun must not consume a transient button value."""
    if JOB_KEY in st.session_state:
        return
    if quota is not None:
        verdict = quota.consume(visitor_key())
        if verdict != QuotaVerdict.ALLOWED:
            st.session_state["copilot_request_error"] = (
                GLOBAL_QUOTA_MESSAGE if verdict == QuotaVerdict.GLOBAL_LIMIT
                else USER_QUOTA_MESSAGE.format(limit=quota.limit))
            return
    preset = st.session_state.get("copilot_preset", "Lunar base")
    base = PRESETS.get(preset, EARTH_CABIN)
    o2, pressure = scenario_point()
    gravity = GravityRegime(st.session_state.get("copilot_g", base.gravity.value)) if preset == CUSTOM else base.gravity
    scenario = HabitatScenario(preset if preset != CUSTOM else "Custom scenario", o2, pressure, gravity)
    job = CopilotJob.prepare(scenario, st.session_state.get("copilot_question", DEFAULT_QUESTION))
    st.session_state[JOB_KEY] = job
    st.session_state.pop("copilot_request_error", None)
    job.start(pipeline, investigations)


def _breakdown_table(result: AnswerResult) -> pd.DataFrame:
    return pd.DataFrame([
        {"Rank": r.rank, "Investigation": r.investigation.id, "Score": r.score, "Criterion": s.criterion,
         "Weight": s.weight, "Value": s.value, "Contribution": s.contribution, "Why": s.rationale}
        for r in result.shortlist for s in r.breakdown.scores])


def narrator_failure_message(issues: tuple[ValidationIssue, ...]) -> str | None:
    """A provider failure (no credits, bad key, rate limit) is not a validation failure: say so in plain words."""
    failure = next((i.message for i in issues if i.code == IssueCode.EMPTY_DRAFT and "Narrator failed" in i.message), None)
    if failure is None:
        return None
    lowered = failure.lower()
    if "insufficient_quota" in lowered or "no credits" in lowered or "credit_balance" in lowered:
        reason = ("The language-model account has no credits left. Add credits in the provider's billing page, "
                  "or clear PSI_LLM_MODEL in .env to use the offline template narrator.")
    elif "429" in lowered or "ratelimit" in lowered or "rate limit" in lowered:
        reason = "The language-model provider is rate limiting requests. Wait a moment and ask again."
    elif "401" in lowered or "authentication" in lowered or "api key" in lowered:
        reason = "The language-model API key was rejected. Check OPENAI_API_KEY in .env."
    else:
        reason = "The language-model call failed before it produced text."
    return f"{reason} No text was generated, so nothing was validated; the deterministic ranking below is unaffected."


def _render(result: AnswerResult, narrator_label: str, context: EvidenceContext) -> None:
    if result.status in (AnswerStatus.APPROVED, AnswerStatus.PARTIAL) and result.draft:
        if result.status == AnswerStatus.PARTIAL:
            st.badge("Partially validated", color="orange", icon=":material/rule:")
            st.warning(f"{len(result.draft.claims)} of {result.claims_total} claims passed validation and are shown; "
                       f"{result.claims_withheld} were withheld because they could not be verified. This answer may be "
                       "incomplete. The ranking, scores and limitations below are complete.")
        else:
            st.badge("Validated answer", color="green", icon=":material/verified:")
        st.caption(f"Text written by: {narrator_label}. Ranking and scores are computed by the application, "
                   "not by the model. Every claim below passed citation, number and plausibility checks.")
        for index, claim in enumerate(result.draft.claims):
            st.markdown(claim.text)
            render_figures(tuple(f for f in result.figure_traces if f.claim_index == index))
            entries = [e for e in result.traceability if e.claim_index == index]
            documents = [e for e in entries if e.citation.kind in (CitationKind.PASSAGE, CitationKind.RECORD)]
            context_only = [e for e in entries if e not in documents]
            for position, entry in enumerate(documents):
                render_citation(entry, result, f"{index}_{position}", context)
            if context_only:  # ranking and curated metadata support the claim but are not documents to read
                with st.expander(f"Ranking and curated metadata used ({len(context_only)})"):
                    for position, entry in enumerate(context_only):
                        render_citation(entry, result, f"{index}_c{position}", context)
        if result.solutions:
            st.markdown("**Derived technologies (catalog)**")
            for s in result.solutions:
                label = "illustrative, not evidence" if s.status == "illustrative" else f"source: {s.source_file}"
                st.caption(f"{s.investigation_id}: {s.technology} ({label})")
    else:
        unavailable = narrator_failure_message(result.issues)
        if unavailable:
            st.badge("Language model unavailable", color="red", icon=":material/cloud_off:")
            st.error(unavailable)
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
    with st.expander("Run trace and retrieved passages (for debugging)"):
        for a in result.attempts:
            st.caption(f"Attempt {a.attempt}: top {a.settings.top_k}, minimum score {a.settings.min_score}, "
                       f"{a.passage_count} passages, {len(a.issues)} issues → {', '.join(a.shortlist_ids) or 'none'}")
            for p in a.passages:
                st.caption(f"retrieved {p.investigation_id} {p.source_file.rsplit('/', 1)[-1]} {p.locator}: "
                           f"{' '.join(p.text.split())[:140]}")
            if a.issues and a.draft is not None:
                st.caption("Rejected draft (not validated, not an answer):")
                st.json(a.draft.model_dump(mode="json"), expanded=False)


@st.fragment(run_every=0.5)
def _pending_answer() -> None:
    job = st.session_state.get(JOB_KEY)
    if job is None:
        return
    if not job.future.done():
        st.info("Preparing the copilot, ranking, retrieving passages and validating…", icon=":material/hourglass_top:")
        st.caption("Your submitted request continues while you edit the view. No second click is needed.")
        return
    try:
        completed = job.future.result()
    except Exception:  # noqa: BLE001 - do not expose provider errors, credentials or response bodies in the UI
        st.session_state["copilot_request_error"] = "The copilot request could not finish. Please try again. Any previous answer is preserved."
    else:
        st.session_state[RESULT_KEY] = completed.result
        st.session_state[LABEL_KEY] = completed.narrator_label
        st.session_state[REQUEST_KEY] = (job.scenario, job.question)
        st.session_state.pop("copilot_request_error", None)
    st.session_state.pop(JOB_KEY, None)
    # Commit first: the single full rerun updates chart highlights and enables submission without resending work.
    st.rerun()


def copilot(pipeline: PipelineHandle, investigations: tuple[Investigation, ...],
            context: EvidenceContext | None = None, quota: DailyQuota | None = None) -> None:
    quota = quota if quota is not None and quota.enabled else None
    context = context or EvidenceContext(None, frozenset())
    _scenario()
    question_step()
    with st.container(key="copilot_question_bubble"):
        st.text_area("Ask about this scenario", DEFAULT_QUESTION, height=110, key="copilot_question",
                                placeholder="Compare the studies at these oxygen and pressure conditions…",
                                help="Examples: how does oxygen change flame spread? Which fuels were tested near "
                                     "these conditions? The answer is limited to the curated records and report passages.")
    with st.container(horizontal=True, vertical_alignment="center", gap="small", key="copilot_mascot"):
        st.image(str(Path(__file__).parent / "assets/flamsa-copilot.svg"), width=76)
        with st.container(width="stretch"):
            st.markdown("**Let's explore the evidence.**")
            st.caption("Compare studies. Follow the sources.")
    st.button("Ask copilot", key="ask_copilot", icon=":material/auto_awesome:", type="primary", width="stretch",
                  disabled=JOB_KEY in st.session_state or (quota is not None and quota.remaining(visitor_key()) == 0),
                  on_click=_submit, args=(pipeline, investigations, quota),
                  help="Ranks investigations for these conditions, retrieves report passages and validates the text.")
    st.caption("Ranks all curated studies, including those outside the chart filters.")
    if quota is not None:
        of = f" of {quota.limit}" if quota.limit > 0 else ""
        st.caption(f"Questions left today: {quota.remaining(visitor_key())}{of}. The count is per visitor and resets "
                   "at 00:00 UTC and whenever the application is released again.")
    response_step(RESULT_KEY in st.session_state)
    with st.expander("How the copilot works"):
        st.write("The application computes the ranking scores. A connected language model or offline template "
                 "explains them using cited records and report passages. Answers must pass citation and number "
                 "checks; insufficient evidence can prevent an explanation from being shown.")
        st.caption("Check the source and review status of each claim. Automated checks do not establish scientific certainty.")
    if JOB_KEY in st.session_state:
        _pending_answer()
    if st.session_state.get("copilot_request_error"):
        st.error(st.session_state["copilot_request_error"])
    if RESULT_KEY in st.session_state:
        submitted = st.session_state.get(REQUEST_KEY)
        if submitted:
            answered_scenario, answered_question = submitted
            st.caption(f"Answer for {answered_scenario.o2_percent:g}% oxygen / {answered_scenario.pressure_psi:g} psi: "
                       f"{answered_question}")
        st.subheader("Answer & sources", anchor="copilot-response")
        _render(st.session_state[RESULT_KEY], st.session_state.get(LABEL_KEY, "Previously completed request"), context)
