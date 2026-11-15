"""Reference-led chart grid using reported data and existing application projections."""

from collections import Counter

import altair as alt
import pandas as pd
import streamlit as st

from psi_fire.application.chart_data import (
    LUNAR_OXYGEN_MIN,
    LUNAR_PRESSURE_MAX,
    BuildChartData,
    InvestigationPlotCoverage,
    PlotExclusion,
    condition_map,
)
from psi_fire.application.explore import Match
from psi_fire.domain.model import O2Basis


def show_chart(chart: alt.Chart | alt.LayerChart) -> None:
    chart = chart.configure(background="transparent", font="sans-serif").configure_view(stroke=None).configure_axis(
        gridColor="#DFE7F0", domainColor="#CFDBE6", labelColor="#526E83", titleColor="#526E83",
        labelFontSize=10, titleFontSize=11, titleFontWeight="normal",
    ).configure_range(category=["#00847F", "#6788D4", "#8DBFBA", "#879EAD", "#C58B36"])
    st.altair_chart(chart, theme=None, width="stretch")


def metrics(matches: tuple[Match, ...], total: int) -> None:
    points = [p for match in matches for p in match.points]
    conditions = condition_map(matches)
    values = [
        ("Investigations", f"{len(matches)} / {total}",
         "PSI studies with records that pass the filters / all studies loaded",
         ("An investigation is one PSI study, such as FLEX or SAFFIRE-II. The first number counts studies with at "
          "least one record that passes the filters above; the second counts every study loaded from data/curated.")),
        ("Reported records", f"{len(points):,}",
         f"{conditions.tests:,} individual tests + {conditions.summaries} daily or matrix summaries",
         ("A record is one row of a curated test_points.csv. Most rows are single tests. ACME-BRE, ACME-E-FIELD and "
          "SLICE report one row per test day, and FLEX-2 lists its planned test matrix. A record is not necessarily "
          "an independent ignition, and a larger count does not make a study more relevant.")),
        ("Tests with O₂ and pressure", f"{len(conditions.rows):,}",
         f"of {conditions.tests:,} individual tests · the dots in the coverage map",
         ("Individual tests that report one O₂ value and one pressure value. Ranges are not reduced to a midpoint "
          "and missing values are not filled in. Most PSI tables report only one of the two, or neither.")),
        ("Lunar-scenario tests", f"{conditions.scenario_ambient}",
         (f"≥{LUNAR_OXYGEN_MIN:g}% O₂ in the chamber, ≤{LUNAR_PRESSURE_MAX:g} psi · "
          f"+{conditions.scenario_stream} with O₂ in the burner stream"),
         (f"Demonstration scenario for a lunar habitat: at least {LUNAR_OXYGEN_MIN:g}% O₂ at or below "
          f"{LUNAR_PRESSURE_MAX:g} psi. The main number counts tests whose O₂ describes the chamber atmosphere. "
          "Inverse flames report the O₂ of the gas leaving the burner instead, so they are counted separately. "
          "All of these are microgravity tests; the PSI has no partial-gravity data.")),
    ]
    columns = st.columns(4)
    for index, (label, value, caption, explanation) in enumerate(values):
        with columns[index], st.container(border=True, key=f"kpi_{index}"):
            st.metric(label, value, help=explanation)
            st.caption(caption)


def filtered_records_csv(matches: tuple[Match, ...]) -> str:
    """Every filtered record with all curated columns, raw values and provenance (same columns as data/curated)."""
    rows = []
    for match in matches:
        for point in match.points:
            data = point.model_dump(mode="json")
            rows.append({**data, **data.pop("extras")})
    return pd.DataFrame(rows).to_csv(index=False)


