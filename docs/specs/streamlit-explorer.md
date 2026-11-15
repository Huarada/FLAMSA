# SPEC-001 — Streamlit investigation explorer

Status: implementation started; consumer defaults authorized by the user's request to begin development. Full acceptance remains pending.
Date: 2026-11-14.
Revision: 0.3 — documentation QA completed; runtime integration gaps remain tracked.
Implementation progress: see [first dashboard implementation](../dashboard.md) for delivered functionality, verification and remaining contract refinements. The baseline below records the preimplementation state, not the current feature inventory.
Scope: implementation stage 1, followed by explicit integration boundaries for stages 2–4.
Authority: CLAUDE.md, the project skill, ADR-0007/0008/0016/0022/0026/0029/0032/0033. This specification does not override scientific curation decisions.

Companion documents: [DDD and application contract design](streamlit-explorer-design.md), [implementation tasks and acceptance traceability](streamlit-explorer-tasks.md), and [QA findings and readiness](streamlit-explorer-qa.md). Requirements live here; responsibilities/types live in the design; executable work and verification coverage live in the task plan. None of these documents is an implementation or an approval of scientific data.

## 1. Product objective

An aerospace researcher or student can find an Investigation, inspect its actual experimental coverage and limitations, and trace a displayed value or claim to its source. The first prototype must be useful without an LLM, network access or finalized manual metadata.

Primary journey: open Explore → inspect available investigations → apply filters → select an Investigation → inspect matching TestPoints → inspect a value or claim's evidence.

Secondary journey: inspect missing data, inferred transformations and draft manual metadata to understand whether an Investigation can support a later scenario ranking.

Stage 1 is exploratory. It must not produce a safety certification, a flammability prediction, a relevance score, or a generated scientific explanation.

## 2. Observed implementation baseline

This is a snapshot of the repository, not a fixed acceptance count. Curation is changing concurrently.

| Available now | Verified source of the contract | Consumer implication |
| --- | --- | --- |
| 15 curated investigations, 1,615 records at inspection | `data/curated/*/{investigation.json,test_points.csv}` | Counts are calculated at load time, never hardcoded |
| Typed `Investigation` and `TestPoint` | `src/psi_fire/domain/model.py` | Consume validated objects, not independently parsed CSVs |
| `InvestigationRepository.all()/get()` | `src/psi_fire/application/ports.py` | Existing inward-facing repository contract |
| `CuratedRepository`, plus `ids()/to_dataframe()` helpers | `src/psi_fire/infrastructure/curated_store.py` | Infrastructure implementation, injected at composition root |
| Column dictionary, source hashes/encoding, source notes and variable classification | `Investigation` | Render available semantics instead of hardcoding investigation-specific columns |
| `ManualMetadata`, `Claim`, `Evidence`, `Sensor` | `src/psi_fire/domain/manual.py` | Preserve claim status, evidence and review state separately |
| Manual metadata for BASS-II, SAFFIRE-III and ACME-CFI-G, all draft at inspection | `data/manual/`, attached to curated aggregate | Other investigations remain browsable without these fields |
| Shared external source registry and captures | `data/sources.json`, capture metadata | An association or successful download is not a verified hardware claim |

There is no Streamlit app, explorer use case, ranking service, RAG service or Narrator implementation in this baseline. Their names below describe proposed interfaces, not existing code. Streamlit version and runtime availability must be established when implementation starts; no version-specific API behavior is assumed here.

## 3. Delivery boundaries

| Priority | Stage-1 requirement |
| --- | --- |
| P0 | Load validated investigations; show catalog and record-level counts |
| P0 | Apply categorical and numeric filters with the semantics in section 6 |
| P0 | Inspect one investigation and its filtered records |
| P0 | Show missingness, raw values, units, notes, source locators and the column definitions needed to interpret displayed values |
| P0 | Show manual claims with draft/review status and their evidence |
| P0 | Handle missing metadata, no matches and invalid datasets explicitly |
| P0 | Open/download sources cited by displayed claims or records, or show an explicit unavailable/unsupported state |
| P1 | Browse additional archived documentation, capture history and failures beyond cited evidence |
| P1 | Select extra quantity columns, family presets and browse the complete column dictionary |
| Later | Side-by-side comparison, complete clean-dataset export and data card |
| Later | HabitatScenario, ranking, ScoreBreakdown, RAG, LangGraph and LLM narrative |

The user subsequently authorized a visible, explicitly disconnected AI workspace (section 14). No fabricated AI answers/ranking, editable scientific data, authentication, write-back review workflow, vector database or new multi-agent execution is included in stage 1.

## 4. Data consumption and ownership

### 4.1 Allowed inputs

1. Curated aggregates loaded through the existing repository.
2. An external-documentation adapter resolving associations through `data/sources.json` and reading archived capture metadata.
3. A source-access adapter that resolves registered or cited source files inside the approved data roots and returns evidence previews or downloadable bytes.

The Streamlit interface does not read `data/manual/`, raw CSVs, PDFs or HTML directly. ManualMetadata is consumed from `Investigation.manual_metadata` after curation, not joined independently in the UI. A manual-file edit becomes visible only after successful recuration and dataset refresh.

Archived sources supplement the validated aggregate; they never silently replace its scientific claims. Loading the app does not recurate data, download pages, parse PDFs or call an LLM.

### 4.2 Display-field mapping

| Display field | Current exact data location | Missing/status rule |
| --- | --- | --- |
| Identity | `Investigation.id`, `psi_id` | Required by the current model |
| Title | `study_metadata.get("study_title")` | Fall back to id; no acronym expansion invented |
| Objective / approach | `study_metadata.get("objective")` / `.get("approach")` | Not reported when absent; label extracted study metadata |
| DOI | `study_metadata.get("doi")` | Optional source text; validate a link before making it clickable |
| Study metadata provenance | `study_metadata_source` + original field label | Show source-record origin; do not mark metadata human-reviewed merely because a file loaded |
| Hardware | `manual_metadata.hardware` | Missing metadata and ClaimStatus not_reported are distinct |
| Sensors | `manual_metadata.sensors` with `value.instrument` and optional `value.measures` | Preserve each Claim; missing measures displays Not stated; no reconstruction from instrument names/camera filenames |
| Gravity / pillars | `manual_metadata.gravity_regime` / `.pillars` | Use claim values/status/evidence, not directory-name inference |
| Nominal atmosphere | `manual_metadata.nominal_atmosphere` | Optional Claim, not a TestPoint condition |
| Earth applications | `manual_metadata.earth_applications` | Optional detail; no empty-state promise of terrestrial applicability |
| Record conditions and lineage | `TestPoint` core fields | Typed values plus row provenance, raw values and notes |
| Additional columns | `TestPoint.extras` and `Investigation.columns` | Never treat a column absent from a specific investigation as measured zero |
| Dataset sources | `source_files[].path/sha256/encoding`, `source_notes[]` | Hash/encoding are technical provenance, not quality grades |
| Full-investigation variable classification | `varied_variables`, `held_constant_variables`, `unreported_variables` | Computed by the current domain model; scope explicitly labelled |

The raw `study_metadata.experiment_hardware` field can be shown as an extracted source-record entry in the evidence view. It does not substitute for a reviewed `manual_metadata.hardware` Claim or become a hardware-filter option automatically. New fields introduced by curation require an explicit contract review; UI code must not scrape alternate files to fill them.

### 4.3 Ownership while curation continues

| Area | Ownership during parallel work |
| --- | --- |
| Raw sources, adapters, normalization, ManualMetadata, evidence verification, curated outputs | Curation workstream |
| This specification, explorer application use cases, presentation models, Streamlit views | Dashboard workstream |
| Domain contracts, repository ports, dependency configuration, ADR | Shared; inspect latest state and coordinate before editing |

The dashboard must not patch a suspect datum. It displays the source note and the current canonical value; scientific corrections belong to curation. A proposed schema change is recorded before updating consumers. Avoid concurrent writes to shared files.

## 5. Proposed application contracts

The implementation remains Python-only; an HTTP API is unnecessary. Domain values and application results are plain typed Python objects. pandas is confined to infrastructure/interface.

| Proposed use case | Input | Output and responsibility |
| --- | --- | --- |
| `ExploreInvestigations` | Immutable `ExplorationQuery` | `ExplorationResult`: catalog rows, matching record references, available options, totals and dataset revision |
| `GetInvestigationDetail` | `investigation_id`, applied query | Full investigation summary, matched records, column dictionary, variable classifications and manual claims |
| `ListInvestigationSources` | `investigation_id` | Validated source references and external captures; acquisition state separated from claim/review state |
| `ReadEvidenceSource` | Opaque source reference and locator | Approved preview/download result or a typed unavailable/unsupported result |

`ExplorationQuery` fields: search text; investigation ids; record levels; fuel names/phases; flow directions; optional O2/pressure/flow bounds; O2 basis; per-active-numeric-field include-missing option; row provenance statuses; has-note option; optional hardware/sensor/pillar/gravity selections; manual review state; catalog sort. Multi-value fields are immutable tuples of canonical ids/enums or existing curated labels; absent bounds are None. Missing selections use an application-level sentinel, never a fabricated domain enum. Default order is id ascending. Display precision and selected extra columns are presentation settings, not scientific filter predicates.

`ExplorationResult` contains at least: dataset revision, total investigations/records, matching investigations/records, counts by RecordLevel, stable catalog rows, filter options and warnings. Selected investigation identity and selection validity are interface state derived from the returned identities, not state stored by an application use case. Catalog sorting never changes which records match. The exact proposed types and dependency ports are defined in the companion design.

