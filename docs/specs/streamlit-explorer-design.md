# SPEC-001 design — DDD, application contracts and state

Status: proposed, revision 0.3, 2026-11-14. Implements the requirements in [SPEC-001](streamlit-explorer.md); this document contains no production implementation. All new names below are proposed unless labelled existing.

## 1. Domain boundary and responsibility map

Keep one fire-safety research domain in one Python application. Curation, exploration and later relevance assessment are workflows/modules around the same Investigation aggregate; this prototype does not need separate microservices, duplicated scientific repositories, an event bus or a generic CQRS framework.

| Element | Responsibility and owner |
| --- | --- |
| Investigation | Existing aggregate root; validated identity, TestPoints, column dictionary, derived variable classification and optional ManualMetadata |
| TestPoint | Existing entity, identified inside its parent by test_point_id; record is not necessarily one measured run |
| Claim / Evidence / Sensor | Existing value structures; preserve values, inference/evidence and review semantics |
| Reported condition filtering | Pure domain predicates: inclusive interval overlap, O2 basis compatibility, same-record conjunction; no I/O, dataframe or widget imports |
| ExplorationQuery | Application request, immutable; contains validated filter selections, not widget objects |
| CatalogRow / DetailResult | Application read projections, not new aggregates; never saved as a second scientific source of truth |
| DatasetRevision / SourceHandle | Application/adapter identities, not physical quantities or scientific claims |
| Streamlit | Converts user events into application requests, formats outputs and manages per-session presentation state |
| Files, registry, hashing, source delivery | Infrastructure adapters implementing inward-facing ports |

Do not put a list of DataFrame filters inside a widget callback and call it a domain service. Conversely, presentation precision, selected columns and row selection do not belong on Investigation. Reuse current flat TestPoint/ColumnInfo design (ADR-0016); do not revive abandoned nested models or add a Hardware aggregate solely to satisfy a diagram.

Current model caveats: frozen Pydantic objects can still contain mutable dictionaries; frozen does not prove deep immutability. Read projections must copy or expose immutable collections and never mutate Investigation.extras/columns/study_metadata. Existing claim status `verified` means source-stated, not peer-reviewed, experimentally validated or scientifically certain. Row lineage status is not a per-field ClaimStatus.

Concurrent curation alignment (ADR-0032/0033/0034): Sensor.instrument is one plain filter label and measures is optional. Do not require a measures string, recover it from the instrument name, or parse count/type/location from Claim.note into undocumented filter values. Notes remain visible as evidenced text. Quotes remain copyable and unaltered; do not merge evidence fragments. Richer sensor fields remain deferred until an explicit model/schema revision.

## 2. Proposed request types and policies

All collections are tuples or immutable sets with canonical ordering for cache keys. Do not pass pandas/Streamlit types across application ports. Types may use existing Pydantic or frozen dataclasses without a new serialization framework.

| Type | Required fields / invariants |
| --- | --- |
| RecordReference | investigation_id: str; test_point_id: str; scope bound to DatasetRevision when used in a result |
| NumericRange | lower: float or None; upper: float or None; at least one finite bound; lower <= upper; quantity-specific bounds checked independently of UI |
| NumericFilter | range: NumericRange; include_missing: bool=False |
| OxygenFilter | NumericFilter plus exactly one existing O2Basis; default ambient when newly activated |
| ValueSelection | selected canonical labels/enums plus include_absent: bool=False; no labels and no missing flag means unrestricted |
| ClaimSelection | selected values plus independent include_not_reported and include_metadata_unavailable flags; an explicitly empty Claim list has its own selectable state where applicable |
| ExplorationQuery | search_text, investigation_ids, record_levels, fuel_names, fuel_phases, flow_directions, optional oxygen/pressure/flow filters, standalone_o2_bases, row_provenance, note_presence, optional hardware/sensor/pillar/gravity ClaimSelections, review_states, catalog_sort |
| SortSpec | field in id/title/matching_record_count/total_record_count; direction ascending or descending; tie-break id ascending |

