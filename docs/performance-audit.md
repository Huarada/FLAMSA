# Workspace processing and navigation audit

Date: 2026-11-14. Trigger: Home-to-Dashboard navigation appeared temporarily broken while the next view was being processed. Scope: startup imports, snapshot lifecycle, filters/export, chart construction and interaction data, source access, Fire behavior and copilot initialization.

## Confirmed bottlenecks and changes

| Area | Finding | Change |
|---|---|---|
| Axis option counts | `partners` constructed full plot rows for every candidate vertical axis just to count them. The profiled default Dashboard made about 80,750 exclusion checks and 569,052 TestPoint value lookups per rerun; this dominated chart preparation. | Preselect eligible horizontal observations once, then count valid vertical scalars/bases without allocating plot rows. Counts are checked against actual plot eligibility. |
| Repeated projections | Variables, pair counts, plot rows and availability reports were recomputed even for identical controls. | Bounded Streamlit data caches, keyed by revision, exact retained row identities, axes, selected chart studies and oxygen basis. Return values are copied, not shared mutable aggregates. |
| CSV | The entire filtered export was rebuilt on every widget interaction. A standalone local sample took about 0.55 s. | Eight-entry cache keyed by revision and retained records. Downloads retain the same data contract. |
| Snapshot | Globally cached JSON was parsed back into every Pydantic aggregate on each rerun. | Reuse the current session's validated snapshot when its revision matches. Global cache remains serialized; freshness and transactional reload checks remain unchanged. |
| Home transition | Home's global `:has(.st-key-home_workspace)` styling and backdrop were removed only as ordinary stale content was cleaned up during a rerun. They could affect the new analysis view while it was streaming. | A stable style/decorations placeholder is explicitly cleared at the beginning of a non-Home rerun. The conceptual scene and Home appearance remain intact. |
| Scenario selection | The default coverage plot built 11,775 invisible synthetic marks for nearest-grid clicks, in addition to 693 real observations. It built these marks even with copilot picking disabled. | Bounded, cached interaction mesh: 3,002 marks at the inspected default geometry, capped at 4,000. Build only when enabled. Clicks are explicitly labelled as snapped; typed input precision and scientific observations are unchanged. |
| Startup dependencies | Home imported the orchestration and statistical engines before showing content. | Load Fire behavior dependencies when its view is used. Remove runtime infrastructure imports used only for interface annotations. |
| Copilot preparation | Merely opening Dashboard constructed the model/orchestration resource, delaying navigation before a question existed. | A typed deferred pipeline delegates to the real cached factory only on an explicit question, or when displaying a saved answer needing its actual narrator label. The form is immediately available; answering/validation/citation logic is unchanged. |

## Measurements and reproduction

The first cProfile run showed Home initialization at 7.568 s and Dashboard first/warm/return reruns at 3.490/3.757/3.784 s. Chart preparation alone took 2.902–3.313 s; axis-partner collection dominated it. These are instrumented AppTest wall times, not browser paint times or service guarantees.

An intermediate run after count/caching/snapshot changes, before the later lazy-initialization and interaction-mesh work, measured Dashboard first/warm/return at 2.347/1.656/1.389 s. A later import-deferral probe brought initial Home to 0.889 s; the first Dashboard still paid engine startup, motivating explicit-question deferral. Instrumentation, machine load and cold imports affect these values; do not combine them into a universal percentage improvement.

`python scripts/benchmark_workspace.py --runs 3` records unprofiled AppTest wall times for Home, Dashboard cold/warm/return, Fire behavior and Investigations. It never asks the copilot and blanks the model setting in its own process. It does not print credentials or modify `.env`.

Chrome was exercised against an isolated local server with the model disabled. The early style change occurred about 0.1–0.2 s after navigation, before the analysis completed; no rendered exception or 1440 px horizontal overflow was observed. Cold browser runs were substantially slower than warm reruns, so eliminating all first-load delay is not claimed. The screenshot is [the optimized Dashboard](screenshots/navigation-dashboard-optimized.png). Final benchmark/test results are recorded in the ADR verification entry.

