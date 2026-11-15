# Navigation scope review against the challenge

Date: 2026-11-14. Status: the user approved the smaller step, removal of the Evidence header destination, now implemented. The broader proposal to move Investigations to secondary navigation remains a recommendation.

## Inputs and current implementation

Reviewed the complete challenge text supplied by the user, CLAUDE.md, the explorer and Fire behavior specifications, SPEC-003, the ADR history, the current application composition and the study/source/copilot views. The challenge asks for a web dashboard that summarizes, ranks and interprets combustion investigations, with possible data extraction and technology-discovery support. It does not prescribe page names or separate Investigations/Evidence destinations. Objectives, fuels, conditions, variables, sensors and hardware are suggested useful attributes rather than a requirement for a particular navigation structure.

The current workspace has Home, Dashboard, Fire behavior, Investigations and Evidence. Both study destinations call the same `detail` component; Evidence passes `Citations & source downloads` as its default tab. Evidence is currently a study-scoped source browser, not a distinct global evidence-search workflow. Investigations additionally exposes a catalog. Its detail includes scientific context, manual claims/review state, raw record inspection, column definitions and source downloads.

The copilot now ranks studies and returns claims, citations, a deterministic breakdown and limitations. It does not make study inspection redundant. Its current DOI link targets the investigation record rather than the exact archived PDF page, and its ranking covers all curated studies rather than only the Dashboard query. A citation must therefore still lead to an accessible study/record/source inspection path, including studies outside the current chart scope.

## Recommendation

| Capability | Product importance | Need for a primary destination | Recommended placement |
|---|---|---|---|
| Browse and inspect all investigations | High: supports study summaries, experimental context and data inspection across all 15 studies. | Moderate; useful independently of a particular chart, but does not need equal visual weight. | Keep a discoverable secondary Studies entry and contextual Open study actions. Reuse the existing detail view. |
| Read evidence and download sources | High: essential to audit claims, measurements and their limitations. | Low at present: the existing Evidence destination duplicates the study detail. | Integrate Sources within study detail, plus View source actions beside charts and copilot citations. |
| Explore filtered measurements | High: primary Dashboard task. | High. | Dashboard. |
| Interpret study-specific physical behavior | High: a clear scientific demonstration, bounded to FLEX/BASS-II/SAFFIRE-II. | High for the current competition narrative. | Fire behavior. |
| Ask/rank a habitat scenario | High: directly addresses the core challenge. | A separate page is not required. | Research copilot attached to the analysis workspace, with explicit ranking scope. |

Suggested main navigation: Home, Dashboard and Fire behavior, with Browse studies as a secondary action. For a smaller initial change, remove only Evidence from the header and keep Investigations until the contextual inspection paths are complete. Either option retains the underlying study/source capabilities and data.

This is progressive disclosure: show the main analysis tasks first and reveal technical detail when requested. [Nielsen Norman Group's guidance](https://www.nngroup.com/articles/progressive-disclosure/) supports this general approach; the exact recommendation here is a judgment based on the project, not a usability-test result.

## Challenge-to-flow coverage

- Summarize: Dashboard coverage and study objective/context.
- Rank: scenario copilot and deterministic breakdown.
- Interpret: Fire behavior and cited copilot responses.
- Extract: filtered CSV and record inspection; preserve original values, units and provenance.
- Compare studies: shared research filtering, comparison charts and a catalog/study inspector; do not reduce the discoverable corpus to the three Fire behavior studies.
- Check scientific support: claim/record locators and archived source access in context.

Removing the source browser's header button does not remove RAG or weaken validation by itself. Deleting source adapters, archived evidence, citation provenance or the record inspector would remove useful capabilities. A smaller menu and a smaller scientific corpus are separate decisions.

## Conditions before implementation

1. A user can open any of the 15 studies independently of whether it has a plottable pair. This matters because the current O2/pressure map has dots for only three studies.
2. Each Fire behavior source-record action continues to open the intended investigation and preserve the applied query.
3. Copilot citations open the cited record/metadata/source with its locator. A DOI-only link is not sufficient for the exact PDF evidence task.
4. A ranked study outside the current research-filter result can be inspected without silently broadening those filters; the temporary out-of-scope detail must be labelled and provide a return path.
5. Study, measurement, raw value, unit, curation note, draft/review status and source download remain discoverable. Preserve browser/session return behavior and document-download safeguards.
6. Update specs, navigation help, callbacks, UI tests and screenshots before removing destinations. Existing contextual buttons currently target Investigations.

The initial review changed no navigation. The subsequent approved increment removes only Evidence from the header and redirects old sessions to Investigations source inspection. No study, source or archived file was removed. Actual task-completion time and discoverability need user testing before claiming the proposed arrangement performs better.