Defaults: no scientific filter, all record levels, empty search, no numeric ranges, all metadata review states, id ascending. Strip outer search whitespace and use casefold for comparisons; search is a literal substring in any one supported identity/title/objective field, not regex or token-wise inference. Preserve original scientific text for display. Nonempty supplied ids/enums must exist in the loaded snapshot; unknown selections produce InvalidExplorationQuery. The interface may reconcile a removed selection after refresh before submitting a new query, with a visible notice.

None means no numeric filter; it is not an unbounded active filter. An active oxygen filter owns its single basis and replaces standalone_o2_bases; having both set is an invalid query. For missing O2, include_missing accepts unknown interval with same/unknown basis only; known different basis is excluded. Match known O2 using basis AND overlap. Evaluate all row filters over one TestPoint, then apply existential selection to Investigation.

Categorical absence, unavailable manual metadata, not_reported Claim and explicit empty pillar assignment are distinct application selection states. Never introduce these sentinels into domain enums. Any selected sensor/pillar value uses OR within that filter; different filters use AND. A known sensor cannot match an empty sensor list. An empty sensor list is displayed as no entries mapped; it does not establish a source-backed no-sensors Claim.

Metadata filters accept draft Claims by default and preserve their status. Review-only selection constrains metadata review state independently of ClaimStatus. Source-based text entries in study_metadata never supply missing manual filter values.

## 3. Proposed results

| Result | Required contents |
| --- | --- |
| ExplorationResult | revision, normalized applied_query, stable CatalogRow tuple, total/matching counts by RecordLevel, stable filter options and typed notices |
| CatalogRow | id, psi_id, title, record_level summary, matching_record_count, total_record_count, RecordReferences, fuel phases, independent atmosphere coverage summaries, metadata review state |
| CoverageSummary | quantity, unit, basis if applicable, scope=matching_records, eligible_count, reported_count, missing_count, minimum/maximum of reported values or None |
| DetailResult | revision, Investigation identity and read projection, effective query/scope, records, applicable ColumnInfo definitions, whole-investigation variable classification, manual claims/evidence |
| SourceDescriptor | opaque source_handle, owning investigation, source category, basename/media_type, locator, optional original URL, optional capture identity, acquisition state, optional expected digest and pinning state |
| SourceReadResult | typed state, safe basename/media_type, optional bytes/plain preview, locator, expected/observed digest when available; no arbitrary path input |

No result stores active widget selection. Every record identifier used to open detail is validated against the snapshot and the claimed parent. An explicit show-all-records action sets detail scope=full_investigation without changing the global query or catalog counts.

Coverage calculation: eligible records are currently matching records; for O2, only records with the displayed basis are eligible. Unknown-basis records are counted separately as basis_unknown_count, not attributed to ambient. For pressure/flow, all matching records are eligible. reported_count counts nonmissing valid interval pairs; missing_count=eligible_count-reported_count. If eligible_count is zero, coverage is Not applicable to this basis, never 0% or a reported zero value. Percentages, if shown, state reported_count/eligible_count. Full-dataset coverage is a separate explicitly scoped projection.

Compute extrema only over eligible reported values. Do not substitute nominal atmosphere or include source lists as exact samples. Sort numeric values by underlying number with missing last in either direction; sort title by casefolded display title with id ascending tie-break. Preserve raw source order for the default TestPoint table; optional record sorts use the selected underlying field and test_point_id as stable tie-break.

## 4. Ports, use-case boundaries and failure translation

The existing InvestigationRepository remains the scientific source; new adapters compose it rather than introducing another curated repository implementation with different semantics.