def coverage_map(matches: tuple[Match, ...]) -> None:
    conditions = condition_map(matches)
    with st.container(border=True, key="coverage_card"):
        st.markdown("#### Experimental coverage · oxygen and pressure")
        st.caption(f"Each dot is one test that reports both values. The shaded box is the lunar-habitat scenario used "
                   f"in this project: at least {LUNAR_OXYGEN_MIN:g}% O₂ at or below {LUNAR_PRESSURE_MAX:g} psi.")
        if conditions.rows:
            frame = pd.DataFrame(conditions.rows)
            right = max(float(frame["O2"].max()), LUNAR_OXYGEN_MIN) + 3
            box = alt.Chart(pd.DataFrame([{"x": LUNAR_OXYGEN_MIN, "x2": right, "y": 0.0, "y2": LUNAR_PRESSURE_MAX}]))
            oxygen_axis = alt.Scale(domain=[10, right], nice=False)  # no test reports less than ~12% O2
            scenario = box.mark_rect(color="#F2B33D", opacity=.18, stroke="#C58B36", strokeDash=[5, 4]).encode(
                x=alt.X("x:Q", scale=oxygen_axis), x2="x2:Q", y="y:Q", y2="y2:Q")
            label = box.mark_text(align="left", baseline="bottom", dx=6, dy=-6, color="#8A5A12", fontWeight=600).encode(
                x=alt.X("x:Q", scale=oxygen_axis), y="y2:Q", text=alt.value("Lunar habitat scenario"))
            dots = alt.Chart(frame).mark_point(filled=True, size=52, opacity=.62, stroke="#FFFFFF", strokeWidth=.5).encode(
                x=alt.X("O2:Q", title="Oxygen (%)", scale=oxygen_axis),
                y=alt.Y("Pressure:Q", title="Pressure (psi)", scale=alt.Scale(zero=True, nice=True)),
                color=alt.Color("Investigation:N", legend=alt.Legend(orient="top", title=None),
                                scale=alt.Scale(range=["#00847F", "#3563B9", "#C26A1B", "#879EAD"])),
                shape=alt.Shape("Oxygen basis:N", scale=alt.Scale(domain=["Chamber atmosphere", "Burner stream"],
                                                                  range=["circle", "triangle-up"]),
                                legend=alt.Legend(orient="top", title="O₂ measured in")),
                tooltip=["Investigation:N", "Record:N", "Fuel:N", "Oxygen basis:N", "Source row:N",
                         alt.Tooltip("O2:Q", title="O₂ (%)"),
                         alt.Tooltip("Pressure:Q", title="Pressure (psi)", format=".2f")],
            )
            show_chart((scenario + label + dots).properties(height=540).interactive())
            st.caption(f"{len(conditions.rows):,} of {conditions.tests:,} individual tests report both values. "
                       f"Inside the box: {conditions.scenario_ambient} tests with O₂ measured in the chamber atmosphere, "
                       f"and {conditions.scenario_stream} inverse flames (triangles) whose O₂ is the gas leaving the "
                       "burner, not the atmosphere a crew would breathe.")
        else:
            st.info("No test that passes the filters reports both oxygen and pressure.")
        if conditions.without_pair:
            st.caption("No test reporting both values: " + ", ".join(conditions.without_pair)
                       + f". Their records stay in the filtered result. {conditions.summaries} daily or matrix "
                       "records are not individual tests and are not plotted.")
        st.caption("A dot inside the box matches the scenario's atmosphere, not its gravity: the PSI has no "
                   "partial-gravity data.")


def open_retained_records(investigation_id: str) -> None:
    st.session_state["selected_investigation"] = investigation_id
    st.session_state["workspace_navigation"] = "Investigations"


def availability_details(reports: tuple[InvestigationPlotCoverage, ...], ids: tuple[str, ...],
                         x_label: str, y_label: str) -> None:
    selected_reports = [report for report in reports if report.investigation_id in ids]
    plotted = [report.investigation_id for report in selected_reports if report.plotted]
    absent = [report.investigation_id for report in selected_reports if not report.plotted]
    if not ids:
        st.info("No investigations selected for this chart. Choose investigations in Chart settings; "
                "the research-filter results remain available.")
    elif absent:
        st.info(f"Showing {len(plotted)} of {len(ids)} chart-selected investigations for these axes. "
                f"No dots for: {', '.join(absent)}. "
                "They remain in the filtered records and in the CSV download.")
    else:
        st.caption(f"All {len(plotted)} chart-selected investigations have reported pairs for these axes.")
    reasons = {
        PlotExclusion.CHART_SCOPE: "Not selected in Chart settings",
        PlotExclusion.SUMMARY: "Daily/matrix summaries, not individual tests",
        PlotExclusion.BASIS: "Oxygen basis differs or is not reported",
        PlotExclusion.BOTH_MISSING: f"{x_label} and {y_label} not reported",
        PlotExclusion.X_MISSING: f"{x_label} not reported",
        PlotExclusion.Y_MISSING: f"{y_label} not reported",
        PlotExclusion.INTERVAL: "Reported as a range, not one scalar pair",
        PlotExclusion.NONNUMERIC: "No finite numeric scalar pair",
    }
    with st.expander("Data availability · why selected investigations have no dots"):
        st.caption("Counts below use the applied research filters. Each omitted record has one primary reason; "
                   "no values are filled in from nominal atmosphere or other investigations.")
        st.dataframe(pd.DataFrame([{
            "Investigation": report.investigation_id,
            "Record level": ", ".join(report.record_levels),
            "Records after filters": report.records,
            "Plotted records": report.plotted,
            "Primary reasons for omitted records": "; ".join(
                f"{count}: {reasons[reason]}" for reason, count in report.exclusions) or "All records plotted",
        } for report in reports]), hide_index=True)
        inspection_id = st.selectbox("Inspect retained investigation", [report.investigation_id for report in reports],
                                     key="chart_availability_investigation")
        report = next(report for report in reports if report.investigation_id == inspection_id)
        st.markdown(f"**{inspection_id}: {report.plotted} plotted / {report.records} retained records**")
        for reason, count in report.exclusions:
            st.write(f"{count} records: {reasons[reason]}.")
        if report.available_quantities:
            st.write("**Available scalar quantities in this table:** " + "; ".join(v.label for v in report.available_quantities))
            st.caption("Field availability does not guarantee a paired individual test. "
                       "Choose different axes in Chart settings; matrix/day summaries remain separate.")
        else:
            st.write("No scalar quantities are available in this curated table. Material descriptions, "
                     "original values and source documents remain available in the investigation detail.")
        st.button("Open retained records", on_click=open_retained_records, args=(inspection_id,),
                  key="open_chart_availability_records", icon=":material/table_chart:")