Matching record identity is `(investigation_id, test_point_id)`. No row number, dataframe index, fuel name or source test number is used as UI identity.

`DatasetRevision` is an infrastructure-calculated fingerprint of validated curated input pairs and the registry. It is not a new scientific domain field. Optional documentation history has a separate DocumentationRevision so a new page capture does not rebuild all scientific results. All scientific use-case results in one screen refer to a single loaded snapshot. A fingerprint detects changed bytes; it is not proof that the producer published an atomic generation. The publication/checkpoint requirement is defined in the design. The application does not accept a new schema merely because JSON parsing succeeds; repository/domain validation and integration checks must pass.

Suggested implementation locations: use cases and result/query types under `application/`; optional scientific filter predicates under `domain/`; source adapters under `infrastructure/`; rendering and dataframe formatting under `interface/`; dependency injection only in `interface/app.py`. Existing repository methods are reused without moving pandas inward.

## 6. Filter contract

### 6.1 General semantics

- Default: all investigations and all record levels, no numeric bounds or scientific metadata restrictions. A user sees the full curated catalog, including records with missing conditions.
- Multiple selections within one filter use OR; different filters use AND.
- All row-level predicates must match the same TestPoint. An Investigation is retained if at least one of its records matches all active row predicates and its investigation-level predicates pass.
- Investigation-level metadata filters constrain the parent, then row filters constrain its records. Do not combine separate experiments into an apparent matching condition.
- A cleared categorical multi-select means unrestricted, not zero results. For enum/value absence use an explicit application sentinel; missing manual metadata, a Claim marked not_reported, and an explicitly empty list have distinct states. Do not collapse them into one domain value called Not reported.
- Apply/reset controls commit the filter set together. Values typed but not applied must not change displayed metrics. Reset restores the default query.
- Primary filter options come from the complete loaded snapshot and remain stable while filtering. Avoid options disappearing and resetting user selections. If recuration removes an option, announce and clear only the invalid selection.
- Metadata-dependent controls remain discoverable but disabled with an explanation when the whole dataset lacks that field. Missing metadata in one investigation never prevents browsing it.

### 6.2 Filter inventory

| Filter | Scope and source | Control/default | Exact behavior |
| --- | --- | --- | --- |
| Text search | Investigation id, PSI id, available study title/objective | Text, empty | Literal case-insensitive substring; no regex, embeddings or invented summary; does not search numeric cells |
| Investigation | `Investigation.id` | Multi-select, unrestricted | Canonical ids only |
| Record level | `TestPoint.record_level` | Multi-select, all | `test`, `test_day`, `test_matrix`; counts and labels stay separate |
| Fuel | `fuel_name` | Multi-select, unrestricted | Use curated labels; no new alias normalization in UI |
| Fuel phase | `fuel_phase` | Multi-select, unrestricted | solid/liquid/gas plus explicit missing option |
| Flow direction | `flow_direction` | Multi-select, unrestricted | Actual enum values plus missing; no synthesized quiescent value from absent speed |
| O2 basis | `o2_basis` | Multi-select while no O2 numeric filter is active; single selected basis for active O2 range, default ambient | Never silently convert an explicit choice; require an unambiguous basis before applying a numeric O2 range |
| O2 range | `o2_percent_min/max` | Optional numeric minimum/maximum, percent | Same-record interval overlap; never substitute burner-stream O2 for cabin O2 |
| Pressure range | `pressure_psi_min/max` | Optional numeric minimum/maximum, psi | Same-record interval overlap |
| Flow speed range | `flow_speed_cm_s_min/max` | Optional numeric minimum/maximum, cm/s | Same-record interval overlap |
| Row provenance | `provenance_status` | verified/inferred, unrestricted | Describes row lineage; not scientific certainty or manual review |
| Has curation note | `provenance_note` | Any/with note/without note | Nonempty note test; no guessed severity classification |
| Hardware | `manual_metadata.hardware` | Current curated labels, unrestricted | Separate missing and explicit not_reported; no family inferred from free-text hardware names |
| Sensor | `manual_metadata.sensors[].value.instrument` | Current curated labels, unrestricted | Any selected known instrument matches; an empty list means no mapped entries, not proof of no sensors |
| Pillar | `manual_metadata.pillars` | Current enum labels, unrestricted | Any selected pillar matches; explicit empty list is distinct from missing metadata |
| Gravity | `manual_metadata.gravity_regime` | Available enum labels, unrestricted | partial_emulated is labelled emulation; do not offer measured partial gravity |
| Manual review | `manual_metadata.review_status` | All/draft/reviewed/metadata unavailable | A verified claim in a draft metadata file remains visibly unreviewed |

Hardware, Sensor, Pillar and Gravity filters are supported when validated manual metadata exists. Their current labels come from values, not filenames or user-supplied source associations. Draft values are included by default with visible status; a user can restrict to reviewed metadata.

### 6.3 Numeric range semantics

For source interval `[a,b]` and requested interval `[L,U]`, match when `b >= L` and `a <= U`, omitting an inequality when that requested bound is unset. Boundaries are inclusive. A single source value has `a == b`. Application query validation must reject L > U, NaN/infinity and invalid domain ranges even when called without Streamlit; the interface also provides immediate validation feedback. O2 bounds are within 0–100; pressure/flow bounds are nonnegative. An active range has at least one finite bound; two unset bounds mean no numeric filter.

An active numeric filter excludes missing source intervals by default. Its explicit include-missing toggle adds records with missing values for that field; these are labelled `Not reported`, not matches supported by measurements. The table and counts identify how many retained records lack each active condition. With several numeric filters, missing policy is applied independently to each one.

For an active O2 range, a known interval must have the selected O2 basis and overlap the requested range. An unknown O2 interval is retained by include-missing only if its basis is the selected basis or is itself unknown; an explicit different basis never matches. Unknown basis is visibly unsupported, not inferred as ambient. This numeric basis rule replaces the inactive standalone basis filter. If several standalone bases were selected before activating an O2 range, the user must choose one before Apply; do not change it silently.

Intervals and lists can have been reduced to envelopes by curation. Overlap establishes reported range overlap, not that an exact condition or every interior value was experimentally tested. Display `_raw` when available so the user can inspect discrete lists and approximations.

Filter only per-record conditions. NominalAtmosphere is shown separately with its Claim status; it never fills missing TestPoint O2/pressure or changes numeric filtering in stage 1. Aggregate extrema and nominal conditions do not constitute a matched test.

Example: record A has ambient O2=30% and pressure=14.7 psi; record B has ambient O2=21% and pressure=10.2 psi. O2 >=30% AND pressure <=10.2 psi returns neither record and does not retain the investigation based on combined extrema.

## 7. Interface specification

All interface strings are English. Use Streamlit's native layout and widgets first. Layout choices must be checked against the installed Streamlit version before coding.

### 7.1 Explore view

1. Product name, concise purpose, loaded dataset revision and refresh action.
2. Filters grouped as Investigation, Experimental conditions, and Evidence/metadata. Advanced controls are collapsible; users do not face all controls at once.
3. Counts: matching investigations / total investigations, and matching records grouped by test/test_day/test_matrix. Never label all rows as experiments or ignitions.
4. Catalog table with stable selection. Selecting a row opens that investigation's detail while preserving the applied filters.
5. Clear empty-state message with active filter summary and reset action.

Catalog default sort: canonical investigation id ascending. Other explicit sorts: matching record count, total record count, and title. Ties resolve by id. No relevance/risk ranking is implied.

| Catalog column | Meaning |
| --- | --- |
| Investigation / PSI id | Stable identity |
| Title | Available study title; fall back to id with no synthesized title |
| Record level | Actual granularity |
| Matching / total records | Filtered rows versus aggregate total |
| Fuel phases | Values among matching rows; missing labelled |
| Ambient O2 coverage (%) | Envelope among matching ambient-basis rows only, with known/total count |
| Oxidizer-stream O2 coverage (%) | Separate optional column when applicable |
| Pressure coverage (psi) | Envelope among matching rows with known pressure; count reported |
| Metadata review | draft/reviewed/unavailable |

Hardware and pillars are optional catalog columns rather than mandatory wide text. Coverage cells say `Reported range`, not `Safe range`. A displayed envelope may span gaps. Totals and current-filter coverage must not be conflated. Coverage denominators and deterministic sort behavior are specified in the design; no graph is required for stage-1 P0. A P1 coverage chart may show reported/missing counts by quantity and record level, with the same denominators; do not invent interval midpoints or predictive curves.

### 7.2 Investigation detail

Use sections or tabs: Overview, Test points, Evidence and documentation. Keep identity, record level, manual review badge and matching/total count visible above them.

Overview shows: source-supported title/objective when available; fuels; conditions and missingness; hardware; gravity; pillars; sensors and what they measure only when stated; nominal atmosphere as a separate claim; and investigation-level source notes. Sensor.instrument is one plain curated label (ADR-0033); counts/type/location may appear in the evidenced Claim.note, not a UI-inferred model field. Optional measures=None displays Not stated. Each manual fact shows its Claim status and evidence access. Conflicting source notes remain visible without UI reconciliation. Proposed richer sensor fields in ADR-0034 are deferred, not silently added to this consumer contract.

Derived varied/held_constant/unreported variables from Investigation describe the full dataset, not the filtered subset. Label that scope explicitly. Recomputing these for a filtered subset is outside stage 1.

