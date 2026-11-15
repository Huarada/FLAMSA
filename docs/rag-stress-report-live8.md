# RAG stress report

Narrator: **Language model (openai:gpt-4.1-mini)**. Runs: 279. Hard failures: **0**. Warnings: 0.

## Per scenario

| Scenario | Runs | Approved (full) | Partial | Insufficient | Avg passages | Avg seconds |
|---|---|---|---|---|---|---|
| lunar_standard (30% / 10.2 psi) | 93 | 72 | 19 | 2 | 10.0 | 10.63 |
| user_o2_38078 (38.078% / 14.7 psi) | 93 | 72 | 18 | 3 | 10.0 | 7.85 |
| user_o2_15_psi_14 (15% / 14 psi) | 93 | 61 | 25 | 7 | 10.0 | 16.12 |

## Per question (retrieval relevance proxy)

| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |
|---|---|---|---|---|---|
| rank_default | ranking | 9 | 10.0 | n/a | 0 |
| rank_compare | ranking | 9 | 10.0 | n/a | 1 |
| rank_criterion | ranking | 9 | 10.0 | n/a | 0 |
| rec_ranges | records | 9 | 10.0 | 0.83 | 1 |
| rec_closest | records | 9 | 10.0 | n/a | 0 |
| rec_lowest_psi | records | 9 | 10.0 | 0.73 | 0 |
| rag_flame_spread | passages | 9 | 10.0 | 0.97 | 2 |
| rag_extinction | passages | 9 | 10.0 | 1.00 | 0 |
| rag_burner | passages | 9 | 10.0 | 0.37 | 3 |
| rag_droplet | passages | 9 | 10.0 | 0.87 | 2 |
| rag_co2 | passages | 9 | 10.0 | 0.77 | 0 |
| meta_pillars | metadata | 9 | 10.0 | n/a | 0 |
| meta_hardware | metadata | 9 | 10.0 | 0.63 | 1 |
| lim_safe | limits | 9 | 10.0 | n/a | 0 |
| lim_gravity | limits | 9 | 10.0 | n/a | 0 |
| lim_extrapolate | limits | 9 | 10.0 | n/a | 0 |
| tech | scope | 9 | 10.0 | n/a | 0 |
| out_of_scope | scope | 9 | 10.0 | n/a | 0 |
| trap_exact | trap | 9 | 10.0 | n/a | 2 |
| trap_limit | trap | 9 | 10.0 | n/a | 0 |
| edge_empty | edge | 9 | 10.0 | n/a | 0 |
| edge_spaces | edge | 9 | 10.0 | n/a | 0 |
| edge_single_char | edge | 9 | 10.0 | n/a | 0 |
| edge_numbers_only | edge | 9 | 10.0 | n/a | 0 |
| edge_portuguese | edge | 9 | 10.0 | n/a | 0 |
| edge_unicode | edge | 9 | 10.0 | n/a | 0 |
| edge_markup | edge | 9 | 10.0 | n/a | 0 |
| edge_sql | edge | 9 | 10.0 | n/a | 0 |
| edge_unknown_study | edge | 9 | 10.0 | n/a | 0 |
| edge_injection | edge | 9 | 10.0 | n/a | 0 |
| edge_long | edge | 9 | 10.0 | n/a | 0 |

## Hard failures

None.

## Warnings

None.

## Validator issue codes in rejected runs (runs affected)

- undeclared_number: 49
- quote_mismatch: 21
- unknown_citation: 18
- number_mismatch: 15
- missing_citation: 4
- malformed_citation: 1

## Rejected runs (scenario / question: codes)

