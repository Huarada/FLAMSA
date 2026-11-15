"""Reconcile comparison widget state with the committed research view."""

from hashlib import sha256

import streamlit as st

from psi_fire.application.explore import ExplorationQuery, Match


def widget_key(name: str, context: object) -> str:
    return f"{name}_widget_{sha256(repr(context).encode()).hexdigest()[:16]}"


def reconcile(matches: tuple[Match, ...]) -> tuple[list[str], list[str], object]:
    available = [m.investigation.id for m in matches]
    query = st.session_state.get("applied_query", ExplorationQuery())
    generation = st.session_state.get("filter_generation", 0)
    previous = st.session_state.get("chart_available_studies", available)
    selected = st.session_state.get("chart_investigations", available)
    reset = st.session_state.get("chart_filter_generation", generation) != generation
    retained = [i for i in selected if i in available]
    invalidated = bool(selected) and not retained
    if reset or set(selected) == set(previous) or invalidated:
        retained = available
    if invalidated and not reset:
        st.caption("The previous chart selection is outside the research results. "
                   "Comparison now includes all retained investigations.")
    st.session_state["chart_investigations"] = retained
    st.session_state["chart_available_studies"] = available
    st.session_state["chart_filter_generation"] = generation
    if reset:
        for name in ("chart_x", "chart_y", "chart_basis"):
            st.session_state.pop(name, None)
    bases = [b for b in ("ambient", "oxidizer_stream")
             if any(p.o2_basis is not None and p.o2_basis.value == b for m in matches for p in m.points)]
    required = query.basis.value if query.oxygen else (
        query.bases[0] if len(query.bases) == 1 and query.bases[0] in bases else None)
    basis_options = [required] if required else bases or ["ambient"]
    if st.session_state.get("chart_basis") not in basis_options:
        st.session_state["chart_basis"] = basis_options[0]
    return available, basis_options, (query, generation)


def quantity_choice(label: str, options: list[str], name: str, labels: dict[str, str],
                    context: object, preferred: str = "") -> str:
    """Separate the durable choice from a native widget with context-dependent labels."""
    selected = st.session_state.get(name)
    if selected not in options:
        selected = preferred if preferred in options else options[0] if options else None
    display = tuple(labels[k] for k in options)
    value = st.selectbox(label, options, index=options.index(selected) if selected is not None else None,
                         format_func=labels.get, disabled=not options,
                         key=widget_key(name, (context, tuple(options), display)))
    st.session_state[name] = value or ""
    return value or ""
