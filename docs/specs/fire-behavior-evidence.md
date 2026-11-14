# SPEC-002 — Fire behavior & safety evidence

Status: implementation increment. English UI/artifacts; conversation may be Portuguese. This section presents source-bounded experimental associations, not habitat certification, a fire-risk score or direct partial-gravity evidence.

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
