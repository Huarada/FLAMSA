# RAG stress report

Narrator: **Language model (openai:gpt-4.1-mini)**. Runs: 279. Hard failures: **0**. Warnings: 0.

## Per scenario

| Scenario | Runs | Approved | Insufficient | Avg passages | Avg seconds |
|---|---|---|---|---|---|
| lunar_standard (30% / 10.2 psi) | 93 | 31 | 62 | 10.0 | 15.60 |
| user_o2_38078 (38.078% / 14.7 psi) | 93 | 50 | 43 | 10.0 | 13.20 |
| user_o2_15_psi_14 (15% / 14 psi) | 93 | 36 | 57 | 10.0 | 12.90 |

## Per question (retrieval relevance proxy)

| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |
|---|---|---|---|---|---|
| rank_default | ranking | 9 | 10.0 | n/a | 3 |
| rank_compare | ranking | 9 | 10.0 | n/a | 8 |
| rank_criterion | ranking | 9 | 10.0 | n/a | 6 |
| rec_ranges | records | 9 | 10.0 | 0.83 | 8 |
| rec_closest | records | 9 | 10.0 | n/a | 5 |
| rec_lowest_psi | records | 9 | 10.0 | 0.73 | 2 |
| rag_flame_spread | passages | 9 | 10.0 | 0.97 | 8 |
| rag_extinction | passages | 9 | 10.0 | 1.00 | 9 |
| rag_burner | passages | 9 | 10.0 | 0.37 | 7 |
| rag_droplet | passages | 9 | 10.0 | 0.87 | 8 |
| rag_co2 | passages | 9 | 10.0 | 0.77 | 6 |
| meta_pillars | metadata | 9 | 10.0 | n/a | 0 |
| meta_hardware | metadata | 9 | 10.0 | 0.63 | 8 |
| lim_safe | limits | 9 | 10.0 | n/a | 5 |
| lim_gravity | limits | 9 | 10.0 | n/a | 5 |
| lim_extrapolate | limits | 9 | 10.0 | n/a | 4 |
| tech | scope | 9 | 10.0 | n/a | 5 |
| out_of_scope | scope | 9 | 10.0 | n/a | 0 |
| trap_exact | trap | 9 | 10.0 | n/a | 7 |
| trap_limit | trap | 9 | 10.0 | n/a | 5 |
| edge_empty | edge | 9 | 10.0 | n/a | 3 |
| edge_spaces | edge | 9 | 10.0 | n/a | 3 |
| edge_single_char | edge | 9 | 10.0 | n/a | 5 |
| edge_numbers_only | edge | 9 | 10.0 | n/a | 5 |
| edge_portuguese | edge | 9 | 10.0 | n/a | 3 |
| edge_unicode | edge | 9 | 10.0 | n/a | 6 |
| edge_markup | edge | 9 | 10.0 | n/a | 4 |
| edge_sql | edge | 9 | 10.0 | n/a | 5 |
| edge_unknown_study | edge | 9 | 10.0 | n/a | 8 |
| edge_injection | edge | 9 | 10.0 | n/a | 3 |
| edge_long | edge | 9 | 10.0 | n/a | 8 |

## Hard failures

None.

## Warnings

None.

## Validator issue codes in rejected runs (runs affected)

- undeclared_number: 128
- number_mismatch: 46
- quote_mismatch: 43
- unknown_citation: 37
- malformed_citation: 12
- missing_citation: 3
- implausible: 2

## Rejected runs (scenario / question: codes)

