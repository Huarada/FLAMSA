# Research filters: validation before remediation

Date: 2026-11-15. Status: audit complete; findings below remain open. No production filtering, chart, cache or UI logic was changed in this audit.

The reported failure is reproducible. Valid research results can leave the comparison chart empty because its independent controls retain incompatible state. A separate browser defect displays an outdated vertical-quantity label and record count. The CSV/JSON-to-research-query selection itself did not disagree with the independent oracle in the tested cases.

## Dataset and method

Dataset revision: `a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204`.

- 15 investigations; 1,615 records: 1,556 individual tests and 59 daily/matrix summaries.
- Baseline coverage map: 693 individual tests with scalar oxygen and pressure. Baseline comparison: 447 tests with ambient oxygen and burn time.
- An independent oracle reads curated CSVs and metadata JSON directly. It checks retained record identities, not only counts, without reusing the application's matching predicates.
- A Streamlit AppTest audit submits actual form widgets and reads the compiled Vega chart datasets through Arrow. It compares the identities of rendered map/profile points with independently eligible CSV rows under the current chart scope, axes and oxygen basis. Matching the current controls does not mean those controls are usable or synchronized.
- Chrome exercised the running application at `127.0.0.1:8501`, at 1440 × 1100, using native controls. Screenshots were visually inspected for the two primary failures and their recovery through existing controls. These are interaction demonstrations, not production fixes.
- Seven production-file hashes were captured in both automated reports and remained unchanged during their respective runs. No curated/raw data was edited and no copilot/model request was submitted.

| Validation layer | Coverage | Result |
| --- | --- | --- |
| Query engine | 9,659 valid queries; 8 invalid queries | No record/map identity mismatch; all invalid cases rejected |
| Widget and chart integration | 378 observed states, including all 225 ordered study transitions | No exception or CSV/Arrow identity mismatch under the actual controls; state coordination failures confirmed |
| Running Chrome | 9 observed states | Expected record/map counts, no rendered exceptions; empty scope, basis conflict and stale labels reproduced |
| Existing full suite | 257 passed; 179 skipped | Skips require pdftotext/Poppler PDF visual-line verification |
| Static checks | Ruff; mypy on domain | Passed |

The query matrix includes every available single categorical option, every two-option combination within a facet, all-options selections, every pair of values across different facets, study × record-level × phase combinations, numeric boundary/missing-value combinations, per-study numeric cases, search and review/note policies. Facets include investigation, record level, fuel phase/material, flow direction, lineage, oxygen basis, hardware, sensors, pillar and gravity. Numeric cases cover oxygen, pressure and flow with inclusive endpoints, absent bounds, explicit missing-value policies and incompatible bases.

The UI matrix additionally covers unapplied drafts, invalid/reversed ranges, cleared selectboxes, inactive numeric inputs, reset, return through Home, independent chart selection and both oxygen bases. This is broad finite coverage, not a proof over every continuous numeric value, arbitrary selection subset, browser/device or concurrent reload interleaving.

## Open findings

### RF-01 — High: changing research scope can empty the chart's independent investigation selection

The comparison uses `chart_investigations`, separately from the research form's investigation selection. After the available investigations change, the native multiselect can discard its previous values and remain empty. The chart then receives no investigation IDs even though the research query retained valid tests. Its controls normally live inside a collapsed expander.

Across all 225 ordered study transitions, 156 ended with an empty local selection while chart axes were available. In 120 transitions, selecting the retained studies alone would recover points on the same axes; the remaining empty states also have scientific availability constraints. These figures measure the scripted transitions, not the frequency of failures among users.

Reproduction: reset; apply FLEX; apply BASS-II; open Chart settings. Research retains 129 rows, but the comparison has no studies selected. Selecting BASS-II with the existing chart control restores its plot. In the AppTest transition, oxygen versus final CO2 would recover 123 points on the same axes; a fresh BASS-II selection chooses initial CO2 and plots 127. Chrome also recovered the initial-CO2 comparison with 127 points.

Evidence: [empty local scope](screenshots/filter-audit-flex-to-bass-empty.png), [recovery through the existing control](screenshots/filter-audit-bass-restored-via-existing-chart-control.png). Root location: `src/psi_fire/interface/reference_dashboard.py`, `chart_grid`, `chart_investigations`.

### RF-02 — High: research oxygen basis and chart oxygen basis can silently conflict

Reproduction: reset; choose Reported oxygen basis = `oxidizer_stream`; apply. The query retains 154 ACME-CFI-G tests and the coverage map plots all 154, but an ambient-basis comparison plots zero. With ACME-CFI-G selected locally, changing only Oxygen basis for plotted O2 to `oxidizer_stream` restores 154 points. Both AppTest and Chrome reproduced this.

The map accepts both bases and distinguishes them with mark shape; the comparison accepts only its selected basis. This scientific distinction is necessary. The bug is the uncoordinated controls and generic empty guidance, not the exclusion of burner-stream oxygen from an ambient comparison.

Evidence: [conflicting basis](screenshots/filter-audit-stream-basis-conflict.png), [aligned basis](screenshots/filter-audit-stream-basis-aligned.png). Root location: research query `bases` versus comparison `chart_basis` in `reference_dashboard.py`.

### RF-03 — Medium: the map-empty message is interpreted as global data loss

`No test that passes the filters reports both oxygen and pressure` is accurate for this particular map, but insufficient as a leading explanation of a valid retained result. Only ACME-CFI-G, CFI and FLEX supply the map's scalar test pairs in this revision; 12 investigations cannot draw a dot on it.

Examples under fresh/reset AppTest states:

