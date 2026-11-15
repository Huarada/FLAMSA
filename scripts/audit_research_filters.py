"""Read-only filter/plot audit against an independent CSV/JSON identity-set oracle."""

import argparse
import csv
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from dataclasses import asdict
from math import isfinite
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from psi_fire.application.chart_data import condition_map
from psi_fire.application.explore import ExplorationQuery, ExploreInvestigations, InvalidExplorationQuery
from psi_fire.domain.exploration import ConditionRange
from psi_fire.domain.model import O2Basis
from psi_fire.infrastructure.explorer import FileSnapshotProvider

FACETS = {"ids": "investigation_id", "levels": "record_level", "phases": "fuel_phase",
          "fuels": "fuel_name", "directions": "flow_direction", "lineage": "provenance_status", "bases": "o2_basis"}
METADATA = {"hardware": "hardware", "sensors": "sensors", "pillars": "pillars", "gravity": "gravity_regime"}
AUDITED_FILES = ("application/explore.py", "domain/exploration.py", "application/chart_data.py",
                 "interface/app.py", "interface/explorer_views.py", "interface/reference_dashboard.py",
                 "interface/dashboard_cache.py", "interface/chart_controls.py")


def source_hashes() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / "src/psi_fire" / name).read_bytes()).hexdigest() for name in AUDITED_FILES}


def number(row: dict[str, str], key: str) -> float | None:
    text = row.get(key, "").strip()
    return float(text) if text else None


def scalar(row: dict[str, str], key: str) -> float | None:
    low, high = number(row, key + "_min"), number(row, key + "_max")
    return low if low is not None and low == high and isfinite(low) else None


class CsvOracle:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], dict[str, str]] = {}
        self.index: dict[str, dict[str, set[tuple[str, str]]]] = defaultdict(lambda: defaultdict(set))
        self.search: dict[str, str] = {}
        self.map_ids: set[tuple[str, str]] = set()
        for directory in sorted((ROOT / "data/curated").iterdir()):
            if not directory.is_dir() or directory.name.startswith("."):
                continue
            metadata = json.loads((directory / "investigation.json").read_text(encoding="utf-8"))
            study = metadata["study_metadata"]
            self.search[directory.name] = " ".join((metadata["id"], metadata["psi_id"],
                                                   study.get("study_title", ""), study.get("objective", ""))).casefold()
            manual = metadata.get("manual_metadata")
            values: dict[str, list[str]] = {}
            for attribute, field in METADATA.items():
                if manual is None:
                    values[attribute] = ["Metadata unavailable"]
                elif attribute == "sensors":
                    values[attribute] = [c["value"]["instrument"] if c["value"] else "Not reported"
                                         for c in manual[field]] or ["No entries mapped"]
                else:
                    value = manual[field]["value"]
                    values[attribute] = (["Not reported"] if value is None else
                                         (value or ["No direct pillar"]) if isinstance(value, list) else [value])
            values["review"] = [manual["review_status"] if manual else "unavailable"]
            with (directory / "test_points.csv").open(encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream):
                    identity = (row["investigation_id"], row["test_point_id"])
                    self.rows[identity] = row
                    for attribute, column in FACETS.items():
                        self.index[attribute][row[column] or "Not reported"].add(identity)
                    for attribute, labels in values.items():
                        for label in labels:
                            self.index[attribute][label].add(identity)
                    self.index["note"]["with note" if row["provenance_note"] else "without note"].add(identity)
                    if row["record_level"] == "test" and all(scalar(row, k) is not None for k in ("o2_percent", "pressure_psi")):
                        self.map_ids.add(identity)

    def expected(self, query: ExplorationQuery) -> set[tuple[str, str]]:
        ids = set(self.rows)
        for attribute in (*FACETS, *METADATA):
            labels = getattr(query, attribute)
            if attribute == "bases" and query.oxygen is not None:
                continue
            if labels:
                ids.intersection_update(set().union(*(self.index[attribute].get(label, set()) for label in labels)))
        if query.review != "all":
            ids.intersection_update(self.index["review"].get(query.review, set()))
        if query.note != "any":
            ids.intersection_update(self.index["note"].get(query.note, set()))
        if query.search.strip():
            ids = {key for key in ids if query.search.strip().casefold() in self.search[key[0]]}
        for condition, field in ((query.oxygen, "o2_percent"), (query.pressure, "pressure_psi"), (query.flow, "flow_speed_cm_s")):
            if condition is None:
                continue
            retained = set()
            for key in ids:
                row = self.rows[key]
                low, high = number(row, field + "_min"), number(row, field + "_max")
                if field == "o2_percent" and row["o2_basis"] and row["o2_basis"] != query.basis.value:
                    continue
                if low is None or high is None:
                    if condition.include_missing:
                        retained.add(key)
                elif ((condition.lower is None or high >= condition.lower)
                      and (condition.upper is None or low <= condition.upper)):
                    retained.add(key)
            ids = retained
        return ids


def ranges(bounds: list[tuple[float | None, float | None]]) -> list[ConditionRange | None]:
    return [None, *(ConditionRange(low, high, missing) for low, high in bounds for missing in (False, True))]


