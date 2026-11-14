"""Native Streamlit presentation for the read-only research explorer."""

from collections import Counter
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from psi_fire.application.evidence import InvestigationSources
from psi_fire.application.explore import (
    DatasetError,
    ExplorationQuery,
    Match,
    coverage,
    review_state,
)
from psi_fire.domain.exploration import ConditionRange
from psi_fire.domain.manual import Claim
from psi_fire.domain.model import O2Basis


def filters(options: dict[str, tuple[str, ...]]) -> None:
    generation = st.session_state.get("filter_generation", 0)
    prefix = f"filters_{generation}_"
    query = st.session_state["applied_query"]
    defaults = {name: getattr(query, name) for name in (
        "search", "ids", "levels", "phases", "fuels", "directions", "lineage", "review", "note",
        "hardware", "sensors", "pillars", "gravity", "bases",
    )}
    defaults["basis"] = query.basis.value
    for condition, enabled, low, high, missing in (
        (query.oxygen, "oxygen_enabled", "ol", "ou", "om"),
        (query.pressure, "pe", "pl", "pu", "pm"), (query.flow, "fe", "fl", "fu", "fm"),
    ):
        defaults.update({enabled: condition is not None, low: condition.lower if condition else None,
                         high: condition.upper if condition else None, missing: bool(condition and condition.include_missing)})
    # Home hides these widgets; reconstruct them from the committed query when they return.
    for name, value in defaults.items():
        st.session_state.setdefault(prefix + name, list(value) if isinstance(value, tuple) else value)
    with st.container(border=True, key="filter_panel"):
        heading, reset = st.columns([5, 1])
        heading.markdown("**Research filters**")
        heading.caption("Conditions must match the same record. Ranges describe reported coverage.")
        heading.caption("Changes take effect after Apply filters. Choices within a filter use OR; different filters use AND.")
        if reset.button("Reset filters", type="tertiary", width="stretch"):
            st.session_state["applied_query"] = ExplorationQuery()
            st.session_state["filter_generation"] = generation + 1
            st.session_state.pop("filter_error", None)
            for key in ("selected_investigation", "selected_record", "extra_columns", "show_all"):
                st.session_state.pop(key, None)
            st.rerun()
        with st.form(prefix + "form"):
            top = st.columns([1.6, 1, 1, 1])
            search = top[0].text_input("Search investigations", placeholder="ID, title or objective", key=prefix + "search")
            ids = top[1].multiselect("Investigation", options["ids"], placeholder="All investigations", key=prefix + "ids")
            levels = top[2].multiselect("Record level", options["record_level"], placeholder="All record levels", key=prefix + "levels")
            phases = top[3].multiselect("Fuel phase", options["fuel_phase"], placeholder="All phases", key=prefix + "phases")
            conditions, metadata = st.columns(2)
            with conditions.expander("Experimental conditions"):
                fuels = st.multiselect("Fuel / material", options["fuel_name"], key=prefix + "fuels")
                directions = st.multiselect("Flow direction", options["flow_direction"], key=prefix + "directions")
                bases = st.multiselect("Reported oxygen basis", options["o2_basis"], key=prefix + "bases")
                basis = st.selectbox("Oxygen measurement basis", ["ambient", "oxidizer_stream"], index=None,
                                     key=prefix + "basis")
                st.caption("Reported oxygen basis filters records without numeric bounds. For an oxygen range, "
                           "choose its single measurement basis; clear or align the reported-basis selection.")
                # Bounds are built after submission so a draft invalid range does not replace results.
                oxygen_enabled = st.checkbox("Filter oxygen", key=prefix + "oxygen_enabled")
                ol = st.number_input("Oxygen minimum (%)", min_value=0.0, max_value=100.0,
                                     value=None, key=prefix + "ol")
                ou = st.number_input("Oxygen maximum (%)", min_value=0.0, max_value=100.0,
                                     value=None, key=prefix + "ou")
                om = st.checkbox("Include unreported oxygen", key=prefix + "om")
                pressure_enabled = st.checkbox("Filter pressure", key=prefix + "pe")
                pl = st.number_input("Pressure minimum (psi)", min_value=0.0, value=None, key=prefix + "pl")
                pu = st.number_input("Pressure maximum (psi)", min_value=0.0, value=None, key=prefix + "pu")
                pm = st.checkbox("Include unreported pressure", key=prefix + "pm")
                flow_enabled = st.checkbox("Filter flow speed", key=prefix + "fe")
                fl = st.number_input("Flow minimum (cm/s)", min_value=0.0, value=None, key=prefix + "fl")
                fu = st.number_input("Flow maximum (cm/s)", min_value=0.0, value=None, key=prefix + "fu")
                fm = st.checkbox("Include unreported flow", key=prefix + "fm")
            with metadata.expander("Evidence and metadata"):
                review = st.selectbox("Manual review", ["all", "draft", "reviewed", "unavailable"],
                                      index=None, key=prefix + "review")
                lineage = st.multiselect("Row lineage", options["provenance_status"], key=prefix + "lineage")
                note = st.selectbox("Curation notes", ["any", "with note", "without note"], index=None, key=prefix + "note")
                hardware = st.multiselect("Hardware", options["hardware"], key=prefix + "hardware")
                sensors = st.multiselect("Sensor", options["sensors"], key=prefix + "sensors")
                pillars = st.multiselect("Fire-safety pillar", options["pillars"], key=prefix + "pillars")
                gravity = st.multiselect("Gravity regime", options["gravity_regime"], key=prefix + "gravity")
            _, action = st.columns([4, 1])
            submitted = action.form_submit_button("Apply filters", type="primary", width="stretch")
        if submitted:
            try:
                st.session_state["candidate_query"] = ExplorationQuery(
                    search=search, ids=tuple(ids), levels=tuple(levels), phases=tuple(phases), fuels=tuple(fuels),
                    directions=tuple(directions), lineage=tuple(lineage), review=review, hardware=tuple(hardware),
                    sensors=tuple(sensors), pillars=tuple(pillars), gravity=tuple(gravity), note=note,
                    oxygen=ConditionRange(ol, ou, om) if oxygen_enabled else None, basis=O2Basis(basis),
                    pressure=ConditionRange(pl, pu, pm) if pressure_enabled else None,
                    flow=ConditionRange(fl, fu, fm) if flow_enabled else None, bases=tuple(bases),
                )
            except ValueError as error:
                st.session_state["filter_error"] = str(error)