- lunar_standard / rec_ranges: undeclared_number
- lunar_standard / rec_closest: undeclared_number, unknown_citation
- lunar_standard / rec_lowest_psi: undeclared_number
- lunar_standard / rag_flame_spread: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / rag_extinction: quote_mismatch, unknown_citation
- lunar_standard / rag_burner: number_mismatch, undeclared_number
- lunar_standard / rag_droplet: missing_citation, number_mismatch, quote_mismatch, undeclared_number
- lunar_standard / rag_co2: undeclared_number
- lunar_standard / meta_hardware: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / lim_safe: malformed_citation, quote_mismatch, undeclared_number
- lunar_standard / lim_extrapolate: malformed_citation, undeclared_number
- lunar_standard / tech: undeclared_number
- lunar_standard / trap_limit: undeclared_number
- lunar_standard / edge_spaces: undeclared_number
- lunar_standard / edge_single_char: quote_mismatch
- lunar_standard / edge_numbers_only: undeclared_number
- lunar_standard / edge_portuguese: undeclared_number
- lunar_standard / edge_markup: number_mismatch, undeclared_number
- lunar_standard / edge_sql: quote_mismatch, undeclared_number
- lunar_standard / edge_unknown_study: undeclared_number, unknown_citation
- lunar_standard / edge_injection: undeclared_number, unknown_citation
- user_o2_38078 / rank_compare: malformed_citation, undeclared_number
- user_o2_38078 / rank_criterion: number_mismatch, undeclared_number
- user_o2_38078 / rec_ranges: number_mismatch
- user_o2_38078 / rec_closest: undeclared_number
- user_o2_38078 / rag_flame_spread: undeclared_number
- user_o2_38078 / rag_extinction: number_mismatch, undeclared_number
- user_o2_38078 / rag_burner: quote_mismatch
- user_o2_38078 / rag_droplet: number_mismatch
- user_o2_38078 / rag_co2: quote_mismatch, undeclared_number
- user_o2_38078 / meta_hardware: undeclared_number, unknown_citation
- user_o2_38078 / trap_exact: undeclared_number, unknown_citation
- user_o2_38078 / edge_single_char: unknown_citation
- user_o2_38078 / edge_portuguese: number_mismatch
- user_o2_38078 / edge_unicode: undeclared_number
- user_o2_38078 / edge_sql: number_mismatch, undeclared_number
- user_o2_38078 / edge_unknown_study: undeclared_number
- user_o2_38078 / edge_long: implausible, number_mismatch, quote_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rank_compare: unknown_citation
- user_o2_15_psi_14 / rank_criterion: malformed_citation
- user_o2_15_psi_14 / rec_ranges: undeclared_number
- user_o2_15_psi_14 / rec_closest: undeclared_number
- user_o2_15_psi_14 / rag_flame_spread: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_extinction: undeclared_number
- user_o2_15_psi_14 / rag_droplet: undeclared_number
- user_o2_15_psi_14 / meta_hardware: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / lim_safe: number_mismatch, undeclared_number
- user_o2_15_psi_14 / lim_extrapolate: number_mismatch, undeclared_number
- user_o2_15_psi_14 / tech: number_mismatch, undeclared_number
- user_o2_15_psi_14 / trap_exact: undeclared_number, unknown_citation
- user_o2_15_psi_14 / trap_limit: number_mismatch, undeclared_number
- user_o2_15_psi_14 / edge_empty: undeclared_number
- user_o2_15_psi_14 / edge_numbers_only: number_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / edge_markup: undeclared_number
- user_o2_15_psi_14 / edge_unknown_study: number_mismatch, undeclared_number
- user_o2_15_psi_14 / edge_injection: undeclared_number
- user_o2_15_psi_14 / edge_long: undeclared_number
- lunar_standard / rank_default: quote_mismatch, undeclared_number
- lunar_standard / rank_compare: malformed_citation
- lunar_standard / rank_criterion: number_mismatch
- lunar_standard / rec_ranges: number_mismatch, undeclared_number
- lunar_standard / rec_closest: undeclared_number, unknown_citation
- lunar_standard / rec_lowest_psi: undeclared_number
- lunar_standard / rag_flame_spread: undeclared_number
- lunar_standard / rag_extinction: quote_mismatch, undeclared_number
- lunar_standard / rag_burner: unknown_citation
- lunar_standard / rag_droplet: number_mismatch, undeclared_number
- lunar_standard / rag_co2: quote_mismatch, undeclared_number
- lunar_standard / meta_hardware: quote_mismatch, unknown_citation
- lunar_standard / lim_safe: undeclared_number
- lunar_standard / lim_gravity: missing_citation, undeclared_number
- lunar_standard / tech: undeclared_number
- lunar_standard / trap_limit: number_mismatch, undeclared_number
- lunar_standard / edge_spaces: undeclared_number
- lunar_standard / edge_single_char: undeclared_number
- lunar_standard / edge_numbers_only: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / edge_sql: undeclared_number
- lunar_standard / edge_unknown_study: undeclared_number
- lunar_standard / edge_long: undeclared_number
- user_o2_38078 / rank_compare: malformed_citation, undeclared_number
- user_o2_38078 / rec_ranges: number_mismatch
- user_o2_38078 / rag_extinction: undeclared_number, unknown_citation
- user_o2_38078 / rag_burner: number_mismatch, unknown_citation
- user_o2_38078 / meta_hardware: undeclared_number
- user_o2_38078 / lim_gravity: undeclared_number
- user_o2_38078 / trap_exact: undeclared_number
- user_o2_38078 / edge_portuguese: unknown_citation
- user_o2_38078 / edge_unicode: unknown_citation
- user_o2_38078 / edge_unknown_study: undeclared_number
- user_o2_38078 / edge_long: number_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rank_default: undeclared_number
- user_o2_15_psi_14 / rank_compare: malformed_citation
- user_o2_15_psi_14 / rank_criterion: malformed_citation
- user_o2_15_psi_14 / rec_ranges: number_mismatch
- user_o2_15_psi_14 / rag_flame_spread: number_mismatch, quote_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_extinction: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_droplet: undeclared_number
- user_o2_15_psi_14 / rag_co2: missing_citation, number_mismatch
- user_o2_15_psi_14 / lim_safe: number_mismatch, quote_mismatch, undeclared_number
- user_o2_15_psi_14 / lim_gravity: quote_mismatch
- user_o2_15_psi_14 / lim_extrapolate: number_mismatch, quote_mismatch, undeclared_number
- user_o2_15_psi_14 / tech: unknown_citation
- user_o2_15_psi_14 / trap_exact: undeclared_number, unknown_citation
- user_o2_15_psi_14 / trap_limit: undeclared_number
- user_o2_15_psi_14 / edge_empty: malformed_citation, undeclared_number
- user_o2_15_psi_14 / edge_single_char: number_mismatch, quote_mismatch, undeclared_number
- user_o2_15_psi_14 / edge_numbers_only: quote_mismatch
- user_o2_15_psi_14 / edge_unicode: undeclared_number
- user_o2_15_psi_14 / edge_unknown_study: number_mismatch
- user_o2_15_psi_14 / edge_long: undeclared_number
- lunar_standard / rank_default: undeclared_number
- lunar_standard / rank_compare: number_mismatch
- lunar_standard / rec_closest: undeclared_number
- lunar_standard / rag_flame_spread: undeclared_number, unknown_citation
- lunar_standard / rag_extinction: quote_mismatch, undeclared_number
- lunar_standard / rag_burner: undeclared_number, unknown_citation
- lunar_standard / rag_droplet: number_mismatch, quote_mismatch, undeclared_number
- lunar_standard / meta_hardware: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / lim_safe: number_mismatch, undeclared_number
- lunar_standard / lim_gravity: undeclared_number
- lunar_standard / trap_exact: malformed_citation, undeclared_number
- lunar_standard / edge_spaces: undeclared_number
- lunar_standard / edge_numbers_only: quote_mismatch, undeclared_number
- lunar_standard / edge_unicode: undeclared_number
- lunar_standard / edge_markup: undeclared_number
- lunar_standard / edge_sql: number_mismatch
- lunar_standard / edge_unknown_study: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / edge_injection: number_mismatch
- lunar_standard / edge_long: undeclared_number
- user_o2_38078 / rank_compare: malformed_citation
- user_o2_38078 / rank_criterion: undeclared_number
- user_o2_38078 / rec_ranges: number_mismatch, quote_mismatch, undeclared_number
- user_o2_38078 / rag_flame_spread: undeclared_number
- user_o2_38078 / rag_extinction: number_mismatch, undeclared_number, unknown_citation
- user_o2_38078 / rag_burner: unknown_citation
- user_o2_38078 / rag_droplet: number_mismatch, quote_mismatch, undeclared_number
- user_o2_38078 / rag_co2: undeclared_number
- user_o2_38078 / meta_hardware: quote_mismatch, undeclared_number, unknown_citation
- user_o2_38078 / lim_gravity: quote_mismatch, undeclared_number
- user_o2_38078 / tech: quote_mismatch
- user_o2_38078 / trap_exact: undeclared_number
- user_o2_38078 / edge_unicode: undeclared_number
- user_o2_38078 / edge_sql: undeclared_number, unknown_citation
- user_o2_38078 / edge_long: implausible, number_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rank_compare: number_mismatch, quote_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rank_criterion: malformed_citation, number_mismatch
- user_o2_15_psi_14 / rec_ranges: number_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rag_flame_spread: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_extinction: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_burner: quote_mismatch
- user_o2_15_psi_14 / rag_droplet: number_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rag_co2: quote_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / meta_hardware: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / lim_extrapolate: number_mismatch, undeclared_number
- user_o2_15_psi_14 / trap_exact: number_mismatch, undeclared_number
- user_o2_15_psi_14 / trap_limit: undeclared_number
- user_o2_15_psi_14 / edge_empty: undeclared_number
- user_o2_15_psi_14 / edge_single_char: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / edge_unicode: undeclared_number
- user_o2_15_psi_14 / edge_markup: quote_mismatch
- user_o2_15_psi_14 / edge_unknown_study: number_mismatch, undeclared_number
- user_o2_15_psi_14 / edge_long: quote_mismatch, undeclared_number

