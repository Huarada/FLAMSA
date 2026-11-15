# SPEC-002 — Fire behavior & safety evidence

Status: implementation increment. English UI/artifacts; conversation may be Portuguese. This section presents source-bounded experimental associations, not habitat certification, a fire-risk score or direct partial-gravity evidence.

## Safety-relevant evidence labels (2026-11-15 increment)

Fire behavior uses full study records with local analysis controls; Dashboard filters remain independent, as already implemented. This supersedes the original shared-filter scope described below and FB-01 for this view.

Identify observations relevant to fire-safety research without estimating ignition probability or declaring a material/environment safe. Labels are deterministic application projections, never LLM judgments. No point's vertical distance from the FLEX line is a risk classifier. Export labels alongside group/record identities in analysis JSON; retain original measurements, qualifiers and provenance in the report and CSVs.

- FLEX: label an identifiable group's adjusted oxygen association as positive only when its 95% slope interval is strictly above zero, negative only when strictly below zero, otherwise unresolved in direction. Missing fits remain unavailable. Encode fit evidence with line patterns and readable labels/tooltips, retaining diluent colors. Raw dots are not assigned risk grades. The mean-response band is not an individual prediction interval or safe operating zone; pressure/diameter are fixed at group means for the drawn trend. A positive association is evidence about reported droplet burning behavior, not a causal ignition threshold.
- BASS-II: use point shapes/tooltips to identify joint measured oxygen decrease and CO2 increase, negative differences needing inspection, and remaining pairs. The zero axes only separate signed differences. Small positive changes are not assumed statistically significant; uncertainty is not quantified. Do not infer exposure, detection performance, combustion onset or a mass yield.
- SAFFIRE-II: use amber cells for positive reported burned length and coral for the exact Complete source category. Preserve raw text in cells/tooltips and the original outcome state. Zero/approximately-zero and unresolved/missing cells use neutral colors, never green/safe. Positive burned length alone does not establish sustained self-propagation. Compare paired gravity columns without converting outcomes into a universal ground-to-orbit law.

Acceptance FB-13: slope intervals touching zero do not receive a directional flag; absent data/fit creates no positive flag; gas signs and unresolved source categories remain explicit. FB-14: rendered charts identify evidence and explain that neither above-line points nor zero/near-zero burned lengths are safety verdicts; JSON/CSV labels agree with deterministic application calculations and record identities.