| Research selection | Retained records | O2/pressure map dots | Comparison dots with the selected axes |
| --- | ---: | ---: | ---: |
| All records | 1,615 | 693 | 447, oxygen / burn time |
| BASS-II | 129 | 0 | 127, oxygen / initial CO2 |
| Solid fuel | 389 | 0 | 4, oxygen / burn time |
| FLEX-2 | 8 | 0 | 0, matrix summaries only |
| Oxidizer-stream oxygen | 154 | 154 | 0 ambient; 154 after basis alignment |

Comparison defaults can differ after prior interactions. This table does not promise that any retained record has every requested quantity. Summaries and interval midpoints must remain excluded from individual-test scatter plots.

### RF-04 — Medium: editable numeric bounds are silently inactive without their checkbox

Entering a minimum of 90 in oxygen, pressure or flow while the corresponding Filter checkbox is off still retains all 1,615 records. Enabling the checkbox produces zero records for these tested bounds. The behavior follows the current query contract, but the editable inactive inputs make the apparent selection ambiguous. This re-confirms the previously logged inactive-input issue; no filter semantics should change implicitly during remediation.

### RF-05 — Medium: fallback axes and generic guidance cannot repair summary-only selections

When there are no eligible scalar pairs, `chart_grid` falls back from positive-count partners to other quantity keys, all with zero eligible records. FLEX-2 retains eight matrix summaries, which cannot become individual tests by broadening Chart settings. The fallback and message should distinguish incompatible controls from unsupported record granularity, missing values and unavailable measurements.

### RF-06 — Medium: a cleared selectbox prevents submission, including inactive oxygen controls

AppTest can set Oxygen measurement basis, Manual review or Curation notes to `None`. Apply then rejects the draft and retains the last valid results. Clearing oxygen basis raises `None is not a valid O2Basis` even with the oxygen numeric filter disabled; the other two raise `Unknown review or note selection`. Transactional preservation is correct, but the validation/default handling is confusing. Programmatic widget states are proven; clearing these particular controls by a physical pointer was not separately verified in Chrome. Do not overstate that browser coverage.

### RF-07 — High: browser quantity label and count become stale while the chart changes

In Chrome, after FLEX → BASS-II and restoring BASS-II locally, the vertical selector still displayed `Burn time (s) · 447 records`, while the chart title and axis displayed initial CO2 and the caption reported 127 plotted records. The 447 label came from the earlier baseline. After aligning stream oxygen, that same selector still advertised 447 while the comparison showed 154.

This is a visible quantity/units inconsistency, not merely a stale count. The chart payload changes correctly under the backend's chosen axes, but the visible control misrepresents them. AppTest record-identity assertions alone did not detect it. The relevant code dynamically changes options/`format_func` and may remove `chart_y` from session state under a stable widget key. Exact Streamlit/frontend invalidation mechanics require a focused regression before selecting a fix; stale frontend label retention is observed, not a proven upstream-library root cause.

Evidence: [selector says burn time while chart says CO2](screenshots/filter-audit-bass-restored-via-existing-chart-control.png), [447 in selector versus 154 plotted](screenshots/filter-audit-stream-basis-aligned.png).

## Expected emptiness and checks that passed

- All 15 metadata records are draft. Selecting reviewed legitimately returns zero; unavailable review also returns zero in this dataset.
- Empty category selections mean unrestricted, OR applies within a facet and AND across facets to the same retained TestPoint where appropriate. Tested combinations matched raw curated identities.
- Including unreported measurements retains rows without manufacturing oxygen, pressure or flow values. Those rows may still be ineligible for a given chart.
- Numeric interval overlap, scalar eligibility, incompatible-basis validation and invalid-range rejection behaved as specified in the tested matrix.
- Invalid drafts retain the last valid committed query; unapplied edits do not change the result scope.
- AppTest reset restored 1,615 rows, 693 map dots and the 447-point default comparison in the tested sequences. Chrome final reset restored baseline research/map counts. Do not claim every browser chart label resets correctly: RF-07 demonstrates otherwise.
- No cache contamination or wrong CSV-to-rendered-point identity was found in the tested transitions. Metadata filter success means correspondence with existing curated claims, not a new scientific review of hardware/sensor evidence.

## Proposed remediation sequence, not implemented

1. Define and test the contract between committed research scope and local chart scope. Preserve valid explicit refinements, reconcile invalidated selections, and distinguish an intentionally empty selection from an emptied stale one.
2. Reconcile oxygen-basis selection explicitly while preserving the scientific distinction between ambient and oxidizer-stream oxygen.
3. Add a real-browser regression for selected quantity labels, units and counts across scope/axis changes; ensure the displayed selection agrees with the compiled chart.
4. Make inactive numeric inputs unambiguous and handle cleared/default selections consistently.
5. Explain each empty state with retained-row counts and the specific missing requirement. Offer applicable comparisons only when scientifically supported, without inventing pressure or treating a matrix as a test.
6. Re-run the oracle, UI transition matrix and native-browser cases after remediation; retain these failures as regression cases.

## Reproducible artifacts

- [Engine oracle script](../scripts/audit_research_filters.py) and [9,659-query results](research-filter-engine-audit.json).
- [Widget/Arrow audit script](../scripts/audit_research_filter_ui.py) and [378-state results](research-filter-ui-audit.json).
- [Chrome observations](research-filter-browser-audit.json) and linked screenshots above. Browser results assert retained-record/map counts and absence of rendered exceptions; comparison behavior and stale labels were additionally inspected visually, with identity verification supplied by the separate Arrow audit.

From the repository root, run `python scripts/audit_research_filters.py` and `python scripts/audit_research_filter_ui.py`. Both are read-only with respect to application/data files, regenerate their own audit reports and make no model requests. Audit scripts intentionally read CSV/JSON directly as an independent verification oracle; this is not an alternate production data-access path.
