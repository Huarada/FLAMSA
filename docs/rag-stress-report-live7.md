# RAG stress report

Narrator: **Language model (openai:gpt-4.1-mini)**. Runs: 279. Hard failures: **0**. Warnings: 0.

## Per scenario

| Scenario | Runs | Approved | Insufficient | Avg passages | Avg seconds |
|---|---|---|---|---|---|
| lunar_standard (30% / 10.2 psi) | 93 | 64 | 29 | 10.0 | 14.41 |
| user_o2_38078 (38.078% / 14.7 psi) | 93 | 72 | 21 | 10.0 | 12.13 |
| user_o2_15_psi_14 (15% / 14 psi) | 93 | 69 | 24 | 10.0 | 12.91 |

## Per question (retrieval relevance proxy)

| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |
|---|---|---|---|---|---|
| rank_default | ranking | 9 | 10.0 | n/a | 0 |
| rank_compare | ranking | 9 | 10.0 | n/a | 4 |
| rank_criterion | ranking | 9 | 10.0 | n/a | 3 |
| rec_ranges | records | 9 | 10.0 | 0.83 | 3 |
| rec_closest | records | 9 | 10.0 | n/a | 1 |
| rec_lowest_psi | records | 9 | 10.0 | 0.73 | 0 |
| rag_flame_spread | passages | 9 | 10.0 | 0.97 | 6 |
| rag_extinction | passages | 9 | 10.0 | 1.00 | 2 |
| rag_burner | passages | 9 | 10.0 | 0.37 | 4 |
| rag_droplet | passages | 9 | 10.0 | 0.87 | 6 |
| rag_co2 | passages | 9 | 10.0 | 0.77 | 5 |
| meta_pillars | metadata | 9 | 10.0 | n/a | 2 |
| meta_hardware | metadata | 9 | 10.0 | 0.63 | 4 |
| lim_safe | limits | 9 | 10.0 | n/a | 3 |
| lim_gravity | limits | 9 | 10.0 | n/a | 1 |
| lim_extrapolate | limits | 9 | 10.0 | n/a | 4 |
| tech | scope | 9 | 10.0 | n/a | 1 |
| out_of_scope | scope | 9 | 10.0 | n/a | 1 |
| trap_exact | trap | 9 | 10.0 | n/a | 1 |
| trap_limit | trap | 9 | 10.0 | n/a | 4 |
| edge_empty | edge | 9 | 10.0 | n/a | 1 |
| edge_spaces | edge | 9 | 10.0 | n/a | 0 |
| edge_single_char | edge | 9 | 10.0 | n/a | 1 |
| edge_numbers_only | edge | 9 | 10.0 | n/a | 2 |
| edge_portuguese | edge | 9 | 10.0 | n/a | 1 |
| edge_unicode | edge | 9 | 10.0 | n/a | 1 |
| edge_markup | edge | 9 | 10.0 | n/a | 3 |
| edge_sql | edge | 9 | 10.0 | n/a | 1 |
| edge_unknown_study | edge | 9 | 10.0 | n/a | 3 |
| edge_injection | edge | 9 | 10.0 | n/a | 3 |
| edge_long | edge | 9 | 10.0 | n/a | 3 |

## Hard failures

None.

## Warnings

None.

## Validator issue codes in rejected runs (runs affected)

- undeclared_number: 52
- number_mismatch: 17
- quote_mismatch: 16
- malformed_citation: 13
- unknown_citation: 11
- missing_citation: 3
- implausible: 1
- empty_draft: 1

## Rejected runs (scenario / question: codes)