def chart_grid(matches: tuple[Match, ...]) -> dict[str, object]:
    coverage_map(matches)
    builder = BuildChartData()
    variables = builder.variables(matches)
    context: dict[str, object] = {}
    data = None
    labels = {v.key: v.label for v in variables}
    x, y = "", ""
    basis = "ambient"
    reports: tuple[InvestigationPlotCoverage, ...] = ()
    ids: list[str] = []
    st.markdown("#### Compare reported quantities")
    with st.expander("Chart settings · axes and investigation scope"):
        if len(variables) >= 2:
            ids = st.multiselect("Investigations in comparison charts", [m.investigation.id for m in matches],
                                 default=[m.investigation.id for m in matches], key="chart_investigations")
            controls = st.columns(3)
            keys = list(labels)
            x = controls[0].selectbox("Horizontal quantity", keys, index=keys.index("o2_percent")
                                      if "o2_percent" in keys else 0, format_func=labels.get, key="chart_x")
            basis = controls[2].selectbox("Oxygen basis for plotted O₂", ["ambient", "oxidizer_stream"], key="chart_basis")
            # Offer only vertical quantities that have plottable pairs with x, most records first.
            pair_counts = builder.partners(matches, x, tuple(ids), O2Basis(basis))
            y_keys = sorted((k for k, n in pair_counts.items() if n), key=lambda k: (-pair_counts[k], k)) or [
                key for key in keys if key != x]
            if st.session_state.get("chart_y") not in y_keys:  # options shrink with x and filters: drop a stale pick
                st.session_state.pop("chart_y", None)
            y = controls[1].selectbox("Vertical quantity", y_keys,
                                      index=y_keys.index("burn_time_s") if "burn_time_s" in y_keys else 0,
                                      format_func=lambda k: f"{labels[k]} · {pair_counts.get(k, 0)} records", key="chart_y")
            data = builder(matches, x, y, tuple(ids), O2Basis(basis))
            reports = builder.coverage(matches, x, y, tuple(ids), O2Basis(basis))
            plotted = Counter(str(row["Investigation"]) for row in data.rows)
            absent = [i for i in ids if i not in plotted]
            st.caption("Plotted records: " + (" · ".join(f"{i} {n}" for i, n in sorted(plotted.items())) or "none")
                       + (f". No plottable pair for these axes: {', '.join(absent)}." if absent else "."))
            context = {"investigations": ids, "horizontal_quantity": x, "vertical_quantity": y,
                       "oxygen_basis": basis, "plotted_records": len(data.rows), "excluded_records": data.excluded,
                       "summary_records_not_plotted": data.summaries,
                       "availability": [{"investigation": r.investigation_id, "records": r.records,
                                         "plotted": r.plotted, "exclusions": dict(r.exclusions)} for r in reports]}
            st.caption("Chart settings refine the profile chart only. Individual tests with paired scalar values are used; "
                       "daily summaries, matrices, missing values and interval midpoints are not plotted as observations.")
    with st.container(border=True, key="profiles_card"):
        if data is None:
            st.info("At least two reported scalar quantities are needed for comparison.")
            st.caption("Retained investigations: " + "; ".join(
                f"{match.investigation.id} ({len(match.points)} records)" for match in matches)
                + ". Open an investigation below to inspect its records and sources.")
        elif not data.rows:
            st.info("No compatible scalar pairs for these axes. Broaden Chart settings.")
        else:
            st.caption(f"{labels[y]} by {labels[x]}")
        if data is not None:
            availability_details(reports, tuple(ids), labels[x], labels[y])
        if data is not None and data.rows:
            # One mark per reported test; overlapping tests are common, so marks are small, translucent and outlined.
            chart = alt.Chart(pd.DataFrame(data.rows)).mark_circle(size=34, opacity=.55, stroke="#FFFFFF", strokeWidth=.5).encode(
                x=alt.X("x:Q", title=labels[x], scale=alt.Scale(zero=False, nice=True)),
                y=alt.Y("y:Q", title=labels[y], scale=alt.Scale(zero=False, nice=True)),
                color=alt.Color("Investigation:N", legend=alt.Legend(orient="top", title=None)),
                tooltip=["Investigation:N", "Record:N", "Fuel:N", "Flow direction:N", "Oxygen basis:N", "Source row:N",
                         alt.Tooltip("x:Q", title=labels[x]), alt.Tooltip("y:Q", title=labels[y])],
            )
            show_chart(chart.properties(height=300).interactive())
            st.caption(f"{len(data.rows)} plotted · {data.excluded} tests without a plottable pair · {data.summaries} daily/matrix "
                       "summary records never plotted. Each dot is one reported test; "
                       "other conditions (pressure, flow, fuel fraction) may differ between dots, so this shows no trend or causal model.")
    return context
