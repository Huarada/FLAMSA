# Fire behavior & safety evidence

Open the amber **Fire behavior** button in the local Streamlit header. Dashboard is the blue archive-exploration button; each has a hover description. The evidence section has FLEX, BASS-II and SAFFIRE-II tabs. Research filters apply to all three; local FLEX fuel, pressure-tolerance and initial-diameter controls refine only FLEX. Opening source records preserves the committed research query.

Contract: [SPEC-002](specs/fire-behavior-evidence.md). This is an experimental-evidence view, not a fire-risk score, habitat certification or direct lunar-gravity validation.

## Opening scientific guide

Before the filters, From physical laws to traceable evidence explains why fuel consumption, atmospheric changes and paired gravity outcomes matter. It defines the approximate d-squared relationship, oxygen/CO2 differences in percentage points and the comparison of ground/flight burned lengths. A model disclosure relates those concepts to the existing conditional regression, defines its symbols and explains source tracing and uncertainty. Numerical calculations and coefficients are unchanged by the guide.

Background references were checked against [NASA's combustion/fire-safety overview](https://www.nasa.gov/missions/station/iss-research/studying-combustion-and-fire-safety/) and [NASA's FLEX requirements document](https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf), including its discussion of diameter-based burning-rate measurement and the approximate diameter-squared/lifetime relationship. These are background links rather than newly curated as-run claims. The student text identifies physical agreement as a consistency check, statistical estimates as conditional associations, and habitat validation as requiring independent environmental evidence.

The navigation/guide increment passed all 11 interface tests and the full suite of 175 tests; 179 PDF visual-line checks remain skipped for missing Poppler. Ruff and strict mypy on the domain/new UI modules passed. Chrome verified both requested hover tooltips, Enter navigation to Fire behavior, four rendered equations, introduction ordering before filters and 390 px layouts without horizontal page overflow. Physical-device, screen-reader and complete cross-browser accessibility checks were not performed.

- [Header tooltip](screenshots/navigation-fire-tooltip.png)
- [Opening guide on desktop](screenshots/fire-behavior-learning-desktop.png)
- [Header at 390 px](screenshots/navigation-mobile.png)
- [Opening guide at 390 px](screenshots/fire-behavior-learning-mobile.png)

## FLEX

The response is the reported droplet burning-rate constant K in mm²/s. Every panel contains one fuel; color identifies diluent. Fits separate exact He/CO2 fractions as well as fuel/diluent. The default pressure window is 1 atm ±5% (13.961105–15.430695 psi). Pressure and initial diameter are linear adjustment covariates when they vary, not silently assumed constants.

The application solves centered/scaled ordinary least squares with an intercept and reports the oxygen coefficient in mm²/s per oxygen percentage point. Groups require six observations, three distinct oxygen levels, three residual degrees of freedom, full rank and standardized condition number <=10,000. Underidentified groups retain points and an explanation rather than a fabricated slope. Raw Spearman rho and adjusted slope are distinct quantities.

Lines hold pressure/diameter at group means and span only observed oxygen bounds. Shading is a 95% model-based interval for the mean response, not an individual-test prediction interval. The slope also has a 95% Student-t interval. Independent, homoskedastic, approximately normal residuals are model assumptions; calibration error, unreported conditions and model-form uncertainty are not resolved. Reference means are model conditions rather than a claim that each oxygen/reference-condition combination was directly tested. No projection to other fuels/blends, lower pressure or partial gravity is implemented.

## Inspected checkpoint

Revision: `a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204`. Default UI settings explicitly select heptane and methanol, ±5% pressure and all reported diameters. Analysis id: `571d906a625be137609dcdf5f1c38418e714cf29f3f342cdaf3741cec1a3c74e`. Numerical libraries: NumPy 2.5.2 and SciPy 1.18.1. These are observations of this checkpoint, never hardcoded dashboard totals.

