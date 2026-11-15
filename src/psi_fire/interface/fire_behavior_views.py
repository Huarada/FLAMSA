"""Experimental evidence cards; coefficients and exclusions come from application projections."""

import json
from dataclasses import asdict

import altair as alt
import pandas as pd
import streamlit as st

from psi_fire.application.explore import ExplorationQuery, Match
from psi_fire.application.fire_behavior import (
    BassEvidence,
    BehaviorDataError,
    BehaviorSettings,
    BuildFireBehavior,
    FlexEvidence,
    SaffireEvidence,
)
from psi_fire.domain.exploration import ConditionRange
from psi_fire.domain.units import ATM_TO_PSI
from psi_fire.interface.reference_dashboard import show_chart


def open_behavior_records(investigation_id: str) -> None:
    st.session_state["selected_investigation"] = investigation_id
    st.session_state["workspace_navigation"] = "Investigations"


def _range(values: tuple[float, float], unit: str) -> str:
    return f"{values[0]:.4g}–{values[1]:.4g} {unit}"


def _csv_download(frame: pd.DataFrame, study: str) -> None:
    st.download_button("Download analyzed records", frame.to_csv(index=False), file_name=f"{study.lower()}-behavior.csv",
                       mime="text/csv", key=f"behavior_csv_{study}", on_click="ignore")


def _record_action(study: str, available: bool) -> None:
    st.button(f"Open {study} source records", on_click=open_behavior_records, args=(study,), disabled=not available,
              key=f"behavior_open_{study}", icon=":material/arrow_forward:")