Test points default to records matching the current query. An explicit `Show all records in this investigation` control may expand scope; the changed scope is shown and must not alter the global filter result.

### 7.3 TestPoint table and inspector

| Default visible group | Fields |
| --- | --- |
| Identity and granularity | `test_point_id`, `record_level` |
| Fuel | `fuel_name`, `fuel_phase` |
| Atmosphere | `o2_basis`, `o2_percent_min/max`, `pressure_psi_min/max`, `diluent` |
| Flow | `flow_speed_cm_s_min/max`, `flow_direction` |
| Lineage | `provenance_status`, note indicator |

`investigation_id` stays in the underlying result even if omitted as redundant in a single-investigation view. Each numeric header states its canonical unit. Min/max pairs may be formatted into one display column; underlying values remain separate and unrounded. A missing display value is `Not reported`, never 0, an empty string implying zero, or a plotted zero.

Additional quantities and outcomes are selected from `Investigation.columns`. Their kind, unit, original headers and derivation are accessible from a data dictionary. No hardcoded global outcome schema is invented. Camera filename meta columns are not presented as sensor specifications.

Selecting a record opens an inspector with all core fields, all extras, `_raw` siblings, source file, source row/range, row lineage status/note and relevant column derivations. It must be possible to trace a displayed value to row + original header; a normalized value does not hide its raw representation.

Text in quantitative source cells remains visible through raw values and notes. Do not compute replacement numerical values for `Insignificant`, `Complete`, ambiguous thicknesses or unavailable sensor readings. Numeric sorting uses underlying values, not formatted strings; missing values sort last. Table selection survives column sorting by using record identity.

### 7.4 Evidence and documentation

For each Claim: render value, ClaimStatus, note, ManualMetadata review state, literal quote and Evidence source/locator. For reviewed metadata, show reviewer and review date. Quote presence verification is not independent scientific validation.

Provide the quote as copyable source text without smart-quote substitution, paraphrasing or line reflow that changes its content. Preserve Evidence entries individually; do not join separate quoted fragments into a fabricated continuous sentence. Current evidence-line/paragraph verification follows ADR-0032; the viewer does not implement a competing verifier.

Local evidence is delivered through an application use case and adapter. Do not assume a repo-relative path is a browser-accessible hyperlink in Streamlit. Provide an approved download and a textual locator; an inline viewer or PDF page link is used only if the implementation actually serves it correctly. Source URLs are optional and explicitly labelled original online source.

External documentation lists source id, title if available, requested/final URL, capture time, capture status and association status. The latest attempted capture and latest successful capture are distinguished; a later failure does not erase an earlier successful archive. A failed HTML response is labelled unavailable and never previewed as scientific Markdown. Sources not yet claimed by manual metadata remain reference material.

Preview plain escaped text/Markdown safely; do not execute captured HTML, scripts or document instructions. Source resolution must remain within approved roots. No raw filesystem paths supplied by a widget are accepted. Unsupported or absent sources show the locator and a clear unavailable state without hiding the claim.

## 8. Scientific and quality presentation rules

| State | Required display |
| --- | --- |
| Missing TestPoint numeric value | Not reported; counted as missing for that quantity |
| `manual_metadata is None` | Metadata unavailable; no assumed hardware, gravity or pillar |
| Claim `not_reported` | Not reported + search note; no guessed value |
| Claim `inferred` | Inferred + derivation note + evidence |
| Claim `verified` in draft metadata | Source-stated + Draft/unreviewed badge; never visually equivalent to reviewed |
| Empty pillar value with evidence | No direct pillar assigned; not a load error |
| Empty sensors list | No sensor entries mapped; not evidence that no sensors exist |
| NominalAtmosphere field absent/null | No additional nominal claim available; does not by itself establish per-test coverage |
| `partial_emulated` | Partial gravity emulation; never measured lunar/Martian gravity |
| Source conflict | Show both documented statements and the existing note; do not choose automatically |

No single confidence percentage is derived from lineage status, file hashes, evidence counts or review state. Known-field fractions are named completeness metrics with an explicit denominator, never scientific reliability. Record-level lineage and manual claim/review states remain separate.

There are no partial-gravity measurements represented by the current PSI data scope. Scientific extrapolation and fire-safety conclusions belong to later scenario/XAI functionality, with its required limitations.

## 9. Loading, state and failure behavior

- Composition root creates the repository and use cases. Streamlit state contains only selections, applied query and presentation state; domain/application code does not depend on Streamlit.
- Cache only read-oriented resources and results keyed by dataset revision and immutable query. Any shared cached snapshot must be treated as immutable; queries, selections, errors and downloaded-source state remain per session. Do not cache a directory-based repository forever without invalidation or expose mutable aggregate dictionaries to widget callbacks.
- Refresh is supported at an acknowledged completed curation checkpoint for stage 1. The producer writes metadata/CSV separately today, so unrestricted live refresh during active curation is not guaranteed coherent. Before/after fingerprints and one retry detect observed concurrent writes but cannot prove a stable pair belongs to one generation. An immutable publication/manifest protocol is a later integration option; this dependency is explicit, not silently assumed implemented.
- Empty curated directory, missing pair, invalid JSON/CSV or model validation failure produces a clear data-load state, not a success message with zero investigations. Do not silently skip a broken investigation.
- If a previously valid snapshot is retained after a refresh failure, label it stale and show its revision; initial load has no stale fallback.
- Sources/capture failures may be shown separately while the validated scientific catalog remains usable. A missing scientific row file cannot be treated as an optional documentation failure.
- Display loading feedback. Widget reruns do not trigger capture, curation or LLM calls. Native tables handle the current data scale; pagination or a new database requires measured need.
- Reset/detail navigation preserve a consistent applied query. If a selected Investigation disappears after refresh/filtering, clear selection and explain; no stale row detail is shown as a current match.

## 10. Acceptance scenarios

