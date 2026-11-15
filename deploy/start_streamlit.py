"""Run the existing workspace on Cloud Run's injected port without a shell wrapper."""

import os
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    port = int(os.environ.get("PORT", "8080"))
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535.")
    os.chdir(root)
    os.execv(sys.executable, [
        sys.executable, "-m", "streamlit", "run", str(root / "src/psi_fire/interface/app.py"),
        "--server.address", "0.0.0.0", "--server.port", str(port),
        "--server.headless", "true", "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
    ])


if __name__ == "__main__":
    main()
