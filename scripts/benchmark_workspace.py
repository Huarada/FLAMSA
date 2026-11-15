"""Measure local Streamlit reruns without asking the copilot or contacting a model provider."""

import argparse
import json
import os
import sys
from pathlib import Path
from time import perf_counter

from streamlit.testing.v1 import AppTest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3, choices=range(1, 11))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    os.environ["PSI_LLM_MODEL"] = ""  # local benchmark process only; never read or print credentials
    app = AppTest.from_file(str(root / "src/psi_fire/interface/app.py"), default_timeout=120)
    rows: list[dict[str, object]] = []

    def measure(label: str, button: str | None = None) -> None:
        if button is not None:
            app.button(key=button).click()
        start = perf_counter()
        app.run()
        if app.exception:
            raise RuntimeError(f"{label}: application exception; inspect the local app before benchmarking")
        rows.append({"action": label, "seconds": round(perf_counter() - start, 4)})

    measure("Home initial")
    measure("Dashboard first", "home_dashboard")
    for index in range(args.runs):
        measure(f"Dashboard rerun {index + 1}")
    measure("Home return", "nav_home")
    measure("Dashboard return", "nav_dashboard")
    measure("Fire behavior first", "nav_fire_behavior")
    measure("Fire behavior rerun")
    measure("Investigations first", "nav_investigations")
    measure("Investigations rerun")
    print(json.dumps({"revision": app.session_state["last_snapshot"].revision,
                      "measurement": "AppTest wall time; excludes browser, network and real model calls",
                      "samples": rows}, indent=2))


if __name__ == "__main__":
    main()
