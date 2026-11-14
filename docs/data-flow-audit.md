# Filter and structured-data integration audit

Inspected on 2026-11-14. Dataset revision: `5fa2ee153f3fa0eee6fa2fbb43e9a546b9982b807ab04f582b075a4f3371fc56`. Counts describe this checkpoint and are not application constants.

## Reconciliation

| Check | Observed result |
| --- | --- |
| Curated investigations | 15 |
| CSV records / loaded TestPoints / unfiltered result records | 1,615 / 1,615 / 1,615 |
| Registered table source hashes compared with current source bytes | 16 of 16 match |
| Normalized data/manual records compared with embedded curated metadata | 15 of 15 match |
| Manual review states | 15 draft; no human-reviewed record |
| Categorical values checked against CSV/JSON-derived identities | 109 across 11 facets, including standalone O2 basis |
| Hardware / sensor filter labels | 14 / 27; labels are current claims, not inferred hardware families |

The integration tests read persisted CSV/JSON independently and reconcile every cell, record id and documented extra-column identity with loaded aggregates. Every categorical option retrieves exactly its expected record identities. A real-data multi-select combination checks OR within a facet and AND across facets. Independent SQLite queries over persisted cells verify oxygen/pressure conjunction, missing-pressure inclusion and flow interval overlap. Separate application fixtures verify same-record matching, inclusive boundaries, invalid ranges and unknown/incompatible oxygen basis.

## Actual consumption path

Registered source tables and manual metadata → existing curation use case → data/curated CSV/JSON pairs → CuratedRepository → validated immutable browsing Snapshot → ExploreInvestigations → matching records shared by metrics, catalog, detail and chart builders.

Raw Excel/source files and data/manual are not read by filter widgets or charts. Corrections must reach the curated pairs before dataset reload. The inspected normalized manual claims and registered table hashes were synchronized at this checkpoint. This does not certify unregistered files, source evidence correctness or scientific measurements.

The snapshot fingerprint covers curated file pairs and data/sources.json. Each rerun compares current bytes with the loaded revision and warns about changes or unreadable inputs. A successful reload preserves valid query selections; removed options are announced. Failure preserves both the old snapshot and query. The check costs approximately 4 ms per call in a ten-call local sample over about 658 KB of curated inputs; this is a local observation, not a deployment guarantee. No automatic curation, idle-page polling or atomic producer publication was added.

## Defects corrected

1. Home topic navigation applied investigation ids while showing an empty investigation multi-select. Controls now initialize from the committed query whenever absent, including after Home hides them. Visible drafts remain staged until Apply.
2. Invalid form submission could leave changed controls beside previous results without identifying the committed scope. An explicit rejection message and readable applied-filter summary now identify which query produced the results. Include-unreported numeric filters disclose retained missing counts.
3. A cached snapshot could conceal newer curated bytes until explicit reload. A visible freshness warning now identifies that state. Reload previously reset filters before validation, losing the query even when loading failed; reconciliation/reset of controls now occurs only after successful loading.
4. Standalone O2-basis filtering was specified but absent. It now uses actual ambient/oxidizer_stream/missing values. Numeric filtering rejects ambiguous/conflicting categorical basis choices.
5. A not_reported sensor claim was grouped with an empty sensor list. They now remain distinct from each other and from unavailable manual metadata.

## Scope and remaining limitations

The six-investigation screenshot case retains all six investigations and 629 records. Its oxygen/burn-time chart uses 271 pairs; the other records remain available and have explicit availability reasons. Chart-local selections and scalar-pair requirements refine the profile only. Record-volume bars display the top six investigations, clearly labelled; the catalog retains the complete filtered list.

Filter options come from the full snapshot and therefore remain stable across filtering. Combinations may legitimately have zero matches. A fuel-phase missing option is absent in this checkpoint because all rows report a phase; missing fuel names, flow directions and O2 bases do have explicit options. Hardware and sensor choices come from claim values; their presence does not upgrade draft review status.

Diluent and investigation-specific extra fields remain available in the record inspector; not every structured column has a dedicated global filter. Applicable quantitative extras can be chosen as chart axes. Semantic hardware-family grouping, generic extra-column filtering and separate typed selection sentinels remain outside this increment. Missing values, nominal atmosphere and interval midpoints never fill missing measurements.

## Verification references

- SPEC-001 section 19 and AC-68–AC-75 define the expected behavior; task traceability lists the corresponding checks.
- tests/infrastructure/test_explorer_integration.py checks persisted cells, every categorical facet, independent numeric queries and revision changes without altering repository data.
- tests/application/test_explorer.py checks scientific predicates, metadata missing states and removed-option reconciliation.
- tests/interface/test_explorer_app.py checks Home synchronization, drafts, invalid Apply, retained missing counts, standalone basis and successful/failed reloads.

Tests do not replace visual accessibility review or human verification of cited scientific documents. PDF layout checks require the separate pdftotext/poppler dependency.

Completed validation: full suite 156 passed, 179 PDF visual-line checks skipped because pdftotext/poppler is absent; Ruff clean; strict mypy on domain and the exploration application passed. Headless Chrome at 1440 by 1700 verified Home related-research navigation followed by Dashboard: the visible Investigation chips and accessible combobox label contain FLEX/FLEX-2/CFI, matching the committed query; record-count bars retain all three investigations while the profile explains their different availability. No rendered exception was observed after the components finished loading. [Browser capture](screenshots/filter-integration.png). Mobile layouts and a full accessibility audit were not verified in this increment.
