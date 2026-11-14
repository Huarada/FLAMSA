# SPEC-001 QA report

Date: 2026-11-14. Reviewed revision: 0.3. Scope: requirements, DDD/application design, implementation traceability and current producer/consumer compatibility. This is a specification QA, not a Streamlit runtime certification or a scientific data review.

## Outcome

The initial specification covered the scientific scope well, but was not sufficiently precise to serve as an implementation contract. This QA corrected conflicting priorities, clarified query semantics and added DDD/port/type/error responsibilities, source delivery, session/accessibility requirements and a task-to-acceptance matrix.

Documentary disposition: revised proposal suitable for review and subsequent pure query/domain work. Integrated stage-1 release remains dependent on the two reproduced integrity gaps and an explicit producer-idle loading checkpoint. No issue is labelled runtime-fixed by a documentation edit. No application, model or curated file was changed during this QA.

## Findings register

| Id | Severity | Finding and evidence | Disposition |
| --- | --- | --- | --- |
| QA-01 | High | Evidence inspection was P0 while archived documentation and dictionary access were P1, leaving minimum source access unclear (SPEC-001 section 3 versus 7.3/7.4) | Corrected: cited source access and definitions for displayed values are P0; extra document history/custom columns remain P1 |
| QA-02 | High | Request/result names existed without concrete selection, default, error or immutability policies (section 5) | Corrected: companion design defines proposed request/results, ports, typed states and responsibilities; no claim these types exist yet |
| QA-03 | High | O2 basis multi-select plus include-missing could either hide every unknown-basis row or accidentally admit known oxidizer-stream rows (section 6) | Corrected: active O2 range has one basis; unknown values/basis have an explicit truth rule; standalone basis filter is inactive then; AC-38 |
| QA-04 | High | Stable file fingerprints were described as one coherent snapshot, despite CuratedStore.save writing JSON then CSV separately | Contract corrected: only completed/idle producer checkpoint supported in stage 1; arbitrary live publication remains unspecified/unimplemented; AC-20/43 |
| QA-05 | High | CuratedRepository.ids enumerates only directories with investigation.json; a CSV-only directory is silently omitted | Reproduced, runtime OPEN: new isolated CSV-only directory returned ids=[]; preflight requirement AC-42 must be implemented by integration owner |
| QA-06 | High | Investigation._check_invariants does not compare manual_metadata.investigation_id with its parent | Reproduced, runtime OPEN: model_validate accepted parent ACME-CFI-G and manual id UNRELATED-INVESTIGATION; must reject at integration/domain boundary before release |
| QA-07 | Medium | No explicit DDD boundary between aggregate, projection, technical revisions and UI selection; predicates could leak into callbacks | Corrected: one research domain, existing aggregate reused, pure predicates in domain, workflow/DTOs in application, files in adapters, state in interface; AC-40 |
| QA-08 | Medium | NaN/infinity/range validation was only phrased as a UI responsibility | Corrected: application query rejects invalid input independently of widgets; no code-side invariant fix is implied; AC-37 |
| QA-09 | Medium | Coverage denominator, zero eligible rows and numeric sort/precision behavior were ambiguous | Corrected: basis-scoped eligible/reported/missing counts, no 0%-from-no-data, stable tie-break and display-only rounding; AC-44 |
| QA-10 | Medium | Acceptance criteria mixed future RAG/comparison and current P0 without execution ownership | Corrected: 50 unique ACs have explicit stage/priority/test ownership; T01–T10 and DATA-01–DATA-13 have traceability; future runtime cases remain deferred |
| QA-11 | Medium | Local evidence links were recognized as a risk but source-reader integrity/version/error contract was incomplete | Corrected: opaque handles, approved resolved roots, safe schemes, pinned versus unpinned hashes and unavailable/changed/unsupported states; AC-45 |
| QA-12 | Medium | Cached resources versus per-user filter state and aggregate dictionary mutation were not fully separated | Corrected: immutable/copying projections, shared read resources only, independent sessions and explicit cache revisions; AC-41 |
| QA-13 | Medium | No keyboard/table-selection fallback, restart/reset contract or measurable prototype performance targets | Corrected: labelled selectors, status text, restart defaults, explicit UI smoke and measured environment-specific targets; AC-46/47 |
| QA-14 | Medium | Empty sensors/pillars, missing metadata and not_reported claims could collapse into one selection sentinel | Corrected: separate value/Claim selection states, explicit empty-list semantics and independent review filter; AC-39 |
| QA-15 | High | Concurrent curation changed Sensor.measures to optional and required plain instrument labels; evidence quote-copy policy also tightened in ADR-0032/0033 | Corrected: optional measures=Not stated, plain labels/evidenced notes, exact copyable independent quotes; richer sensor fields remain deferred per ADR-0034; AC-49/50 |