| Proposed application port | Minimum operation | Purpose |
| --- | --- | --- |
| InvestigationSnapshotProvider | load() -> InvestigationSnapshot | Enumerate/validate selected curated folders, obtain repository aggregates and return one stable in-memory snapshot with revision |
| DocumentationRepository | list_for(investigation_id) -> tuple[SourceDescriptor,...] | Read shared registry/capture history without treating it as scientific claims |
| EvidenceSourceReader | read(source_handle, revision) -> SourceReadResult | Resolve approved evidence and deliver bytes safely |

InvestigationSnapshot contains a revision and immutable aggregate/read-only projections. Its implementation uses the existing repository for scientific deserialization. Directory preflight and publication policy are adapter responsibilities; fingerprinting is not placed in the domain.

Use cases are classes with constructor DI and __call__ operations. ExploreInvestigations(snapshot, query) and GetInvestigationDetail(snapshot, id, query, detail_scope) share one snapshot; Source descriptors remain scoped to its investigation/revision. The composition root loads/injects a snapshot once, not a separate directory read on every detail click. A repository can still be replaced by an in-memory adapter for application tests.

| Failure / result state | Required behavior |
| --- | --- |
| InvalidExplorationQuery | Field-specific message; keep last applied query until user fixes draft inputs |
| InvestigationNotFound / RecordNotFound | Clear expired selection with notice; no fallback to an arbitrary row |
| DatasetUnavailable | Initial-load data state; no fabricated zero-results catalog |
| DatasetInvalid | Affected id and validation summary; fail the scientific snapshot rather than skip malformed pairs |
| DatasetBusy | Checkpoint/publication unavailable; retain prior snapshot only with explicit stale state |
| SourceUnavailable | Catalog/detail stay usable; show source and locator, but no claimed preview |
| SourceUnsupported | No inline parser/viewer for the type; approved download may still be offered |
| SourceChanged | Expected pinned digest differs; show mismatch, do not present changed bytes as the cited version |
| SourceDenied | Unregistered/out-of-scope reference or disallowed URL scheme; no file read |

These names are proposed application errors/result variants, not currently implemented exceptions. Translate expected OSError/JSON/CSV/Pydantic failures at the adapter boundary, preserving causes for development diagnostics; do not catch every Exception and return an empty list. Invariants remain in the domain. File-I/O failures are application/infrastructure failures, not new scientific DomainErrors. User-facing messages omit stack traces, absolute machine paths and secrets; diagnostics retain useful investigation/source ids.

## 5. Snapshot publication, integration preflight and source integrity

### 5.1 Required preflight

- Determine selected curated directory ids from the curated directory, not from all registered raw investigations: a valid MVP may curate only a selected 8–10 investigations.
- Every selected investigation directory must have both agreed files. A CSV-only or JSON-only directory is an error. Ignore only explicitly noninvestigation technical files/directories; no blanket silent skip rule.
- Directory id must equal Investigation.id; TestPoint parent ids must agree; ManualMetadata.investigation_id must equal its parent; each TestPoint.record_level must agree with the declared investigation granularity for the current model.
- Validate required core headers, unique headers, documented extras, unique composite record ids and finite numeric conditions. An unsupported incompatible schema fails with an actionable message; unknown optional metadata fields are not treated as confirmed capabilities merely because the current aggregate ignores extras.
- Existing canonical values/notes are not repaired here. These are structural integrity checks, not another normalization pipeline.

Two gaps were reproduced during QA: CuratedRepository.ids currently omits a directory with only test_points.csv, and Investigation currently accepts a manual_metadata.investigation_id different from its own id. These remain open integration defects, not claimed fixes. See the QA report and ADR entries.

### 5.2 Honest snapshot guarantee

CuratedStore.save writes JSON and CSV separately. A reader cannot prove they belong to one producer generation by seeing stable hashes twice. A stable metadata-new/CSV-old pair can still validate. Do not label optimistic fingerprint checks atomic publication.