- lunar_standard / rag_burner: number_mismatch, unknown_citation
- lunar_standard / rag_droplet: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / rag_co2: missing_citation
- lunar_standard / trap_limit: undeclared_number
- lunar_standard / edge_numbers_only: number_mismatch, undeclared_number
- lunar_standard / edge_sql: malformed_citation, missing_citation, quote_mismatch, undeclared_number
- lunar_standard / edge_unknown_study: undeclared_number
- lunar_standard / edge_long: implausible, undeclared_number
- user_o2_38078 / rank_compare: undeclared_number
- user_o2_38078 / rank_criterion: undeclared_number
- user_o2_38078 / rec_closest: undeclared_number
- user_o2_38078 / rag_flame_spread: empty_draft
- user_o2_38078 / rag_burner: undeclared_number, unknown_citation
- user_o2_38078 / meta_pillars: number_mismatch
- user_o2_38078 / meta_hardware: quote_mismatch
- user_o2_38078 / edge_markup: undeclared_number
- user_o2_38078 / edge_long: undeclared_number
- user_o2_15_psi_14 / rank_criterion: malformed_citation, undeclared_number
- user_o2_15_psi_14 / rec_ranges: number_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_flame_spread: quote_mismatch
- user_o2_15_psi_14 / rag_extinction: undeclared_number
- user_o2_15_psi_14 / rag_droplet: number_mismatch, quote_mismatch
- user_o2_15_psi_14 / rag_co2: number_mismatch, undeclared_number
- user_o2_15_psi_14 / lim_safe: quote_mismatch, unknown_citation
- user_o2_15_psi_14 / lim_extrapolate: number_mismatch, undeclared_number
- user_o2_15_psi_14 / trap_limit: undeclared_number
- user_o2_15_psi_14 / edge_markup: malformed_citation
- lunar_standard / rank_compare: undeclared_number
- lunar_standard / rag_flame_spread: quote_mismatch, undeclared_number
- lunar_standard / rag_burner: unknown_citation
- lunar_standard / rag_droplet: undeclared_number
- lunar_standard / rag_co2: undeclared_number
- lunar_standard / meta_hardware: quote_mismatch, unknown_citation
- lunar_standard / lim_safe: malformed_citation
- lunar_standard / lim_extrapolate: undeclared_number
- lunar_standard / out_of_scope: undeclared_number
- lunar_standard / edge_numbers_only: undeclared_number
- lunar_standard / edge_unicode: undeclared_number
- lunar_standard / edge_markup: malformed_citation, undeclared_number
- lunar_standard / edge_unknown_study: undeclared_number
- user_o2_38078 / rank_compare: undeclared_number
- user_o2_38078 / rank_criterion: number_mismatch, undeclared_number
- user_o2_38078 / meta_hardware: quote_mismatch, undeclared_number
- user_o2_38078 / lim_safe: undeclared_number
- user_o2_38078 / edge_injection: undeclared_number
- user_o2_15_psi_14 / rec_ranges: undeclared_number
- user_o2_15_psi_14 / rag_flame_spread: unknown_citation
- user_o2_15_psi_14 / rag_droplet: malformed_citation, number_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_co2: number_mismatch
- user_o2_15_psi_14 / lim_extrapolate: number_mismatch, quote_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / trap_limit: undeclared_number
- user_o2_15_psi_14 / edge_empty: malformed_citation, quote_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / edge_injection: malformed_citation
- lunar_standard / rag_flame_spread: malformed_citation, undeclared_number
- lunar_standard / rag_burner: number_mismatch, unknown_citation
- lunar_standard / rag_droplet: quote_mismatch, undeclared_number
- lunar_standard / lim_extrapolate: undeclared_number
- lunar_standard / trap_limit: undeclared_number
- lunar_standard / edge_unknown_study: undeclared_number
- lunar_standard / edge_injection: malformed_citation
- lunar_standard / edge_long: number_mismatch, quote_mismatch, undeclared_number
- user_o2_38078 / rank_compare: undeclared_number
- user_o2_38078 / rag_droplet: number_mismatch
- user_o2_38078 / meta_pillars: number_mismatch
- user_o2_38078 / meta_hardware: quote_mismatch
- user_o2_38078 / lim_gravity: quote_mismatch, undeclared_number
- user_o2_38078 / tech: undeclared_number
- user_o2_38078 / trap_exact: undeclared_number
- user_o2_15_psi_14 / rec_ranges: number_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_flame_spread: malformed_citation, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rag_extinction: undeclared_number
- user_o2_15_psi_14 / rag_co2: missing_citation
- user_o2_15_psi_14 / edge_single_char: malformed_citation, number_mismatch, quote_mismatch
- user_o2_15_psi_14 / edge_portuguese: malformed_citation, undeclared_number

## Variance across repeated rounds

Approved per round: [66, 67, 72] (mean 68.3, std 2.6).

Cells always approved: 47; never approved: 8; mixed (same input, different outcome): 38.