def _flex_card(evidence: FlexEvidence, settings: BehaviorSettings, analysis_id: str) -> None:
    with st.container(border=True, key="behavior_flex"):
        st.subheader("FLEX · Oxygen and droplet burning rate")
        st.write("How does the reported droplet burning-rate constant change with oxygen?")
        low = ATM_TO_PSI * (1 - settings.pressure_tolerance_fraction)
        high = ATM_TO_PSI * (1 + settings.pressure_tolerance_fraction)
        st.caption(f"{len(evidence.observations)} analyzed / {evidence.matched_records} research-filter records · "
                   f"{len(evidence.excluded)} excluded · Pressure band {low:.3f}–{high:.3f} psi")
        st.caption("K is a droplet burning-rate constant in mm²/s. It is not the burning speed of an entire fire.")
        if not evidence.matched_records:
            st.info("FLEX is outside the applied research filters. Include it above to see this analysis.")
        elif not evidence.observations:
            st.info("No reported scalar records meet these FLEX analysis settings.")
        else:
            estimated = [group for group in evidence.groups if group.estimate]
            if estimated:
                summary_columns = st.columns(min(2, len(estimated)))
                for index, group in enumerate(estimated):
                    fit = group.estimate
                    assert fit is not None
                    with summary_columns[index % len(summary_columns)], st.container(border=True):
                        st.metric(f"{group.fuel} · {group.diluent}", f"{fit.slope_mm2_s_per_o2_point:.5f}", help=group.label)
                        st.caption("Adjusted mm²/s per O₂ percentage point")
                        st.caption(f"95% model CI {fit.lower_slope:.5f}–{fit.upper_slope:.5f} · n={fit.observations}")
            rows = [{"kind": "observation", "Fuel": point.fuel, "Diluent": point.diluent, "Group": point.group,
                     "Oxygen": point.oxygen_percent, "K": point.k_mm2_s, "Lower": None, "Upper": None,
                     "Pressure (psi)": point.pressure_psi, "Diameter (mm)": point.diameter_mm,
                     "Record": point.reference.test_point_id, "Source row": point.reference.source_row}
                    for point in evidence.observations]
            for group in evidence.groups:
                if group.estimate:
                    for prediction in group.estimate.line:
                        rows.append({"kind": "fit", "Fuel": group.fuel, "Diluent": group.diluent, "Group": group.label,
                                     "Oxygen": prediction.oxygen_percent, "K": prediction.expected_k_mm2_s,
                                     "Lower": prediction.lower_k_mm2_s, "Upper": prediction.upper_k_mm2_s})
            base = alt.Chart(pd.DataFrame(rows)).encode(
                x=alt.X("Oxygen:Q", title="Ambient O₂ (%)", scale=alt.Scale(zero=False)),
                color=alt.Color("Diluent:N", scale=alt.Scale(domain=["N2", "CO2+N2", "He+N2"],
                                                           range=["#3563B9", "#00847F", "#879EAD"]),
                                legend=alt.Legend(orient="top")),
            )
            points = base.transform_filter(alt.datum.kind == "observation").mark_circle(size=42, opacity=.7).encode(
                y=alt.Y("K:Q", title="Reported K (mm²/s)"),
                tooltip=["Fuel:N", "Diluent:N", "Group:N", "Record:N", "Source row:N", "Pressure (psi):Q",
                         "Diameter (mm):Q", alt.Tooltip("Oxygen:Q", title="O₂ (%)"), alt.Tooltip("K:Q", title="K (mm²/s)")],
            )
            fits = base.transform_filter(alt.datum.kind == "fit")
            band = fits.mark_area(opacity=.13).encode(y="Lower:Q", y2="Upper:Q", detail="Group:N")
            lines = fits.mark_line(strokeWidth=2).encode(y="K:Q", detail="Group:N",
                                                        tooltip=["Group:N", "Oxygen:Q", "K:Q"])
            for fuel in sorted({point.fuel for point in evidence.observations}):
                st.markdown(f"**Fuel: {fuel}**")
                show_chart((band + lines + points).transform_filter(alt.datum.Fuel == fuel).properties(height=260))
            st.caption("Points are reported tests. Lines and shading are adjusted model means and their 95% model-based "
                       "intervals at group-mean pressure/diameter, only within the observed oxygen range. "
                       "Fuel and He/CO₂ blend fractions never mix between fits.")
            table = []
            for group in evidence.groups:
                fit = group.estimate
                table.append({"Stratum": group.label, "n": len(group.record_ids),
                              "O₂ range": _range(group.oxygen_range, "%"),
                              "Pressure range": _range(group.pressure_range, "psi"),
                              "Diameter range": _range(group.diameter_range, "mm"),
                              "Adjusted slope (mm²/s per O₂ point)": fit.slope_mm2_s_per_o2_point if fit else None,
                              "95% lower": fit.lower_slope if fit else None, "95% upper": fit.upper_slope if fit else None,
                              "Raw Spearman rho": fit.raw_spearman_rho if fit else None,
                              "Fit status": "Estimated" if fit else group.unavailable_reason})
            with st.expander("Slopes, tested ranges and groups without an identifiable fit"):
                st.dataframe(pd.DataFrame(table), hide_index=True)
                fits_by_label = {group.label: group for group in evidence.groups if group.estimate}
                if fits_by_label:
                    label = st.selectbox("Inspect fitted stratum", list(fits_by_label), key="behavior_fit_inspection")
                    group = fits_by_label[label]
                    fit = group.estimate
                    assert fit is not None
                    st.code(f"Analysis {analysis_id}\nFLEX | {label} | n={fit.observations}\n"
                            f"Adjusted O2 slope: {fit.slope_mm2_s_per_o2_point:.8g} mm²/s per percentage point\n"
                            f"95% model CI: [{fit.lower_slope:.8g}, {fit.upper_slope:.8g}]\n"
                            f"O2: {_range(group.oxygen_range, '%')}; pressure: {_range(group.pressure_range, 'psi')}; "
                            f"initial diameter: {_range(group.diameter_range, 'mm')}\n"
                            f"Reference means: {dict(fit.reference_conditions)}\n"
                            f"Adjustment covariates: {', '.join(fit.adjusted_covariates) or 'constant within group'}\n"
                            f"Records: {', '.join(group.record_ids)}", language=None, wrap_lines=True)
            frame = pd.DataFrame([{**asdict(point), **asdict(point.reference)} for point in evidence.observations])
            frame = frame.drop(columns="reference")
            with st.expander("FLEX analyzed records and provenance"):
                st.dataframe(frame, hide_index=True)
                _csv_download(frame, "FLEX")
        st.warning("These conditional associations do not establish a universal law or a fire-safety limit. "
                   "Intervals assume independent, homoskedastic, approximately normal errors; calibration error, "
                   "model-form uncertainty and unreported conditions are not resolved. "
                   "Do not transfer near-1-atm slopes to lower pressure, other blends or lunar gravity.")
        st.markdown("**FLEX at lunar-habitat conditions (not part of the fit)**")
        st.write(f"FLEX tests with O₂ ≥30% and pressure ≤10.2 psi: **{len(evidence.strict_scenario_records)}**. "
                 "The archive's tests in that range are ACME-CFI-G gas flames; the Dashboard coverage map shows them.")
        comparison = evidence.comparison_pressure_range
        st.caption(f"For the separately labelled ≤10.5 psi comparison: {len(evidence.comparison_records)} tests"
                   + (f", reported pressures {_range(comparison, 'psi')}." if comparison else ".")
                   + " Counts use the applied research filters and exact stored bounds, not rounded labels.")
        _record_action("FLEX", bool(evidence.matched_records))


