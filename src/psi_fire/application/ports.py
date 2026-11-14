from typing import Protocol

from psi_fire.domain.model import Investigation


class InvestigationCurator(Protocol):
    """Builds a validated Investigation from raw sources."""

    def curate(self, investigation_id: str) -> Investigation: ...


class InvestigationStore(Protocol):
    def save(self, investigation: Investigation) -> None: ...


class InvestigationRepository(Protocol):
    def all(self) -> list[Investigation]: ...

    def get(self, investigation_id: str) -> Investigation: ...