- mixed: lunar_standard / edge_injection: 2 of 3 approved
- mixed: lunar_standard / edge_long: 1 of 3 approved
- mixed: lunar_standard / edge_markup: 2 of 3 approved
- mixed: lunar_standard / edge_numbers_only: 1 of 3 approved
- mixed: lunar_standard / edge_sql: 2 of 3 approved
- mixed: lunar_standard / edge_unicode: 2 of 3 approved
- mixed: lunar_standard / lim_extrapolate: 1 of 3 approved
- mixed: lunar_standard / lim_safe: 2 of 3 approved
- mixed: lunar_standard / meta_hardware: 2 of 3 approved
- mixed: lunar_standard / out_of_scope: 2 of 3 approved
- mixed: lunar_standard / rag_co2: 1 of 3 approved
- mixed: lunar_standard / rag_flame_spread: 1 of 3 approved
- mixed: lunar_standard / rank_compare: 2 of 3 approved
- mixed: lunar_standard / trap_limit: 1 of 3 approved
- mixed: user_o2_15_psi_14 / edge_empty: 2 of 3 approved
- mixed: user_o2_15_psi_14 / edge_injection: 2 of 3 approved
- mixed: user_o2_15_psi_14 / edge_markup: 2 of 3 approved
- mixed: user_o2_15_psi_14 / edge_portuguese: 2 of 3 approved
- mixed: user_o2_15_psi_14 / edge_single_char: 2 of 3 approved
- mixed: user_o2_15_psi_14 / lim_extrapolate: 1 of 3 approved
- mixed: user_o2_15_psi_14 / lim_safe: 2 of 3 approved
- mixed: user_o2_15_psi_14 / rag_droplet: 1 of 3 approved
- mixed: user_o2_15_psi_14 / rag_extinction: 1 of 3 approved
- mixed: user_o2_15_psi_14 / rank_criterion: 2 of 3 approved
- mixed: user_o2_15_psi_14 / trap_limit: 1 of 3 approved
- mixed: user_o2_38078 / edge_injection: 2 of 3 approved
- mixed: user_o2_38078 / edge_long: 2 of 3 approved
- mixed: user_o2_38078 / edge_markup: 2 of 3 approved
- mixed: user_o2_38078 / lim_gravity: 2 of 3 approved
- mixed: user_o2_38078 / lim_safe: 2 of 3 approved
- mixed: user_o2_38078 / meta_pillars: 1 of 3 approved
- mixed: user_o2_38078 / rag_burner: 2 of 3 approved
- mixed: user_o2_38078 / rag_droplet: 2 of 3 approved
- mixed: user_o2_38078 / rag_flame_spread: 2 of 3 approved
- mixed: user_o2_38078 / rank_criterion: 1 of 3 approved
- mixed: user_o2_38078 / rec_closest: 2 of 3 approved
- mixed: user_o2_38078 / tech: 2 of 3 approved
- mixed: user_o2_38078 / trap_exact: 2 of 3 approved

## Claim-level versus answer-level failure (first attempt)

Drafts: 278; mean claims per draft 4.7; claims with an issue 172 of 1299 (per-claim failure rate 0.13).
Answers with at least one failing claim: 0.41. If claims failed independently at that rate, the expected answer failure would be 0.49.
Runs that needed a second attempt: 115; of those approved after the retry: 41 (0.36).

## Numbers behind `undeclared_number` (final rejection of each run)

| Explanation | Count |
|---|---|
| not a known fact (model-stated) | 38 |
| value of an uncited record of a cited investigation | 38 |
| system fact of an UNCITED investigation | 32 |
| page number from a citation locator | 1 |

Most frequent values:

- 21: 15
- 10: 15
- 40: 11
- 33: 10
- 4.1: 5
- 1: 5
- 20: 4
- 0.4: 4
- 21291: 3
- 2: 3
- 3: 3
- 0.25: 3

Examples (number | explanation | sentence):

