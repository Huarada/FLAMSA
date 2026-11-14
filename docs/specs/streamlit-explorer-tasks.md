# SPEC-001 tasks and verification matrix

Status: proposed, revision 0.3, 2026-11-14. Requirements: [SPEC-001](streamlit-explorer.md). Design: [consumer contracts](streamlit-explorer-design.md). QA: [findings](streamlit-explorer-qa.md).

No task is marked implemented. Documentation QA is complete; no acceptance scenario is marked runtime-passed by this plan. Existing curation tests are not substitutes for explorer acceptance tests.

## Implementation increments

| Task | Work and ownership | Dependency | Acceptance coverage | Completion evidence |
| --- | --- | --- | --- | --- |
| T01 | Confirm reviewed spec defaults and current model compatibility; dashboard + curation owners | None | AC-48 | Contract review and explicit deferred scope recorded |
| T02 | Add immutable query/result types and validation; application | T01 | AC-11, AC-37, AC-39 | Tests call requests without Streamlit; finite/range/id/default-state cases |
| T03 | Add pure interval/basis/same-record matching policy; domain | T02 | AC-04–AC-10, AC-36, AC-38 | Small deliberately adversarial fixtures, inclusive boundaries, unknown-basis truth table |
| T04 | Implement snapshot preflight and agree producer-idle load/refresh checkpoint; infrastructure + curation owner | T01; resolve integration gaps | AC-01, AC-20, AC-21, AC-42, AC-43 | Orphan, identity, header/granularity and observed-write cases; operating checkpoint documented |
| T05 | Implement ExploreInvestigations/GetInvestigationDetail projections with constructor DI; application | T02, T03, T04 | AC-02, AC-12, AC-19, AC-23, AC-40, AC-44 | Port-based tests of counts, denominators, scope and deterministic ordering |
| T06 | Implement cited evidence descriptors and safe reader; infrastructure/application | T04 | AC-15, AC-17, AC-45 | Supported download, missing/unpinned/changed/denied file and valid-root checks |
| T07 | Build native Streamlit Explore/detail/record inspector; interface | T05, T06; discover/install supported Streamlit | AC-03, AC-11, AC-13–AC-16, AC-22, AC-46, AC-47, AC-49, AC-50 | Actual UI smoke with real validated records plus missing/draft data fixtures |
| T08 | Add per-session state, explicit refresh/cache invalidation and offline handling; interface | T07 | AC-20, AC-24, AC-25, AC-41, AC-43, AC-46 | Independent session tests/manual check, no raw/curated writes, restart/reset behavior |
| T09 | Optional documentation history, column presets and coverage visualization; outer layers | P0 complete | AC-18, AC-26–AC-28, AC-31, AC-34 | Latest-attempt/latest-success states, no fabricated data or merged quantity bases |
| T10 | Execute release verification, record limitations and runtime metrics | T02–T08 | AC-48 plus all P0 scenarios | Ruff, strict domain mypy, existing and new tests, Streamlit startup/browser smoke, measured performance |

T02/T03 may be developed against in-memory fixtures while curation continues. T04 requires integration coordination; do not silently patch the curation model or files from the interface. T09 cannot delay the first functioning P0 prototype.

## Acceptance priority and test ownership

Each AC appears exactly once in this matrix. Future-stage scenarios are specified now as guardrails, not falsely required as completed stage-1 features.