| Fuel / blend | n fitted | Adjusted oxygen slope (mm²/s per O2 point) | 95% model interval | Tested O2 | Tested pressure (psi) | Initial diameter (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| heptane / N2, He=0%, CO2=0% | 32 | 0.01847212 | 0.00619679–0.03074746 | 13–30% | 14.6282892–14.91640752 | 1.10–4.67 |
| methanol / N2, He=0%, CO2=0% | 41 | 0.01832300 | 0.01570562–0.02094038 | 12–30% | 14.64955968–14.96861688 | 1.61–3.97 |

FLEX retains 151 eligible scalar observations from 274 matched records; 123 have an explicit exclusion reason. Only the two N2 strata meet all fitting rules at this checkpoint. Scatter observations from other diluents remain visible; their blend strata have insufficient oxygen variation or observations for these estimates. The global-filtered raw Spearman rho values in the two fitted strata are about 0.488 and 0.818; they are not copied from earlier full-table correlations.

The exact O2 >=30% AND pressure <=10.2 psi count is zero. Seventeen tests instead fall within the separately labelled <=10.5 psi comparison, at about 10.33–10.50 psi. Bounds are evaluated before display rounding. Those lower-pressure records never enter the near-1-atm fit, and the fit is not extrapolated to them. Both coverage counts use research filters rather than local fit controls.

## BASS-II

For each complete ambient-oxygen test, compute initial O2 minus final O2 and final CO2 minus initial CO2 in percentage points. The inspected checkpoint has 121 complete pairs from 129 matched records. Seven pairs have a negative measured difference and remain visible with a quality marker. An epsilon of 1e-10 only prevents binary floating-point roundoff from creating a sign flag; the exported differences themselves are unchanged.

No regression, concentration clipping, missing-value fill, CO2 mass/volume conversion, emission-yield estimate or detector-performance threshold is introduced. Initial/final readings and their row identities are available alongside the derived differences. The current curated missing values take precedence over the older data-quality review's unresolved-fix inventory.

## SAFFIRE-II

The outcome matrix and paired table retain all nine matching samples at the checkpoint. Numeric and raw burned lengths/spread rates remain distinct. Complete is categorical, Acceleratory is not a constant rate, and approximately zero is shown as approximately zero. Mixed-material text, source notes, uncertain thickness and missing material labels stay visible. Ground sample length is not assumed equal to flight sample length to convert Complete into millimeters.

The silicone samples have different reported 1 g outcomes: two Complete labels, a finite 7.6 cm length and an approximately-zero length. Their reported microgravity lengths are approximately zero. This evidence supports inspecting screening differences per sample, without declaring every silicone sample identical or fitting a universal ground-to-orbit law.

## Reproducibility and boundaries

Download analysis JSON includes dataset revision, immutable local settings, actual applied research filters, numerical-library versions, policy version, deterministic analysis id, observations, exclusion reasons, group record ids, reference conditions, coefficients/intervals and source-column/checksum metadata. Per-study CSV exports carry analyzed measurements plus record/source identity; SAFFIRE-II includes both canonical numeric fields and original source labels. The analysis id identifies data/settings/policy/environment; selecting the same scope through a different query can share the scientific analysis while the exported applied filters still describe that query.

Calculations live in application/behavior_statistics.py and application/fire_behavior.py, with no pandas/Streamlit/I/O/LLM dependency in these modules. NumPy/SciPy are explicit dependencies. The domain and ingestion pipeline were not modified. Interface code only selects settings, renders projections and exports them. Ordinary dashboard profiles remain reported-point scatters; conditional fitted lines are confined to this requested evidence section.

Methods: [NIST least squares](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm), [SciPy Student-t interval example](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html). Multivariable residual degrees of freedom are n minus the fitted parameter count; the bivariate example's n−2 is not used for a model with additional varying covariates.

## Verification

The full suite passed 174 tests; 179 PDF visual-line checks were skipped because pdftotext/poppler is absent. Fourteen focused analysis/integration/UI tests passed after final projection changes. Ruff and strict mypy on the domain and the two new application modules passed.

Tests cover an orthogonal factorial example with analytically known slope/interval, diameter confounding, insufficient/collinear groups, near-identical but distinct blends, strict pressure thresholds, signed gas changes, raw gravity outcomes, canonical-unit guards, source-cell reconciliation, deterministic identity, empty research scopes, copilot state and source navigation.

Headless Chrome checked all three tabs and source navigation. The initial Vega-Lite facet view overflowed narrow screens; separate native charts now fill their containers. At a 390 px emulated viewport, the revised FLEX card fits within the viewport. Browser-specific accessibility, physical-device behavior and the statistical error assumptions are not established by these checks.

- [FLEX preview](screenshots/fire-behavior-flex.png)
- [BASS-II preview](screenshots/fire-behavior-bass.png)
- [SAFFIRE-II preview](screenshots/fire-behavior-saffire.png)
- [Narrow FLEX view](screenshots/fire-behavior-mobile.png)