- 21 | system fact of an UNCITED investigation | The FLEX investigation provides relevant data on droplet burning rate constants at oxygen concentrations close to the lunar base scenario's 30% ambient oxygen and pressure near 10.4 psi. It shows that the burning rate constant for
- 10 | not a known fact (model-stated) | The FLEX-2 investigation includes droplet burning rate measurements over a range of oxygen concentrations including the lunar base scenario's 30% ambient oxygen and pressure near 10 psi. It notes that burning rate constants vary w
- 33 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation provides combustion data at oxygen concentrations slightly higher than the lunar base scenario (around 33-34% oxygen) and at pressures somewhat lower than the scenario (around 7.3 psi), making it somew
- 20 | value of an uncited record of a cited investigation | The BASS-II investigation is relevant for solid fuel combustion in microgravity and shows that flame spread was observed at oxygen concentrations as low as 17.5%, indicating that oxygen levels below 20% may reduce flammability ris
- 40 | not a known fact (model-stated) | The FLEX-2 investigation covers a wide range of oxygen mole fractions from 10% to 40% and pressures including the lunar base scenario, focusing on liquid fuel combustion and burning characteristics, making it relevant for understa
- 18 | value of an uncited record of a cited investigation | Based on the BASS-II investigation, a safe oxygen limit to reduce flame spread risk in a habitat environment is likely below about 18%, as flame spread was not observed below this oxygen concentration in microgravity tests.
- 4.1 | value of an uncited record of a cited investigation | FLEX is ranked above ACME-CFI-G primarily because it has a higher overall score (0.735 vs. 0.7) despite ACME-CFI-G having perfect oxygen and pressure proximity scores. FLEX's score benefits from a high data richness value (0.982) 
- 15.9 | value of an uncited record of a cited investigation | The BASS-II investigation is relevant for solid fuel combustion and fire safety in habitats but has low oxygen proximity due to scenario oxygen being about 15.9% away from the nearest test, and no pressure data for ambient conditi
- 21291 | not a known fact (model-stated) | The ACME-CFI-G investigation includes tests closest to the scenario oxygen concentration of 38.078% at approximately 14.7 psi pressure, with test points such as 21291 J3 having an oxygen concentration of 38.0783875% and pressure o
- 2 | system fact of an UNCITED investigation | The CFI investigation provides data on cool flame and hot flame combustion of liquid fuels such as n-dodecane at pressures near atmospheric and below 2 atm, but its oxygen concentrations are significantly lower than the habitat sc
- 3 | system fact of an UNCITED investigation | The ACME-CFI-G investigation studied inverse flames with oxygen/nitrogen mixtures at pressures near 3 atm and oxygen concentrations close to 38%, providing insights into flame size and extinction behavior under controlled oxidizer
- 10 | value of an uncited record of a cited investigation | FLEX investigation includes 274 individual tests with verified lineage, mostly using methanol and heptane fuels at oxygen concentrations close to 15% ambient and pressures near 10 to 14.5 psi, relevant to habitat fire safety.
- 0.4 | not a known fact (model-stated) | The FLEX-2 investigation tested oxygen mole fractions from 0.1 to 0.4 (10 to 40 percent) and pressures ranging from about 7.35 psi to 44 psi, encompassing the habitat scenario's oxygen and pressure conditions.
- 7 | not a known fact (model-stated) | The FLEX-2 investigation includes studies of flame extinction diameters and burning rates for various fuels at pressures ranging from about 7 to 44 psi and oxygen concentrations from 17% to 30%, covering and extending beyond the h
- 2.5 | not a known fact (model-stated) | The FLEX-2 investigation studied droplet combustion at oxygen mole fractions near 15% and pressures around 2.5 psi (190 mmHg), showing that single droplets can burn to completion under these low oxygen and pressure conditions, whi
- 13 | value of an uncited record of a cited investigation | The FLEX investigation includes tests at oxygen concentrations from 13% to 21% ambient and pressures near 1 atm, which is close to the habitat scenario of 15% oxygen at 14 psi, indicating relevant data within the tested range.
- 1 | system fact of an UNCITED investigation | The CFI investigation includes droplet combustion tests at pressures near 1 atm and oxygen concentrations above the habitat scenario, indicating partial but not exact coverage of the habitat oxygen and pressure conditions.
- 44 | system fact of an UNCITED investigation | The ACME-CFI-G investigation tests combustion at pressures near 3 atm (approximately 44 psi) and oxygen concentrations higher than the habitat scenario, thus less directly relevant for the 15% oxygen and 14 psi pressure habitat co
- 3.2 | value of an uncited record of a cited investigation | FLEX achieves perfect oxygen and pressure proximity scores of 1.0 each, indicating that the scenario's oxygen concentration of 30% ambient and pressure of 10.2 psi are inside the tested ranges, whereas ACME-CFI-G has lower oxygen 
- 2.2 | value of an uncited record of a cited investigation | FLEX achieves perfect oxygen and pressure proximity scores of 1.0 each, indicating that the scenario's oxygen concentration of 30% ambient and pressure of 10.2 psi are inside the tested ranges, whereas ACME-CFI-G has lower oxygen 
- 10.4 | value of an uncited record of a cited investigation | The investigation FLEX is relevant to a habitat scenario with oxygen concentration near 38% ambient and pressure near 14.7 psi, as it includes tests with oxygen concentrations close to 34% ambient and pressures near 10.4 psi, and 
- 4 | system fact of an UNCITED investigation | The CFI investigation used hardware including a color camera with live downlink to the Telescience Support Center for process monitoring, and narrow-band and wide-band radiometers to measure radiation emission from flames. The exp
- 30 | system fact of an UNCITED investigation | The ACME-CFI-G investigation tested gaseous fuels at elevated oxygen concentrations between 30% and 40% ambient and pressures around 0.5 to 2 atm, which are higher than typical habitat conditions.
- 40 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation tested gaseous fuels at elevated oxygen concentrations between 30% and 40% ambient and pressures around 0.5 to 2 atm, which are higher than typical habitat conditions.
- 0.5 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation tested gaseous fuels at elevated oxygen concentrations between 30% and 40% ambient and pressures around 0.5 to 2 atm, which are higher than typical habitat conditions.
- 17 | system fact of an UNCITED investigation | The curated PSI data contains no technology recommendations for safe oxygen limits; however, the cited investigations show that combustion behavior changes significantly below about 17-19% oxygen at pressures near 14.7 psi, which 
- 19 | value of an uncited record of a cited investigation | The curated PSI data contains no technology recommendations for safe oxygen limits; however, the cited investigations show that combustion behavior changes significantly below about 17-19% oxygen at pressures near 14.7 psi, which 
- 14.7 | value of an uncited record of a cited investigation | The curated PSI data contains no technology recommendations for safe oxygen limits; however, the cited investigations show that combustion behavior changes significantly below about 17-19% oxygen at pressures near 14.7 psi, which 
- 17.5 | value of an uncited record of a cited investigation | The BASS-II investigation studied flame spread over solid fuels at oxygen concentrations down to about 17.5%, showing that flame spread can occur at oxygen levels near and below the lunar base scenario's 30% oxygen, with micrograv
- 39 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation studied cool flame combustion of gaseous fuels at pressures around 3 atm and oxygen concentrations near 39%, which is higher than the lunar base oxygen level. It provides insights into the effects of o

