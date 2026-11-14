"""Evidence delivery behind a replaceable application port."""

from typing import Protocol


class SourceReader(Protocol):
    def list_for(self, investigation_id: str) -> tuple[dict[str, str], ...]: ...
    def read(self, investigation_id: str, handle: str) -> tuple[bytes, str, str]: ...


class InvestigationSources:
    def __init__(self, reader: SourceReader) -> None:
        self._reader = reader

    def __call__(self, investigation_id: str) -> tuple[dict[str, str], ...]:
        return self._reader.list_for(investigation_id)

    def read(self, investigation_id: str, handle: str) -> tuple[bytes, str, str]:
        return self._reader.read(investigation_id, handle)
