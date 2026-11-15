# Formula audit: README, Dashboard and Fire behavior

Date: 2026-11-14. Scope: mathematical meaning, dimensions, current curated values, implemented computations and presentation. Read with [SPEC-002](specs/fire-behavior-evidence.md) and [methods](fire-behavior.md).

## Finding and recommended scope

Keep the three opening cards: the approximate droplet d-squared model, signed same-test gas differences and paired ground/flight outcomes. Keep the conditional FLEX regression and its uncertainty in the methods disclosure. The ground/flight arrow denotes a comparison, not an equation or physical law.

Retain R1–R8 in the README with their distinct roles and assumptions made explicit. Their presence in the README does not imply that the application computes or verifies all of them. The general Dashboard explores coverage and available measurement pairs; Fire behavior applies narrower, study-specific analysis rules to the same filtered repository snapshot. A generic scatter plot does not establish the controlled association estimated by the FLEX model.

Do not add all README equations to the opening cards. Two useful future additions to an optional technical disclosure are the derived burn-time relation and the average length/time relation. Both have existing automated consistency checks; neither needs a new performance plot or safety score. A new live residual analysis would need a spec, source eligibility rules and application-layer computations before being presented as implemented.

## Formula-to-implementation map

| Relation | Scientific assessment and conditions | Current role | Recommendation |
|---|---|---|---|
| R1: `d² = d0² − Kt`; `tb ≈ (d0² − de²)/K` | Approximate quasi-steady droplet model. Squared diameter, rather than diameter, decreases linearly when K is constant. Heating, radiation, transients and extinction limit its applicability. mm² divided by mm²/s gives seconds. | d² displayed in the opening guide; burn-time ratio checked in infrastructure tests. Reported K is consumed by Fire behavior, not reconstructed from this equation. | Keep d² visible. Burn-time rearrangement is suitable for optional technical detail, with reported extinction diameter required. |
| R2: Spalding K expression and positive oxygen derivative | Idealized transport model; the derivative holds other properties fixed. Oxygen mass fraction is not oxygen percentage. SI inputs give K in m²/s. Required conductivity, heat capacity, temperatures, latent heat and density are not mapped per test. | Theoretical background only; no Spalding calculator in either view. | Retain with assumptions in the README; do not promote it to a calculated prediction or universal trend. |
| R2: conditional OLS K model and Student-t slope interval | Matches the application: exact fuel/blend strata, near-atmospheric pressure band, varying pressure/diameter covariates, full rank, sample/variation/conditioning checks. Classical error assumptions underlie the interval. | Deterministic application computation, Fire behavior chart/details/export; regression equation in the guide disclosure. | Keep. Define n as observations and p as fitted parameters including intercept. A confidence interval is not a safety bound or individual-test prediction interval. |
| R3: `de ≈ a + b d0` | Conditional radiative-extinction relationship. Linear need not mean proportional through the origin. Different regimes and fuels cannot be pooled into one asserted law. | Documentary context, not an enforced automated law or current Fire behavior fit. | Retain the qualified form in the README; defer a chart until extinction regimes and data eligibility are specified. |
| R4: `Zst = (1 + s YF/YO2)⁻¹` and mole-to-mass conversion | Consistent with a fuel/N2 stream and oxidizer/N2 stream and the stated complete-combustion oxygen demand. X must be a fraction, not a percentage. Distinguish burner and ambient oxygen for normal/inverse flames. | ACME-CFI-G automated curation consistency check; outside the three current Fire behavior studies. | Retain in technical documentation. Add to a future CFI-G module only with stream labels and composition context. |
| R5: sequential chamber oxygen relations | The before/after inequality is an observed dataset property. Oxygen consumption alone does not guarantee decreasing mole fraction in every closed reacting mixture. Continuity between tests requires the same atmosphere without interventions. | ACME-CFI-G before/after automated check; sequence continuity is an exploratory checkpoint. | Retain as a qualified observation; differing pairs are consistent with atmosphere resets but do not independently identify their cause. |
| R6: `ΔO2 = O2,i − O2,f`; `ΔCO2 = CO2,f − CO2,i` | Signed concentration differences, in percentage points. All four readings must belong to the same test. Negative differences remain visible. | Deterministic application computation and BASS-II chart. | Keep visible. Describe changes in measured atmosphere, not measured CO2 mass, exposure or detection performance. |
| R6: PMMA reaction and `ΔnCO2 / ΔnO2 = 5/6` | Balanced complete-combustion reaction. Ratio concerns molar amounts. Comparing mole-fraction changes needs a common wet/dry basis, gas inventory assumptions and consideration of water, incomplete combustion and sensor error. | README theoretical context; exploratory origin-constrained coefficient 0.822 from 24 pairs. No production fitted line or automated stoichiometric acceptance test. | Retain as contextual chemistry. Do not add a 5/6 line or a “validated combustion law” label to the present chart. |
| R6: approximate oxygen mass from concentration drop and PV/RT | Must divide a percentage-point drop by 100 and use consistent units. Requires explicit P, V, T and approximately constant total gas inventory. | Illustrative README estimate only; no mapped per-test gas-inventory model. | Keep only with numerical assumptions. Defer a live mass/yield calculation until per-test inputs and uncertainty are specified. |
| R7: average `v = L/t` | cm/s requires reported length in mm divided by 10 before dividing by seconds. An average speed does not resolve accelerating flame motion. | Two complete numeric SAFFIRE-II rows checked in tests; UI preserves reported numeric and categorical outcomes. | Keep in README; suitable for optional technical detail. Never derive a rate from Complete, Acceleratory, missing or approximate-zero labels. |
| R8: `mass flow = volume flow × density`; `density = P W/(RT)` | Dimensionally correct for compatible units and the same volumetric reference conditions. sccm needs its reference state; agreement at 300 K does not establish instrument temperature or calibration. | SPICE gas-density consistency test; outside the three Fire behavior studies. | Retain in technical documentation. A future SPICE module must state flow reference conditions rather than silently select them. |