def query_description(query: ExplorationQuery) -> dict[str, object]:
    defaults = asdict(ExplorationQuery())
    return {key: value for key, value in asdict(query).items() if value != defaults[key]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/research-filter-engine-audit.json")
    args = parser.parse_args()
    start = perf_counter()
    hashes = source_hashes()
    snapshot = FileSnapshotProvider(ROOT).load()
    explore, oracle = ExploreInvestigations(snapshot), CsvOracle()
    cases: dict[ExplorationQuery, str] = {}

    def add(name: str, **kwargs: object) -> None:
        cases.setdefault(ExplorationQuery(**kwargs), name)

    add("baseline")
    attributes = (*FACETS, *METADATA)
    labels = {name: tuple(sorted(oracle.index[name])) for name in attributes}
    option_names = {"ids": "ids", "levels": "record_level", "phases": "fuel_phase", "fuels": "fuel_name",
                    "directions": "flow_direction", "lineage": "provenance_status", "bases": "o2_basis",
                    "hardware": "hardware", "sensors": "sensors", "pillars": "pillars", "gravity": "gravity_regime"}
    option_errors = {name: {"csv": labels[name], "application": explore.options()[option_names[name]]}
                     for name in attributes if labels[name] != explore.options()[option_names[name]]}
    for name, choices in labels.items():
        for choice in choices:
            add("single:" + name + ":" + choice, **{name: (choice,)})
        add("all-options:" + name, **{name: choices})
        for a, b in itertools.combinations(choices, 2):
            add("or:" + name, **{name: (a, b)})
    for left, right in itertools.combinations(attributes, 2):
        for a, b in itertools.product(labels[left], labels[right]):
            add("and:" + left + ":" + right, **{left: (a,), right: (b,)})
    for inv, level, phase in itertools.product(labels["ids"], labels["levels"], labels["phases"]):
        add("primary-three-facets", ids=(inv,), levels=(level,), phases=(phase,))
    oxygen = ranges([(0, None), (None, 0), (21, 21), (30, None), (0, 100), (99, 100)])
    pressure = ranges([(None, 0), (None, 10.2), (None, 10.5), (14.6, 14.8), (None, 100)])
    flow = ranges([(None, 0), (None, 1), (10, 20), (30, None)])
    for o, p, f, basis in itertools.product(oxygen, pressure, flow, O2Basis):
        add("numeric-cross-product", oxygen=o, pressure=p, flow=f, basis=basis)
    for inv in labels["ids"]:
        for name, choices in (("oxygen", oxygen), ("pressure", pressure), ("flow", flow)):
            for condition, basis in itertools.product(choices, O2Basis):
                add("per-study-numeric:" + name, ids=(inv,), basis=basis, **{name: condition})
        add("search-id:" + inv, search=inv.lower())
    for search in ("no-such-investigation", "[.*]", "  flex  ", "PSI-25", "fire"):
        add("search:" + search, search=search)
    for review in ("all", "draft", "reviewed", "unavailable"):
        for note in ("any", "with note", "without note"):
            add("review-and-note", review=review, note=note)
    results, mismatches, errors = [], [], []
    for index, (query, name) in enumerate(cases.items(), 1):
        try:
            matches = explore(query)
            actual = {(m.investigation.id, p.test_point_id) for m in matches for p in m.points}
            expected = oracle.expected(query)
            plotted = condition_map(matches)
            actual_dots = {(str(row["Investigation"]), str(row["Record"])) for row in plotted.rows}
            expected_dots = expected & oracle.map_ids
            if actual != expected or actual_dots != expected_dots:
                mismatches.append({"case": index, "name": name, "query": query_description(query),
                                   "missing": sorted(expected-actual), "extra": sorted(actual-expected),
                                   "map_missing": sorted(expected_dots-actual_dots), "map_extra": sorted(actual_dots-expected_dots)})
            results.append({"case": index, "group": name, "query": query_description(query), "studies": len(matches),
                            "records": len(actual), "map_dots": len(actual_dots), "summaries": plotted.summaries})
        except Exception as error:  # noqa: BLE001 - collect every audit failure instead of aborting on the first
            errors.append({"case": index, "name": name, "error": type(error).__name__ + ": " + str(error)})
        if index % 500 == 0:
            print(f"Checked {index}/{len(cases)} queries; mismatches={len(mismatches)}, errors={len(errors)}", flush=True)
    invalid = []
    for name, factory in (
        ("reversed", lambda: ConditionRange(30, 20)), ("negative", lambda: ConditionRange(-1, None)),
        ("nan", lambda: ConditionRange(float("nan"), None)), ("infinity", lambda: ConditionRange(None, float("inf"))),
        ("no-bounds", lambda: ConditionRange()),
        ("unknown-study", lambda: explore(ExplorationQuery(ids=("DOES-NOT-EXIST",)))),
        ("oxygen-over-100", lambda: explore(ExplorationQuery(oxygen=ConditionRange(101, None)))),
        ("conflicting-bases", lambda: explore(ExplorationQuery(oxygen=ConditionRange(20, None), bases=("oxidizer_stream",)))),
    ):
        try:
            factory()
            invalid.append({"name": name, "rejected": False})
        except (ValueError, InvalidExplorationQuery) as error:
            invalid.append({"name": name, "rejected": True, "reason": str(error)})
    report = {"date": "2026-11-15", "revision": snapshot.revision, "code_hashes": hashes,
              "code_unchanged": hashes == source_hashes(), "seconds": round(perf_counter()-start, 2),
              "rows_in_csv": len(oracle.rows), "options_per_facet": {key: len(value) for key, value in labels.items()},
              "option_mismatches": option_errors, "cases": len(results), "mismatches": mismatches,
              "errors": errors, "invalid_queries": invalid, "results": results}
    output = args.output
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("results", "code_hashes")}, indent=2), flush=True)
    if mismatches or errors or option_errors or not report["code_unchanged"] or not all(x["rejected"] for x in invalid):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
