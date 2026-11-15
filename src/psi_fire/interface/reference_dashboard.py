"""Reference-led chart grid using reported data and existing application projections."""

from collections import Counter
from math import ceil, sqrt
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from psi_fire.application.chart_data import (
    LUNAR_OXYGEN_MIN,
    LUNAR_PRESSURE_MAX,
    InvestigationPlotCoverage,
    PlotExclusion,
    condition_map,
)
from psi_fire.application.explore import Match
from psi_fire.domain.model import O2Basis
from psi_fire.interface.chart_controls import quantity_choice, reconcile, widget_key
from psi_fire.interface.copilot_panel import EARTH_CABIN, RESULT_KEY, pick_scenario, scenario_point
from psi_fire.interface.dashboard_cache import (
    chart_variables,
    comparison_projection,
    partner_counts,
    record_scope,
)


def show_chart(chart: alt.Chart | alt.LayerChart, **chart_options: Any) -> Any:
    chart = chart.configure(background="transparent", font="sans-serif").configure_view(stroke=None).configure_axis(
        gridColor="#DFE7F0", domainColor="#CFDBE6", labelColor="#526E83", titleColor="#526E83",
        labelFontSize=10, titleFontSize=11, titleFontWeight="normal",
    ).configure_range(category=["#00847F", "#6788D4", "#8DBFBA", "#879EAD", "#C58B36"])
    return st.altair_chart(chart, theme=None, width="stretch", **chart_options)


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


ANSWER_RANK = "Rank in last answer"
NOT_IN_ANSWER = "not in answer"
DOT_OPACITY = 0.62
FADED_DOT_OPACITY = 0.12
COVERAGE_KEY = "coverage_chart"
PICK_GRID_O2_STEP = 0.5  # matches the copilot's oxygen input step
PICK_GRID_PSI_STEP = 1.0  # shortcut: coarse pressure grid keeps the chart light; refine with a custom click handler
MAX_PICK_GRID_POINTS = 4_000
NEAR_O2_PERCENT = 5.0   # "near" window around the scenario marker, in the same units as the axes
NEAR_PRESSURE_PSI = 2.0
SCENARIO_MARKER_COLOR = "#008B8B"  # dark cyan, distinct from the teal data series
BIN_O2_PERCENT = 1.0     # tests this close in oxygen and pressure share one bubble
BIN_PRESSURE_PSI = 0.5
PRESSURE_FOCUS_PSI = 20.0  # default zoom: the habitat-relevant band; a few high-pressure tests stretched the axis
MIN_LABELLED_TESTS = 5     # bubbles with fewer tests show their count only in the tooltip
BUBBLE_SIZE_RANGE = [40, 900]
STREAM_BASIS = "Burner stream"


@st.cache_data(max_entries=16, show_spinner=False)
def pick_grid(right: float, top_psi: float) -> pd.DataFrame:
    """Bound interaction-only marks; source observations and exact scenario inputs are unchanged."""
    width = max(0.0, right - 10)
    count = (int(width / PICK_GRID_O2_STEP) + 1) * (int(top_psi / PICK_GRID_PSI_STEP) + 2)
    stride = max(1, ceil(sqrt(count / MAX_PICK_GRID_POINTS)))
    while True:
        oxygen = [10 + i * PICK_GRID_O2_STEP * stride for i in range(int(width / (PICK_GRID_O2_STEP * stride)) + 1)]
        pressure = [i * PICK_GRID_PSI_STEP * stride for i in range(int(top_psi / (PICK_GRID_PSI_STEP * stride)) + 2)]
        if len(oxygen) * len(pressure) <= MAX_PICK_GRID_POINTS:
            return pd.DataFrame([{"o2": o, "psi": p} for o in oxygen for p in pressure])
        stride += 1


def _pick_layers(right: float, top_psi: float, oxygen_axis: alt.Scale,
                 pressure_axis: alt.Scale) -> tuple[alt.Chart, alt.Chart]:
    """Invisible grid so a click on empty space selects the nearest (oxygen, pressure); plus the scenario marker."""
    pick = alt.selection_point(name="pick", fields=["o2", "psi"], on="click", nearest=True, clear=False)
    grid = alt.Chart(pick_grid(right, top_psi)).mark_point(
        opacity=0, size=60).encode(x=alt.X("o2:Q", title="Oxygen (%)", scale=oxygen_axis),
        y=alt.Y("psi:Q", title="Pressure (psi)", scale=pressure_axis)).add_params(pick)
    o2, psi = scenario_point()
    marker = alt.Chart(pd.DataFrame([{"o2": o2, "psi": psi}])).mark_point(
        filled=True, size=300, color=SCENARIO_MARKER_COLOR, stroke="#FFFFFF", strokeWidth=2, opacity=1).encode(
        x=alt.X("o2:Q", title="Oxygen (%)", scale=oxygen_axis),
        y=alt.Y("psi:Q", title="Pressure (psi)", scale=pressure_axis),
        tooltip=[alt.Tooltip("o2:Q", title="Scenario O₂ (%)", format=".1f"),
                 alt.Tooltip("psi:Q", title="Scenario pressure (psi)", format=".1f")])
    return grid, marker