def applied_filter_summary(query: ExplorationQuery, matches: tuple[Match, ...]) -> None:
    labels = (("Investigation", query.ids), ("Record level", query.levels), ("Fuel phase", query.phases),
              ("Fuel / material", query.fuels), ("Flow direction", query.directions), ("Row lineage", query.lineage),
              ("Hardware", query.hardware), ("Sensor", query.sensors), ("Fire-safety pillar", query.pillars),
              ("Gravity regime", query.gravity))
    active = [f"{label}: {', '.join(values)}" for label, values in labels if values]
    if query.search.strip():
        active.append(f"Search: {query.search.strip()}")
    if query.review != "all":
        active.append(f"Manual review: {query.review}")
    if query.note != "any":
        active.append(f"Curation notes: {query.note}")
    if query.bases and not query.oxygen:
        active.append("Reported oxygen basis: " + ", ".join(query.bases))
    for label, condition, unit in (("Oxygen", query.oxygen, "%"), ("Pressure", query.pressure, "psi"),
                                    ("Flow speed", query.flow, "cm/s")):
        if condition:
            bounds = [text for text in (
                f">= {condition.lower:g}" if condition.lower is not None else "",
                f"<= {condition.upper:g}" if condition.upper is not None else "",
            ) if text]
            active.append(f"{label}: {' and '.join(bounds)} {unit}"
                          + (f" ({query.basis.value})" if label == "Oxygen" else "")
                          + (", including unreported" if condition.include_missing else ""))
    st.caption("Applied filters · " + (" · ".join(active) or "All records; no restrictions"))
    points = tuple(point for match in matches for point in match.points)
    missing = []
    for label, field, condition in (("oxygen", "o2_percent", query.oxygen),
                                     ("pressure", "pressure_psi", query.pressure),
                                     ("flow speed", "flow_speed_cm_s", query.flow)):
        if condition and condition.include_missing:
            missing.append(f"{coverage(points, field)['missing']} without reported {label}")
    if missing:
        st.caption("Retained by the include-unreported policy: " + "; ".join(missing)
                   + ". These records do not provide measured support for the requested condition.")


def interval_text(summary: dict[str, object]) -> str:
    if summary["min"] is None:
        return "Not reported" if summary["eligible"] else "Not applicable"
    return f"{summary['min']:.5g}–{summary['max']:.5g} ({summary['reported']}/{summary['eligible']})"


