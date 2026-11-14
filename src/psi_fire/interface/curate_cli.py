"""Composition root for curation: python -m psi_fire.interface.curate_cli [INVESTIGATION_ID ...]"""

import sys
from pathlib import Path

from psi_fire.application.curate_investigations import CurateInvestigations
from psi_fire.infrastructure.curated_store import CuratedStore
from psi_fire.infrastructure.ingestion.pipeline import CsvInvestigationCurator
from psi_fire.infrastructure.source_registry import SourceRegistry

REPO_ROOT = Path(__file__).resolve().parents[3]


def main(argv: list[str]) -> int:
    registry = SourceRegistry(REPO_ROOT / "data" / "sources.json")
    curate = CurateInvestigations(
        CsvInvestigationCurator(registry, REPO_ROOT, manual_dir=REPO_ROOT / "data" / "manual"),
        CuratedStore(REPO_ROOT / "data" / "curated"),
    )
    for investigation in curate(argv or registry.ids()):
        inferred = sum(tp.provenance_status == "inferred" for tp in investigation.test_points)
        print(f"{investigation.id:<13} {investigation.record_level.value:<12} "
              f"{investigation.test_point_count:>5} test points ({inferred} inferred), "
              f"varied: {', '.join(investigation.varied_variables) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