## Variance across repeated rounds

Approved per round: [36, 40, 41] (mean 39.0, std 2.2).

Cells always approved: 21; never approved: 31; mixed (same input, different outcome): 41.

- mixed: lunar_standard / edge_injection: 1 of 3 approved
- mixed: lunar_standard / edge_long: 1 of 3 approved
- mixed: lunar_standard / edge_markup: 1 of 3 approved
- mixed: lunar_standard / edge_portuguese: 2 of 3 approved
- mixed: lunar_standard / edge_single_char: 1 of 3 approved
- mixed: lunar_standard / edge_unicode: 2 of 3 approved
- mixed: lunar_standard / lim_extrapolate: 2 of 3 approved
- mixed: lunar_standard / lim_gravity: 1 of 3 approved
- mixed: lunar_standard / rag_co2: 1 of 3 approved
- mixed: lunar_standard / rank_compare: 1 of 3 approved
- mixed: lunar_standard / rank_criterion: 2 of 3 approved
- mixed: lunar_standard / rank_default: 1 of 3 approved
- mixed: lunar_standard / rec_lowest_psi: 1 of 3 approved
- mixed: lunar_standard / rec_ranges: 1 of 3 approved
- mixed: lunar_standard / tech: 1 of 3 approved
- mixed: lunar_standard / trap_exact: 2 of 3 approved
- mixed: lunar_standard / trap_limit: 1 of 3 approved
- mixed: user_o2_15_psi_14 / edge_injection: 2 of 3 approved
- mixed: user_o2_15_psi_14 / edge_markup: 1 of 3 approved
- mixed: user_o2_15_psi_14 / edge_numbers_only: 1 of 3 approved
- mixed: user_o2_15_psi_14 / edge_single_char: 1 of 3 approved
- mixed: user_o2_15_psi_14 / edge_unicode: 1 of 3 approved
- mixed: user_o2_15_psi_14 / lim_gravity: 2 of 3 approved
- mixed: user_o2_15_psi_14 / lim_safe: 1 of 3 approved
- mixed: user_o2_15_psi_14 / meta_hardware: 1 of 3 approved
- mixed: user_o2_15_psi_14 / rag_burner: 2 of 3 approved
- mixed: user_o2_15_psi_14 / rag_co2: 1 of 3 approved
- mixed: user_o2_15_psi_14 / rank_default: 2 of 3 approved
- mixed: user_o2_15_psi_14 / rec_closest: 2 of 3 approved
- mixed: user_o2_15_psi_14 / tech: 1 of 3 approved
- mixed: user_o2_38078 / edge_portuguese: 1 of 3 approved
- mixed: user_o2_38078 / edge_single_char: 2 of 3 approved
- mixed: user_o2_38078 / edge_sql: 1 of 3 approved
- mixed: user_o2_38078 / edge_unknown_study: 1 of 3 approved
- mixed: user_o2_38078 / lim_gravity: 1 of 3 approved
- mixed: user_o2_38078 / rag_co2: 1 of 3 approved
- mixed: user_o2_38078 / rag_droplet: 1 of 3 approved
- mixed: user_o2_38078 / rag_flame_spread: 1 of 3 approved
- mixed: user_o2_38078 / rank_criterion: 1 of 3 approved
- mixed: user_o2_38078 / rec_closest: 2 of 3 approved
- mixed: user_o2_38078 / tech: 2 of 3 approved