def catalog(matches: tuple[Match, ...]) -> pd.DataFrame:
    return pd.DataFrame([{
        "Investigation": m.investigation.id,
        "PSI id": m.investigation.psi_id,
        "Record level": m.investigation.record_level.value,
        "Matching records": len(m.points),
        "Total records": len(m.investigation.test_points),
        "Ambient O₂ (%)": interval_text(coverage(m.points, "o2_percent", O2Basis.AMBIENT)),
        "Oxidizer O₂ (%)": interval_text(coverage(m.points, "o2_percent", O2Basis.OXIDIZER_STREAM)),
        "Pressure (psi)": interval_text(coverage(m.points, "pressure_psi")),
        "Manual review": review_state(m.investigation),
    } for m in matches])


def dashboard(matches: tuple[Match, ...], total: int) -> None:
    points = tuple(p for m in matches for p in m.points)
    levels = Counter(p.record_level.value for p in points)
    with st.container(horizontal=True):
        st.metric("Investigations", f"{len(matches)} / {total}")
        st.metric("Individual test records", f"{levels['test']:,}")
        st.metric("Test-day summaries", f"{levels['test_day']:,}")
        st.metric("Test-matrix records", f"{levels['test_matrix']:,}")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("#### Record coverage by investigation")
        data = pd.DataFrame([{"Investigation": m.investigation.id, "Records": len(m.points),
                              "Record level": m.investigation.record_level.value} for m in matches])
        st.bar_chart(data, x="Investigation", y="Records", color="Record level", horizontal=True, height=310)
        st.caption("Record count describes data volume, not relevance or effective sample size.")
    with right:
        st.markdown("#### Reported experimental conditions")
        data = []
        for label, field, basis in (("Ambient O₂", "o2_percent", O2Basis.AMBIENT),
                                    ("Oxidizer O₂", "o2_percent", O2Basis.OXIDIZER_STREAM),
                                    ("Pressure", "pressure_psi", None), ("Flow speed", "flow_speed_cm_s", None)):
            value = coverage(points, field, basis)
            data.append({"Condition": label, "Reported": value["reported"], "Not reported": value["missing"]})
        st.bar_chart(pd.DataFrame(data), x="Condition", y=["Reported", "Not reported"],
                     horizontal=True, stack=True, height=310)
        unknown = sum(p.o2_basis is None for p in points)
        st.caption(f"Matching records only. O₂ counts use each stated basis; {unknown} records have unknown basis.")


def claim_view(label: str, claim: Claim) -> None:  # type: ignore[type-arg]
    with st.expander(f"{label} · {claim.status.value}"):
        if claim.value is None:
            st.write("Not reported")
        elif hasattr(claim.value, "instrument"):
            st.write(claim.value.instrument)
            st.caption("Measures: " + (claim.value.measures or "Not stated"))
        else:
            st.write(claim.model_dump(mode="json")["value"])
        if claim.note:
            st.write(claim.note)
        for evidence in claim.evidence:
            st.caption(f"{evidence.source_file} · {evidence.locator}")
            st.code(evidence.quote, language=None, wrap_lines=True)
            if evidence.source_url and urlparse(evidence.source_url).scheme in {"http", "https"}:
                st.link_button("Original online source", evidence.source_url)