- lunar_standard / rag_droplet: quote_mismatch, undeclared_number, unknown_citation
- user_o2_38078 / rag_burner: unknown_citation
- user_o2_15_psi_14 / rag_flame_spread: undeclared_number, unknown_citation
- user_o2_15_psi_14 / trap_exact: undeclared_number
- lunar_standard / rag_droplet: quote_mismatch, undeclared_number, unknown_citation
- user_o2_38078 / rag_burner: unknown_citation
- user_o2_15_psi_14 / rec_ranges: number_mismatch, quote_mismatch, undeclared_number
- user_o2_15_psi_14 / rag_flame_spread: quote_mismatch, unknown_citation
- user_o2_15_psi_14 / rag_burner: unknown_citation
- user_o2_38078 / rank_compare: undeclared_number
- user_o2_15_psi_14 / meta_hardware: quote_mismatch, unknown_citation
- user_o2_15_psi_14 / trap_exact: quote_mismatch

## Variance across repeated rounds

Answered (full or partial) per round: [89, 88, 90] (mean 89.0, std 0.8).

Cells always approved: 85; never approved: 0; mixed (same input, different outcome): 8.

- mixed: lunar_standard / rag_droplet: 1 of 3 answered
- mixed: user_o2_15_psi_14 / meta_hardware: 2 of 3 answered
- mixed: user_o2_15_psi_14 / rag_burner: 2 of 3 answered
- mixed: user_o2_15_psi_14 / rag_flame_spread: 1 of 3 answered
- mixed: user_o2_15_psi_14 / rec_ranges: 2 of 3 answered
- mixed: user_o2_15_psi_14 / trap_exact: 1 of 3 answered
- mixed: user_o2_38078 / rag_burner: 1 of 3 answered
- mixed: user_o2_38078 / rank_compare: 2 of 3 answered

## Claim-level versus answer-level failure (first attempt)

Drafts: 277; mean claims per draft 4.7; claims with an issue 157 of 1311 (per-claim failure rate 0.12).
Answers with at least one failing claim: 0.40. If claims failed independently at that rate, the expected answer failure would be 0.45.
Runs that needed a second attempt: 113; of those approved after the retry: 101 (0.89).

## Numbers behind `undeclared_number` (final rejection of each run)

| Explanation | Count |
|---|---|
| not a known fact (model-stated) | 47 |
| value of an uncited record of a cited investigation | 29 |
| system fact of an UNCITED investigation | 23 |

Most frequent values:

- 10: 18
- 40: 14
- 21: 12
- 0.25: 6
- 33: 5
- 20: 4
- 4.1: 3
- 21291: 3
- 0.5: 3
- 5: 3
- 0.4: 3
- 44: 2

Examples (number | explanation | sentence):

