"""Resolve a cited source to a registered, readable document (SPEC-003 section 4.1). No filesystem access here."""

from dataclasses import dataclass
from enum import StrEnum

from psi_fire.application.answer_types import TraceEntry
from psi_fire.application.evidence import InvestigationSources
from psi_fire.application.explore import DatasetError


class SourceStatus(StrEnum):
    AVAILABLE = "available"
    UNREGISTERED = "unregistered"  # the citation names no file, or the file is not registered for the investigation
    UNAVAILABLE = "unavailable"    # registered, but the archived file cannot be read or no longer matches


@dataclass(frozen=True)
class SourceAccess:
    status: SourceStatus
    handle: str | None = None
    path: str | None = None
    label: str | None = None
    digest: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class SourceDocument:
    access: SourceAccess
    content: bytes
    file_name: str
    media_type: str


class ResolveCitationSource:
    """The model only names a path; access always goes through the registered sources of that investigation."""

    def __init__(self, sources: InvestigationSources) -> None:
        self._sources = sources

    def __call__(self, entry: TraceEntry) -> SourceAccess:
        if not entry.source_file:
            return SourceAccess(SourceStatus.UNREGISTERED, reason="The citation names no source file.")
        registered = self._sources(entry.citation.investigation_id)
        match = next((s for s in registered if s["path"] == entry.source_file), None)
        if match is None:
            return SourceAccess(SourceStatus.UNREGISTERED, path=entry.source_file,
                                reason="This file is not registered as a source of the investigation.")
        return SourceAccess(SourceStatus.AVAILABLE, match["handle"], match["path"], match["label"], match["digest"])

    def open(self, entry: TraceEntry) -> SourceDocument | SourceAccess:
        """The document, or the access record explaining why it cannot be shown."""
        access = self(entry)
        if access.status != SourceStatus.AVAILABLE or access.handle is None:
            return access
        try:
            content, name, media = self._sources.read(entry.citation.investigation_id, access.handle)
        except DatasetError as error:
            return SourceAccess(SourceStatus.UNAVAILABLE, access.handle, access.path, access.label, access.digest,
                                str(error))
        return SourceDocument(access, content, name, media)