def scenario_indicators(frame: pd.DataFrame) -> None:
    """Three numbers that say how well the chosen condition is covered by tests (shown with the copilot)."""
    o2, psi = scenario_point()
    near = frame[((frame["O2"] - o2).abs() <= NEAR_O2_PERCENT) & ((frame["Pressure"] - psi).abs() <= NEAR_PRESSURE_PSI)]
    gap = (((frame["O2"] - o2) / NEAR_O2_PERCENT) ** 2 + ((frame["Pressure"] - psi) / NEAR_PRESSURE_PSI) ** 2).min()
    inside = o2 >= LUNAR_OXYGEN_MIN and psi <= LUNAR_PRESSURE_MAX
    first, second, third = st.columns(3)
    first.metric("Tests near the marker", f"{len(near):,}",
                 help=f"Tests within ±{NEAR_O2_PERCENT:g}% O₂ and ±{NEAR_PRESSURE_PSI:g} psi of the dark-cyan marker. "
                      "Zero means the scenario lies in an untested area.")
    second.metric("Investigations near", near["Investigation"].nunique(),
                  help="Different PSI studies with at least one test in that window.")
    third.metric("Coverage", "Tested nearby" if gap <= 1 else "Extrapolated",
                 delta="inside lunar box" if inside else "outside lunar box", delta_color="off",
                 help="Extrapolated: the closest test is outside the window above, so conclusions go beyond the data.")


def _apply_pick() -> None:
    """on_select callback: runs before the single rerun, so widget state may be written here."""
    picked = st.session_state[COVERAGE_KEY].selection.get("pick") or []
    if picked:
        pick_scenario(float(picked[0]["o2"]), float(picked[0]["psi"]))


def bubbles_of(frame: pd.DataFrame) -> pd.DataFrame:
    """One row per (study, oxygen basis, nearby conditions): the number of tests is the point of the chart."""
    keyed = frame.assign(o2_bin=(frame["O2"] / BIN_O2_PERCENT).round() * BIN_O2_PERCENT,
                         psi_bin=(frame["Pressure"] / BIN_PRESSURE_PSI).round() * BIN_PRESSURE_PSI)
    grouped = keyed.groupby(["Investigation", "Oxygen basis", "o2_bin", "psi_bin", ANSWER_RANK], as_index=False).agg(
        n=("O2", "size"), O2=("O2", "mean"), Pressure=("Pressure", "mean"),
        O2_min=("O2", "min"), O2_max=("O2", "max"), psi_min=("Pressure", "min"), psi_max=("Pressure", "max"),
        Fuels=("Fuel", lambda s: ", ".join(sorted({str(v) for v in s})[:3])))
    return grouped.drop(columns=["o2_bin", "psi_bin"])


