"""A small slice of scripts/stress_rag.py in the normal suite: edge cases must never crash or break invariants."""

import importlib.util
import json
from pathlib import Path

from psi_fire.application.explore import LoadExplorer
from psi_fire.infrastructure.answering_factory import build_answering_pipeline
from psi_fire.infrastructure.explorer import FileSnapshotProvider

ROOT = Path(__file__).resolve().parents[2]


def test_the_stress_matrix_slice_has_no_hard_failures():
    spec = importlib.util.spec_from_file_location("stress_rag", ROOT / "scripts/stress_rag.py")
    stress = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stress)
    cases = json.loads((ROOT / "data/eval/stress_cases.json").read_text(encoding="utf-8"))
    cases["questions"] = [q for q in cases["questions"] if q["category"] in {"edge", "trap"}][:6] + cases["questions"][:2]
    investigations = LoadExplorer(FileSnapshotProvider(ROOT))().investigations
    report = stress.run_matrix(build_answering_pipeline(ROOT, {}), investigations, cases,
                               {"user_o2_38078", "invalid_negative_o2", "empty_region"})
    assert report.runs and not report.failures, report.failures