## Retrieved passages for the regions you asked about

**lunar_standard / rank_default** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- ACME-CFI-G p. 14: analysis of the chamber atmosphere, e.g., for oxygen, nitrogen, carbon dioxide, carbon monoxide, and fuel gase
- ACME-CFI-G p. 78: runs. The CIR includes an optics bench, combustion chamber, fuel, and oxidizer control, and five different cam

**lunar_standard / rag_flame_spread** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2, BASS)
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

**user_o2_38078 / rag_droplet** (approved; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI)
- FLEX p. 7: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 64: ACME/CFI-G Final Report (2022) 21 November 2022 64 Figure 1. CFI-G Inverse Flames at Increasing Oxidizer Flow 
- ACME-CFI-G p. 10: subsequently removed, leaving only three fibers in the final testing for the BRE and Coflow Laminar Diffusion 

**user_o2_38078 / rag_co2** (approved; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 62: ACME/CFI-G Final Report (2022) 21 November 2022 62 varying the concentration ratios of the oxygen/nitrogen mix
- ACME-CFI-G p. 51: Gases) with 14 ethane flames, sometimes diluted with nitrog en, ignited in various oxygen/nitrogen atmospheres

**user_o2_15_psi_14 / rank_default** (approved; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2)
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

**user_o2_15_psi_14 / rag_co2** (insufficient_evidence; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 11: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- BASS-II p. 87: NASA/TM-20210011385 79 6.1.4.6 Gas Sensor Results The initial and final O2, CO2, and CO readings were recorded
- BASS-II p. 18: NASA/TM-20210011385 10 Figure 1.7.—O2 consumed, CO2 and CO generated per gram of fuel mass loss for two differ