| AC | Stage / priority | Verification owner and expected evidence |
| --- | --- | --- |
| AC-01 | 1 / P0 | Snapshot integration: dynamic catalog/counts by granularity |
| AC-02 | 1 / P0 | Application: absent manual metadata remains browsable |
| AC-03 | 1 / P0 | UI: claim state and draft badge visible with evidence |
| AC-04 | 1 / P0 | Domain: inclusive numerical bounds |
| AC-05 | 1 / P0 | Domain/application: separate rows cannot satisfy conjunction |
| AC-06 | 1 / P0 | Domain/UI: explicit atmosphere basis |
| AC-07 | 1 / P0 | Application: per-field missingness policy |
| AC-08 | 1 / P0 | UI/application: envelope/raw list scope |
| AC-09 | 1 / P0 | Application: nominal claim does not fill TestPoint |
| AC-10 | 1 / P0 | Application/UI: matrix granularity preserved |
| AC-11 | 1 / P0 | UI/application: draft versus applied query |
| AC-12 | 1 / P0 | UI/application: truthful empty results |
| AC-13 | 1 / P0 core; P1 custom columns | UI: displayed quantity definition always reachable; selector optional |
| AC-14 | 1 / P0 | UI: stable composite identity after sorting |
| AC-15 | 1 / P0 | Application/UI: canonical/raw/source/derivation inspector |
| AC-16 | 1 / P0 | UI: source notes without scientific correction |
| AC-17 | 1 / P0 | Adapter/UI: real local-source access |
| AC-18 | 1 / P0 claim guard; P1 history | Application/UI: no association promoted to verified fact |
| AC-19 | 1 / P0 | Application/UI: full-variable-classification scope |
| AC-20 | 1 / P0 | Snapshot/UI: observed interference, stale state and checkpoint policy |
| AC-21 | 1 / P0 | Snapshot: scientific invalid pair is fatal |
| AC-22 | 1 / P0 | Application/UI: reviewed-only empty state |
| AC-23 | 1 / P0 | Application: empty pillar versus absent Claim |
| AC-24 | 1 / P0 | Offline UI smoke with archived sources |
| AC-25 | 1 / P0 | Adapter/UI: read-only scientific exploration |
| AC-26 | 1 / P0 inspector; P1 preset | UI: geometry absent/raw handling |
| AC-27 | 1 / P0 existing values | Application/UI: physical phase never recoded |
| AC-28 | 1 / P0 existing values | UI: distinct temperature/measurement names |
| AC-29 | 1 / P0 existing values | UI: no fabricated detector-performance metric |
| AC-30 | 1 / P0; export later | Application/UI: granularity and source grouping preserved |
| AC-31 | Later comparison; 1 / P0 no pooling | Comparison specification; current UI preserves separate quantity bases |
| AC-32 | 3–4 / deferred | RAG/narrative contract tests; no stage-1 retrieval implemented |
| AC-33 | 2 / deferred; 1 / P0 gravity labels | Scenario specification; current labels do not imply lunar measurements |
| AC-34 | 1 / P0 no invented uncertainty | UI inspection of calibration references |
| AC-35 | Later populated claims; 1 / P0 no invention | UI if Earth claims exist; no requirement to curate new claims |
| AC-36 | 1 / P0 | Application/UI: sparse coverage semantics |
| AC-37 | 1 / P0 | Application: invalid request errors without widget dependency |
| AC-38 | 1 / P0 | Domain/application: O2 missing/basis truth table |
| AC-39 | 1 / P0 | Application: ClaimSelection missing-state distinctions |
| AC-40 | 1 / P0 | Architecture/application: port substitution; no infrastructure imports |
| AC-41 | 1 / P0 | UI: two-session isolation and unmodified snapshot |
| AC-42 | 1 / P0 prerequisite | Integration: orphan and parent/manual identity validation |
| AC-43 | 1 / P0 checkpoint; live publication later | Runbook + adapter/UI: no atomic-generation guarantee from hashes alone |
| AC-44 | 1 / P0 | Application: exact denominator reconciliation |
| AC-45 | 1 / P0 | Adapter: source integrity/root/type states |
| AC-46 | 1 / P0 | UI: restart/reset/removal behavior |
| AC-47 | 1 / P0 | UI browser smoke: labelled selector fallback/keyboard path |
| AC-48 | 1 / P0 release | Recorded verification matrix with pass/fail/deferred and environment |
| AC-49 | 1 / P0 | UI/model compatibility: optional sensor measures and plain labels |
| AC-50 | 1 / P0 | UI: stored quote copied without transformations |
| AC-51 | 1 / authorized analytics amendment | Application/UI: chart selections remain scoped to filtered records |
| AC-52 | 1 / authorized analytics amendment | Application: explicit median grouping; separate fuels/bases |
| AC-53 | 1 / authorized analytics amendment | Application: exclude ranges/missing pairs with counts |
| AC-54 | 1 / authorized analytics amendment | Application: granularity and nominal-atmosphere separation |
| AC-55 | 1 / authorized analytics amendment | UI: descriptive tabs rather than ambiguous view buttons |
| AC-56 | 1 / authorized assistant surface | UI: visible disconnected status, controls disabled, no fake messages |
| AC-57 | 1 / authorized assistant surface | UI: actual context/configuration preview |
| AC-58 | Later assistant execution / deferred | Typed-action validation and revision-scoping tests at integration time |
| AC-59 | 1 / reference-led UI amendment | Browser/UI: horizontal filters, top navigation and chart cards |
| AC-60 | 1 / reference-led UI amendment | AppTest/browser: copilot toggle preserves filter/axis state |
| AC-61 | 1 / reference-led UI amendment | AppTest: workspace navigation keeps details and sources available |
| AC-62 | 1 / reference-led UI amendment | Chart specification: endpoint ticks for singleton coverage |
| AC-63 | 1 / reference-led UI amendment | UI/config export: revision, applied query and matching ids |
| AC-64 | 1 / chart-availability correction | Application/UI: selected-versus-plotted report and precise exclusion reasons |
| AC-65 | 1 / chart-availability correction | AppTest: opening an omitted investigation retains global query |
| AC-66 | 1 / chart-availability correction | Application: primary reasons reconcile with plotting, summaries and local chart scope |
| AC-67 | 1 / chart-availability correction | UI: record-level count and caption reflect filtered scope |
| AC-68 | 1 / filter integration | AppTest: topic links and Home round trips hydrate categorical/numeric controls |
| AC-69 | 1 / filter integration | AppTest: drafts and invalid submissions preserve committed results |
| AC-70 | 1 / filter integration | CSV/JSON integration: every option and multi-select intersection retains expected identities |
| AC-71 | 1 / filter integration | Application/AppTest: standalone basis and explicit numeric-basis conflict handling |
| AC-72 | 1 / filter integration | Infrastructure/AppTest: changed bytes, reload success/failure and selection reconciliation |
| AC-73 | 1 / filter integration | Integration: every persisted CSV cell and record reaches the aggregate/explorer |
| AC-74 | 1 / filter integration | AppTest: retained unreported-condition count is disclosed |
| AC-75 | 1 / filter integration | Application: absent metadata, empty sensor list and not_reported claim remain distinct |
| AC-76 | 1 / supplied homepage | Browser: packaged original JPEG, English copy and conceptual-artwork caption |
| AC-77 | 1 / supplied homepage | Browser/AppTest: hotspot/native-selector synchronization and query preservation |
| AC-78 | 1 / supplied homepage | Browser/AppTest: topic-specific related ids hydrate investigation filters |
| AC-79 | 1 / supplied homepage | Browser: 1440/390 px layouts, uncropped scene, 44 px targets and keyboard activation |
| AC-80 | 1 / supplied homepage | Application/UI: real counts and planned AI status, no illustrative ranking or LIVE badge |