Primary interpretation references: [NASA FLEX objectives](https://gipoc.grc.nasa.gov/wp/fcf-cir/flex/), [NASA BASS-II sensor measurements](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20150019858.pdf), [NASA Saffire-II silicone results](https://ntrs.nasa.gov/api/citations/20170008805/downloads/20170008805.pdf). These references motivate interpretation; individual plotted claims still use the archived project records.

## Consumption and architecture

Add Fire behavior to Workspace navigation, using the same validated snapshot and committed research query as Dashboard/Investigations/Evidence. All cards consume matching TestPoints; absent investigations remain visibly absent, without secretly clearing filters. Local FLEX settings refine only that analysis. Domain/core data and ingestion are unchanged. Application code computes every derived quantity, coefficient and interval deterministically, without pandas, Streamlit or an LLM. Interface code renders projections and prepares downloads. Numerical libraries are explicit dependencies.

## FLEX — oxygen and the droplet burning-rate constant

Plot reported scalar ambient O2 (%) against reported K (mm²/s), colored by diluent and separated by fuel. Missing/interval/nonfinite/non-test observations are excluded with individual reasons. Eligible observations need reported pressure, initial diameter, He and CO2 fractions, and a named fuel/diluent. Default pressure band: 1 atm ±5%, where 1 atm = the existing canonical conversion. Optional narrowing never widens beyond ±5%. Do not infer nominal pressure.

Fit separately for each fuel/diluent/He-fraction/CO2-fraction stratum, with N2 acting as the balance gas. A shared diluent name does not hold its blend composition fixed. Use ordinary least squares with intercept and O2, adjusting additionally for reported pressure and initial droplet diameter when they vary. Center/scale predictors before solving; transform the oxygen coefficient back to mm²/s per O2 percentage point. These are conditional associations under a linear model, not a claim that all test conditions were experimentally controlled.

Require at least six observations, three distinct oxygen levels, at least three residual degrees of freedom, full design rank and acceptable standardized condition number. Otherwise retain scatter observations and explain why no slope is estimated. Show n, O2/pressure/diameter ranges, fixed blend fractions, covariates/reference means, coefficient, 95% Student-t model-based slope interval and raw within-stratum Spearman rho when defined. The fitted line and 95% mean-response band hold adjustment covariates at their group means and span only observed O2 bounds. Do not connect different strata or extend a fit to lower pressure, other fuels/blends or lunar gravity. Residual normality, homoskedasticity and independent errors are assumptions, not verified properties; intervals omit calibration/model-form uncertainty.

An explicit coverage note counts O2 >=30% AND pressure <=10.2 psi on the same matched test. At the initial inspected revision a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204, that strict count is zero. Seventeen tests instead report approximately 10.33–10.50 psi (<=10.5). Compute both counts from current matched rows; do not hardcode 17 or round pressures before selection. The near-1-atm fit never uses or predicts those lower-pressure tests.

## BASS-II — reported oxygen and carbon-dioxide changes

Compute oxygen consumption in percentage points as initial O2 minus final O2, and CO2 increase as final CO2 minus initial CO2, using the same individual test with four finite reported concentrations and ambient oxygen basis. Plot all complete valid concentration pairs, including small negative changes with an explicit measurement-quality label; do not clamp them, impute values or assert consumption/production when the difference is negative. Show missing/incompatible exclusions and source rows. No regression or conversion to mass/volume is requested. Concentration changes alone do not establish emission yield, sensor performance or cabin exposure.

## SAFFIRE-II — paired microgravity and 1 g outcomes

Render all matching sample rows as a paired outcome matrix/table for burned length and spread rate. Preserve raw Approximate zero, Complete, Acceleratory, mixed-material and note-qualified values. Complete is categorical, not an inferred numeric length; Acceleratory is not a constant spread rate. Missing values remain missing; zero length does not synthesize a zero spread rate. Include material/thickness, source ids/rows and reported atmosphere/flow context. Do not fit a law to nine samples or claim identical ground/orbit conditions unless the source establishes them. The silicone cases differ: some report Complete in 1 g, one reports a finite length and another approximately zero.

## Reproducibility and presentation

The opening student-facing guide precedes Research filters, as defined by SPEC-001 section 22. It explains the approximate d-squared relationship, signed concentration differences and paired ground/flight outcomes with symbols and units. A further disclosure connects the physical model to the existing conditional regression and uncertainty/source trail. The guide presents existing scientific relationships and analysis responsibilities; it does not introduce a new numerical proof, validation pass/fail score or universal safety conclusion.

Every plotted/compared record retains investigation id, TestPoint id, source file/row, lineage/note and source checksum via the loaded aggregate. Exclusions reconcile with matched input totals. An analysis JSON includes revision, policy/version, applied filters, local settings, observations, groups, coefficient/interval/reference values, source column definitions/checksums and a deterministic analysis id. Per-card source tables are downloadable as CSV. Methods link to NIST least squares and SciPy's Student-t interval documentation. Actions open existing source records through the current navigation path.

## Acceptance

- FB-01: navigation shares the snapshot/query; filtering away a target study yields an explicit empty card without broadening scope.
- FB-02: only same-record scalar quantities with expected canonical units enter computations; malformed contracts fail visibly.
- FB-03: FLEX fits never mix fuel or He/CO2 blend strata, nor use pressure outside the configured near-atmospheric band.
- FB-04: synthetic confounded data recover the known adjusted oxygen effect; rank-deficient/low-n/low-variation groups have no invented slope.
- FB-05: model-based intervals, reference conditions and plotted line bounds are deterministic, finite and restricted to observed O2.
- FB-06: strict lunar-scenario counts use exact bounds; the approximate lower-pressure comparison is labelled separately.
- FB-07: BASS-II differences preserve sign, source identity and raw measurements; missing pairs are counted, never filled.
- FB-08: SAFFIRE-II retains categorical/approximate/note-qualified values and all matching samples without numeric conversion of Complete/Acceleratory.
- FB-09: each card reconciles retained/excluded observations and exposes evidence rows and units.
- FB-10: JSON/CSV exports contain the actual analyzed data, settings, revision, deterministic identity and provenance.
- FB-11: changing local controls, enabling copilot or opening a source study preserves the committed query.
- FB-12: browser/UI checks cover readable charts, empty selections and available source navigation; ranking/LLM behavior is not introduced.

Methods: [NIST least squares](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm), [SciPy regression and confidence intervals](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html). Source interpretation also references the local data-quality review; current curated values take precedence over that historical review's pending-fix inventory.
