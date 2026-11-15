"""Claim-level evidence of a copilot answer: excerpt, document, locator, figures and a "View source" inspection."""

from dataclasses import dataclass
from pathlib import PurePosixPath

import streamlit as st

from psi_fire.application.answer_types import AnswerResult, FigureTrace, TraceEntry
from psi_fire.application.source_access import ResolveCitationSource, SourceAccess, SourceDocument
from psi_fire.domain.answering import CitationKind

KIND_LABELS = {CitationKind.PASSAGE: "Document passage", CitationKind.METADATA: "Curated metadata",
               CitationKind.RECORD: "Experimental record", CitationKind.BREAKDOWN: "Computed ranking"}
DIGEST_PREVIEW_CHARS = 16


@dataclass(frozen=True)
class EvidenceContext:
    """What the copilot may do with a citation. `visible_ids` are the investigations in the dashboard filters."""

    resolver: ResolveCitationSource | None
    visible_ids: frozenset[str]


def inspection_scope(visible_ids: frozenset[str], investigation_id: str) -> str | None:
    """A label when the cited study is outside the filters; None when it is inside them."""
    if investigation_id in visible_ids:
        return None
    return (f"{investigation_id} is outside the dashboard filters currently applied. The filters, the scenario and "
            "this answer are unchanged; close this window to return.")


def _doi_url(result: AnswerResult, investigation_id: str) -> str | None:
    doi = next((r.investigation.study_metadata.get("doi") for r in result.shortlist
                if r.investigation.id == investigation_id), None)
    return f"https://doi.org/{doi}" if doi else None


def locator_line(entry: TraceEntry) -> str:
    c = entry.citation
    document = PurePosixPath(entry.source_file).name if entry.source_file else "no source file"
    what = c.test_point_id or c.field or ""
    parts = [KIND_LABELS[c.kind], f"{c.investigation_id} {what}".strip(), document, entry.locator or "no locator"]
    return " · ".join(parts)


def render_figures(traces: tuple[FigureTrace, ...]) -> None:
    for t in traces:
        unit = f" {t.unit}" if t.unit else ""
        raw = f"; raw value as archived: {t.raw}" if t.raw else "; no raw text kept for this value"
        st.caption(f"Figure · {t.investigation_id} · TestPoint {t.test_point_id} · {t.column} = {t.value:g}{unit}"
                   f"{raw} · {t.source_file} row {t.source_row} · provenance {t.provenance_status}")


def render_citation(entry: TraceEntry, result: AnswerResult, key: str, context: EvidenceContext) -> None:
    if entry.citation.quote:
        st.markdown(f"> \"{entry.citation.quote}\"")
    st.caption(locator_line(entry))
    if entry.status:
        st.caption(entry.status)
    has_document = entry.citation.kind != CitationKind.BREAKDOWN
    if context.resolver is not None and has_document and st.button(
            "View source", key=f"view_{key}", icon=":material/find_in_page:",
            help="Inspect the original cited source and download its PDF or data file, when available."):
        inspect_source(entry, result, context)


def _identity(access: SourceAccess) -> None:
    st.markdown("**Source identity**")
    st.caption(f"Registered file: {access.path or 'none'} · {access.label or ''}")
    digest = access.digest
    st.caption(f"SHA-256 {digest[:DIGEST_PREVIEW_CHARS]}… (archived version pinned)" if digest
               else "Version unpinned: the archived path is retained but no checksum is recorded.")


def _study_context(entry: TraceEntry, result: AnswerResult) -> None:
    inv = next(r.investigation for r in result.shortlist if r.investigation.id == entry.citation.investigation_id)
    st.markdown("**Study context**")
    st.write(inv.study_metadata.get("objective", "Objective not reported in the curated study metadata."))
    manual = inv.manual_metadata
    st.caption("Manual metadata unavailable." if manual is None
               else f"Manual metadata review: {manual.review_status.value}")
    url = _doi_url(result, inv.id)
    if url:
        st.link_button("Investigation record (DOI, not the exact page)", url)
    if entry.citation.kind == CitationKind.RECORD:
        point = next(tp for tp in inv.test_points if tp.test_point_id == entry.citation.test_point_id)
        with st.expander(f"Record {point.test_point_id}: raw values and lineage"):
            st.caption(f"{point.source_file} · source row(s) {point.source_row} · "
                       f"provenance {point.provenance_status.value}")
            st.json(point.model_dump(mode="json"), expanded=False)


@st.dialog("Source inspection", width="large")
def inspect_source(entry: TraceEntry, result: AnswerResult, context: EvidenceContext) -> None:
    label = inspection_scope(context.visible_ids, entry.citation.investigation_id)
    (st.warning if label else st.info)(label or "This study is inside the current dashboard filters.")
    st.markdown(f"**{locator_line(entry)}**")
    if entry.citation.quote:
        st.code(entry.citation.quote, language=None, wrap_lines=True)
    if entry.status:
        st.caption(entry.status)
    assert context.resolver is not None  # the button only exists with a resolver
    opened = context.resolver.open(entry)
    if isinstance(opened, SourceDocument):
        _identity(opened.access)
        st.download_button("Download the cited document", opened.content, file_name=opened.file_name,
                           mime=opened.media_type, on_click="ignore", key=f"dl_{opened.access.handle}")
        st.caption(f"Open it at {entry.locator or 'the cited locator'} to read the evidence in context.")
    else:
        _identity(opened)
        st.error(f"Source {opened.status.value}: {opened.reason} The citation above stays visible, but the "
                 "document cannot be shown.")
    _study_context(entry, result)