## Challenge-data requirement traceability

| Data requirement | Stage-1 consumer task / later dependency | Representative acceptance coverage |
| --- | --- | --- |
| DATA-01 | T05/T07 study metadata; purpose classification later curation | AC-02, AC-15, AC-27 |
| DATA-02 | T07 inspector; T09 optional presets; geometry curation later | AC-13, AC-26 |
| DATA-03 | T03/T05 scientific conditions | AC-05–AC-09, AC-28, AC-38, AC-44 |
| DATA-04 | T03/T07 flow/setup; richer hierarchy later curation | AC-10, AC-15, AC-31 |
| DATA-05 | T07 source-reported outcomes; ranking/limits later | AC-13, AC-16, AC-36 |
| DATA-06 | T07 existing smoke quantities; detector performance later curation | AC-29, AC-49 |
| DATA-07 | T07 droplet quantities/notes; suppression interpretation later | AC-13, AC-16, AC-28 |
| DATA-08 | T05/T07 distinct bases; side-by-side comparison later | AC-19, AC-23, AC-31 |
| DATA-09 | T07 identity/lineage; export/data card later | AC-15, AC-25, AC-30 |
| DATA-10 | T07 manual claims; research-to-control relationships later | AC-03, AC-18, AC-49 |
| DATA-11 | T07 current gravity labels; HabitatScenario/ranking later | AC-09, AC-33 |
| DATA-12 | T07 populated claims only; technology relationships later | AC-18, AC-35 |
| DATA-13 | T06/T07 evidence/status/source conflicts | AC-03, AC-34, AC-45, AC-50 |

## Verification method

SPEC-002 fire-behavior extension traceability:

| Acceptance | Implemented responsibility | Verification |
| --- | --- | --- |
| FB-01, FB-11 | Shared ExploreInvestigations results; local analysis settings and existing source navigation | tests/interface/test_fire_behavior_app.py |
| FB-02, FB-03, FB-06 | Unit guards, same-record scalars, fixed blend groups, exact pressure coverage | tests/application/test_fire_behavior.py; tests/infrastructure/test_fire_behavior_data.py |
| FB-04, FB-05 | Deterministic adjusted OLS, df/rank/condition guards, Student-t intervals | Analytic factorial and confounding fixtures in tests/application/test_fire_behavior.py |
| FB-07, FB-08 | Signed gas deltas and raw/categorical paired gravity outcomes | Application fixtures and independent curated-cell reconciliation |
| FB-09, FB-10 | Exclusions, source/checksum/column metadata and finite reproducible export | tests/infrastructure/test_fire_behavior_data.py; application identity/export tests |
| FB-12 | Native chart tabs, source actions, copilot context, responsive fuel panels | UI tests and Chrome screenshots linked from docs/fire-behavior.md |

Use minimal behavior-focused fixtures for same-record filters, known versus unknown O2 basis, granularity, metadata identity, explicit empty claims and source errors. Use current curated data only for compatibility/integration checks; do not freeze ongoing curation counts as universal test constants. Cite the dataset revision when recording real-data results.

Import/layer checks: domain imports only allowed dependencies; application imports domain/own ports, not infrastructure/pandas/Streamlit; widgets call use cases, not raw loaders. The composition root may import infrastructure to construct dependencies. Import checks must distinguish composition from ordinary interface callbacks.

No snapshot, source-access or UI acceptance is considered passed by this documentary QA. Existing code prerequisites remain open until corrected and verified by their owners. Run commands from CLAUDE.md at implementation completion; if pytest's default temp/cache directories are inaccessible, use a fresh workspace-local test directory and report that environment choice. Record Streamlit version and browser/runtime evidence separately; test success is not proof the app rendered correctly.
