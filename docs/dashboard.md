# Streamlit explorer — first implementation

Run from the repository root:

```powershell
python -m pip install -e ".[dashboard]"
python -m streamlit run src/psi_fire/interface/app.py --server.address 127.0.0.1 --server.port 8501
```

Open http://127.0.0.1:8501. Requires Python 3.11+ and Streamlit 1.60+. This is a local research prototype with English UI text; no internet connection or LLM credentials are needed for exploration.

## Included

Dashboard overview (ADR-0107): four KPI cards with help text (investigations, reported records split into individual tests and daily/matrix summaries, tests reporting both O2 and pressure, and lunar-scenario tests). Directly below, a full-width O2 x pressure coverage map plots every individual test that reports both values, draws the demonstration scenario (at least 30% O2, at most 10.2 psi) as a box and separates chamber-atmosphere O2 from inverse-flame burner-stream O2. The comparison scatter follows it. The record-level donut, the records-per-investigation bars and the Open investigation card were removed from the Dashboard; the card remains on Investigations. Older paragraphs below that describe those cards or the envelope coverage chart are superseded.

Header navigation: prominent native Dashboard and Fire behavior buttons use blue and amber treatments, with individual help tooltips. Home and Investigations remain directly accessible, and the current view is labelled. Evidence was removed as a separate destination; its sources remain within Investigations → Citations & source downloads. Existing sessions on Evidence redirect to Investigations with the sources tab selected, preserving filters. Older screenshots/paragraphs showing a separate Evidence destination are historical. All actions keep the existing per-session navigation/query path. [Historical header tooltip preview](screenshots/navigation-fire-tooltip.png).

The Fire behavior view starts with From physical laws to traceable evidence, before Research filters. Three student-facing cards explain the d-squared model, signed gas-concentration differences and paired gravity outcomes, define symbols/units, and connect the analysis to fire-safety research. Optional detail explains the fitted coefficients, uncertainty and source trail. Physical consistency, statistical association and independent safety validation are explicitly distinguished. [Introduction preview](screenshots/fire-behavior-learning-desktop.png).

Fire behavior & safety evidence: a dedicated Workspace destination uses the committed research query for three source-bounded analyses. FLEX plots reported K versus oxygen by fuel/diluent, with separately stratified pressure/diameter-adjusted slopes and 95% model intervals where identifiable; BASS-II plots signed same-test gas-concentration differences; SAFFIRE-II compares raw ground/microgravity outcomes without converting Complete or Acceleratory into numbers. Source rows, exclusions, tested ranges and reproducible JSON/CSV exports are available. See [SPEC-002](specs/fire-behavior-evidence.md) and [methods, checkpoint results and verification](fire-behavior.md). These analyses do not establish habitat-safety thresholds or measured lunar gravity.

Filter/data integration audit: controls initialize from the applied query, including Home topic links and return navigation. Invalid submissions preserve previous results and explicitly show the committed scope. Standalone Reported oxygen basis is available; numeric oxygen ranges reject conflicting categorical basis selections. Include-unreported filters disclose retained missing-condition counts. See [the data-flow audit](data-flow-audit.md) for source reconciliation and test coverage.

Chart availability: selecting an investigation in Research filters does not guarantee that it reports both scalar quantities chosen for the profile axes. The profile card now states how many chart-selected investigations have dots and names those without them. Data availability lists each matching investigation, retained records, plotted records and primary reasons: missing quantities, non-scalar intervals, incompatible O2 basis, summary granularity or chart-local deselection. Its Open retained records action preserves the research query. Available scalar fields can guide a deliberate axis change; missing values are never imputed. Coverage omissions and the record-level metric caption are also explicit.

English Home: the first destination uses the now-supplied FLAMSA JPEG in an image-backed introduction and an uncropped interactive research scene. Four numbered, keyboard-operable image points synchronize with the native topic selector and contextual investigation panel. Native actions open related loaded investigations or the existing dashboard. Snapshot-based counters replace fictitious ranking scores; Earth-application links require curated claims. The image is labelled conceptual artwork, including its embedded instrument readings. Research copilot now provides deterministic scenario ranking, a criterion breakdown and checked explanations through a connected model or offline template; Home describes that implemented workflow. Fire behavior has its own Home action. See the [Home content audit](home-content-audit.md). Home/Dashboard navigation and topic changes preserve the applied query; Open related research explicitly selects its displayed ids. The original light workspace palette remains in place, with blue actions and a dark image surface within Home. See [homepage design and verification](homepage-design.md), [desktop preview](screenshots/homepage-supplied-desktop.png) and [mobile scene](screenshots/homepage-supplied-mobile-scene.png).

FLAMSA glass theme: light blue/slate atmospheric gradients, a CSS horizon arc in the hero, translucent cards with backdrop blur and fallback solid surfaces. Existing analytic series colors remain unchanged; the new reference's neon-green palette and photographic background were not imported. A local SVG interpretation of the reference flame/FLAMSA wordmark is included under interface/assets and packaged with the dashboard. It is not an original brand-file extraction. No remote image/font dependency is added. [Desktop glass-theme preview](screenshots/flamsa-glass.png).

Reference-led layout update: the supplied screenshot now guides the white/teal card layout, top Dashboard/Investigations/Evidence navigation, horizontal multi-select filter panel and four-metric summary. The Dashboard shows comparative profiles (Lines/Scatter switch), record-volume bars, a record-level composition donut and reported-interval coverage with visible endpoints even for singleton ranges. All values come from the current filtered dataset, never the illustrative reference numbers.

