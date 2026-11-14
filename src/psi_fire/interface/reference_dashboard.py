"""Reference-led chart grid using reported data and existing application projections."""

from collections import Counter

import altair as alt
import pandas as pd
import streamlit as st

from psi_fire.application.chart_data import BuildChartData, InvestigationPlotCoverage, PlotExclusion
from psi_fire.application.explore import Match, coverage
from psi_fire.domain.model import O2Basis


def show_chart(chart: alt.Chart | alt.LayerChart) -> None:
    chart = chart.configure(background="transparent", font="sans-serif").configure_view(stroke=None).configure_axis(
        gridColor="#DFE7F0", domainColor="#CFDBE6", labelColor="#526E83", titleColor="#526E83",
        labelFontSize=10, titleFontSize=11, titleFontWeight="normal",
    ).configure_range(category=["#00847F", "#6788D4", "#8DBFBA", "#879EAD", "#C58B36"])
    st.altair_chart(chart, theme=None, width="stretch")


def metrics(matches: tuple[Match, ...], total: int, selected: str) -> None:
    points = [p for match in matches for p in match.points]
    current = next(match for match in matches if match.investigation.id == selected)
    levels = sorted({p.record_level.value for p in points})
    columns = st.columns(4)
    values = [("Investigations", f"{len(matches)} / {total}", "Matching / loaded investigations"),
              ("Reported records", f"{len(points):,}", "Across the applied research filters"),
              ("Record levels", str(len(levels)), " · ".join(levels)),
              ("Selected investigation", f"{len(current.points)} / {len(current.investigation.test_points)}",
               f"{selected} · matching / total")]
    for index, (label, value, caption) in enumerate(values):
        with columns[index], st.container(border=True, key=f"kpi_{index}"):
            st.metric(label, value)
            st.caption(caption)


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
                "These investigations remain in the filtered records and record-count charts.")
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


def chart_grid(matches: tuple[Match, ...], selected: str) -> dict[str, object]:
    builder = BuildChartData()
    variables = builder.variables(matches)
    context: dict[str, object] = {}
    data = None
    labels = {v.key: v.label for v in variables}
    x, y = "", ""
    basis = "ambient"
    reports: tuple[InvestigationPlotCoverage, ...] = ()
    ids: list[str] = []
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
    left, right = st.columns([1.7, 1])
    with left, st.container(border=True, key="profiles_card"):
        st.markdown("#### Compare experimental profiles")
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
    with right, st.container(border=True, key="volume_card"):
        st.markdown("#### Records by investigation")
        st.caption(f"Top {min(6, len(matches))} of {len(matches)} · matching record counts")
        rows = sorted([{"Investigation": m.investigation.id, "Records": len(m.points)} for m in matches],
                      key=lambda row: (-row["Records"], row["Investigation"]))[:6]
        bars = alt.Chart(pd.DataFrame(rows)).mark_bar(cornerRadiusEnd=3, size=15).encode(
            y=alt.Y("Investigation:N", sort="-x", title=None, axis=alt.Axis(domain=False, ticks=False)),
            x=alt.X("Records:Q", title="Records", axis=alt.Axis(tickCount=4)),
            color=alt.condition(alt.datum.Investigation == selected, alt.value("#00847F"), alt.value("#8DBFBA")),
            tooltip=["Investigation:N", "Records:Q"],
        ).properties(height=260)
        show_chart(bars)
        st.caption("Volume is not scientific relevance or effective sample size.")

    composition, ranges = st.columns([1, 1.7])
    points = tuple(p for match in matches for p in match.points)
    with composition, st.container(border=True, key="composition_card"):
        st.markdown("#### Dataset composition")
        st.caption("Distribution across reported record levels")
        counts = Counter(p.record_level.value for p in points)
        frame = pd.DataFrame([{"Record level": key, "Records": value} for key, value in counts.items()])
        donut = alt.Chart(frame).mark_arc(innerRadius=64, outerRadius=88).encode(
            theta="Records:Q", color=alt.Color("Record level:N", legend=alt.Legend(title=None, orient="right")),
            tooltip=["Record level:N", "Records:Q"],
        )
        total = alt.Chart(pd.DataFrame([{"text": f"{len(points):,}"}])).mark_text(
            fontSize=25, fontWeight=600, color="#203747").encode(text="text:N")
        show_chart((donut + total).properties(height=220))
        st.caption("Records, not necessarily independent ignitions.")
    with ranges, st.container(border=True, key="coverage_card"):
        heading, selector = st.columns([1.6, 1])
        heading.markdown("#### Experimental coverage")
        heading.caption("Reported envelopes, not individual points")
        quantities = {"Oxygen concentration (%)": "o2_percent", "Pressure (psi)": "pressure_psi",
                      "Flow speed (cm/s)": "flow_speed_cm_s"}
        quantity = selector.selectbox("Coverage quantity", list(quantities), label_visibility="collapsed", key="coverage_axis")
        field = quantities[quantity]
        coverage_rows = []
        without_coverage = []
        for match in matches:
            value = coverage(match.points, field, O2Basis(basis) if field == "o2_percent" else None)
            if value["min"] is not None:
                coverage_rows.append({"Investigation": match.investigation.id, "Minimum": value["min"],
                                      "Maximum": value["max"], "Reported": value["reported"], "Eligible": value["eligible"]})
            else:
                without_coverage.append(match.investigation.id)
        if coverage_rows:
            coverage_frame = pd.DataFrame(coverage_rows)
            ranges_chart = alt.Chart(coverage_frame).mark_rule(strokeWidth=7).encode(
                y=alt.Y("Investigation:N", title=None, axis=alt.Axis(domain=False, ticks=False)),
                x=alt.X("Minimum:Q", title=quantity, scale=alt.Scale(zero=False)), x2="Maximum:Q",
                color=alt.condition(alt.datum.Investigation == selected, alt.value("#00847F"), alt.value("#879EAD")),
                tooltip=["Investigation:N", "Minimum:Q", "Maximum:Q", "Reported:Q", "Eligible:Q"],
            )
            endpoints = alt.Chart(coverage_frame).transform_fold(["Minimum", "Maximum"], as_=["Bound", "Value"]).mark_tick(
                size=13, thickness=2, color="#879EAD").encode(x="Value:Q", y=alt.Y("Investigation:N", title=None))
            show_chart((ranges_chart + endpoints).properties(height=max(190, min(330, len(coverage_rows) * 23))))
        else:
            st.info("No reported coverage for this quantity and selected basis.")
        st.caption(f"O₂ basis: {basis}. Envelopes may contain untested gaps; nominal atmosphere is not substituted.")
        if without_coverage:
            st.caption("No reported interval for this quantity/basis: " + ", ".join(without_coverage)
                       + ". Their records remain in the filtered result.")
    return context