| Id | Given / When | Expected outcome |
| --- | --- | --- |
| AC-01 | Valid curated dataset, initial load | All validated investigations listed; counts computed dynamically and split by RecordLevel |
| AC-02 | No manual metadata for an Investigation | It remains browsable; metadata unavailable is explicit |
| AC-03 | Source-stated hardware in draft metadata | Value, claim status, evidence and draft badge all shown |
| AC-04 | Numeric filter boundary equals a source bound | Inclusive match |
| AC-05 | Different rows independently meet O2 and pressure | Investigation excluded unless one row meets both |
| AC-06 | O2 filter is activated | Basis is explicit; oxidizer-stream records cannot silently satisfy an ambient filter |
| AC-07 | Unknown pressure and active pressure filter | Excluded by default; included only by its missing-value option and labelled unsupported by pressure data |
| AC-08 | Numeric range from discrete raw list | Reported envelope and raw list remain inspectable; no exact tested-condition claim |
| AC-09 | Nominal atmosphere available but row pressure absent | Nominal claim shown separately; row pressure stays missing and numeric filter semantics unchanged |
| AC-10 | `test_matrix` matches range filter | Result labelled matrix record, never individual experimental run |
| AC-11 | User changes filter widgets before Apply | Results and metrics still reflect the applied query |
| AC-12 | No records match | Empty state, active filters and Reset available; no plots or fabricated matches |
| AC-13 | Extra quantity column selected | Canonical unit, original headers and derivation accessible from dictionary |
| AC-14 | Select and sort a TestPoint table | Same composite record identity opens the correct inspector |
| AC-15 | Inspect normalized value | Canonical/raw values, source row, column mapping and lineage visible |
| AC-16 | Zero/negative/suspect value has a curation note | No UI correction; currently curated value/note rendered accurately |
| AC-17 | Source reference is local | Download/preview works without assuming filesystem links are HTTP routes |
| AC-18 | External source failed, or source id only associated by user | Acquisition/review state visible; no verified hardware fabricated |
| AC-19 | Filter subset changes | Full-investigation variable classification retains explicit full-dataset scope |
| AC-20 | Files change during refresh | Complete validated snapshot or visible error/stale state; no mixed-version view |
| AC-21 | Invalid or missing curated pair | Load failure identifies affected Investigation; no silent skip |
| AC-22 | No metadata is human-reviewed yet | Reviewed-only filter produces a truthful empty state |
| AC-23 | Pillars value is explicitly empty | No direct pillar assigned; missing and not_reported states remain distinct |
| AC-24 | Application has no internet or LLM credentials | Explorer and archived evidence still operate for locally available data |
| AC-25 | User opens sources or filters repeatedly | No source downloads, dataset writes or changes to raw/curated files |
| AC-26 | Sample/burner geometry is unavailable or only embedded in a fuel description | Preserve description; do not invent normalized dimensions or geometry |
| AC-27 | Material-fuel study uses gaseous fuel as an emulator | Physical FuelPhase remains gas; source-supported research purpose is displayed separately |
| AC-28 | Adiabatic temperature, peak burner temperature and camera observations coexist | Preserve quantity identities; do not label all of them measured flame temperature |
| AC-29 | Detection dataset reports smoke age and mass-loss rate but no detector latency | Available measurements shown; no detection-time or detector-performance metric fabricated |
| AC-30 | Model user inspects repeated/summarized rows | Record granularity, source ids, duplicate/continuation notes and raw ranges retained |
| AC-31 | Comparing investigations with different hardware or measurement bases | Differences are explicit; no pooled scientific result or causal conclusion generated |
| AC-32 | A RAG context contains mixed draft, inferred and reviewed claims | Evidence identity, claim status and review state travel with every included claim |
| AC-33 | User requests lunar/Martian applicability | Evidence relevance is distinct from measured partial-gravity support; limitations remain visible |
| AC-34 | An instrument has a calibration document | Calibration availability does not create an uncertainty estimate or establish valid calibration for a specific run |
| AC-35 | Manual metadata contains an Earth application | Application is rendered with evidence/status; no terrestrial benefit invented from a shared instrument name |
| AC-36 | Experimental conditions have gaps within a min/max envelope | Coverage labels do not imply continuous sampling, a flammability threshold or an exact tested point |
| AC-37 | Query is called without Streamlit using reversed/nonfinite bounds or unknown ids | Typed validation result; no file access or stale-query substitution |
| AC-38 | O2 range has ambient basis and include-missing enabled | Unknown O2/unknown basis may appear as unsupported; explicit oxidizer-stream rows do not match |
| AC-39 | Selected hardware, not_reported claim and unavailable metadata coexist | Matching policies distinguish known value, explicitly not_reported and unavailable metadata |
| AC-40 | Tests use repository/application ports without importing infrastructure | Use cases work with in-memory port implementations and return plain typed results |
| AC-41 | Two browser sessions use the same loaded dataset | Filters/selection are independent; neither changes cached scientific objects |
| AC-42 | Curated folder contains a CSV-only directory or a selected pair has mismatched identities | Snapshot fails validation rather than silently omitting/attaching data |
| AC-43 | Refresh requested while producer is actively writing without publication protocol | Explicit busy/checkpoint-unavailable state or retained labelled snapshot; no atomic-generation claim |
| AC-44 | Filtered ambient rows include missing intervals and another O2 basis exists | Coverage denominator is scoped and missing counts reconcile with displayed rows |
| AC-45 | Evidence source is missing, changed, outside scope or unsupported | Typed evidence result; scientific catalog remains available; no arbitrary filesystem read |
| AC-46 | App restarted or reset with invalid/removed selection | Reset uses defaults; expired selection is cleared explicitly; UI state is not assumed durable |
| AC-47 | User cannot interact with table row selection | Labelled investigation/record selectors provide the same detail and evidence path |
| AC-48 | Implementation declares a stage-1 release | Required task/acceptance evidence and runtime smoke results recorded; future-stage scenarios remain explicitly deferred |
| AC-49 | Sensor.instrument is present and Sensor.measures is None | Display plain instrument label and Not stated; no guessed measurement/type/count |
| AC-50 | A reviewer copies an Evidence.quote to search the source | Exact stored quote is available without typographic substitution or joining separate evidence fragments |
| AC-51 | User selects comparison investigations and axes | Scatter and line views consume the applied-filter result; chart-only selections do not silently alter the catalog |
| AC-52 | Multiple records share an x value | Lines show an explicitly labelled median per investigation/fuel/flow/basis group; raw scatter remains available |
| AC-53 | Plot axis has missing or nondegenerate interval values | Exclude the unsupported pair and report excluded count; never invent a midpoint |
| AC-54 | A record is a daily summary or planned matrix | Do not plot it as an individual test pair or fill conditions from nominal atmosphere |
| AC-55 | User opens investigation details | Clearly named tabs identify research context, experimental records/raw values and cited source downloads |
| AC-56 | AI integration is absent | Copilot area is visible, labelled Not connected, with disabled input/action and no generated responses |
| AC-57 | User inspects copilot context | Actual revision, applied filters, result investigation ids and chart configuration are exposed; no invented facts |
| AC-58 | Later copilot proposes dashboard changes | Only validated application actions can affect chart/filter state; no arbitrary code, scientific-data edits or score calculation |
| AC-59 | User opens the Dashboard | Top navigation, horizontal research filters, metric cards and reference-led chart grid are visible without a filter sidebar |
| AC-60 | User opens/closes the Research copilot toggle | Panel is hidden initially; opening/closing it preserves applied filters and selected chart quantities |
| AC-61 | User switches Dashboard/Investigations/Evidence | Scientific snapshot and query remain shared; records/source downloads remain reachable |
| AC-62 | A coverage interval is a singleton | A visible endpoint marker represents the value without inventing interval width |
| AC-63 | User exports the current view | JSON identifies revision, applied filters and result ids; it is labelled a view configuration, not the clean-dataset export bundle |
| AC-64 | Selected investigations lack paired quantities for the profile axes | Show chart-selected versus plotted counts and per-investigation primary exclusion reasons outside the hidden chart-settings caption; retain all research-filter matches |
| AC-65 | User opens retained records from chart availability | Open the chosen investigation without changing the applied research query or fabricating a chart pair |
| AC-66 | Chart scope or reported coverage omits a matching investigation | Distinguish not-selected-for-chart, missing quantities, interval values, oxygen basis and summary records; counts reconcile without double-counting |
| AC-67 | Filtered results contain only some record levels | The metric count and its caption name exactly the present record levels |

Tests should target these scientific/behavioral contracts and source-access boundaries, not widget implementation details. Use application unit tests for query semantics, a few repository-backed cases for existing data quirks, and Streamlit smoke tests for selection, empty states and evidence presentation when supported by the installed version.

## 11. Integration boundaries for stages 2–4

Stage 2 adds HabitatScenario, deterministic RelevanceRanker and ScoreBreakdown. Browsing filters narrow exploration; they are not a relevance score or proof a dataset is applicable to a habitat. The lunar scenario can retrieve nearby evidence with explicit extrapolation even when a strict overlap filter would find none. Scores and missing-criterion policies require their own specification and ADR.

Stage 3 retrieves numerical evidence from typed TestPoints and documentary evidence from reviewed sections with source/capture/locator identities. Free-text hardware matches and user source associations must not become verified claims. This explorer's source identities and evidence inspector should be reused.

Stage 4 supplies the computed score, scenario and retrieved evidence to Narrator. Citations must resolve to supporting evidence, and numerical claims must match it. Source-stated content, inferred claims and human review status remain distinct. Invalid narrative uses the deterministic fallback. Retrieval/ranking/narration do not move into Streamlit callbacks.

## 12. Implementation sequence and review gate

1. Review this specification, especially numeric missingness, row granularity, draft metadata and evidence delivery.
2. Implement typed exploration query/results and use cases against the current repository; verify AC-04 through AC-10 before widget work.
3. Build the native Streamlit shell, catalog, selection and detail using those use cases.
4. Add row inspector, source access, quality states and explicit refresh/invalidation.
5. Verify acceptance cases, architecture, Ruff, strict domain mypy, existing tests and Streamlit startup. Report any unverified criteria.

Review points to confirm before coding: primary users are researchers/students; default view is the full catalog; draft metadata is visible with badges; filters use overlap and match the same record; unknown numeric values are excluded only when their corresponding numeric filter is active; no ranking, chat or full export is included in stage 1. These are proposed defaults derived from project goals, not newly discovered scientific facts.

Definition of ready: proposed defaults are reviewed, curation-facing fields are aligned with the latest models, integration prerequisites in the QA report have owners, and schema changes are identified before coding. Pure query/domain work can begin from the reviewed contract; integrated data-loading completion requires the listed producer/consumer prerequisites. Definition of done: P0 scope works through application use cases with validated data, the required acceptance matrix passes, source access is usable, and no scientific data-writing or LLM dependency is introduced into exploration. Stage-1 release is not completion of the project's ranking/export MVP.

## 13. Additional data requirements derived from the challenge brief

This section maps the user-supplied NASA challenge brief to useful data consumption requirements. The brief defines product scope; it does not replace investigation-specific evidence for experimental facts. Proposed fields below are not current domain fields unless an exact current mapping is given. Missing values remain unknown. No new source acquisition or scientific curation is authorized by this specification update alone.

Availability vocabulary: **current** = a field exists in the curated model/dictionary for at least one investigation, not necessarily with complete values; **derived** = a transparent calculation from existing inputs, requiring a documented rule; **curation** = requires a source-supported manual fact or agreed schema extension; **later** = belongs to a subsequent feature stage. Availability must be checked against the loaded dataset, not inferred from this list.

### 13.1 Challenge-to-data traceability

