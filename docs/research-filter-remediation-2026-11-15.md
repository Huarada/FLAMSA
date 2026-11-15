# Research filter remediation

Date: 2026-11-15. Implements SPEC-001 section 27, AC-96 through AC-100. Historical findings: [pre-remediation audit](research-filter-validation-2026-11-15.md), ADR-0154 and ADR-0155. The historical reports remain unchanged; after-fix reports are separate files.

## Changes by audited finding

| Finding | Implemented behavior |
| --- | --- |
| RF-01: local study selection invalidated by research changes | Reconcile before rendering widgets. Preserve valid refinements; extend an all-studies selection to the new result; recover a nonempty selection when no member survives. Preserve intentional emptiness. Reset explicitly restores chart defaults. |
| RF-02: oxygen-basis conflict | Use the active numeric oxygen basis or the single explicitly restricted reported basis. Otherwise offer bases present in retained records and preserve a valid local choice. Explain that chamber and burner-stream oxygen are separate. |
| RF-03: misleading map emptiness | State that the map alone has no eligible points, include the retained-record count and name both required scalar measurements. Direct users to other quantities or retained records. |
| RF-04: inactive numeric values silently ignored | Reject Apply with an enable-or-clear instruction for inactive bounds or include-unreported choices. Preserve the committed query. Keep the batched form; no rerun on every draft numeric change. |
| RF-05: zero-count fallback axes | Offer only positive-count vertical partners. Disable the vertical selector when none exists. Distinguish summaries, insufficient quantities, missing pairs and intentional empty scope; retain record navigation. |
| RF-06: cleared selectbox rejected | Normalize cleared optional selections to documented defaults: ambient numeric oxygen basis, review all, notes any. Active-range and cross-basis validation remain enforced by the application. |
| RF-07: stale native quantity label/count | Separate durable logical choices from native widget keys. Widget identity includes research context and displayed options/counts, so frontend selected text is refreshed when its meaning changes. |

`interface/chart_controls.py` owns presentation state only. It does not implement scientific matching or ranking. Existing application projections, repository consumption, cache boundaries, scalar eligibility and source/provenance contracts remain in place. Empty comparison contexts use null rather than a fabricated excluded-record count when no pair of axes exists. No dataset, scientific formula, ranking weight or model configuration was changed.

## Results

- The independent CSV/JSON oracle repeated all **9,659 valid queries** and **8 invalid-query cases**, with no mismatched retained/map record identities and all invalid cases rejected.
- The widget/Arrow audit repeated **378 states**, including all **225 ordered study transitions**. Checks cover actual plotted identities, committed queries, inactive-input errors, cleared defaults, automatic stream basis, positive-count vertical options and reset.
- The earlier matrix had **156 empty local selections** among study transitions and **120 recoverable empty comparisons** on the same axes. Both counts are **zero** after remediation. This is a result for the defined transition matrix, not a claim that every study has plottable measurements.
- Native Chrome checked twelve states and asserted visible selected labels as well as record/map counts. FLEX → BASS-II automatically showed initial CO2 with **127 records** in both selector and comparison. Restricting research to burner-stream oxygen automatically showed burn time with **154 records**, the stream basis and **154 plotted tests**. A native numeric edit reproduced the explicit inactive-input error, and FLEX-2 showed a disabled vertical selector with a summary-only explanation. There were no rendered exceptions. [BASS-II screenshot](screenshots/filter-fixed-flex-to-bass-reconciled.png), [stream comparison screenshot](screenshots/filter-fixed-stream-basis-synchronized.png), [summary-only screenshot](screenshots/filter-fixed-summary-only-disabled-partner.png).
- Full suite: **261 passed, 179 skipped**. Skips require pdftotext/Poppler PDF visual-line verification. Targeted regression tests and final static checks are recorded in the ADR verification entry.

Artifacts: [query-engine results](research-filter-engine-after-fixes.json), [widget/Arrow results](research-filter-ui-after-fixes.json), [native-browser observations](research-filter-browser-after-fixes.json), [regression tests](../tests/interface/test_filter_chart_regressions.py). Run the two audit scripts with `--output` to preserve historical reports, for example `python scripts/audit_research_filter_ui.py --output docs/research-filter-ui-after-fixes.json`.

## Deliberate limits

The coverage map still correctly has no dots for BASS-II or summary-only FLEX-2. Pressure is not invented, ranges are not reduced to midpoints, and summaries are not promoted to individual tests. Review filtering still returns zero for reviewed metadata because this revision contains only draft metadata. These are expected source constraints, now explained more clearly.

No paid/live-model request, physical-device or full accessibility/screen-reader audit was performed. Chrome validation used a desktop viewport; automated widget and record-identity checks provide broader functional coverage, not exhaustive coverage of every browser or continuous numeric value. Frontend label assertions are necessary in addition to backend AppTest checks. The browser probe did not find native clear buttons for the three optional selectboxes; its default-selection observation does not prove native clearing. Cleared-None normalization is covered by AppTest. After the final matrix, an equivalent Ruff normalization combined identical branches in the presentation helper; four focused regressions passed again after that formatting change.
