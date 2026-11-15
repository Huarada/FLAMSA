# Home content audit against challenge and implementation

Date: 2026-11-14. Scope: Home text, displayed counts, thematic links and entry points. Reviewed the complete user-supplied challenge brief, CLAUDE.md, project skill, relevant ADR decisions, SPEC-001/002/003 and current Home, analysis, ranking, copilot and evidence implementations.

## Assessment

The Home's conceptual scene, archive counts, curated topic links, review-state disclosure and fire-safety scope were substantially aligned with the project. The main functional description was stale: it said deterministic ranking was planned and no relevance scores were computed, although ranking, retrieval, checked narration and citation inspection are now implemented. This contradicted the challenge's central summarize/rank/interpret workflow and the actual copilot.

The audit updates the copy and adds a direct Fire behavior entry using the existing navigation callback. It does not redesign the page, change the ranking, generate a model prediction, recurate data or claim that the automated checks establish experimental truth.

## Findings and corrections

| Item | Finding | Corrected presentation |
|---|---|---|
| Ranking status | Home said Planned and No relevance scores are computed yet; domain/ranking.py and SPEC-003 already implement scores, breakdown and answering. | Describe current archive-wide scenario ranking, deterministic scores, connected-model or offline-template narration, citations and possible insufficient-evidence output. |
| Archive scope | ISS combustion data was narrower than the actual set, which includes the Saffire/Cygnus investigations. | NASA PSI combustion data; no implication that every record was measured aboard the ISS. |
| Challenge purpose | The first paragraph mainly instructed interaction with the image. | Explain comparison, scenario relevance and source inspection, explicitly naming prevention, detection and suppression for crewed environments. Keep scene instructions as a separate caption. |
| Fire behavior | A central implemented scientific view lacked a direct Home action or a clear description of its three analyses. | Add Open Fire behavior, preserve the committed query, and name FLEX burning rate, BASS-II gas changes and SAFFIRE-II ground/flight comparison in the flame theme. |
| Data extraction | Filtered CSV export existed but was absent from the three-step workflow description. | Explain downloading matching records for the user's own analysis. This is not a claim that a predictive model or complete export bundle exists. |
| Source access | Evidence was removed from the header in ADR-0132. | Point users to Investigations and Citations & source downloads; keep raw values, units, transformations and review status visible. |
| Earth applications | Documented applications could be read as demonstrated or reviewed benefits. | Call them curated connections/claims, explain inferred and human-review status, and distinguish a research connection from a proven technology benefit. |
| Decision framing | From records to traceable decisions could imply validated safety decisions despite uncalibrated relevance weights. | From reported measurements to cited explanations; ranking does not certify habitat safety. |
| Gravity | Partial-gravity limitations were only prominent when the habitat theme was selected. | State the current archive's absence of direct lunar/Martian partial-gravity measurements in the common scope caption. |

## Claims retained after review

- Snapshot-based counters are correct: 15 curated investigations, 1,615 reported records and 0/15 human-reviewed manual metadata files at the inspected revision `a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204`. These are current results, not fixed UI constants. Dataset/schema validation and human scientific review are different activities.
- Reported records include individual tests, daily summaries and planned matrix records. The Home does not relabel them as independent experimental runs.
- The four thematic starting-point lists are navigation aids, not relevance rankings or complete scientific classifications. Only loaded investigations are linked. Ten investigations currently have nonempty curated Earth-application claims, all within draft manual metadata; no extra technology was invented.
- The illustration remains explicitly conceptual. Its displayed instrument numbers, blue flame and lunar scene are not experimental measurements.
- Habitat relevance is conditional on source conditions and assumptions; rockets/propellants remain outside scope. No predictive simulator, lunar-gravity measurements, certified safety threshold or calibrated risk score is advertised.
- The new copy does not promise a live NASA data connection, autonomous dashboard actions, a populated technology-solutions catalog or an answer for every question.

## Traceability and verification

SPEC-001 section 24 defines the updated Home contract (AC-88/89). `tests/interface/test_explorer_app.py` checks the current feature description, source/CSV scope, live metadata-review count and navigation to Fire behavior while retaining the applied query. Existing application tests cover valid loaded ids and the prohibition on fabricated Earth applications; existing interface tests cover theme selection and navigation.

Runtime checks and limitations are recorded in the corresponding ADR verification entry. The review does not establish usability improvements, validate a real provider response, recheck every PDF quote or certify scientific applicability. No visual redesign was performed.