[Desktop layout preview](screenshots/research-overview.png). The reference was implemented from the supplied image without requiring a Figma file or Dev Mode. Native widgets/graphs remain in Streamlit; static presentation CSS is isolated in interface/workspace_style.py. After a running server has loaded older view modules or theme settings, restart the local Streamlit process to obtain a consistent layout revision.

Research copilot is hidden by default. Its toggle opens an optional right-hand panel while preserving filters and axis choices; closing it returns the full chart width. Chart settings are collapsed initially to keep the overview readable. Investigation records and citations are reached through the top navigation or the investigation preview card. Download filtered records (CSV) exports every record that passes the filters, with all curated columns, raw source values and provenance; the file name carries the dataset revision.

The analytics amendment adds scatter plots and descriptive comparative median lines, with investigation/axis/series multi-selection and source-record tooltips. Unsupported interval/missing pairs and non-test summaries are excluded explicitly. Lines are not time histories or causal/flammability models; other experimental conditions may vary. Bars retain their original coverage semantics.

Investigation details now use descriptive tabs. A side panel reserves space for a research copilot, clearly labelled Not connected with disabled controls and actual dashboard context. No model is called and no assistant action executor is implemented. See SPEC-001 section 14 for the future validated-action contract.

- A catalog of validated curated investigations; totals are computed dynamically and distinguish individual test records, test-day summaries and matrices.
- Native charts of matching record volume and reported/missing conditions. Oxygen coverage is split by measurement basis; count is not relevance or scientific confidence.
- Applied form filters for identity/text, record level, fuel/phase, flow, numerical oxygen/pressure/speed intervals, lineage/notes, review state and existing hardware/sensor/pillar/gravity values. Numeric predicates match the same record, with inclusive overlap and explicit missingness rules.
- Investigation overview, draft/review status, source-backed manual claims, exact copyable quotes, source notes and full-investigation variable classifications.
- A TestPoint table, optional extra columns, complete record/raw/provenance inspector and column definitions.
- Registered source preparation/download, approved-root resolution, checksum checks where pinned and explicit unavailable/version-unpinned states. Cited documents and shared archived sources are accessible without running their contents or fetching online pages.
- Native light theme: restrained blue/teal palette, no remote fonts, no custom CSS/HTML widgets, clear labels and keyboard-accessible selector navigation.

## Architecture

`domain/exploration.py` implements interval/basis matching. `application/explore.py` provides immutable requests, read use cases and coverage calculations without pandas/Streamlit. `application/evidence.py` defines the source-delivery port. `infrastructure/explorer.py` composes the existing CuratedRepository with discovery/identity/granularity/header checks, revision fingerprinting and approved source access. `interface/app.py` is the composition root; `explorer_views.py` renders native Streamlit components.

Cached scientific data is JSON rather than pickled generic Pydantic classes. Each rerun reconstructs validated objects from the serializable cache, preventing session-specific presentation changes from mutating a shared aggregate. Filters are per session; form drafts do not affect results before Apply. No scientific files are edited by the app.

## Dataset updates

Start/load the explorer after curation completes. For updates, finish curation, confirm it is idle in Dataset controls, then Reload dataset. The app checks hashes before/after loading, but this is not atomic producer publication. Successful refresh preserves valid applied filters and announces any unavailable categorical values removed during reconciliation. Failed refresh retains the previous snapshot and query with a stale-data warning. Do not use concurrent live curation as if JSON/CSV pairs were transactional.

The dashboard reads data/curated/*/test_points.csv plus investigation.json. Edits to Excel/raw sources or data/manual are not consumed directly: run the existing curation process first, then reload. Dataset controls shows the loaded revision and totals. A byte-level freshness check on each rerun warns when curated input pairs or the registry differ from the loaded revision; it never regenerates scientific files or silently replaces the browsing snapshot. There is no background watcher for files changed while the page is idle.

Consumer preflight rejects CSV-only/JSON-only directories, directory/manual-parent identity mismatches, invalid core headers, inconsistent granularity and nonfinite quantities. The underlying generic repository/domain still require their own invariant fixes; this adapter does not rewrite those components.

## Specification progress and remaining work

Implementation starts SPEC-001; it does not claim all 50 acceptance scenarios complete. Domain/application tests cover range validation, same-record conjunction, O2 basis/missingness, inclusive boundaries, unknown selections and review filtering. Integration checks cover real-data compatibility, incomplete pairs, manual-parent identities, registered downloads and altered checksums. AppTest covers default rendering, Test points/Evidence navigation, empty search and Reset. See tests/application/test_explorer.py, tests/infrastructure/test_explorer_snapshot.py and tests/interface/test_explorer_app.py.

Remaining stage-1 refinements: full documentary capture history display, broader session/accessibility/performance verification, family column presets and exact typed read projections/error variants from the design. Application selection sentinels currently use documented display labels rather than separate selection objects. Do not silently consider these proposed interfaces fully implemented.

Ranking/XAI, RAG, LLM narration, side-by-side comparison and the complete clean-dataset export bundle remain future increments. Source downloads are evidence access, not the clean-dataset export use case. No fire-safety certification or predictive conclusions are produced.