def _bass_card(evidence: BassEvidence) -> None:
    with st.container(border=True, key="behavior_bass"):
        st.subheader("BASS-II · Oxygen decrease and CO₂ increase")
        st.write("How do reported gas concentrations change during the same burn?")
        st.caption(f"{len(evidence.observations)} complete pairs / {evidence.matched_records} research-filter records · "
                   f"{len(evidence.excluded)} excluded")
        if evidence.observations:
            frame = pd.DataFrame([{**asdict(point), **asdict(point.reference),
                                   "Material": point.fuel or "Not reported",
                                   "Quality": "Negative difference; inspect measurements" if point.negative_change
                                   else "Nonnegative differences"} for point in evidence.observations]).drop(columns="reference")
            zero = alt.Chart(pd.DataFrame({"zero": [0]}))
            points = alt.Chart(frame).mark_point(filled=True, size=48, opacity=.7).encode(
                x=alt.X("oxygen_consumed_points:Q", title="Initial − final O₂ (percentage points)"),
                y=alt.Y("co2_increase_points:Q", title="Final − initial CO₂ (percentage points)"),
                color=alt.Color("Material:N", legend=alt.Legend(orient="top", columns=2)),
                shape=alt.Shape("Quality:N", legend=alt.Legend(orient="bottom", labelLimit=280, title=None)),
                tooltip=["test_point_id:N", "source_row:N", "Material:N", "Quality:N", "oxygen_initial_percent:Q",
                         "oxygen_final_percent:Q", "co2_initial_percent:Q", "co2_final_percent:Q",
                         "oxygen_consumed_points:Q", "co2_increase_points:Q"],
            )
            show_chart((zero.mark_rule(color="#B7C5D4").encode(x="zero:Q")
                        + zero.mark_rule(color="#B7C5D4").encode(y="zero:Q") + points).properties(height=330))
            negatives = sum(point.negative_change for point in evidence.observations)
            st.caption(f"{negatives} pairs contain a negative measured difference and remain visible. "
                       "Values are signed differences, without clamping or imputation.")
            with st.expander("BASS-II measured differences and provenance"):
                st.dataframe(frame, hide_index=True)
                _csv_download(frame, "BASS-II")
        else:
            st.info("No complete BASS-II concentration pairs remain in the applied research filters.")
        st.caption("These are concentration changes in percentage points, not CO₂ mass, emitted volume or a calibrated "
                   "emission yield. No cabin-exposure or detector-performance limit is inferred.")
        _record_action("BASS-II", bool(evidence.matched_records))