Final unprofiled AppTest sample after explicit-question deferral:

| Action | Seconds |
|---|---:|
| Initial Home | 2.0315 |
| First Dashboard | 0.3930 |
| Dashboard reruns | 0.2120 / 0.2169 / 0.2266 |
| Return to Home | 0.0301 |
| Return to Dashboard | 0.2153 |
| First Fire behavior | 1.1222 |
| Fire behavior rerun | 0.3140 |
| First Investigations | 0.0635 |
| Investigations rerun | 0.0675 |

The final isolated Chrome run completed the navigation at 691 ms, removed Home's dark style by the first recorded sample at 91 ms, and recorded a first canvas at 740 ms. Both Vega chart containers were present, with no exception or horizontal overflow at 1440 px. The longest sampled browser timer gap was 333 ms; a zero-jank guarantee is not claimed. These measurements exclude a real model request and are local observations rather than a production SLA.

The existing port-8501 process initially mixed the updated composition root with an old imported `chart_grid` function, causing a signature error. After verifying the listener's command and restarting that specific Streamlit process, the real port-8501 view passed Chrome checks: script completion at 1,516 ms, Home styling cleared at 132 ms, two chart containers, zero exceptions and no horizontal overflow. Its longest sampled timer gap was 67 ms. The health endpoint returned HTTP 200. The screenshot above was replaced with this verified running-instance capture; the failed-probe image was not retained as the final artifact. The isolated test server was stopped.

Full verification: 254 tests passed and 179 PDF visual-line checks skipped because pdftotext/Poppler is unavailable. Ruff and mypy passed for the domain and the new cache/deferred modules plus the chart projection. No real model request was made.

## Correctness and architectural boundaries

- Count equivalence covers ambient/burner oxygen bases, oxygen/pressure/time/CO2 axes, summaries, missing values and source intervals. No missing value is filled and no source observation is dropped for performance.
- Cache keys include data revision and exact retained identities; a changed filter, chart scope, axis or oxygen basis cannot reuse another result. Cached row mutation does not affect later readers.
- Session snapshot reuse does not replace full-byte freshness checks with timestamps, and reload failure still retains the previous query/data with a stale warning.
- Application computations remain free of Streamlit/pandas. Cache, styling, lazy UI-resource composition and CSV formatting remain in the interface; real infrastructure is wired by the composition root.
- The deferred handle preserves the real answer, narrator label and error behavior. Relevance scores, OLS coefficients, intervals, citation validation/retry and registered source checksum checks are not weakened.
- The interaction mesh is display-only data. Reducing it changes click snapping, not measured test conditions, plotted counts, mathematical calculations or manually entered scenario precision.

## Remaining costs and limits

The initial import of Streamlit/Altair/pandas and the browser's chart renderer still has a cold-start cost. Fire behavior imports SciPy on first use. The first explicit copilot question may initialize provider libraries, build the graph, load/vectorize passages or rebuild a missing/stale PDF index; actual model/network latency was not measured and no paid API call was made.

The Home still uses decorative animation and externally loaded fonts with fallbacks. Self-hosting fonts and testing low-power/mobile devices are follow-ups if real-device measurements show a problem. No visual redesign or removal of the requested artwork/motion was made.

Source inspection still hashes/reads registered files when needed for integrity; this can cost time for large PDFs. No unsafe file-content cache or skipped checksum check was introduced. Hidden study/Fire behavior tabs still render their content under current Streamlit semantics; further lazy tab/fragments work should be driven by measurements and preserve shared marker/query state. The page's controls intentionally share reruns where changing the scenario also updates the plot.

Caches are bounded process-memory optimizations, not persistent scientific artifacts. Restart the app after changing analysis policy/implementation; scientific data edits still require the existing curate/reload workflow. No cross-browser, physical-device, production-load or real-provider latency guarantee is claimed.