Stage-1 operating contract: load or refresh only after a completed curation command and while the producer is idle, then work from the frozen in-memory snapshot. This is an operator/workstream checkpoint, not a claim that the application can automatically detect every external writer. Before/after file fingerprints with one retry detect observed interference; absent a checkpoint, keep the old snapshot or report DatasetBusy. Deployment/run documentation must state this limit.

If arbitrary live refresh during concurrent curation becomes required, first specify a producer manifest/commit marker or immutable version-directory publication with the curation owner. This QA does not change the producer or approve a new on-disk schema. Source availability and schema alignment are prerequisites for integrated release; pure query/use-case implementation need not wait for a live publication protocol.

Maintain separate scientific and documentary revisions. Optional source-list changes need not invalidate scientific query results. A documentation error does not convert a valid scientific dataset into a partial catalog.

### 5.3 Evidence resolution

Opaque source handles resolve only to files already cited by a loaded aggregate or associated through the registry. Resolve absolute paths/junctions/symlinks and ensure the final file stays inside approved roots before reading. A widget must not submit a path directly to Path/open. Original online URLs must use http/https before becoming clickable; deny file/javascript/data schemes.

Expected hashes are available for curated source_files and captured artifacts where recorded; compare them when serving those pinned bytes. An evidence path without a pinned digest is marked version-unpinned. Do not claim source-version verification from path existence or from computing its current hash alone. Preserve locator/quote even if the source is unavailable; no re-extraction/OCR or fuzzy quote verification occurs on a widget rerun.

Do not execute captured HTML or treat document instructions as trusted. Escape raw text; use downloads and safe previews. For P0, download plus a visible page/paragraph/row locator is sufficient; an inline PDF viewer is optional and cannot be assumed from a local path. No automatic external fetch is triggered by browsing.

## 6. Streamlit state, accessibility and nonfunctional acceptance

Per session, keep draft_query, applied_query, selected investigation/record, detail scope, selected columns and snapshot revision. Only Apply changes applied_query. Validation failure preserves current results and shows the draft error. Reset clears selections/extra-column choices and restores defaults. Refresh validates before replacing the snapshot; revalidate selections and query options against it and announce any removal. Browser reload/process restart need not persist selections in stage 1; deep links/session restoration are deferred.

Shared resource caches contain only thread-safe read services or immutable snapshot data. No session-specific query or mutable shared dataframe is stored in a global resource. Copy presentation data before applying formatters or adding columns. Repeated widget events reuse the loaded snapshot without reading source PDFs or recalculating curation.

Use labelled controls, unit-bearing headers, status text in addition to color, and meaningful loading/error/empty states. Provide labelled Investigation and TestPoint selector fallbacks if table selection is unavailable or inaccessible. No critical fact is available only in a hover tooltip or a chart. Optional advanced filters do not hide the current applied filter summary. Test ordinary browser width and keyboard access in the actual installed Streamlit version.

Presentation defaults: at most four significant digits for noninteger quantity display, while preserving full precision/raw in the inspector. Do not round before filtering, sorting or calculating ranges. If distinct endpoints would display as equal, expand precision or show an approximation marker and exact inspector values. Counts and ids are not formatted as floating point. Source content and long notes wrap in the inspector rather than being permanently truncated.

Prototype performance targets, to measure on a recorded local environment near the current data scale: initial validated catalog within 5 seconds, cached query/detail navigation within 1 second. Report source hashing/download preparation separately, and record a baseline before optimizing. These are proposed prototype targets, not proven measurements or reasons to skip validation. Stage 1 must work without internet or LLM credentials for available local data.

## 7. Change-control rule

Requirements are SPEC-001; this design defines proposed consumer types; tasks map requirements to acceptance evidence. A schema or query-semantics change updates all affected documents and test expectations before implementation changes. Source curation remains independently owned. No aggregate schema change, UI feature or scientific inference becomes accepted merely because this design lists it. Review the QA report's runtime prerequisites before claiming stage-1 completion.
