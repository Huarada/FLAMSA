from collections.abc import Iterable

from psi_fire.application.ports import InvestigationCurator, InvestigationStore
from psi_fire.domain.model import Investigation


class CurateInvestigations:
    """Use case: raw PSI sources -> validated aggregates -> curated store. Fails fast on the first invalid one."""

    def __init__(self, curator: InvestigationCurator, store: InvestigationStore) -> None:
        self._curator = curator
        self._store = store

    def __call__(self, investigation_ids: Iterable[str]) -> list[Investigation]:
        curated = []
        for investigation_id in investigation_ids:
            investigation = self._curator.curate(investigation_id)
            self._store.save(investigation)
            curated.append(investigation)
        return curated