def _saffire_card(evidence: SaffireEvidence) -> None:
    with st.container(border=True, key="behavior_saffire"):
        st.subheader("SAFFIRE-II · Microgravity versus 1 g")
        st.write("Does the reported 1 g screening outcome agree with the microgravity sample outcome?")
        st.caption(f"{len(evidence.observations)} paired sample rows / {evidence.matched_records} research-filter records · "
                   f"{len(evidence.excluded)} excluded")
        if evidence.observations:
            cells = []
            for point in evidence.observations:
                label = point.reference.test_point_id
                for condition, raw, state in (("Microgravity", point.microgravity_length_raw, point.microgravity_length_state),
                                               ("1 g", point.normal_gravity_length_raw, point.normal_gravity_length_state)):
                    cells.append({"Sample": label, "Condition": condition, "Raw burned length": raw or "Not reported",
                                  "Outcome": state, "Record": point.reference.test_point_id,
                                  "Material": point.fuel or "Not reported",
                                  "Source row": point.reference.source_row})
            base = alt.Chart(pd.DataFrame(cells)).encode(
                x=alt.X("Condition:N", sort=["Microgravity", "1 g"], title=None,
                        axis=alt.Axis(orient="top", labelAngle=0)),
                y=alt.Y("Sample:N", sort=None, title=None),
            )
            rectangles = base.mark_rect(cornerRadius=5, stroke="white", strokeWidth=3).encode(
                color=alt.Color("Outcome:N", scale=alt.Scale(
                    domain=["Approximately zero", "Zero length reported", "Numeric length; inspect qualifiers",
                            "Complete (source label)", "Mixed / see source note", "Not reported"],
                    range=["#DCE7F3", "#DCE7F3", "#AFC8E8", "#EED6A6", "#D5D0E4", "#F0F3F6"]),
                    legend=alt.Legend(orient="bottom", columns=1, labelLimit=300)),
                tooltip=["Sample:N", "Material:N", "Condition:N", "Raw burned length:N", "Outcome:N", "Source row:N"],
            )
            text = base.mark_text(fontSize=11, color="#203747").encode(text="Raw burned length:N")
            show_chart((rectangles + text).properties(height=max(150, 38 * len(evidence.observations))))
            table = pd.DataFrame([{"Sample": point.reference.test_point_id, "Material": point.fuel or "Not reported",
                                   "Thickness (source)": point.thickness_raw or "Not reported",
                                   "O₂ (source)": point.oxygen_raw or "Not reported", "Flow (source)": point.flow_raw,
                                   "Flow direction": point.flow_direction,
                                   "Microgravity length (source)": point.microgravity_length_raw or "Not reported",
                                   "1 g length (source)": point.normal_gravity_length_raw or "Not reported",
                                   "Microgravity spread rate (source)": point.microgravity_rate_raw or "Not reported",
                                   "1 g spread rate (source)": point.normal_gravity_rate_raw or "Not reported",
                                   **asdict(point.reference)} for point in evidence.observations])
            primary = ["Sample", "Material", "Thickness (source)", "Microgravity length (source)", "1 g length (source)",
                       "Microgravity spread rate (source)", "1 g spread rate (source)"]
            st.dataframe(table[primary], hide_index=True)
            table["microgravity_length_mm"] = [point.microgravity_length_mm for point in evidence.observations]
            table["normal_gravity_length_mm"] = [point.normal_gravity_length_mm for point in evidence.observations]
            table["microgravity_spread_rate_cm_s"] = [point.microgravity_rate_cm_s for point in evidence.observations]
            table["normal_gravity_spread_rate_cm_s"] = [point.normal_gravity_rate_cm_s for point in evidence.observations]
            with st.expander("SAFFIRE-II numeric fields, conditions and provenance"):
                st.dataframe(table, hide_index=True)
            _csv_download(table, "SAFFIRE-II")
        else:
            st.info("SAFFIRE-II has no matching sample rows in the applied research filters.")
        st.caption("Complete and Acceleratory remain source labels, not invented numeric lengths or rates. "
                   "Approximately zero is retained as reported; missing spread rate is not replaced with zero. "
                   "Material, thickness, atmosphere and flow differ between samples. These paired outcomes do not "
                   "establish a universal 1 g-to-orbit conversion or direct lunar-gravity behavior.")
        _record_action("SAFFIRE-II", bool(evidence.matched_records))


