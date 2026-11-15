# Dashboard research-filter audit

Date: 2026-11-14. Revision: `a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204`.

## Finding

The message `No test that passes the filters reports both oxygen and pressure.` is emitted by `interface/reference_dashboard.py:coverage_map`, not by the research-filter engine. It means the oxygen/pressure coverage map has zero eligible dots. It does not mean the filtered records are empty or that all their measurements are unavailable.

The execution chain is Research filters → candidate query validation → committed `applied_query` → `ExploreInvestigations` → matching records → `condition_map`. The map only accepts individual `test` rows with finite scalar oxygen and pressure on the same row. Daily/matrix summaries and non-singleton ranges do not become dots. Metadata nominal atmospheres are not substituted for missing per-test readings.

The supplied examples and existing contracts confirm same-record matching, OR within categorical selections, AND between filters, inclusive interval overlap, explicit numeric include-missing policies and commit-on-Apply. No incorrect row matching was found in the audited paths. Three interface issues and one documentation inconsistency are recorded below; none requires inventing pressure or oxygen values.

## Current data coverage

| Investigation | Retained records without filters | O2/pressure map dots | Reason for missing dots |
|---|---:|---:|---|
| ACME-CFI-G | 333 | 333 | All rows have both scalar conditions; chamber/stream basis remains separate. |
| CFI | 87 | 87 | All rows have both scalar conditions. |
| FLEX | 274 | 273 | One row has no scalar pressure. |
| BASS-II | 129 | 0 | No mapped per-test pressure. Oxygen readings are present. |
| SAFFIRE-I | 2 | 0 | No scalar pressure; one row also lacks scalar oxygen. |
| SAFFIRE-II | 9 | 0 | No scalar pressure; two rows also lack scalar oxygen. |
| BASS | 122 | 0 | Neither condition is mapped as a scalar core quantity. |
| SAFFIRE-III | 2 | 0 | Neither condition is mapped as a scalar core quantity. |
| SAME | 20 | 0 | Neither condition is mapped as a scalar core quantity. |
| SAME-R | 109 | 0 | Neither condition is mapped as a scalar core quantity. |
| SPICE | 469 | 0 | Neither condition is mapped as a scalar core quantity. |
| ACME-BRE | 18 | 0 | Daily summaries. |
| ACME-E-FIELD | 21 | 0 | Daily summaries. |
| SLICE | 12 | 0 | Daily summaries. |
| FLEX-2 | 8 | 0 | Test-matrix records, not individual tests. |

Total: 1,615 retained records = 1,556 individual tests + 59 summaries. There are 693 map dots from three investigations. Thus 12 of 15 investigations have no dots in this particular map, even without numerical restrictions. This is a coverage limitation, not a failure to load their records.

## Reproduced cases

| Applied research query | Retained records | Map dots | Assessment |
|---|---:|---:|---|
| No restrictions | 1,615 | 693 | Normal baseline. |
| Fuel phase = solid | 389 across seven investigations | 0 | Correct matching; no selected solid-fuel row has the scalar pair. Other measurements remain available. |
| Investigation = BASS-II | 129 | 0 | Correct matching; pressure is unreported in the mapped table. |
| Investigation = FLEX-2 | 8 | 0 | Correct matching; all eight are matrix summaries. |
| Fuel phase = gas | 853 | 333 | Only ACME-CFI-G supplies dots. |
| All three known fuel phases | 1,615 | 693 | Same as unrestricted at this revision; no missing fuel phases were found. |
| Ambient O2 >= 30%, pressure <= 10.2 psi, missing excluded | 28 | 20 | Twenty ACME-CFI-G individual tests plus eight overlapping FLEX-2 matrix envelopes. The latter are retained by interval matching and never plotted as observations. |

With no filters, scenario counts are 20 chamber-atmosphere tests and 28 burner-stream tests. The latter are not cabin-atmosphere matches. These counts are distinct from the map's total 693 dots and from FLEX-specific Fire behavior coverage.