## Independently recomputed checkpoints

Curated revision: `a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204`. These are dataset checkpoints, not universal constants or immutable future counts.

| Check | Current result | Interpretation |
|---|---|---|
| FLEX d² burn-time ratio, finite reported inputs, K > 0, tb > 0, de ≥ 0, d0 > 1.1 de | n = 155; median 1.049190953; Q1 = 1.029186418; Q3 = 1.077274089 (linear-interpolated quartiles) | Approximate agreement. The 10% diameter-change screen is a numerical sensitivity policy. Missing extinction diameter is excluded. |
| ACME-CFI-G recomputed Zst | 331 rows; maximum absolute error 0.00004080997963 | Consistent composition mapping and unit conversion within the automated tolerance of 0.001. |
| ACME-CFI-G normal flame sequence | 179 rows; 168 same-day consecutive pairs, 156 continuous to 1e-6 percentage points | The remaining 12 differences do not by themselves prove a particular refill event. |
| BASS-II exploratory PMMA origin-constrained slope | 24 complete pairs; oxygen decrease > 0.2 percentage points with 1e-10 roundoff allowance; sum(xy)/sum(x²) = 0.8220215701 | Descriptive concentration fit without reported uncertainty; no production regression. |
| Illustrative O2 mass for a ten-point decrease | 32.7 g at 101325 Pa, 250 L and 298.15 K | Approximately 17 g PMMA equivalent under complete combustion and fixed gas-inventory assumptions; not measured mass for an individual burn. |

The default Fire behavior near-atmospheric fit remains n = 32 for heptane/N2 (slope 0.0184721, 95% interval 0.0061968–0.0307475) and n = 41 for methanol/N2 (0.0183230, 0.0157056–0.0209404), in mm²/s per oxygen percentage point. Eligibility and local settings must accompany these numbers. The fit adjusts varying pressure and initial diameter; it does not establish that every other physical condition was controlled.

For the exact lunar atmosphere scenario, FLEX still has zero tests satisfying O2 ≥ 30% and pressure ≤ 10.2 psi on the same test. Seventeen satisfy the distinct ≤ 10.5 psi comparison. No partial-gravity interpolation or extrapolated near-atmospheric slope is established by those counts.

## Corrections made in this audit

- Removed the physical-consistency test's substitution of missing extinction diameter with zero. Replaced the stale 257-observation README checkpoint with the complete-reported-input checkpoint above.
- Visually checked page 2 of README reference [1]. Its prose says diameter decreases linearly, while its displayed model and normalized axes use squared diameter. Preserved the literal quotation and explicitly identified the discrepancy rather than treating the prose as the governing law.
- Separated the Spalding theoretical model, conditional empirical regression and causal interpretation. Corrected the claim that every near-atmospheric group receives a fit.
- Replaced strict extinction-diameter proportionality with a qualified linear form and removed unsupported pooled causal assertions.
- Clarified molar amounts versus concentration changes, the exploratory status of 0.822, the absence of a fitted BASS-II line, percentage-point conversion and the assumptions behind the illustrative mass estimate.
- Corrected the generalization that all silicone samples burned completely in 1 g. Samples 2-1/2-4 report Complete, 2-2 reports 7.6 cm, and 2-3 approximately zero; flight outcomes remain source-qualified.
- Added density units and flow-reference caveats. Clarified that pytest checks do not run automatically on every dashboard load or curation.
- Preserved raw/curated/manual data and production scientific calculations. An approximate-model residual is not a sufficient reason to erase an otherwise valid source measurement.

## Sources, verification and limits

The implementation map was checked against `application/fire_behavior.py`, `application/behavior_statistics.py`, `interface/behavior_introduction.py`, the Fire behavior view, SPEC-002 and `tests/infrastructure/test_physical_consistency.py`. Numerical checkpoints were independently recalculated from the current repository aggregates.

Verification: Ruff passed; mypy passed for all six domain files; the full pytest suite reported 175 passed and 179 skipped. The skipped checks require pdftotext/Poppler for PDF visual-line verification. Local README/audit Markdown links resolve; all 14 README display-math blocks and 33 pairs of inline-math delimiters were checked mechanically. These mechanical checks do not establish visual rendering correctness.

Primary theoretical background: [Princeton droplet-combustion research group](https://www.princeton.edu/~fldryer/nasa.dir/backgrnd.htm) states the classical d² assumptions and discusses departures from them. Statistical background: [NIST least squares](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm) distinguishes fitted coefficients, residual variance and observations/parameter counts. Study reports are listed in the README and source registry; these external background pages do not replace per-test provenance.

This audit does not independently replicate the experiments, verify regression error assumptions, establish sensor calibration or certify a habitat. Apart from reference [1], page 2, the archived README PDF quotations were not individually rechecked visually in this audit; the cited textbook is not archived. Browser/GitHub mathematical rendering was not revalidated because this increment changes documentation and a consistency test, not the UI.