def _coverage_controls(frame: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Study picker, burner-stream switch and zoom switch. Returns the frame to draw and whether all pressures show."""
    studies = sorted(frame["Investigation"].unique())
    previous = [s for s in st.session_state.get("coverage_studies", studies) if s in studies]
    st.session_state["coverage_studies"] = previous or studies  # filters can remove a study the user had selected
    chosen = st.multiselect("Studies shown", studies, key="coverage_studies",
                            help="Each study measured something different (droplets of liquid fuel in FLEX and CFI, "
                                 "gas flames in ACME-CFI-G). Show one at a time to read a single story.")
    stream = st.toggle("Include oxygen measured in the burner stream", key="coverage_stream",
                       help="Some ACME-CFI-G tests report the oxygen of the gas leaving the burner, not the "
                            "atmosphere a crew would breathe. They are hidden unless you switch this on.")
    full = st.toggle("Show all pressures", key="coverage_full",
                     help=f"By default the chart zooms on 0-{PRESSURE_FOCUS_PSI:g} psi, where habitat conditions "
                          "are. A few high-pressure tests would otherwise flatten that band.")
    shown = frame[frame["Investigation"].isin(chosen)]
    if not stream:
        shown = shown[shown["Oxygen basis"] != STREAM_BASIS]
    return shown, full


def coverage_map(matches: tuple[Match, ...]) -> None:
    conditions = condition_map(matches)
    with st.container(border=True, key="coverage_card"):
        st.markdown("#### Experimental coverage · oxygen and pressure")
        st.caption("**What it shows:** which oxygen and pressure conditions PSI experiments actually tested. Each "
                   "bubble groups tests with nearly the same conditions: **its size and number are how many tests**, "
                   "color is the study. Empty areas have no test data, so any conclusion there is an extrapolation. "
                   f"The shaded box is the lunar-habitat reference ({LUNAR_OXYGEN_MIN:g}% O₂ or more at "
                   f"{LUNAR_PRESSURE_MAX:g} psi or less); the amber ring is Earth air.")
        copilot_on = bool(st.session_state.get("show_copilot"))
        if copilot_on:
            st.caption("Click the chart to set the copilot's scenario. Clicks snap to a display grid; type the values "
                       "in the copilot for exact conditions.")
            with st.expander("How the chart and the copilot work together"):
                st.write("The dark-cyan marker and the copilot's Oxygen and Pressure fields follow your click. "
                         "**Ask copilot** then ranks the investigations closest to that point and the language "
                         "model explains the ranking using only cited records and report passages. Bubbles near "
                         "the marker mean well-covered conditions; a marker in an empty area means the answer rests "
                         "on distant tests. The ranking weighs five criteria (O₂ closeness, pressure closeness, "
                         "fire-safety pillar, fuel type, data richness), so a study can rank high with few bubbles "
                         "near the marker. After you ask, the studies in the answer stay highlighted and the rest fade.")
        if conditions.rows:
            frame, full_range = _coverage_controls(pd.DataFrame(conditions.rows))
            answered = st.session_state.get(RESULT_KEY) if copilot_on else None
            ranks = {r.investigation.id: r.rank for r in answered.shortlist} if answered else {}
            frame = frame.assign(**{ANSWER_RANK: frame["Investigation"].map(
                lambda i: f"#{ranks[i]}" if i in ranks else NOT_IN_ANSWER)})
            if frame.empty:
                st.info("No test remains with these study and oxygen-basis choices.")
            else:
                _draw_coverage(frame, ranks, full_range, copilot_on)
            st.caption(f"{len(conditions.rows):,} of {conditions.tests:,} individual tests report both values. "
                       f"Inside the box: {conditions.scenario_ambient} tests with O₂ measured in the chamber atmosphere, "
                       f"and {conditions.scenario_stream} inverse flames (triangles when shown) whose O₂ is the gas "
                       "leaving the burner, not the atmosphere a crew would breathe.")
        else:
            retained = sum(len(m.points) for m in matches)
            st.info(f"This oxygen–pressure map has no eligible points; {retained:,} records remain in the research results. "
                    "A dot requires an individual test with both a scalar oxygen value and a scalar pressure value. "
                    "Use the comparison below for other reported quantities or open the retained records.")
        if conditions.without_pair:
            st.caption("No test reporting both values: " + ", ".join(conditions.without_pair)
                       + f". Their records stay in the filtered result. {conditions.summaries} daily or matrix "
                       "records are not individual tests and are not plotted.")
        st.caption("A bubble inside the box matches the scenario's atmosphere, not its gravity: the PSI has no "
                   "partial-gravity data.")


def _draw_coverage(frame: pd.DataFrame, ranks: dict[str, int], full_range: bool, copilot_on: bool) -> None:
    scenario_o2, scenario_psi = scenario_point()
    top = float(frame["Pressure"].max()) + 5 if full_range else max(PRESSURE_FOCUS_PSI, scenario_psi + 2)
    pressure_axis = alt.Scale(domain=[0, top], nice=False, clamp=True)
    right = max(float(frame["O2"].max()), LUNAR_OXYGEN_MIN, scenario_o2) + 3
    oxygen_axis = alt.Scale(domain=[10, right], nice=False)  # no test reports less than ~12% O2
    x_enc = alt.X("O2:Q", title="Oxygen (%)", scale=oxygen_axis)
    y_enc = alt.Y("Pressure:Q", title="Pressure (psi)", scale=pressure_axis)
    bubbles = bubbles_of(frame)
    visible = bubbles[bubbles["Pressure"] <= top]

    box = alt.Chart(pd.DataFrame([{"x": LUNAR_OXYGEN_MIN, "x2": right, "y": 0.0, "y2": LUNAR_PRESSURE_MAX}]))
    zone = box.mark_rect(color="#F2B33D", opacity=.18, stroke="#C58B36", strokeDash=[5, 4], clip=True).encode(
        x=alt.X("x:Q", scale=oxygen_axis), x2="x2:Q", y=alt.Y("y:Q", scale=pressure_axis), y2="y2:Q")
    zone_label = box.mark_text(align="right", baseline="top", dx=-6, dy=4, color="#8A5A12", fontWeight=600,
                               clip=True).encode(x=alt.X("x2:Q", scale=oxygen_axis),
                                                 y=alt.Y("y2:Q", scale=pressure_axis),
                                                 text=alt.value("Lunar habitat reference"))
    earth = alt.Chart(pd.DataFrame([{"O2": EARTH_CABIN.o2_percent, "Pressure": EARTH_CABIN.pressure_psi,
                                     "Label": f"Earth air ({EARTH_CABIN.o2_percent:g}%, "
                                              f"{EARTH_CABIN.pressure_psi:g} psi)"}]))
    earth_ring = earth.mark_point(shape="circle", filled=False, size=420, stroke="#C58B36", strokeWidth=2.5,
                                  clip=True).encode(x=x_enc, y=y_enc)
    earth_text = earth.mark_text(align="left", dx=14, dy=-14, color="#8A5A12", fontWeight=600, clip=True).encode(
        x=x_enc, y=y_enc, text="Label:N")
    dots = alt.Chart(visible).mark_point(filled=True, stroke="#FFFFFF", strokeWidth=.6, clip=True).encode(
        opacity=alt.condition(f"!{len(ranks)} || datum['{ANSWER_RANK}'] != '{NOT_IN_ANSWER}'",
                              alt.value(.85), alt.value(FADED_DOT_OPACITY)),
        x=x_enc, y=y_enc,
        size=alt.Size("n:Q", scale=alt.Scale(type="sqrt", range=BUBBLE_SIZE_RANGE),
                      legend=alt.Legend(orient="bottom", title="Tests per bubble")),
        color=alt.Color("Investigation:N", legend=alt.Legend(orient="top", title=None),
                        scale=alt.Scale(range=["#00847F", "#3563B9", "#C26A1B", "#879EAD"])),
        shape=alt.Shape("Oxygen basis:N", scale=alt.Scale(domain=["Chamber atmosphere", STREAM_BASIS],
                                                          range=["circle", "triangle-up"]),
                        legend=alt.Legend(orient="top", title="O₂ measured in")),
        tooltip=["Investigation:N", f"{ANSWER_RANK}:N", alt.Tooltip("n:Q", title="Tests here"), "Fuels:N",
                 "Oxygen basis:N", alt.Tooltip("O2_min:Q", title="O₂ min (%)", format=".1f"),
                 alt.Tooltip("O2_max:Q", title="O₂ max (%)", format=".1f"),
                 alt.Tooltip("psi_min:Q", title="Pressure min (psi)", format=".2f"),
                 alt.Tooltip("psi_max:Q", title="Pressure max (psi)", format=".2f")])
    counts = alt.Chart(visible[visible["n"] >= MIN_LABELLED_TESTS]).mark_text(
        fontSize=10, fontWeight=700, color="#12304A", dx=11, dy=-11, clip=True).encode(x=x_enc, y=y_enc, text="n:Q")
    layers = zone + zone_label + dots + counts + earth_ring + earth_text
    if copilot_on:
        grid, marker = _pick_layers(right, top, oxygen_axis, pressure_axis)
        layers = grid + layers + marker
    show_chart(layers.properties(height=540).interactive(),
               **({"on_select": _apply_pick, "key": COVERAGE_KEY} if copilot_on else {}))
    hidden = int(bubbles.loc[bubbles["Pressure"] > top, "n"].sum())
    if hidden:
        st.caption(f"{hidden:,} tests above {top:g} psi are outside this zoom. Switch on **Show all pressures** to see them.")
    if copilot_on:
        scenario_indicators(frame)
    absent = [i for i in ranks if i not in set(frame["Investigation"])]
    if absent:
        st.caption(f"Ranked in the last answer but with no bubble here: {', '.join(absent)}. No plotted test of "
                   "these studies reports both oxygen and pressure (or the filters exclude them); the ranking "
                   "still uses their other records and metadata.")


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


def chart_grid(matches: tuple[Match, ...], revision: str) -> dict[str, object]:
    coverage_map(matches)
    scope = record_scope(matches)
    variables = chart_variables(revision, scope, matches)
    context: dict[str, object] = {}
    data = None
    labels = {v.key: v.label for v in variables}
    x, y = "", ""
    basis = "ambient"
    reports: tuple[InvestigationPlotCoverage, ...] = ()
    ids: list[str] = []
    st.markdown("#### Compare reported quantities")
    available_ids, basis_options, control_context = reconcile(matches)
    with st.expander("Chart settings · axes and investigation scope"):
        if len(variables) >= 2:
            ids = st.multiselect("Investigations in comparison charts", available_ids,
                                 default=st.session_state["chart_investigations"],
                                 key=widget_key("chart_studies", (control_context, available_ids)))
            st.session_state["chart_investigations"] = ids
            controls = st.columns(3)
            keys = list(labels)
            with controls[0]:
                x = quantity_choice("Horizontal quantity", keys, "chart_x", labels, control_context, "o2_percent")
            with controls[2]:
                basis = quantity_choice("Oxygen basis for plotted O₂", basis_options, "chart_basis",
                                        {b: b for b in basis_options}, control_context, "ambient")
            # Offer only vertical quantities that have plottable pairs with x, most records first.
            pair_counts = partner_counts(revision, scope, x, tuple(ids), O2Basis(basis), matches)
            y_keys = sorted((k for k, n in pair_counts.items() if n), key=lambda k: (-pair_counts[k], k))
            with controls[1]:
                y = quantity_choice("Vertical quantity", y_keys, "chart_y",
                                    {k: f"{labels[k]} · {pair_counts[k]} records" for k in y_keys},
                                    (control_context, scope, ids, x, basis), "burn_time_s")
            st.caption(f"Comparison oxygen basis: {basis}. This follows the research basis when restricted; "
                       "burner-stream oxygen and chamber-atmosphere oxygen are never combined.")
            if y:
                data, reports = comparison_projection(revision, scope, x, y, tuple(ids), O2Basis(basis), matches)
                plotted = Counter(str(row["Investigation"]) for row in data.rows)
                absent = [i for i in ids if i not in plotted]
                st.caption("Plotted records: " + (" · ".join(f"{i} {n}" for i, n in sorted(plotted.items())) or "none")
                           + (f". No plottable pair for these axes: {', '.join(absent)}." if absent else "."))
            context = {"investigations": ids, "horizontal_quantity": x, "vertical_quantity": y,
                       "oxygen_basis": basis, "plotted_records": len(data.rows) if data else 0,
                       "excluded_records": data.excluded if data else None,
                       "summary_records_not_plotted": sum(p.record_level.value != "test" for m in matches for p in m.points),
                       "availability": [{"investigation": r.investigation_id, "records": r.records,
                                         "plotted": r.plotted, "exclusions": dict(r.exclusions)} for r in reports]}
            st.caption("Chart settings refine the profile chart only. Individual tests with paired scalar values are used; "
                       "daily summaries, matrices, missing values and interval midpoints are not plotted as observations.")
    with st.container(border=True, key="profiles_card"):
        if data is None:
            if not ids and len(variables) >= 2:
                st.info("No investigations selected for this comparison. Choose investigations in Chart settings; "
                        "the research-filter results remain available.")
            elif not any(p.record_level.value == "test" for m in matches for p in m.points):
                st.info("The retained records are daily or matrix summaries, not individual tests. "
                        "They cannot supply scatter-plot observations; inspect the records and reported ranges instead.")
            elif len(variables) < 2:
                st.info("At least two reported scalar quantities are needed for comparison.")
            else:
                st.info(f"No individual tests in the chart selection report a compatible scalar partner for {labels[x]}. "
                        "Choose another horizontal quantity or inspect the retained records. "
                        "Missing values and interval midpoints are not substituted.")
            st.caption("Retained investigations: " + "; ".join(
                f"{match.investigation.id} ({len(match.points)} records)" for match in matches)
                + ". Open an investigation below to inspect its records and sources.")
            inspection_id = st.selectbox("Inspect retained investigation", available_ids,
                                         key="chart_availability_investigation")
            st.button("Open retained records", on_click=open_retained_records, args=(inspection_id,),
                      key="open_chart_availability_records", icon=":material/table_chart:")
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