## Confirmed issues

### F-01: coverage-map diagnostics do not explain the actual cause

Severity: medium, presentation. The same generic message is used for solid-fuel tests missing pressure and for FLEX-2 where there are no individual tests at all. `ConditionMap` returns counts and investigation names, but no per-record reason distribution. The later availability table concerns user-selected comparison axes rather than this fixed map, so it does not explain this map reliably.

Reproduction: apply Fuel phase = solid; the UI retains 389 records and displays the quoted message. Apply Investigation = FLEX-2; it retains eight summaries and displays the same message. Both are scientifically expected exclusions, but the interface does not clearly distinguish them at the empty map.

Recommended fix: state retained records and individual-test count next to the empty map, then classify missing oxygen, missing pressure, both missing, interval-only conditions and summary records. Say explicitly that the result remains available in the CSV/record views. Keep map eligibility unchanged.

### F-02: editable numerical bounds can be silently ignored

Severity: medium, usability. Oxygen/pressure/flow inputs remain editable while their corresponding Filter checkbox is off. Submission builds a `ConditionRange` only when the checkbox is enabled, so Apply filters can succeed while discarding the entered numerical restriction.

Reproduction: from the default Dashboard, enter Oxygen minimum = 90 and click Apply filters without checking Filter oxygen. The committed query has `oxygen=None`; records remain 1,615 and map dots remain 693, with no error. This follows the checkbox implementation, but the editable inputs and successful Apply create a misleading interaction. The same code pattern applies to pressure and flow.

Recommended fix: either derive activation from supplied bounds, or make inactive controls clearly disabled with an explanation. If checkbox activation remains, warn on submission when populated bounds are excluded. Preserve explicit missing-data and measurement-basis policies.

### F-03: comparison-chart selection can become empty after a valid research-filter change

Severity: medium, chart state. The local `chart_investigations` widget stores a narrower scope separately from the research query. When a new research result removes every selected chart investigation, Streamlit discards unavailable selections. The application does not distinguish this automatic invalidation from the user's deliberate empty selection.

Reproduction: start unrestricted; select only FLEX under Investigations in comparison charts; then apply Research filters → Investigation = BASS-II. The research result contains 129 BASS-II records, but the chart investigation selection is empty. The comparison panel reports no compatible scalar pairs and no investigations selected, although BASS-II has other compatible quantities. Independently, the coverage map remains empty because pressure is absent; these are two different causes.

Recommended fix: reconcile local chart scope against the new result, preserve valid explicit choices, and show an actionable notice when automatic invalidation empties it. Offer an explicit action to select all retained investigations; do not silently override an intentionally empty selection. Research Reset filters restored the full scope in the reproduced sequence.

### F-04: README omits CFI from oxygen/pressure coverage

Severity: low, documentation. The lunar-habitat section says only FLEX and ACME-CFI-G report both quantities per test. CFI also contributes 87 scalar pairs, with pressure traced to its source Pressure column in atm and converted to psi. The correct coverage list at this revision is ACME-CFI-G, CFI and FLEX.

Recommended fix: correct that statement and distinguish general pair availability from matching the enriched-oxygen/reduced-pressure lunar scenario. CFI does not enter the strict ambient query shown above. This finding supplements the earlier formula audit.

## Verification and scope

The coverage matrix and scenario counts were computed from validated repository aggregates. Streamlit AppTest reproduced the default view, inactive oxygen bound, solid-fuel scope, matrix-only scope, stale local-chart selection and reset, with no application exception. No copilot request or external model call was made; `PSI_LLM_MODEL` was explicitly empty for these probes.

This is an audit and bug log. Production filtering, chart eligibility and curated/raw data were not changed. Findings describe the current revision; the user's exact active selections and live browser session were not available. Native AppTest validates Python/widget state, not physical browser interaction or visual layout. Test results are recorded in the corresponding ADR verification entry.
