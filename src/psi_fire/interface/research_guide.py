"""Optional, source-aware guidance for the Dashboard's three-step research journey."""

from time import monotonic

import streamlit as st

ATTENTION_SECONDS = 20


def track_workspace(current: str) -> None:
    if current != "Dashboard":
        st.session_state.pop("research_attention_started", None)


def _attention_style() -> None:
    started = st.session_state.setdefault("research_attention_started", monotonic())
    elapsed = min(ATTENTION_SECONDS, max(0, monotonic() - started))
    generation = st.session_state.get("research_attention_render", 0) + 1
    st.session_state["research_attention_render"] = generation
    # A new name seeks remounted elements to the shared deadline instead of granting another twenty seconds.
    css = """<style>
    @keyframes research-guide-beacon-GENERATION {
      0%,100% { box-shadow: 0 0 0 0 rgba(var(--guide-glow), 0), 0 4px 16px rgba(var(--guide-glow), .16); }
      50% { box-shadow: 0 0 0 7px rgba(var(--guide-glow), .18), 0 5px 28px rgba(var(--guide-glow), .42); }
    }
    @keyframes copilot-question-beacon-GENERATION {
      0%,100% { box-shadow: 0 0 0 0 #b56dff00, 0 6px 22px #5f2da040; }
      50% { box-shadow: 0 0 0 9px #b56dff40, 0 0 36px 12px #9a42ef78; }
    }
    [class*="st-key-guide_step_"] { animation: research-guide-beacon-GENERATION 2s ease-in-out 10;
      animation-delay: -ELAPSEDs; }
    .stApp:has(.st-key-research_guide_controls) .st-key-copilot_question_bubble {
      animation: copilot-question-beacon-GENERATION 2s ease-in-out 10; animation-delay: -ELAPSEDs; }
    </style>"""
    st.html(css.replace("GENERATION", str(generation)).replace("ELAPSED", f"{elapsed:.3f}"))


def _save_preference() -> None:
    st.session_state["research_guide_visible"] = st.session_state["research_guide_toggle"]


def guide_controls() -> None:
    _attention_style()
    st.session_state.setdefault("research_guide_visible", True)
    st.session_state.setdefault("research_guide_toggle", st.session_state["research_guide_visible"])
    with st.container(horizontal=True, vertical_alignment="center", key="research_guide_controls"):
        st.markdown("**From a condition to a cited answer**")
        st.toggle("Show the 3-step guide", key="research_guide_toggle", on_change=_save_preference,
                  help="Show short explanations beside the map, the question box and the response.")


def _enabled() -> bool:
    return (st.session_state.get("workspace_navigation") == "Dashboard"
            and st.session_state.get("research_guide_visible", True))


def map_step(copilot_visible: bool, *, map_available: bool) -> None:
    if not _enabled():
        return
    with st.container(border=True, key="guide_step_1"):
        st.markdown("**Step 1 · Choose your atmosphere on this map**")
        if not map_available:
            st.markdown("No coverage map is available for these filters. Adjust or reset **Research filters** "
                        "to show tests with both oxygen and pressure, or type conditions directly in Research copilot.")
        elif copilot_visible:
            st.markdown("Click the **oxygen and pressure coverage map** to fill the copilot's conditions. "
                        "The marker and its Oxygen and Pressure fields follow your selection. "
                        "You can also type exact values in the copilot.")
            st.markdown("[Continue to Research copilot ↓](#research-copilot)")
        else:
            st.markdown("Turn on **Research copilot** above, then click this coverage map to choose oxygen and "
                        "pressure for your question. Other comparison charts do not set the copilot's conditions.")


def question_step() -> None:
    if not _enabled():
        return
    _attention_style()
    with st.container(border=True, key="guide_step_2"):
        st.markdown("**Step 2 · Find research that answers your question**")
        st.markdown("Ask which NASA investigations fit your selected conditions, and why. Research copilot "
                    "explains the computed ranking using experimental records and **cited passages from PDF "
                    "reports**, so you can check the evidence instead of searching every report yourself.")


def response_step(available: bool) -> None:
    if not _enabled():
        return
    with st.container(border=True, key="guide_step_3"):
        st.markdown("**Step 3 · Read the answer and check its sources**")
        st.markdown("Your response appears below **Ask copilot**. "
                    "**Scroll down the page to read the complete answer and citations.**")
        st.markdown("For a document citation, choose **View source → Download the cited document** to save "
                    "the original NASA PDF or data file, when available. Computed ranking scores do not have "
                    "a source document to download.")
        if available:
            st.markdown("[Go to the answer and sources ↓](#copilot-response)")