| Requirement | Challenge need | Additional data to consume | Availability and delivery |
| --- | --- | --- | --- |
| DATA-01 | Understand objectives and experimental design | Objective, approach, research purpose, hypotheses when stated, distinction between direct safety study and supporting combustion research | Current ISA-Tab `study_metadata.objective/approach/hypothesis`; source-backed research-purpose classification requires curation; detail now, ranking later |
| DATA-02 | Compare fabrics, plastics, droplets and burners | Fuel/material identity, FuelPhase, sample shape, thickness/length/width/diameter, burner/nozzle size, fiber support | Current fields in selected investigations; shape/material-family normalization requires curation; optional detail columns in stage 1 |
| DATA-03 | Understand atmospheric conditions | O2 basis and timing, pressure, diluent identities and component concentrations, ambient temperature, premixed fuel fraction when reported | Current fields in selected dictionaries; measurement location/timing and absent components require curation; never assume atmosphere balance |
| DATA-04 | Understand airflow and geometry | Flow speed/direction, burner configuration, confinement/duct dimensions, hardware hierarchy, stagnant versus ventilated conditions | Current flow fields and some burner fields; duct dimensions/hierarchy/quiescent claim require curation; no fan-setting-to-speed conversion in UI |
| DATA-05 | Support prevention/material selection research | Ignition input, flame spread/burn length, extinction observations, source-reported flammability endpoints | Some current quantities; endpoint definitions and actual limit claims require curation; ranking/model use later |
| DATA-06 | Support detection research | Smoke source/material, generation duration, particle aging/mixing, mass loss, detector instrument/principle, particle-size or response measurements if reported | Some current SAME/SAME-R quantities; detector-specific performance and aerosol measurements require evidence and schema review |
| DATA-07 | Support suppression research | Suppressant identity/concentration, droplet size, extinction diameter, burning-rate constant, burn duration, termination reason and initial conditions | Some current FLEX/CFI quantities; mechanism/efficacy interpretation requires curated evidence; no automatic suppression success label |
| DATA-08 | Compare investigations scientifically | Shared/different fuels, condition bases, granularity, hardware/apparatus, gravity regime, measured variables and variable definitions | Current model/dictionary plus curated claims; comparison feature later |
| DATA-09 | Extract data for predictive models | Predictor/outcome meaning, units, raw values, source ids, record grouping, missingness, transformation notes and support for reproducible selection | Current fields plus derived manifests; full export/schema/data card later |
| DATA-10 | Inform future safety controls/equipment | Evidence-supported link from observation to prevention/detection/suppression need, instrument purpose, mechanism and relevant limitations | Existing Claim/Sensor structure supports some facts; additional research-to-control relationships require curation and review |
| DATA-11 | Explain exploration habitat relevance | Intended habitat, target atmosphere/gravity, selected pillars/fuel phases, distance from tested coverage, evidence gaps | HabitatScenario and ranking later; habitat applicability is an explicit inference, not a new measured property |
| DATA-12 | Surface Earth applications and shared technology | `manual_metadata.earth_applications`, source-supported instrument reuse, relationship type and supporting quote | Existing Earth-application claims when populated; cross-investigation/instrument relationships require curation; optional later detail |
| DATA-13 | Communicate quality and uncertainty | Claim/review state, source conflicts, measurement definitions, instrument resolution/uncertainty/calibration validity if actually documented | Current status/notes; uncertainty and run-specific calibration require curation; no inferred confidence percentage |

### 13.2 Concrete current columns worth exposing

These are inspected dictionary keys, not a universal schema. The explorer discovers whether a column exists per Investigation, then consumes it through TestPoint.extras/ColumnInfo. A field's existence does not mean every row reports it.

| Investigation family | Existing optional columns | Interpretation constraint |
| --- | --- | --- |
| SAFFIRE-I/II/III | `sample_length_mm`, `sample_width_mm`, `sample_thickness_mm`; I/II also `ignition_power_w`, `ignition_time_s`, `burn_time_s`; II also `microgravity_burn_length_mm`, `microgravity_spread_rate_cm_s`, `normal_gravity_burn_length_mm`, `normal_gravity_spread_rate_cm_s` | Preserve sample dimensions and ambiguous raw cells; do not move normal-gravity comparison values into a microgravity measurement column |
| BASS / BASS-II | Fuel description and sample identifiers; BASS-II `o2_final_percent`, `co2_initial_percent`, `co2_final_percent`, `co_initial_ppm`, `co_final_ppm`; gain/fan/air settings and frame counts as recorded metadata | Do not parse dimensions embedded in fuel descriptions without an adapter rule; instrument settings are not calibrated flow speed, resolution or measured radiation |
| SAME | `sample_mass_loss_rate_mg_s`, `smoke_aging_duration_s` | Smoke-source generation and aging quantities are not detector latency or particle-size measurements |
| SAME-R | `smoke_generation_duration_s`, `primary_aging_time_s`, `primary_mixing_time_s`, `net_aging_time_s`, `rt_r0_ratio`, `test_description` | Do not invent the meaning of a ratio acronym, detector model or particle distribution; consult the source definition |
| FLEX | `droplet_initial_diameter_mm`, `flame_extinction_diameter_mm`, `burning_rate_constant_mm2_s`, `burn_time_s`, `test_outcome`, `co2_percent`, `he_percent`, `n2_percent` | Burning-rate constant in mm²/s differs from flame-spread speed; distinguish extinction, disruption and unreported outcomes |
| FLEX-2 | `droplet_initial_diameter_mm_min/max`, `ambient_temperature_k` and core atmosphere/flow ranges | Planned matrix envelopes must not become a synthetic Cartesian product of measured runs |
| CFI | `fiber_supported_droplet`, `he_percent`, `n2_percent`, run identifiers and core conditions | Presence of a fiber and run ids are context; liquid-fuel identity and actual outcomes remain separately represented |
| ACME-BRE | `burner_size_mm`, `flames_ignited` and date components | Ignited-flame count summarizes a test day; do not count each row as one ignition or recode gas as solid because of the study's research purpose |
| ACME-CFI-G | `flame_configuration`, `cool_flame_observed`, `hot_ignition`, `termination_mode`, `burn_time_s`, `peak_burner_temperature_k`, `adiabatic_flame_temperature_k`, `fuel_mass_flow_rate_mg_s`, `oxygen_mass_flow_rate_mg_s`, `ambient_fuel_fraction_percent`, `ambient_fuel_fraction_after_test_percent`, `burner_fuel_fraction_percent`, `o2_after_test_percent`, `flame_color` | Normal/inverse flames and ambient/burner compositions remain separate; adiabatic temperature and peak burner temperature must not be relabelled measured flame temperature; unknown text codes remain raw until defined |
| ACME-E-FIELD | `burner_campaign`, `electrode_polarity`, `fuel_concentration_percent_min/max`, `flames_ignited`, test-day identifiers | Electrical polarity is not an effective gravity magnitude; emulation is not a direct partial-gravity measurement |
| SPICE | `nozzle_diameter_mm`, `fuel_volume_flow_rate_sccm`, `fuel_mass_flow_rate_mg_s`, `hydrocarbon_mass_flow_rate_mg_s` and GMT timing metadata | Volumetric and mass flow are distinct; do not convert sccm to mass flow without gas/reference-state information |
| SLICE | `test_date_and_remarks`, fuel descriptions | A sparse campaign summary does not establish sensor availability, O2/pressure or detailed flame behavior |

Promote these to optional detail-column presets such as Material and ignition, Smoke generation, Droplet combustion and Gas burner configuration. Presets group available columns; they do not assign scientific pillars automatically. Avoid a very wide default table. Outcome filters are opt-in per investigation and use documented source semantics, never generic success/failure guesses.

### 13.3 Proposed curation extensions, with explicit source obligations

These proposals are a curation backlog, not instructions to modify current models during dashboard implementation. Each requires Claim-like value/status/evidence, an applicable record or investigation scope, a source locator and scientific review before use.

| Proposed concept | Why it matters | Minimum evidence / limit |
| --- | --- | --- |
| Sample geometry and material family | Compare thermal/material scale beyond fuel text | Source identifies shape, composition and dimensions; preserve unknowns and original descriptions |
| Hardware hierarchy | Distinguish facility, rack, apparatus, duct and experiment configuration | Separate source-backed relationships; shared rack does not prove identical experimental setup |
| Measurement definition | Compare instruments and quantities correctly | Measured quantity, location, unit, timing/reference basis, instrument and analysis method when stated |
| Experiment purpose versus physical fuel | Explain surrogate/emulator studies | Curated purpose with evidence; physical FuelPhase remains unchanged |
| Outcome definition and endpoint | Support later modeling and suppression analysis | Source-defined outcome, observation/termination/censoring meaning and applicable record; do not infer failure to ignite from a missing value |
| Nominal/test/measured/planned condition roles | Separate scenario targets, design envelopes and observed values | Explicit role supported by source or documented derivation; no automatic reassignment based on column name alone |
| Ground/flight/control and replicate grouping | Avoid invalid comparisons and misleading model validation | Source-defined groups and counterpart ids; identical rows are not automatically confirmed replicates |
| Instrument calibration and uncertainty | Help users assess usable measurements | Document id, validity interval/configuration, uncertainty/resolution and unit only if documented; no values inferred from file presence |
| Source conflict and adjudication state | Preserve contradictory reports | Both statements, their locators, scope and review decision when one exists; never overwrite a conflict silently |
| Cross-study instrument/technology relationships | Discover relevant detection research and terrestrial applications | Named instrument or technology, relation type, direction and citation; shared words are insufficient |

DAFT/DAFT-2, other ACME investigations and future partial-gravity investigations can be discoverability references, but are not added as loaded investigations or counted as available datasets without an approved registry entry and curated data. Relationships stated in the supplied challenge brief are leads to investigate; they are not replacements for local investigation evidence.

### 13.4 Additional views and filters by delivery stage

- **Stage 1, existing P0:** retain evidence/status/coverage display and correct per-record filters from this specification. Geometry, outcomes and instrument settings already present are accessible through the record inspector; they need not be global filters.
- **Stage 1, P1:** optional family-specific column presets, quantity-availability indicator (reported records / applicable records), and documented configuration/outcome filters for the selected Investigation. Show whether counts refer to matching or full records. Missing observations stay distinct from a column that is not part of an investigation's schema.
- **Stage 2:** scenario support panel with ambient O2/pressure coverage, gravity support, matching fuel/flow context, missing criteria and explicit extrapolation. Material geometry and instrument metadata provide context; they receive no implicit ranking weight without a separately specified criterion.
- **Comparison feature:** compare 2–3 investigations with units, physical quantity, O2 basis, record level, setup and provenance alongside values. Highlight differences and missingness; do not pool dissimilar quantities, infer causal effects or draw a flammability boundary from min/max ranges.
- **Export feature:** describe available predictors/outcomes and preserve source grouping, transformation notes and selection revision. No full export or prediction model is added to stage 1 by this section.