- 10 | not a known fact (model-stated) | The FLEX-2 investigation includes droplet burning tests over a range of oxygen concentrations including the scenario oxygen level of 30% ambient and pressures near 10 psi. It shows that the burning rate constant is affected by oxy
- 33 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation provides combustion data at oxygen concentrations somewhat higher than the lunar base scenario's 30%, with tests around 33-34% oxygen at pressures near 7.3 psi, which is lower than the scenario pressur
- 40 | not a known fact (model-stated) | The FLEX-2 investigation covers a broad range of oxygen mole fractions from 10% to 40% and pressures including the lunar base scenario's 10.2 psi, making it relevant for understanding combustion limits and behavior at the scenario
- 21 | system fact of an UNCITED investigation | The BASS investigation focuses on solid fuel combustion and fire safety in spacecraft habitats, with testing restricted to oxygen concentrations at or above 21%, thus relevant for habitat fire safety but not providing a specific s
- 4.1 | value of an uncited record of a cited investigation | Although ACME-CFI-G has perfect oxygen and pressure proximity scores of 1.0, FLEX's oxygen proximity is slightly lower at 0.796 due to the scenario oxygen being 4.1% away from the nearest test, but FLEX's perfect pressure proximit
- 21291 | not a known fact (model-stated) | The ACME-CFI-G investigation includes tests very close to the scenario oxygen concentration of 38.078% at near atmospheric pressure, with test points such as 21291 J3 having an oxygen concentration of 38.0783875% and pressure near
- 0.25 | not a known fact (model-stated) | The CFI investigation studies droplet combustion and cool flame behavior at pressures ranging from 0.25 atm to 5 atm and oxygen concentrations lower than the scenario's 38.078%. It provides fundamental combustion data but no habit
- 20 | value of an uncited record of a cited investigation | The FLEX investigation provides burning rate constants for methanol droplets at oxygen concentrations near 20% and pressures near 1 atm, but does not include data at 33.3% oxygen; thus it is less directly relevant for exact burnin
- 10 | value of an uncited record of a cited investigation | FLEX investigation includes 274 individual tests with verified lineage, mostly using methanol and heptane fuels at oxygen percentages close to 15% and pressures near 10 to 14.5 psi, relevant to habitat fire safety scenarios.
- 14.7 | value of an uncited record of a cited investigation | ACME-CFI-G investigation has a score of 0.651 and includes tests at pressures near 14.7 psi and oxygen percentages somewhat higher than 15%, but with no shared fire-safety pillars and no solid fuel tests, making it less directly a
- 17.5 | value of an uncited record of a cited investigation | The BASS-II investigation tested solid fuels at ambient oxygen concentrations including 15% and 17.5%, but did not report pressure values, so it is relevant for oxygen conditions but lacks pressure data for the habitat scenario.
- 3.7 | not a known fact (model-stated) | The FLEX-2 investigation tested oxygen mole fractions from 0.1 to 0.4 (10% to 40%) and pressures from about 0.25 atm to over 1 atm, including tests at 0.15 oxygen mole fraction and 190 mmHg (about 3.7 psi), covering a broad range 
- 44 | system fact of an UNCITED investigation | The ACME-CFI-G investigation examined inverse flames in a combustion chamber with burner oxygen flow and chamber atmospheres, varying oxidizer flow rate and oxygen concentration at pressures around 3 atm (approximately 44 psi), wh
- 0.5 | not a known fact (model-stated) | The CFI investigation used hardware including a combustion chamber with droplet fuel and igniters, color cameras with live downlink, narrow-band and wide-band radiometers to measure flame radiation, and other diagnostic equipment.
- 140 | value of an uncited record of a cited investigation | The FLEX investigation provides methanol droplet combustion burning rate constants at oxygen concentrations close to 15% ambient, but at pressures near 10.3 psi, which is somewhat lower than the scenario pressure of 14 psi. The bu
- 141 | value of an uncited record of a cited investigation | The FLEX investigation provides methanol droplet combustion burning rate constants at oxygen concentrations close to 15% ambient, but at pressures near 10.3 psi, which is somewhat lower than the scenario pressure of 14 psi. The bu
- 142 | not a known fact (model-stated) | The FLEX investigation provides methanol droplet combustion burning rate constants at oxygen concentrations close to 15% ambient, but at pressures near 10.3 psi, which is somewhat lower than the scenario pressure of 14 psi. The bu
- 40 | value of an uncited record of a cited investigation | The FLEX investigation includes methanol droplet combustion tests at 15% oxygen and about 10.3 psi pressure, with burning rate constants reported, but no tests at 33.3% oxygen are present. The BASS-II investigation includes solid 
- 2.5 | not a known fact (model-stated) | The FLEX-2 investigation includes droplet combustion tests at oxygen mole fractions close to 15% and pressures lower than the habitat scenario, around 2.5 psi (190 mmHg). It studies droplet interactions and extinction limits in mi
- 5 | system fact of an UNCITED investigation | The CFI investigation provides data on cool flame combustion behavior of liquid fuels at pressures ranging from 0.25 atm to 5 atm, which includes the scenario pressure of 14 psi (approximately 0.95 atm). It includes oxygen concent
- 3.2 | value of an uncited record of a cited investigation | FLEX matches the scenario oxygen concentration perfectly with a value of 1.0 for oxygen proximity, while ACME-CFI-G has a lower oxygen proximity value of 0.838 due to the scenario oxygen being 3.2 percent away from the nearest tes
- 2.2 | value of an uncited record of a cited investigation | FLEX also has a perfect pressure proximity score of 1.0 because the scenario pressure is essentially zero away from the nearest test, whereas ACME-CFI-G has a pressure proximity of 0.85 due to the scenario pressure being 2.2 psi a
- 0.4 | not a known fact (model-stated) | The FLEX-2 investigation covers oxygen mole fractions from 0.1 to 0.4 ambient, including the lunar base scenario oxygen concentration, and studies burning rate, extinction diameter, and flame characteristics as functions of oxygen
- 9 | not a known fact (model-stated) | The CFI investigation tests liquid fuel combustion at oxygen concentrations and pressures somewhat different from the lunar base scenario, with oxygen concentration about 9% lower and pressure about 0.8 psi higher than the scenari
- 0.8 | system fact of an UNCITED investigation | The CFI investigation tests liquid fuel combustion at oxygen concentrations and pressures somewhat different from the lunar base scenario, with oxygen concentration about 9% lower and pressure about 0.8 psi higher than the scenari
- 0.25 | system fact of an UNCITED investigation | The CFI investigation studies cool flame combustion of n-dodecane and mixtures over pressures from 0.25 atm to 5 atm and oxygen concentrations including 21%, but the scenario oxygen of 30% and pressure of about 10.2 psi (about 0.7
- 0.7 | not a known fact (model-stated) | The CFI investigation studies cool flame combustion of n-dodecane and mixtures over pressures from 0.25 atm to 5 atm and oxygen concentrations including 21%, but the scenario oxygen of 30% and pressure of about 10.2 psi (about 0.7
- 83 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation used the Microgravity Science Glovebox (MSG) facility aboard the ISS. It employed three Photomultiplier Tube (PMT) modules for detection. The experiments were conducted in a chamber with a free volume 
- 90 | value of an uncited record of a cited investigation | The ACME-CFI-G investigation used the Microgravity Science Glovebox (MSG) facility aboard the ISS. It employed three Photomultiplier Tube (PMT) modules for detection. The experiments were conducted in a chamber with a free volume 
- 0.44 | value of an uncited record of a cited investigation | The curated PSI data contains no direct test point reporting the exact burning rate at 33.3% oxygen. However, the FLEX investigation includes methanol droplet combustion tests at oxygen concentrations close to 34% ambient and pres

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

**lunar_standard / rag_co2** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 11: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 62: ACME/CFI-G Final Report (2022) 21 November 2022 62 varying the concentration ratios of the oxygen/nitrogen mix
- ACME-CFI-G p. 66: ACME/CFI-G Final Report (2022) 21 November 2022 66 fuel was diluted with nitrogen. The other test parameters i

**user_o2_38078 / rank_default** (approved; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI)
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 14: analysis of the chamber atmosphere, e.g., for oxygen, nitrogen, carbon dioxide, carbon monoxide, and fuel gase
- ACME-CFI-G p. 78: runs. The CIR includes an optics bench, combustion chamber, fuel, and oxidizer control, and five different cam

**user_o2_38078 / rag_flame_spread** (approved; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI)
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

**user_o2_15_psi_14 / rag_droplet** (approved; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2)
- FLEX p. 7: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- BASS-II p. 40: quasi-steady (while the flame spread rate is constant, the flame shape may evolve in an unsteady manner), quas
- BASS-II p. 138: NASA/TM-20210011385 130 17. Chan, Ryan Lesley: Effect of Oxygen Concentration on Flame Spread Over Thin Fuels 

**user_o2_15_psi_14 / rag_co2** (approved; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 11: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- BASS-II p. 87: NASA/TM-20210011385 79 6.1.4.6 Gas Sensor Results The initial and final O2, CO2, and CO readings were recorded
- BASS-II p. 18: NASA/TM-20210011385 10 Figure 1.7.—O2 consumed, CO2 and CO generated per gram of fuel mass loss for two differ