def detail(match: Match, sources: InvestigationSources, default_tab: str | None = None) -> None:
    inv = match.investigation
    st.divider()
    st.caption(f"INVESTIGATION / {inv.psi_id}")
    st.subheader(inv.id)
    st.write(inv.study_metadata.get("study_title", ""))
    st.caption(f"{inv.record_level.value} · {len(match.points)} matching / {len(inv.test_points)} total records")
    st.caption("Use the tabs below: study context and instruments; experimental rows and original values; "
               "or the documents cited by this investigation.")
    tabs = st.tabs(["Research & scientific context", "Experimental records & raw values", "Citations & source downloads"],
                   default=default_tab)
    with tabs[0]:
        left, right = st.columns([1.6, 1])
        with left:
            st.markdown("#### Research objective")
            st.write(inv.study_metadata.get("objective", "Objective not reported in the curated study metadata."))
            if inv.study_metadata_source:
                st.caption(f"Extracted study metadata · {inv.study_metadata_source} · Comment[Objective]")
            with st.expander("Experimental approach"):
                st.write(inv.study_metadata.get("approach", "Not reported"))
            st.markdown("#### Variables across the full investigation")
            st.write("**Varied:** " + (", ".join(inv.varied_variables) or "None reported"))
            st.write("**Held constant:** " + (", ".join(inv.held_constant_variables) or "None reported"))
            st.write("**Unreported:** " + (", ".join(inv.unreported_variables) or "None"))
            with st.expander(f"Source notes ({len(inv.source_notes)})"):
                for note in inv.source_notes:
                    st.caption(f"{note.source_file} · row {note.source_row}")
                    st.text(note.text)
        with right:
            st.markdown("#### Scientific context")
            manual = inv.manual_metadata
            if manual is None:
                st.info("Manual metadata unavailable. Hardware, sensors and gravity have not been mapped here.")
            else:
                if manual.review_status.value == "draft":
                    st.warning("Draft metadata · not yet human-reviewed")
                else:
                    st.success(f"Reviewed by {manual.reviewed_by} · {manual.reviewed_on}")
                claim_view("Hardware", manual.hardware)
                claim_view("Gravity regime", manual.gravity_regime)
                claim_view("Fire-safety pillars", manual.pillars)
                if manual.nominal_atmosphere:
                    claim_view("Nominal atmosphere (not per-test measurements)", manual.nominal_atmosphere)
                for index, sensor in enumerate(manual.sensors, 1):
                    claim_view(f"Sensor {index}", sensor)
                for index, application in enumerate(manual.earth_applications, 1):
                    claim_view(f"Earth application {index}", application)
    with tabs[1]:
        all_records = st.toggle("Show all records in this investigation", key="show_all")
        points = inv.test_points if all_records else match.points
        st.caption("Full investigation" if all_records else "Records matching applied filters")
        base = ["test_point_id", "record_level", "fuel_name", "fuel_phase", "o2_basis",
                "o2_percent_min", "o2_percent_max", "pressure_psi_min", "pressure_psi_max",
                "flow_speed_cm_s_min", "flow_speed_cm_s_max", "flow_direction", "provenance_status"]
        extra_options = [c for c in inv.columns if c not in base]
        extra = st.multiselect("Additional columns", extra_options, key=f"columns_{inv.id}")
        frame = pd.DataFrame([{c: p.value(c) for c in base + extra} for p in points])
        st.dataframe(frame, hide_index=True, height=330)
        st.caption("Units are encoded in column names. Empty numeric cells mean not reported; ranges may contain gaps.")
        record_id = st.selectbox("Inspect a record", [p.test_point_id for p in points], key=f"record_{inv.id}")
        point = next(p for p in points if p.test_point_id == record_id)
        with st.container(border=True):
            st.markdown(f"**{point.test_point_id}** · {point.provenance_status.value}")
            st.caption(f"{point.source_file} · source row(s) {point.source_row}")
            if point.provenance_note:
                st.info(point.provenance_note)
            st.json(point.model_dump(mode="json"), expanded=False)
        with st.expander("Column definitions and transformations"):
            st.dataframe(pd.DataFrame([{"Column": name, "Kind": info.kind,
                                        "Unit": info.unit.value if info.unit else "",
                                        "Original headers": ", ".join(info.source_headers),
                                        "Derivation": info.derivation or ""}
                                       for name, info in inv.columns.items()]), hide_index=True)
    with tabs[2]:
        st.write("Download the cited source and use its row, page or paragraph locator to review the evidence.")
        try:
            entries = sources(inv.id)
            if not entries:
                st.info("No registered sources available.")
                return
            labels = {s["handle"]: f"{s['path'].rsplit('/', 1)[-1]} · {s['label']}" for s in entries}
            handle = st.selectbox("Source document", list(labels), format_func=labels.get, key=f"source_{inv.id}")
            source = next(s for s in entries if s["handle"] == handle)
            st.caption(source["path"])
            st.write(source["locator"] or "Use the claim or record locator shown in the inspector.")
            st.caption("Checksum pinned" if source["digest"] else "Version unpinned · source path retained")
            if st.button("Prepare source download", key=f"prepare_{inv.id}_{handle}"):
                content, name, media = sources.read(inv.id, handle)
                st.download_button("Download source", content, file_name=name, mime=media,
                                   key=f"download_{handle}", on_click="ignore")
        except (DatasetError, OSError, ValueError) as error:
            st.warning(str(error) if isinstance(error, DatasetError) else "Source metadata unavailable.")
