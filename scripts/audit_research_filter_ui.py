"""Exercise filter widgets and study transitions without changing production code or asking a model."""

import argparse
import json
import os
import sys
from pathlib import Path
from time import perf_counter

import pyarrow as pa
from audit_research_filters import CsvOracle, number, source_hashes
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from psi_fire.application.explore import ExplorationQuery

WIDGETS = {"ids": "Investigation", "levels": "Record level", "phases": "Fuel phase", "fuels": "Fuel / material",
           "directions": "Flow direction", "lineage": "Row lineage", "bases": "Reported oxygen basis",
           "hardware": "Hardware", "sensors": "Sensor", "pillars": "Fire-safety pillar", "gravity": "Gravity regime"}


def scalar(row: dict[str, str], key: str) -> float | None:
    try:
        direct = number(row, key)
        if direct is not None:
            return direct
        low, high = number(row, key + "_min"), number(row, key + "_max")
        return low if low is not None and low == high else None
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/research-filter-ui-audit.json")
    args = parser.parse_args()
    os.environ["PSI_LLM_MODEL"] = ""
    start, hashes, oracle = perf_counter(), source_hashes(), CsvOracle()
    app = AppTest.from_file(str(ROOT / "src/psi_fire/interface/app.py"), default_timeout=90).run()
    app.button(key="nav_dashboard").click().run()
    results, failures = [], []

    def widget(kind: str, label: str):
        return next(item for item in getattr(app, kind) if item.label == label)

    def optional(kind: str, label: str):
        return next((item for item in getattr(app, kind) if item.label == label), None)

    def apply() -> None:
        widget("button", "Apply filters").click().run()

    def reset() -> None:
        widget("button", "Reset filters").click().run()

    def observe(name: str, expected_query: ExplorationQuery | None = None) -> dict[str, object]:
        q = app.session_state["applied_query"]
        retained = oracle.expected(q)
        chart_scope = optional("multiselect", "Investigations in comparison charts")
        axes = {label: optional("selectbox", label) for label in
                ("Horizontal quantity", "Vertical quantity", "Oxygen basis for plotted O₂")}
        values = {label: item.value for label, item in axes.items() if item}
        selected = chart_scope.value if chart_scope else []
        x, y = values.get("Horizontal quantity"), values.get("Vertical quantity")
        basis = values.get("Oxygen basis for plotted O₂")

        def eligible(ids: list[str], oxygen_basis: str | None) -> set[tuple[str, str]]:
            if not x or not y:
                return set()
            return {key for key in retained if key[0] in ids and oracle.rows[key]["record_level"] == "test"
                    and scalar(oracle.rows[key], x) is not None and scalar(oracle.rows[key], y) is not None
                    and (not (x.startswith("o2_") or y.startswith("o2_"))
                         or oracle.rows[key]["o2_basis"] == oxygen_basis)}

        actual_map, actual_profile = set(), set()
        for chart in app.get("vega_lite_chart"):
            for data in chart.proto.datasets:
                table = pa.ipc.open_stream(data.data.data).read_all()
                columns = set(table.column_names)
                if {"Investigation", "Record", "O2", "Pressure"} <= columns:
                    actual_map |= set(zip(table["Investigation"].to_pylist(), table["Record"].to_pylist(), strict=True))
                if {"Investigation", "Record", "x", "y"} <= columns:
                    actual_profile |= set(zip(table["Investigation"].to_pylist(), table["Record"].to_pylist(), strict=True))
        expected_map, expected_profile = retained & oracle.map_ids, eligible(selected, basis)
        metrics = {item.label: item.value for item in app.metric}
        checks = {"no_exception": not app.exception, "map_ids_match_csv": actual_map == expected_map,
                  "profile_ids_match_csv": actual_profile == expected_profile,
                  "metric_count_matches_csv": metrics.get("Reported records") == f"{len(retained):,}" if retained else not metrics,
                  "query_matches_submission": q == expected_query if expected_query is not None else True}
        if name.startswith("transition:") and chart_scope:
            checks["study_transition_reconciles_chart_scope"] = selected == sorted({k[0] for k in retained})
        if name.startswith("inactive-bound:"):
            checks["inactive_bound_explicitly_rejected"] = any("inactive bounds" in item.value for item in app.error)
        if name.startswith("cleared-select:"):
            checks["cleared_select_uses_default"] = not app.error
        if name == "stream-filter-default-chart-basis":
            checks["stream_basis_follows_research"] = basis == "oxidizer_stream" and len(actual_profile) == 154
        if name == "final-reset":
            checks["reset_restores_default_comparison"] = len(actual_profile) == 447
        vertical = axes["Vertical quantity"]
        if vertical:
            checks["no_zero_count_vertical_options"] = all("· 0 records" not in label for label in vertical.options)
        result = {"case": name, "records": len(retained), "studies": len({key[0] for key in retained}),
                  "map_dots": len(actual_map), "profile_dots": len(actual_profile),
                  "chart_studies": selected, "axes": values,
                  "same_axes_with_all_retained_studies": len(eligible(sorted({k[0] for k in retained}), basis)),
                  "same_axes_with_stream_basis": len(eligible(sorted({k[0] for k in retained}), "oxidizer_stream")),
                  "checks": checks, "errors": [item.value for item in app.error],
                  "exceptions": [item.message for item in app.exception], "info": [item.value for item in app.info]}
        results.append(result)
        if not all(checks.values()):
            failures.append(result)
        if len(results) % 25 == 0:
            print(f"Observed {len(results)} UI states; identity/exception failures={len(failures)}", flush=True)
        return result

    observe("baseline", ExplorationQuery())
    for attribute, label in WIDGETS.items():
        choices = list(widget("multiselect", label).options)
        for choice in choices:
            reset()
            widget("multiselect", label).set_value([choice])
            apply()
            observe("single:" + attribute + ":" + choice, ExplorationQuery(**{attribute: (choice,)}))
        reset()
        widget("multiselect", label).set_value(choices)
        apply()
        observe("all-options:" + attribute, ExplorationQuery(**{attribute: tuple(choices)}))
    for review in ("all", "draft", "reviewed", "unavailable"):
        for note in ("any", "with note", "without note"):
            reset()
            widget("selectbox", "Manual review").set_value(review)
            widget("selectbox", "Curation notes").set_value(note)
            apply()
            observe("review-note:" + review + ":" + note, ExplorationQuery(review=review, note=note))
    for field, toggle, lower in (("oxygen", "Filter oxygen", "Oxygen minimum (%)"),
                                 ("pressure", "Filter pressure", "Pressure minimum (psi)"),
                                 ("flow", "Filter flow speed", "Flow minimum (cm/s)")):
        reset()
        widget("number_input", lower).set_value(90.0)
        apply()
        observe("inactive-bound:" + field, ExplorationQuery())
        widget("checkbox", toggle).check()
        apply()
        observe("enabled-bound:" + field)
        widget("checkbox", {"oxygen": "Include unreported oxygen", "pressure": "Include unreported pressure",
                            "flow": "Include unreported flow"}[field]).check()
        apply()
        observe("include-missing:" + field)
    for label in ("Oxygen measurement basis", "Manual review", "Curation notes"):
        reset()
        widget("selectbox", label).set_value(None)
        apply()
        observe("cleared-select:" + label, ExplorationQuery())
    reset()
    widget("checkbox", "Filter oxygen").check()
    widget("number_input", "Oxygen minimum (%)").set_value(30.0)
    widget("number_input", "Oxygen maximum (%)").set_value(20.0)
    apply()
    observe("invalid-range-keeps-baseline", ExplorationQuery())
    reset()
    widget("multiselect", "Reported oxygen basis").set_value(["oxidizer_stream"])
    apply()
    observe("stream-filter-default-chart-basis")
    widget("selectbox", "Oxygen basis for plotted O₂").set_value("oxidizer_stream").run()
    observe("stream-filter-aligned-chart-basis")
    reset()
    widget("multiselect", "Investigations in comparison charts").set_value(["FLEX"]).run()
    observe("chart-flex-only-before-reset")
    reset()
    observe("research-reset-with-same-options")
    studies = list(widget("multiselect", "Investigation").options)
    for source in studies:
        reset()
        for target in studies:
            widget("multiselect", "Investigation").set_value([source])
            apply()
            chart = optional("multiselect", "Investigations in comparison charts")
            if chart:
                chart.set_value([source]).run()
            widget("multiselect", "Investigation").set_value([target])
            apply()
            observe("transition:" + source + "->" + target, ExplorationQuery(ids=(target,)))
    reset()
    widget("multiselect", "Investigation").set_value(["FLEX"])
    apply()
    committed = app.session_state["applied_query"]
    widget("multiselect", "Investigation").set_value(["SPICE"]).run()
    observe("unapplied-draft", committed)
    app.button(key="nav_home").click().run()
    app.button(key="nav_dashboard").click().run()
    observe("home-return-restores-committed-scope", committed)
    reset()
    observe("final-reset", ExplorationQuery())
    output = {"date": "2026-11-15", "revision": app.session_state["last_snapshot"].revision,
              "code_hashes": hashes, "code_unchanged": hashes == source_hashes(), "states": len(results),
              "study_transitions": len(studies)**2, "seconds": round(perf_counter()-start, 2),
              "identity_failures": failures, "all_chart_data_checked_as_arrow": True, "results": results,
              "empty_profile_states": sum(r["profile_dots"] == 0 and r["records"] > 0 for r in results)}
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k not in ("results", "code_hashes", "identity_failures")}, indent=2))
    print("Identity/exception failures:", len(failures), flush=True)
    if failures or not output["code_unchanged"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