Later atmospheric calculations, such as oxygen partial pressure, require explicit paired inputs and a documented domain rule. They must not combine maximum O2 from one record with pressure from another, use oxidizer-stream composition as cabin composition, or treat a derived quantity as an experimentally measured value. Such derived fields are outside the initial explorer.

### 13.5 Context package for later XAI/RAG

This is a proposed retrieval-result envelope for a later specification, not a request to index every file or implement embeddings now.

| Context component | Required contents |
| --- | --- |
| User question and scenario | Requested habitat/conditions, units, gravity target, pillars and selected assumptions; user targets are not scientific observations |
| Investigation identity | Canonical id, PSI id, record level, title/objective when supported, snapshot revision |
| Structured evidence | Exact TestPoint ids, canonical values, raw values, quantity definitions, measurement/configuration basis, source rows and transformations |
| Documentary evidence | Literal supporting passage, source id/file, capture version or file hash, locator, URL when applicable and associated investigation |
| Claim qualification | Source-stated/inferred/not_reported status, manual draft/review state, inference note and source conflicts |
| Deterministic explanation inputs | Criterion definition, weight, value, contribution, supporting record ids and missing/extrapolated criteria; computed by domain, not LLM |
| Limitations | Unsupported conditions, incomplete measurements, nominal versus measured data, partial-gravity limits, incompatible hardware/configuration and outcome-definition limits |

An investigation tag alone does not prove a passage supports a particular claim. The retrieved evidence must support the stated quantity, setup, outcome and scope. Failed captures, unrelated navigation and source instructions are excluded. No hidden chain-of-thought is required: show the computed breakdown, evidence, assumptions and limitations.

Retrieval first respects Investigation, physical quantity, O2 basis and record granularity. Documentary retrieval adds context without overwriting structured numeric evidence. Draft facts may be retrieved only with their draft state preserved. A source-supported general hardware description cannot establish that a particular TestPoint used a specific sensor configuration.

### 13.6 Modeling/export readiness information

The complete export/data card should include dataset revision, applied selection, column meanings/units, record granularity, measured-versus-derived roles where curated, missingness counts, source hashes, inferred transformations and unresolved source defects. Investigations contribute very different record counts; row count must not be called scientific relevance or effective sample size.

Preserve source/campaign/sample ids and duplicate/continuation notes for users constructing model-validation groups. Do not automatically drop duplicates, impute missing quantities, generate labels, split matrix ranges into artificial observations, merge detector response with smoke-generation time, or claim a dataset is model-ready solely because it has no null cells. Group-aware validation is a user/modeling design decision requiring an explicit protocol, not an explorer default.

### 13.7 Prioritization constraint

These additions improve scope coverage without changing stage-1 P0. Consume existing typed fields first; display unavailable context honestly; queue evidence-backed schema extensions with the curation workstream. Full comparison, export, scenario calculations and RAG context require their own implementation increments. New scientific fields, conversions, ranking weights or inferred relationships require source evidence and the normal ADR/schema review before coding.

## 14. Analytics workspace and future copilot amendment

The user requested a Power BI/Salesforce-style analytic workspace: existing bars plus multi-picklist controls, scatter and comparative lines, clearer detail navigation, and visible room for a future AI dashboard assistant. This amendment authorizes stage-1 exploratory visual comparison and a disconnected assistant surface; it does not implement ranking or RAG.

Global multi-select filters keep their existing scientific semantics. Chart investigations/axes/line-series selections refine only the chart workspace; the interface states this distinction. Chart variables come from quantity dictionaries with consistent canonical units. Paired reported scalar values come from the same record; O2-related quantities respect the selected measurement basis. Missing/range values are excluded and counted, with no interval midpoints or nominal-value substitution. Daily summaries and planned matrices are excluded from individual-test plots.

Scatter shows source-record identity and scientific context in tooltips; legend highlighting and zoom change only the visualization. Lines group by investigation, fuel, flow direction and O2 basis and show the median vertical value at each reported horizontal value. This is descriptive aggregation with a count, not a time series, causal relationship, interpolated measurement or flammability boundary. Other ungrouped experimental conditions may differ; the caveat stays visible. Users can inspect raw scatter and records to assess confounders. Source derivations and measurement semantics remain those of the selected columns.

Investigation navigation uses descriptive tabs: Research & scientific context, Experimental records & raw values, Citations & source downloads. The copilot panel has a visible disconnected status and disabled question/action controls. It displays actual dashboard context and intended capabilities without synthetic messages, external requests or silent filter changes.

Future assistant action contract: typed proposals such as SetFilters, SetChartAxes, SetComparisonSeries and OpenEvidence, scoped to the loaded dataset revision. Proposals must pass existing query/quantity/source validation and be previewed for user application. The assistant may narrate supplied evidence later; it cannot execute arbitrary code, edit source data or compute/override deterministic scores. The executor and model remain unimplemented until their own integration increment.

## 15. Supplied-image layout amendment

The user supplied a screenshot as the design reference and requested a copilot toggle. Implementation can use this image directly; neither a Figma URL nor Dev Mode/code extraction is required. The reference's curves/counts are illustrative and do not replace scientific source data.

Use a light neutral canvas, white cards, restrained teal accents, top workspace navigation and horizontal filters. The dashboard grid pairs comparative profiles with record-volume bars, followed by composition and interval-coverage charts. A compact investigation preview opens full details. Actual dimensions are adapted to Streamlit/browser layout; no pixel-identical Figma extraction is claimed.

The Research copilot toggle defaults off and controls an optional panel, freeing chart width when hidden. Existing filters, quantities and source semantics are preserved. Chart settings are progressively disclosed. The Lines/Scatter switch selects visual presentation of the same valid chart data. Default line series choose an available series per investigation for readable cross-investigation comparison; this is a display default, not a scientific relevance ranking.

Dataset composition counts record levels explicitly; coverage envelopes retain the selected quantity and O2 basis, exclude missing conditions and show endpoints for single values. Export view is a configuration JSON only. Scope/pinning/draft limitations and the disconnected assistant state remain applicable.

## 16. FLAMSA light-glass visual amendment

The user requested the atmospheric background/glass effects of a new reference while retaining the current palette and adding FLAMSA identity. Keep the existing light canvas, cool blue/slate/teal analytic palette and all scientific/interaction semantics. Apply translucent surfaces, subtle backdrop blur, restrained shadows and a decorative CSS horizon rather than neon-green charts or a new dark theme. The horizon is decoration, not scientific imagery.

Use the local SVG interpretation of the supplied flame/wordmark reference until an original brand asset is provided. Include the asset in package data. Maintain readable labels and focus indicators, solid-surface fallback for browsers without backdrop-filter, and reduced-motion behavior. Copilot toggle, filters and data access remain unchanged. This amendment does not authorize new aggregations, chart trends or source-data edits.

## 17. English homepage adaptation

The user supplied a Portuguese React/TanStack homepage concept and requested its addition in English. Add Home as the initial Streamlit destination, retaining Dashboard/Investigations/Evidence. Preserve the light-glass FLAMSA identity, English introductory copy, four selectable research themes, a visual scene and navigation to the real archive. Topic buttons are native Streamlit controls; there is no separate React runtime.

The imported hero JPEG was not supplied. Use a locally packaged SVG concept scene, explicitly labelled illustrative rather than a NASA photograph or a specific experimental setup. Numbered topics are Flame behavior, Earth applications, Exploration habitats, and Detection and diagnostics. Buttons/pills select the explanatory panel and source-bounded related investigations. Related ids must exist in the loaded snapshot; Earth-application links require actual nonempty curated claims. An Open related research action replaces the current filter selection with the displayed ids and opens Investigations; ordinary Home/Dashboard navigation preserves the applied query.

Homepage counters use the actual snapshot, and review counts are not confidence scores. Do not port the original hardcoded relevance scores, illustrative ranking, LIVE connection badge, unsupported instrument/technology relationships, or studies not in the curated archive as implemented results. Describe ranking and AI as planned until implemented. No scientific data or source claims are changed by translating/adapting marketing copy.

## 18. Research-filter results versus chart data availability

The user reported that selecting BASS, BASS-II, CFI, FLEX, FLEX-2 and SAFFIRE-II yielded only FLEX and SAFFIRE-II in the oxygen/burn-time scatter. On the inspected snapshot the research query retains six investigations and 629 records. Only 271 records support the selected scalar pair: FLEX 268 and SAFFIRE-II 3. BASS lacks both quantities; BASS-II and CFI lack burn time; FLEX-2 has eight matrix summaries; the remaining excluded individual tests have missing quantities or an interval instead of a scalar. These are observed snapshot counts, not future hardcoded defaults.

Application-level chart eligibility must produce both plotted rows and a per-investigation availability projection from the same decision policy. Every matching investigation appears in the projection, including zero-plotted and chart-deselected investigations. Each nonplotted record has one primary reason, allowing records=plotted+primary omissions per investigation. Scalar variables are reported as alternatives for inspection, without promising an actual paired observation or plotting matrix rows as tests.

Show the selected/plotted investigation difference directly in the profile card. A labelled availability expander contains record totals, granularity and primary reasons, plus an action opening the retained investigation with the global query unchanged. Do not inject zeros, nominal atmosphere, values from another study, interval midpoints or fake legend series to make all selected names appear as dots. Other charts and record detail preserve the full matching scope. Coverage charts name investigations missing the current reported interval/basis, and record-level captions derive their labels from filtered data.

## 19. Filter and structured-data integration audit