High means potential incorrect scientific selection/evidence or an unimplementable release claim; Medium means architecture/testability/usability ambiguity. Severity describes this project's implementation risk, not a general-purpose security rating.

## Evidence gathered

- Read CLAUDE.md, the current project skill, SPEC-001, ADR decisions, domain/model.py, domain/manual.py, application/ports.py, curated_store.py, source_registry.py and current dependency/test inventory.
- Loaded all current curated aggregates through CuratedRepository: 15 investigations and 1,615 records at inspection. Counts are compatibility evidence, not permanent product requirements.
- Reproduced QA-05 using a fresh isolated directory under a unique workspace-local temporary path; no curated directory was changed.
- Reproduced QA-06 by validating an in-memory copy of an existing aggregate with a deliberately different manual id; no manual/curated file was changed.
- Checked coverage and uniqueness of requirement/acceptance/task/finding identifiers and local companion links after edits. The implementation task document records every AC exactly once in its acceptance matrix.

The above reproduction demonstrates that the current deserialization/model path does not enforce the complete proposed integrity contract. It does not prove all current data is corrupt; the current dataset loaded successfully. Missing producer generation markers and weak type-level guarantees are implementation prerequisites, not justification to rewrite scientific data in Streamlit.

## Readiness and ownership

| Gate | Present status | Required next evidence |
| --- | --- | --- |
| Requirements/defaults review | Proposed; documentary QA complete | User/product review of current spec/design, especially missingness and draft-state defaults |
| Pure query/domain implementation | Can follow reviewed types without changing curators | Behavior tests for same-record/basis/range semantics |
| Curated-pair discovery integrity | OPEN (QA-05) | CSV-only and JSON-only directory rejection with selected-curated-scope enumeration |
| Manual-parent identity integrity | OPEN (QA-06) | Mismatched manual id rejected, compatible current data still loads |
| Producer/consumer coordination | Explicit stage-1 idle-checkpoint operating contract proposed | Curation/dashboard owners record how startup/refresh occurs only after producer completion; otherwise retain old snapshot/report unavailable |
| Streamlit runtime/dependency choice | Not implemented or verified | Supported installed version, startup and UI/browser smoke |
| Full project MVP | Not complete through this spec | Separate ranking/XAI/export increments remain required |

Curation owner resolves scientific model/publishing changes; dashboard owner supplies consumer preflight and UI/application code. Coordinate the two integration fixes rather than creating a competing repository or putting patches in callbacks. A versioned producer manifest is only needed if concurrent live refresh is required; it is not silently added to the current data schema by this QA.

## Not verified

Subsequent authorized amendment: SPEC-001 section 14 expands the current requirement matrix from the 50 cases reviewed in this QA to 58, adding analytic chart behavior, clearer detail tabs and a disconnected assistant workspace. See docs/dashboard.md and the analytics ADR entries for implementation verification; this original QA report does not retroactively certify every new acceptance case.

No explorer use cases, filter implementation, source-access implementation, Streamlit session behavior, browser rendering, accessibility outcome, performance measurement, ranking or RAG exists to validate under this task. No new evidence extraction, source download, source assertion review, full runtime acceptance suite or data correction was performed. A green curation suite would not close these gaps. Report runtime results per task at implementation time, not as documentary QA passes.