## Claim-level versus answer-level failure (first attempt)

Drafts: 279; mean claims per draft 4.6; claims with an issue 420 of 1277 (per-claim failure rate 0.33).
Answers with at least one failing claim: 0.76. If claims failed independently at that rate, the expected answer failure would be 0.84.
Runs that needed a second attempt: 211; of those approved after the retry: 49 (0.23).

## Numbers behind `undeclared_number` (final rejection of each run)

| Explanation | Count |
|---|---|
| value of an uncited record of a cited investigation | 133 |
| not a known fact (model-stated) | 106 |
| system fact of an UNCITED investigation | 101 |

Most frequent values:

- 21: 49
- 33.3: 33
- 33: 20
- 20: 17
- 0.4: 15
- 0.25: 15
- 10: 14
- 19: 14
- 17.5: 13
- 40: 11
- 5: 11
- 3: 9

Examples (number | explanation | sentence):

- 18 | value of an uncited record of a cited investigation | The FLEX investigation tested oxygen concentrations at ambient levels of 18% to 30% and pressures close to 10.2 psi, which are relevant to the lunar base scenario with 30% oxygen and 10.2 psi pressure. Specific test points include
- 0.4 | not a known fact (model-stated) | The FLEX-2 investigation tested oxygen mole fractions ranging from 0.1 to 0.4 (10% to 40%) and pressures from approximately 7.35 psi to 44.1 psi, covering and exceeding the lunar base scenario's oxygen and pressure conditions. The
- 10 | not a known fact (model-stated) | The FLEX-2 investigation tested oxygen mole fractions ranging from 0.1 to 0.4 (10% to 40%) and pressures from approximately 7.35 psi to 44.1 psi, covering and exceeding the lunar base scenario's oxygen and pressure conditions. The
- 40 | not a known fact (model-stated) | The FLEX-2 investigation tested oxygen mole fractions ranging from 0.1 to 0.4 (10% to 40%) and pressures from approximately 7.35 psi to 44.1 psi, covering and exceeding the lunar base scenario's oxygen and pressure conditions. The
- 0.25 | system fact of an UNCITED investigation | The CFI investigation studied cool flame combustion behavior over a pressure range from 0.25 atm to 5 atm (approximately 3.68 psi to 73.5 psi), which includes and exceeds the lunar base scenario pressure of 10.2 psi, with oxygen c
- 5 | system fact of an UNCITED investigation | The CFI investigation studied cool flame combustion behavior over a pressure range from 0.25 atm to 5 atm (approximately 3.68 psi to 73.5 psi), which includes and exceeds the lunar base scenario pressure of 10.2 psi, with oxygen c
- 3.68 | not a known fact (model-stated) | The CFI investigation studied cool flame combustion behavior over a pressure range from 0.25 atm to 5 atm (approximately 3.68 psi to 73.5 psi), which includes and exceeds the lunar base scenario pressure of 10.2 psi, with oxygen c
- 25 | value of an uncited record of a cited investigation | The FLEX investigation includes tests at an oxygen concentration exactly matching the lunar base scenario's 30% ambient oxygen and a pressure very close to 10.2 psi, with test points 25, 26, and 27 having oxygen concentrations of 
- 26 | value of an uncited record of a cited investigation | The FLEX investigation includes tests at an oxygen concentration exactly matching the lunar base scenario's 30% ambient oxygen and a pressure very close to 10.2 psi, with test points 25, 26, and 27 having oxygen concentrations of 
- 27 | not a known fact (model-stated) | The FLEX investigation includes tests at an oxygen concentration exactly matching the lunar base scenario's 30% ambient oxygen and a pressure very close to 10.2 psi, with test points 25, 26, and 27 having oxygen concentrations of 
- 33 | value of an uncited record of a cited investigation | The lowest pressure reported for the ACME-CFI-G investigation is approximately 7.35 psi, as shown by multiple test points with ethane fuel at oxygen concentrations around 33-34% ambient.
- 17.5 | value of an uncited record of a cited investigation | The BASS-II investigation studied flame spread over thin solid fuels (PMMA rods) in microgravity and normal gravity, analyzing the effect of oxygen concentration on flame spread. It found that flame spread was observed at oxygen c
- 19 | value of an uncited record of a cited investigation | The BASS-II investigation studied flame spread over thin solid fuels (PMMA rods) in microgravity and normal gravity, analyzing the effect of oxygen concentration on flame spread. It found that flame spread was observed at oxygen c
- 21 | system fact of an UNCITED investigation | The BASS investigation includes oxygen concentration measurements in the ISS cabin atmosphere and MSG working volume, with testing restricted to oxygen concentrations at or above 21%, relevant for habitat fire safety and flame spr
- 3 | system fact of an UNCITED investigation | The ACME-CFI-G investigation data includes tests at oxygen concentrations near 30% ambient and chamber pressures close to 3 atm, which are relevant to a lunar base habitat scenario with 30% oxygen and about 10.2 psi pressure (appr
- 0.7 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation data includes tests at oxygen concentrations near 30% ambient and chamber pressures close to 3 atm, which are relevant to a lunar base habitat scenario with 30% oxygen and about 10.2 psi pressure (appr
- 1 | system fact of an UNCITED investigation | The CFI investigation data is at oxygen concentrations around 21% ambient and pressures near 1 atm, which are lower than the lunar base scenario oxygen and pressure, making it less directly relevant for burner-stream versus chambe
- 0.44 | value of an uncited record of a cited investigation | The FLEX investigation provides data on methanol droplet combustion at oxygen concentrations including 20% and 30% ambient oxygen at pressures close to 10.2 psi, relevant to the lunar base scenario. It shows that the droplet burni
- 50 | not a known fact (model-stated) | The FLEX-2 investigation indicates that the burning rate constant is only a weak function of pressure and changes in ambient composition, including oxygen concentration, can cause changes in burning rates by about 50%. This sugges
- 0.5 | system fact of an UNCITED investigation | The CFI investigation used hardware including a color camera with live downlink to the Telescience Support Center (TSC) to monitor combustion processes. Narrow-band and wide-band radiometers were used to measure radiation emission
- 27 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation is relevant but less closely matched to the lunar habitat scenario, as its closest oxygen concentration is about 27% ambient (3.2% higher than scenario) and pressure about 8 psi (2.2 psi lower than sce
- 3.2 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation is relevant but less closely matched to the lunar habitat scenario, as its closest oxygen concentration is about 27% ambient (3.2% higher than scenario) and pressure about 8 psi (2.2 psi lower than sce
- 8 | system fact of an UNCITED investigation | The ACME-CFI-G investigation is relevant but less closely matched to the lunar habitat scenario, as its closest oxygen concentration is about 27% ambient (3.2% higher than scenario) and pressure about 8 psi (2.2 psi lower than sce
- 2.2 | not a known fact (model-stated) | The ACME-CFI-G investigation is relevant but less closely matched to the lunar habitat scenario, as its closest oxygen concentration is about 27% ambient (3.2% higher than scenario) and pressure about 8 psi (2.2 psi lower than sce
- 7.8 | not a known fact (model-stated) | The BASS-II investigation does not report pressure data for ambient conditions and has oxygen concentrations 7.8% away from the lunar base scenario, indicating extrapolation beyond the tested oxygen range and no pressure data for 
- 9 | not a known fact (model-stated) | The CFI investigation tests at oxygen concentrations 9% away and pressures 0.8 psi away from the lunar base scenario, indicating partial extrapolation beyond the oxygen range but close pressure proximity.
- 0.8 | system fact of an UNCITED investigation | The CFI investigation tests at oxygen concentrations 9% away and pressures 0.8 psi away from the lunar base scenario, indicating partial extrapolation beyond the oxygen range but close pressure proximity.
- 20 | value of an uncited record of a cited investigation | The FLEX investigation is highly relevant to a lunar base habitat scenario with 30% oxygen at about 10.2 psi, as it includes 274 individual tests with oxygen concentration and pressure values very close to the scenario conditions,
- 15 | not a known fact (model-stated) | The CFI investigation provides data on cool and warm flame combustion of liquid fuels such as n-dodecane and its mixtures at pressures higher than the lunar habitat scenario, around 11 to 15 psi, and oxygen concentrations near 21%
- 10.4 | value of an uncited record of a cited investigation | The FLEX investigation is relevant to a lunar base habitat scenario with 30% oxygen at about 10.2 psi because it includes tests at oxygen concentrations and pressures very close to the scenario conditions, specifically tests with 

## Retrieved passages for the regions you asked about

**lunar_standard / rank_default** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- ACME-CFI-G p. 14: analysis of the chamber atmosphere, e.g., for oxygen, nitrogen, carbon dioxide, carbon monoxide, and fuel gase
- ACME-CFI-G p. 78: runs. The CIR includes an optics bench, combustion chamber, fuel, and oxidizer control, and five different cam

**lunar_standard / rag_flame_spread** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 4: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 65: ACME/CFI-G Final Report (2022) 21 November 2022 65 This composite image shows the effects of the oxidizer flow
- ACME-CFI-G p. 64: ACME/CFI-G Final Report (2022) 21 November 2022 64 Figure 1. CFI-G Inverse Flames at Increasing Oxidizer Flow 

**lunar_standard / rag_droplet** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2, BASS)
- FLEX p. 7: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 10: subsequently removed, leaving only three fibers in the final testing for the BRE and Coflow Laminar Diffusion 
- ACME-CFI-G p. 64: ACME/CFI-G Final Report (2022) 21 November 2022 64 Figure 1. CFI-G Inverse Flames at Increasing Oxidizer Flow 

**lunar_standard / rag_co2** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 11: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 62: ACME/CFI-G Final Report (2022) 21 November 2022 62 varying the concentration ratios of the oxygen/nitrogen mix
- ACME-CFI-G p. 66: ACME/CFI-G Final Report (2022) 21 November 2022 66 fuel was diluted with nitrogen. The other test parameters i

**user_o2_38078 / rank_default** (approved; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI, SAME-R)
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 14: analysis of the chamber atmosphere, e.g., for oxygen, nitrogen, carbon dioxide, carbon monoxide, and fuel gase
- ACME-CFI-G p. 78: runs. The CIR includes an optics bench, combustion chamber, fuel, and oxidizer control, and five different cam

**user_o2_38078 / rag_flame_spread** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI, SAME-R)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- ACME-CFI-G p. 65: ACME/CFI-G Final Report (2022) 21 November 2022 65 This composite image shows the effects of the oxidizer flow
- ACME-CFI-G p. 64: ACME/CFI-G Final Report (2022) 21 November 2022 64 Figure 1. CFI-G Inverse Flames at Increasing Oxidizer Flow 

**user_o2_38078 / rag_droplet** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI, SAME-R)
- FLEX p. 7: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 64: ACME/CFI-G Final Report (2022) 21 November 2022 64 Figure 1. CFI-G Inverse Flames at Increasing Oxidizer Flow 
- ACME-CFI-G p. 10: subsequently removed, leaving only three fibers in the final testing for the BRE and Coflow Laminar Diffusion 

**user_o2_38078 / rag_co2** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI, SAME-R)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 62: ACME/CFI-G Final Report (2022) 21 November 2022 62 varying the concentration ratios of the oxygen/nitrogen mix
- ACME-CFI-G p. 51: Gases) with 14 ethane flames, sometimes diluted with nitrog en, ignited in various oxygen/nitrogen atmospheres

**user_o2_15_psi_14 / rank_default** (approved; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- BASS-II p. 138: NASA/TM-20210011385 130 17. Chan, Ryan Lesley: Effect of Oxygen Concentration on Flame Spread Over Thin Fuels 
- BASS-II p. 6: 4.1.3 References .............................................................................................

**user_o2_15_psi_14 / rag_flame_spread** (insufficient_evidence; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 4: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- BASS-II p. 6: 4.1.3 References .............................................................................................
- BASS-II p. 138: NASA/TM-20210011385 130 17. Chan, Ryan Lesley: Effect of Oxygen Concentration on Flame Spread Over Thin Fuels 

**user_o2_15_psi_14 / rag_droplet** (insufficient_evidence; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2, BASS)
- FLEX p. 7: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- BASS-II p. 40: quasi-steady (while the flame spread rate is constant, the flame shape may evolve in an unsteady manner), quas
- BASS-II p. 138: NASA/TM-20210011385 130 17. Chan, Ryan Lesley: Effect of Oxygen Concentration on Flame Spread Over Thin Fuels 

**user_o2_15_psi_14 / rag_co2** (approved; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 11: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- BASS-II p. 87: NASA/TM-20210011385 79 6.1.4.6 Gas Sensor Results The initial and final O2, CO2, and CO readings were recorded
- BASS-II p. 18: NASA/TM-20210011385 10 Figure 1.7.—O2 consumed, CO2 and CO generated per gram of fuel mass loss for two differ