def fire_behavior(matches: tuple[Match, ...], revision: str, query: ExplorationQuery) -> dict[str, object]:
    st.caption("Experimental associations with traceable records. The applied research filters govern every card.")
    flex = next((match for match in matches if match.investigation.id == "FLEX"), None)
    fuels = sorted({point.fuel_name for point in flex.points if point.fuel_name}) if flex else []
    with st.expander("FLEX analysis settings · local to this section"):
        controls = st.columns(3)
        selected_fuels = controls[0].multiselect("FLEX fuels (empty = all matching)", fuels, default=fuels,
                                                key="behavior_fuels")
        tolerance = controls[1].selectbox("Near-1-atm pressure tolerance (%)", [5, 2, 1], key="behavior_pressure_tolerance")
        diameter_options = {"All reported diameters; adjusted in model": None, "1–2 mm": ConditionRange(1, 2),
                            "2–3 mm": ConditionRange(2, 3), "3–4 mm": ConditionRange(3, 4)}
        diameter = controls[2].selectbox("Initial diameter scope", list(diameter_options), key="behavior_diameter_scope")
        st.caption("Fits separate fuel and fixed He/CO₂ fractions; pressure and initial diameter are adjustment covariates. "
                   "Other unreported conditions are not established as controlled. Settings do not change research filters.")
    settings = BehaviorSettings(tuple(selected_fuels), tolerance / 100, diameter_options[diameter])
    try:
        report = BuildFireBehavior()(revision, matches, settings)
    except BehaviorDataError as error:
        st.error(f"Fire-behavior analysis unavailable: {error}")
        return {}
    st.caption(f"Dataset {revision[:12]} / Analysis {report.analysis_id[:12]} / {report.policy_version}")
    payload = {**asdict(report), "applied_filters": asdict(query)}
    st.download_button("Download analysis JSON", json.dumps(payload, indent=2, allow_nan=False),
                       file_name=f"fire-behavior-{report.analysis_id[:12]}.json", mime="application/json",
                       key="behavior_json", on_click="ignore")
    flex_tab, bass_tab, saffire_tab = st.tabs(["FLEX · Burning rate", "BASS-II · Gas changes", "SAFFIRE-II · Gravity"])
    with flex_tab:
        _flex_card(report.flex, settings, report.analysis_id)
    with bass_tab:
        _bass_card(report.bass)
    with saffire_tab:
        _saffire_card(report.saffire)
    with st.expander("Methods, source columns and excluded records"):
        st.write("OLS estimates use centered/scaled predictors, an intercept, and pressure/diameter covariates when they "
                 "vary. Slope and mean-response intervals use Student's t with n minus the fitted parameter count degrees "
                 "of freedom. Spearman rho describes the raw within-stratum pairs, not the adjusted effect.")
        st.link_button("Least-squares methodology · NIST", "https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm")
        st.link_button("Student-t interval reference · SciPy", "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html")
        for source in report.sources:
            st.markdown(f"**{source.investigation_id}**")
            for path, digest in source.source_files:
                st.caption(f"{path} / SHA-256 {digest}")
            st.dataframe(pd.DataFrame([{"Field": key, "Canonical unit": unit, "Original headers": ", ".join(headers)}
                                       for key, unit, headers in source.columns]), hide_index=True)
        exclusions = [*report.flex.excluded, *report.bass.excluded, *report.saffire.excluded]
        if exclusions:
            st.dataframe(pd.DataFrame([{**asdict(item.reference), "Exclusion reason": item.reason}
                                       for item in exclusions]), hide_index=True)
    return {"analysis_id": report.analysis_id, "policy": report.policy_version,
            "flex_records": len(report.flex.observations), "bass_records": len(report.bass.observations),
            "saffire_records": len(report.saffire.observations),
            "slopes": [{"stratum": group.label, **asdict(group.estimate)} for group in report.flex.groups if group.estimate]}
