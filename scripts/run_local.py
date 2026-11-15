"""Create an isolated environment, install declared extras and launch the local workspace."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = ROOT / ".venv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Use the template narrator without model calls.")
    parser.add_argument("--dev", action="store_true", help="Also install pytest, Ruff and mypy.")
    parser.add_argument("--install-only", action="store_true", help="Prepare dependencies without starting Streamlit.")
    parser.add_argument("--reinstall", action="store_true", help="Run pip even if the dependency marker matches.")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    if sys.version_info < (3, 11):  # noqa: UP036 - launcher runs before package version enforcement
        parser.error("Python 3.11 or newer is required; Python 3.12 is recommended.")
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    python = ENVIRONMENT / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        print("Creating .venv...", flush=True)
        venv.EnvBuilder(with_pip=True).create(ENVIRONMENT)
    extras = "dashboard,rag,openai" + (",dev" if args.dev else "")
    dependency_key = hashlib.sha256((ROOT / "pyproject.toml").read_bytes() + extras.encode()).hexdigest()
    marker = ENVIRONMENT / "flamsa-dependencies.json"
    previous = json.loads(marker.read_text(encoding="utf-8")) if marker.is_file() else {}
    if args.reinstall or previous.get("dependency_key") != dependency_key:
        print("Installing dependencies declared in pyproject.toml...", flush=True)
        subprocess.run([str(python), "-m", "pip", "install", "-e", f".[{extras}]"], cwd=ROOT, check=True)
        marker.write_text(json.dumps({"dependency_key": dependency_key, "extras": extras}), encoding="utf-8")
    if args.install_only:
        print(f"Environment ready: {python}")
        return
    environment = os.environ.copy()
    if args.offline:
        environment["PSI_LLM_MODEL"] = ""
    print(f"Opening FLAMSA at http://127.0.0.1:{args.port}", flush=True)
    result = subprocess.run([
        str(python), "-m", "streamlit", "run", "src/psi_fire/interface/app.py",
        "--server.address", "127.0.0.1", "--server.port", str(args.port),
        "--browser.gatherUsageStats", "false",
    ], cwd=ROOT, env=environment, check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