The committed ExplorationQuery is the source of truth for displayed results. Initialize absent filter widgets from it, including Home topic links and return navigation after Home has hidden the controls. Existing visible form drafts remain drafts until Apply. Invalid submissions retain the last valid query, show an explicit failure message and keep the actual applied scope visible. A readable applied-filter summary must describe categorical selections, numeric bounds, oxygen basis and include-unreported policies. Report retained missing-condition counts for each active include-unreported numeric filter.

Reported oxygen basis supports standalone categorical selection from the loaded records, including missing basis. For an active numeric oxygen range, a nonempty categorical basis selection must contain only the explicitly selected numeric basis; otherwise reject Apply with an actionable message. No silent basis substitution is allowed.

The dashboard consumes validated curated CSV/JSON pairs rather than loading Excel/raw files or data/manual directly. Corrections require a completed curation publication followed by dataset reload. Compare the loaded revision with current curated input bytes on each Streamlit rerun and visibly announce changed or unreadable inputs. This is a freshness signal, not automatic curation, an atomic publication guarantee, a background watcher or a check of uncurated source edits.

Successful reload preserves valid applied filters, announces removed categorical values and rehydrates controls from the reconciled query. A failed reload retains both the previous snapshot and applied query with a stale-data warning. This supersedes the earlier implementation's reset-all-on-reload behavior.

Acceptance additions:

- AC-68: Home related-research links and Home round trips show filter values equal to the applied query, including numeric settings.
- AC-69: Form drafts and invalid submissions leave metrics/records on the last valid query, with actual scope and validation failure visible.
- AC-70: Every categorical option from the current CSV/JSON snapshot can retrieve its expected parent/row identities; union within a facet and intersection across facets preserve row identity and missing semantics.
- AC-71: Standalone oxygen-basis filtering works without numeric bounds; ambiguous/conflicting numeric-basis selections are rejected without changing results.
- AC-72: Changed curated inputs trigger a visible freshness warning; reload failure preserves prior query/results, and successful reload preserves valid selections while announcing removals.
- AC-73: Direct CSV rows, aggregate rows and unfiltered result identities reconcile, including every documented extra quantity and its raw companion.
- AC-74: Active include-unreported numeric filters disclose the number of retained records lacking each condition.
- AC-75: Sensor metadata unavailable, an empty sensor list and a not_reported sensor Claim produce distinct filter states.

## 20. Supplied homepage assets and interactive scene

The user supplied the complete React homepage reference, its stylesheet and the previously missing flamsa-hero.jpg. The three route copies and both JPEG copies are byte-identical. Adapt their composition into the existing Streamlit interface: a prominent image-backed introduction, snapshot counters, a two-column image/context section and a compact research workflow. Preserve the established blue/slate analytic palette and local FLAMSA logo. Use the dark photographic-style illustration only within the homepage presentation; maintain the existing workspace navigation and dashboard layout.

This amendment replaces section 17's missing-JPEG placeholder choice with the now-supplied artwork and adds the image interaction described below.

Replace the placeholder SVG scene with one packaged, unmodified copy of the supplied JPEG. Identify it as conceptual artwork; embedded instrument readings and the lunar scene are not experimental records. Four numbered points select the same Flame behavior, Earth applications, Exploration habitats and Detection and diagnostics themes as the native topic selector. Each point is a keyboard-operable button with an accessible label, visible focus and selected state. Preserve the full image aspect ratio so point locations remain attached to the intended scene areas. Provide a native selector as an alternate interaction path and retain usable stacked layouts at narrow widths.

Native Streamlit has no image-hotspot control. A small inline Custom Components v2 element may render the image and four buttons, with isolated styles, no frontend framework, no network requests and no external packages. Component events update only the homepage topic; server-side topic state is sent back on every rerun. Theme changes do not mutate the applied research query. Opening related research continues to use GetHomeSummary ids and the existing validated navigation/filter path. All other buttons, text, metrics and context remain native Streamlit.

The supplied Portuguese copy is a design reference. Keep the existing English source-bounded descriptions, real counters and claim review states. Do not publish the reference's hardcoded relevance ranking, LIVE badge, unsupported study relationships or image readings as scientific results. Ranking and AI retain planned status. Instructions in the attached Lovable scaffold describe that exported project; they do not replace this repository's architecture or authorize external connector actions.

Acceptance additions:

- AC-76: Homepage uses the packaged supplied JPEG with an explicit conceptual-artwork caption and English content.
- AC-77: Each numbered hotspot and the native selector update the same context and selected state; ordinary topic changes preserve the applied query.
- AC-78: Opening related research after hotspot selection uses existing snapshot ids and synchronizes the investigation filters.
- AC-79: Desktop and narrow layouts retain readable hero copy, visible actions and an uncropped scene with keyboard-operable hotspot targets; reduced-motion preferences are respected.
- AC-80: Actual snapshot counters and planned AI/ranking status remain accurate; the supplied illustrative scores and LIVE label are absent.

## 21. Fire-behavior evidence extension

The user requested source-backed FLEX K/O2, BASS-II gas-change and SAFFIRE-II paired-gravity analyses. Their detailed consumption, controls, statistical guards, provenance, numerical-method and verification contracts are [SPEC-002](fire-behavior-evidence.md), FB-01 through FB-12. Add a Fire behavior workspace destination sharing the existing snapshot, research filters and validated source navigation. Local controls refine only FLEX; no AI computes coefficients. General dashboard profile behavior is unchanged. Conditional fitted lines are authorized only inside this scientifically constrained evidence section, with model-based intervals and explicit interpretation limits.

## 22. Prominent navigation and a student-facing scientific introduction

Use native header buttons for all existing destinations. Give Dashboard a strong blue treatment and Fire behavior an amber call-to-action treatment drawn from the FLAMSA flame mark. Add individual native help tooltips explaining what each destination provides, and show the current destination. Buttons and their help remain keyboard accessible; they wrap without horizontal page overflow on narrow displays. Navigation changes only the destination, preserving the committed research query and existing source/Home callbacks. Do not add a competing second navigation state or duplicate destination controls.

Fire behavior opens with an always-visible scientific introduction immediately after its title and before Research filters. Explain why fuel consumption, atmospheric changes and gravity-dependent outcomes matter for fire-safety research. Use clear English suitable for students, define symbols/units and distinguish the d-squared physical model, signed concentration calculations, fitted associations and paired experimental observations. Explain the path from a physical relationship to an independently traceable check; do not label correlation as proof of a universal law or certify a habitat. Optional detail may show the existing conditional regression formula and how to inspect ranges/intervals/source records. This is explanatory presentation of existing analyses, not a new scientific validation result or a replacement of their calculations.

Acceptance additions:

- AC-81: Dashboard and Fire behavior are visually prominent native header buttons with distinct blue/amber treatment and purpose-specific help.
- AC-82: All four destinations (Home, Dashboard, Fire behavior, Investigations) and existing source/Home actions preserve navigation behavior and applied filters; the current destination remains visible.
- AC-83: The Fire behavior introduction appears before filters and includes student-facing definitions of K, oxygen/CO2 differences and paired gravity outcomes.
- AC-84: The introduction identifies evidence/assumption boundaries and the existing deterministic calculation/source path, with no new fabricated proof or safety score.
- AC-85: Browser checks confirm header hover help, readable introduction/equations, keyboard navigation and narrow-screen wrapping.

Laptop/desktop navigation buttons stretch across their allotted header space with larger text, padding and targets: 56 px minimum height at 1200 px and above, 52 px at 1024–1199 px with a reduced gap so all four destinations remain on one row. Narrow layouts retain at least 44 px targets and native wrapping. Preserve the existing blue/amber palette, help, keys and navigation callbacks; Dataset controls remains a separate action with a desktop target aligned in size.

## 23. Consolidate source inspection within Investigations

Remove Evidence from primary navigation. Keep the Investigations catalog, scientific context, experimental records/raw values and Citations & source downloads. Source-reader ports, registered file/checksum checks, stored evidence and existing Fire behavior/source callbacks remain available. This section supersedes earlier references to Evidence as a workspace destination, including AC-61 and section 17; it does not remove evidence as a domain concept or scientific requirement.

Sessions whose stored destination is Evidence redirect to Investigations and initially select Citations & source downloads, without replacing the committed query or selected investigation. The copilot continues its existing citation rendering; improved claim-to-source actions belong to the orchestration workstream and are tracked in docs/copilot-evidence-handoff.md. This navigation increment does not claim that DOI links already open exact PDF pages.

- AC-86: No Evidence header action is rendered; an existing Evidence session redirects to Investigations, retaining applied filters and source access.
- AC-87: Investigations exposes the sources tab and can prepare a registered source download; Fire behavior source-record actions and Home flows remain valid.

## 24. Home copy reflects the implemented challenge workflow

Present the archive as NASA PSI combustion data rather than implying every investigation flew aboard the ISS. Explain the implemented workflow: compare reported conditions, rank studies for a habitat scenario in Research copilot, inspect cited sources and export matching records as CSV. Name prevention, detection and suppression as the challenge's fire-safety research pillars. Do not promise a predictive simulator, calibrated risk score, human-reviewed metadata where none exists or demonstrated lunar/Martian gravity coverage.

Replace the obsolete planned-ranking/no-scores statement from the initial Home increment with the actual deterministic ranking, criterion breakdown, evidence checks and possible insufficient-evidence outcome. The copilot's model-backed narration depends on configuration; a template is available offline. Do not imply that a language model computes ranking scores or that automated validation establishes scientific truth.

