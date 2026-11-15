# RAG stress report

Narrator: **Language model (openai:gpt-4.1-mini)**. Runs: 93. Hard failures: **4**. Warnings: 0.

## Per scenario

| Scenario | Runs | Approved | Insufficient | Avg passages | Avg seconds |
|---|---|---|---|---|---|
| lunar_standard (30% / 10.2 psi) | 31 | 12 | 19 | 10.0 | 16.73 |
| user_o2_38078 (38.078% / 14.7 psi) | 31 | 14 | 17 | 10.0 | 12.90 |
| user_o2_15_psi_14 (15% / 14 psi) | 31 | 10 | 21 | 10.0 | 26.25 |

## Per question (retrieval relevance proxy)

| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |
|---|---|---|---|---|---|
| rank_default | ranking | 3 | 10.0 | n/a | 2 |
| rank_compare | ranking | 3 | 10.0 | n/a | 3 |
| rank_criterion | ranking | 3 | 10.0 | n/a | 3 |
| rec_ranges | records | 3 | 10.0 | 0.83 | 2 |
| rec_closest | records | 3 | 10.0 | n/a | 1 |
| rec_lowest_psi | records | 3 | 10.0 | 0.73 | 2 |
| rag_flame_spread | passages | 3 | 10.0 | 0.97 | 3 |
| rag_extinction | passages | 3 | 10.0 | 1.00 | 2 |
| rag_burner | passages | 3 | 10.0 | 0.37 | 1 |
| rag_droplet | passages | 3 | 10.0 | 0.87 | 3 |
| rag_co2 | passages | 3 | 10.0 | 0.77 | 3 |
| meta_pillars | metadata | 3 | 10.0 | n/a | 1 |
| meta_hardware | metadata | 3 | 10.0 | 0.63 | 3 |
| lim_safe | limits | 3 | 10.0 | n/a | 2 |
| lim_gravity | limits | 3 | 10.0 | n/a | 2 |
| lim_extrapolate | limits | 3 | 10.0 | n/a | 0 |
| tech | scope | 3 | 10.0 | n/a | 2 |
| out_of_scope | scope | 3 | 10.0 | n/a | 1 |
| trap_exact | trap | 3 | 10.0 | n/a | 3 |
| trap_limit | trap | 3 | 10.0 | n/a | 2 |
| edge_empty | edge | 3 | 10.0 | n/a | 0 |
| edge_spaces | edge | 3 | 10.0 | n/a | 2 |
| edge_single_char | edge | 3 | 10.0 | n/a | 1 |
| edge_numbers_only | edge | 3 | 10.0 | n/a | 2 |
| edge_portuguese | edge | 3 | 10.0 | n/a | 2 |
| edge_unicode | edge | 3 | 10.0 | n/a | 2 |
| edge_markup | edge | 3 | 10.0 | n/a | 1 |
| edge_sql | edge | 3 | 10.0 | n/a | 1 |
| edge_unknown_study | edge | 3 | 10.0 | n/a | 2 |
| edge_injection | edge | 3 | 10.0 | n/a | 1 |
| edge_long | edge | 3 | 10.0 | n/a | 2 |

## Hard failures

- lunar_standard: the ranking changed with the question (must depend on the scenario only)
- user_o2_38078: the ranking changed with the question (must depend on the scenario only)
- user_o2_15_psi_14: the ranking changed with the question (must depend on the scenario only)
- user_o2_38078: ranking is not deterministic

## Warnings

None.

## Validator issue codes seen (scenario, codes)

- lunar_standard: malformed_citation
- lunar_standard: malformed_citation,number_mismatch,undeclared_number
- lunar_standard: number_mismatch,undeclared_number,unknown_citation
- lunar_standard: quote_mismatch
- lunar_standard: quote_mismatch,undeclared_number
- lunar_standard: quote_mismatch,undeclared_number,unknown_citation
- lunar_standard: undeclared_number
- lunar_standard: undeclared_number,unknown_citation
- user_o2_15_psi_14: missing_citation,number_mismatch,quote_mismatch,undeclared_number
- user_o2_15_psi_14: number_mismatch
- user_o2_15_psi_14: number_mismatch,quote_mismatch
- user_o2_15_psi_14: number_mismatch,quote_mismatch,undeclared_number
- user_o2_15_psi_14: number_mismatch,quote_mismatch,undeclared_number,unknown_citation
- user_o2_15_psi_14: number_mismatch,undeclared_number
- user_o2_15_psi_14: number_mismatch,undeclared_number,unknown_citation
- user_o2_15_psi_14: number_mismatch,unknown_citation
- user_o2_15_psi_14: quote_mismatch
- user_o2_15_psi_14: quote_mismatch,undeclared_number
- user_o2_15_psi_14: undeclared_number,unknown_citation
- user_o2_15_psi_14: unknown_citation
- user_o2_38078: malformed_citation,number_mismatch,unknown_citation
- user_o2_38078: missing_citation
- user_o2_38078: number_mismatch
- user_o2_38078: number_mismatch,quote_mismatch,undeclared_number
- user_o2_38078: number_mismatch,undeclared_number
- user_o2_38078: number_mismatch,undeclared_number,unknown_citation
- user_o2_38078: quote_mismatch
- user_o2_38078: quote_mismatch,undeclared_number
- user_o2_38078: undeclared_number
- user_o2_38078: undeclared_number,unknown_citation
- user_o2_38078: unknown_citation

## Retrieved passages for the regions you asked about

**lunar_standard / rank_default** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2)
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

**user_o2_38078 / rank_default** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI, SAME-R)
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

**user_o2_15_psi_14 / rank_default** (insufficient_evidence; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2, BASS)
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