Provide a native Open Fire behavior action alongside Dashboard and Investigations, preserving the committed query. Keep the interactive conceptual-artwork label, snapshot-derived counters, curated-only Earth links, claim/review status distinctions and explicit scope limits. Earth-application navigation is not a demonstrated technology recommendation; the solutions catalog is a separate capability. Preserve the existing visual design and topic navigation.

- AC-88: Home describes current ranking, CSV/source access and all three research pillars, without the retired no-scores claim; counters retain snapshot-derived review status.
- AC-89: Home opens Fire behavior without replacing research filters, and its copy distinguishes source-bounded analysis from prediction or habitat certification.

## 25. Navigation latency and bounded read projections

Clear Home-only styles and decorations through a stable placeholder at the beginning of a navigation rerun, before slow analysis. Preserve its visual design and reduced-motion controls. Main analysis must render before an answering-engine initialization; merely visiting the Dashboard or toggling Research copilot must not initialize the model/orchestration engine. Build the cached real pipeline only for an explicit question (or rendering a pre-existing answer needing its actual narrator label). Leave first-answer feedback and all validation/citation behavior intact.

Reuse the validated parsed snapshot within its session when the cached revision is unchanged. Keep the existing byte-based curated freshness check, transactional reload/error behavior and global serialized snapshot cache; do not share mutable Pydantic aggregates across sessions or treat file timestamps as scientific revision evidence.

Bound chart projection/axis-option caches to 32 entries and filtered CSV caches to eight entries. Keys include dataset revision and the exact retained investigation/TestPoint identities, plus relevant axes, chart ids and oxygen basis. The excluded heavy Match argument is covered by these explicit keys. Cached outputs are copied by Streamlit so one consumer cannot corrupt another. Compute axis counts without constructing unused plot rows; counts must equal actual eligibility for ranges, missing values, summaries and measurement basis.

Cap the scenario-picker's interaction mesh at 4,000 synthetic marks (16 cached geometries). These invisible marks are UI controls, never scientific observations; source dots and manual scenario precision remain unchanged. Explain that clicks snap to a display grid and exact conditions can be typed. Construct the mesh only when copilot picking is enabled. Fire behavior scientific dependencies load only when that view is used. No numerical validation, source checksum check or record is removed to gain speed.

- AC-90: optimized partner counts equal production plot counts for current scalar axes/bases without allocating plot rows.
- AC-91: cache boundaries separate revisions, retained row identities, axes, selected chart studies and oxygen bases; mutable returned rows do not contaminate cache hits.
- AC-92: navigation removes Home decoration/styles early; Dashboard/copilot controls remain usable without constructing an answering pipeline or sending a model request.
- AC-93: the interaction mesh stays within its mark budget; registered source access, filter reload/error behavior and exact typed scenario values remain available.

## 26. Friendly Research copilot presentation

Add a compact static flame mascot directly below Ask about this scenario and above Ask copilot. Extend the existing amber/slate FLAMSA vector identity using a packaged SVG, without a remote asset request, animation, fictional scientific readings or simulated connection state. The mascot is decorative guidance, not an authority or a validation indicator.

Give the right panel approximately 30% of the Dashboard's comparison area on wide screens, with native responsive layout. Shorten introductory instructions, increase the question field to 110 px and make Ask copilot a primary action. Keep the visible statement that ranking covers all curated studies, including those outside chart filters; place the longer explanation of deterministic scores, narration, citation checks and uncertainty in an optional How the copilot works disclosure.

Preserve scenario/input keys, defaults, chart selection synchronization, deferred engine initialization, actual question submission, answer/status/breakdown/limitation rendering and View source actions. Interface text remains English. Visual friendliness must not imply that a model is connected, evidence is human-reviewed or a result is guaranteed.

- AC-94: the mascot is rendered between the question and submit action, with readable native controls at desktop/mobile widths and no new horizontal overflow.
- AC-95: the primary submit action, scenario/marker state, deferred initialization and validated-answer/source flows retain their behavior; scope and uncertainty explanations remain accessible.

The question field uses a scoped dark-purple speech-bubble container with a small decorative tail pointing toward the FLAMSA mascot below it. Keep the native editable textarea, its label/help/key and keyboard interaction. Use light text, a visible focus treatment and a contrasting placeholder; do not restyle the scenario inputs, generated answers or the rest of the workspace. The tail is CSS-only and non-interactive. This presentation does not turn the user's editable question into a generated mascot response.

## 27. Research filters and comparison controls remain consistent

Research filtering remains transactional and uses the existing application query contract. The comparison may refine that result, but a research change must reconcile its local selection before rendering widgets: preserve a valid subset; extend an all-studies selection to the new result; when a nonempty selection loses every member, select the retained studies and announce recovery. An intentionally cleared local selection stays empty until the user selects studies or resets filters. Reset restores default chart choices as well as the research query.

Use the numeric query's oxygen basis, or a single explicitly selected reported basis, for an oxygen comparison. Otherwise offer bases actually reported in the retained records and preserve a valid local choice. Never combine burner-stream oxygen with ambient oxygen. Show this relationship near the chart controls.

Keep logical chart choices separate from native widget identities. Refresh a widget when its available choices, displayed quantity labels/counts or committed research context changes. Visible selected labels, units and counts must describe the current chart, including after an axis disappears. Only positive-count vertical partners may be selected. With no partners, disable that selector and explain whether records are summaries, no studies were selected, or measurements cannot form pairs; provide retained-record access.

Keep the batched research form. Reject a submitted draft with bounds or include-unreported enabled for an inactive numeric filter, with an actionable enable-or-clear message; do not silently discard it. A cleared optional select means its documented default (oxygen numeric basis: ambient, review: all, notes: any), while invalid active ranges still preserve the previous valid query. Explain defaults and inactive input behavior within the form.

- AC-96: all ordered study changes preserve valid refinements or recover invalidated nonempty local selections; intentional emptiness and reset have distinct behavior.
- AC-97: stream-only research automatically uses stream oxygen in comparisons; numeric oxygen basis is honored and incompatible research bases remain rejected.
- AC-98: native-browser quantity labels/units/counts agree with rendered chart axes after research and basis changes; zero-count vertical axes cannot be selected.
- AC-99: inactive bounds are rejected explicitly, cleared selects use documented defaults, and invalid drafts preserve committed results.
- AC-100: each chart's empty state names its missing requirements and retained records; summaries remain summaries, with no invented pressure or scalar midpoint.

## 28. A copilot request survives presentation reruns

An explicit Ask copilot click captures the question, scenario and loaded investigations once in its callback, before charts or other presentation code can be interrupted. Read current widget state rather than stale callback argument values. Store its job in session state before starting work. Engine initialization and answering run without Streamlit UI calls on a worker thread; fragment polling owns progress and commits completed results on the UI thread. Presentation reruns or draft edits must neither discard nor repeat the pending request. Disable submission while pending. On completion, preserve the result and actual narrator label before refreshing the charts; showing an existing answer must not initialize another engine. Identify the submitted question/scenario separately from later edits.

An operational exception clears pending state, displays an actionable error without provider secrets, and preserves any previous completed answer. Retry requires an explicit click. This contract is per live session, not a durable cross-process queue. Citation checks, deterministic scoring and scientific limits remain unchanged; no automatic extra model request is added.

- AC-101: one first click completes despite a widget rerun during initialization/answering, with exactly one answerer call and visible output without another click.
- AC-102: pending requests disable submission; approved and insufficient-evidence results, source access and chart highlighting survive completion; rerendering does not call the engine again.
- AC-103: an operational failure releases the pending state, preserves the prior answer and permits an explicit retry without exposing exception details.

## 29. Investigations is a focused full-study browser

Remove Research filters and its applied-filter summary from Investigations. Use the study picker, catalog and existing detail/source tabs to browse all loaded studies and each study's full records, independently of the committed Dashboard/Fire behavior filters. Explain that scope briefly. Preserve the committed query while entering, selecting studies and leaving this view, including when that query has no matching records. Dashboard filters rehydrate on return.

This supersedes earlier descriptions of shared filter controls and matching-only study records in Investigations. Dashboard and Fire behavior retain their existing filtering contracts. Home theme links continue to focus a related study when opening this full-study browser.

The Investigations CSV action exports the selected study's complete records and is labelled accordingly; other views retain their matching-record export. Scientific scope remains available without presenting an irrelevant applied-filter JSON panel. Source navigation, study selection, reload integrity and corpus-wide copilot ranking remain available.

- AC-104: Investigations has no Research filters controls and remains usable under an empty or restrictive Dashboard query; browsing/exporting full studies does not replace that query.

## 30. Fire behavior uses study-specific analysis controls

Remove Research filters, its summary/error display and applied Dashboard-query disclosure from Fire behavior. Analyze complete FLEX, BASS-II and SAFFIRE-II records regardless of the stored Dashboard query, including when that query matches nothing. Preserve that query for returning to Dashboard. Keep the educational introduction, local analysis controls, scientific exclusions, deterministic fits/intervals, paired observations, source actions, copilot and analysis export. This supersedes earlier shared-filter behavior for Fire behavior.

The header CSV exports all source records of those three studies and is labelled Download study records (CSV); analysis JSON retains the effective study scope and local settings, never the unrelated Dashboard query. Investigations and Fire behavior describe Dashboard as the owner of Research filters. No missing measurements or summary rows become individual observations.

- AC-105: Fire behavior has no Research filters panel, retains all three analyses under restrictive/empty Dashboard queries, preserves local controls and source navigation, and restores the Dashboard query on return.
