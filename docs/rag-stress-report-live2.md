# RAG stress report

Narrator: **Language model (openai:gpt-4.1-mini)**. Runs: 93. Hard failures: **0**. Warnings: 0.

## Per scenario

| Scenario | Runs | Approved | Insufficient | Avg passages | Avg seconds |
|---|---|---|---|---|---|
| lunar_standard (30% / 10.2 psi) | 31 | 10 | 21 | 10.0 | 16.85 |
| user_o2_38078 (38.078% / 14.7 psi) | 31 | 12 | 19 | 10.0 | 28.32 |
| user_o2_15_psi_14 (15% / 14 psi) | 31 | 13 | 18 | 10.0 | 14.44 |

## Per question (retrieval relevance proxy)

| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |
|---|---|---|---|---|---|
| rank_default | ranking | 3 | 10.0 | n/a | 2 |
| rank_compare | ranking | 3 | 10.0 | n/a | 3 |
| rank_criterion | ranking | 3 | 10.0 | n/a | 3 |
| rec_ranges | records | 3 | 10.0 | 0.83 | 3 |
| rec_closest | records | 3 | 10.0 | n/a | 2 |
| rec_lowest_psi | records | 3 | 10.0 | 0.73 | 1 |
| rag_flame_spread | passages | 3 | 10.0 | 0.97 | 2 |
| rag_extinction | passages | 3 | 10.0 | 1.00 | 3 |
| rag_burner | passages | 3 | 10.0 | 0.37 | 1 |
| rag_droplet | passages | 3 | 10.0 | 0.87 | 2 |
| rag_co2 | passages | 3 | 10.0 | 0.77 | 2 |
| meta_pillars | metadata | 3 | 10.0 | n/a | 0 |
| meta_hardware | metadata | 3 | 10.0 | 0.63 | 3 |
| lim_safe | limits | 3 | 10.0 | n/a | 2 |
| lim_gravity | limits | 3 | 10.0 | n/a | 1 |
| lim_extrapolate | limits | 3 | 10.0 | n/a | 2 |
| tech | scope | 3 | 10.0 | n/a | 1 |
| out_of_scope | scope | 3 | 10.0 | n/a | 1 |
| trap_exact | trap | 3 | 10.0 | n/a | 3 |
| trap_limit | trap | 3 | 10.0 | n/a | 2 |
| edge_empty | edge | 3 | 10.0 | n/a | 1 |
| edge_spaces | edge | 3 | 10.0 | n/a | 2 |
| edge_single_char | edge | 3 | 10.0 | n/a | 3 |
| edge_numbers_only | edge | 3 | 10.0 | n/a | 1 |
| edge_portuguese | edge | 3 | 10.0 | n/a | 3 |
| edge_unicode | edge | 3 | 10.0 | n/a | 1 |
| edge_markup | edge | 3 | 10.0 | n/a | 1 |
| edge_sql | edge | 3 | 10.0 | n/a | 2 |
| edge_unknown_study | edge | 3 | 10.0 | n/a | 1 |
| edge_injection | edge | 3 | 10.0 | n/a | 2 |
| edge_long | edge | 3 | 10.0 | n/a | 2 |

## Hard failures

None.

## Warnings

None.

## Validator issue codes in rejected runs (runs affected)

- undeclared_number: 48
- unknown_citation: 14
- quote_mismatch: 12
- number_mismatch: 10
- malformed_citation: 5
- empty_draft: 1

## Rejected runs (scenario / question: codes)

- lunar_standard / rank_default: undeclared_number
- lunar_standard / rank_compare: malformed_citation, undeclared_number
- lunar_standard / rank_criterion: malformed_citation
- lunar_standard / rec_ranges: number_mismatch, undeclared_number
- lunar_standard / rec_lowest_psi: undeclared_number
- lunar_standard / rag_flame_spread: undeclared_number
- lunar_standard / rag_extinction: quote_mismatch, undeclared_number
- lunar_standard / rag_droplet: quote_mismatch, undeclared_number
- lunar_standard / meta_hardware: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / lim_safe: undeclared_number
- lunar_standard / lim_extrapolate: undeclared_number
- lunar_standard / trap_exact: number_mismatch, unknown_citation
- lunar_standard / trap_limit: undeclared_number
- lunar_standard / edge_empty: undeclared_number, unknown_citation
- lunar_standard / edge_spaces: unknown_citation
- lunar_standard / edge_single_char: undeclared_number
- lunar_standard / edge_portuguese: undeclared_number
- lunar_standard / edge_sql: quote_mismatch, undeclared_number, unknown_citation
- lunar_standard / edge_unknown_study: undeclared_number
- lunar_standard / edge_injection: undeclared_number
- lunar_standard / edge_long: quote_mismatch
- user_o2_38078 / rank_default: undeclared_number
- user_o2_38078 / rank_compare: malformed_citation, undeclared_number
- user_o2_38078 / rank_criterion: number_mismatch, undeclared_number
- user_o2_38078 / rec_ranges: number_mismatch, undeclared_number
- user_o2_38078 / rec_closest: undeclared_number
- user_o2_38078 / rag_extinction: unknown_citation
- user_o2_38078 / rag_droplet: number_mismatch, undeclared_number
- user_o2_38078 / rag_co2: quote_mismatch, undeclared_number
- user_o2_38078 / meta_hardware: number_mismatch, quote_mismatch, undeclared_number
- user_o2_38078 / lim_safe: undeclared_number
- user_o2_38078 / tech: undeclared_number
- user_o2_38078 / out_of_scope: undeclared_number
- user_o2_38078 / trap_exact: undeclared_number
- user_o2_38078 / edge_single_char: undeclared_number
- user_o2_38078 / edge_portuguese: undeclared_number, unknown_citation
- user_o2_38078 / edge_markup: undeclared_number
- user_o2_38078 / edge_sql: undeclared_number
- user_o2_38078 / edge_injection: undeclared_number
- user_o2_38078 / edge_long: empty_draft
- user_o2_15_psi_14 / rank_compare: malformed_citation, undeclared_number
- user_o2_15_psi_14 / rank_criterion: malformed_citation, unknown_citation
- user_o2_15_psi_14 / rec_ranges: undeclared_number
- user_o2_15_psi_14 / rec_closest: undeclared_number
- user_o2_15_psi_14 / rag_flame_spread: quote_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / rag_extinction: unknown_citation
- user_o2_15_psi_14 / rag_burner: undeclared_number
- user_o2_15_psi_14 / rag_co2: number_mismatch, quote_mismatch
- user_o2_15_psi_14 / meta_hardware: quote_mismatch, undeclared_number
- user_o2_15_psi_14 / lim_gravity: undeclared_number
- user_o2_15_psi_14 / lim_extrapolate: undeclared_number, unknown_citation
- user_o2_15_psi_14 / trap_exact: number_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / trap_limit: undeclared_number
- user_o2_15_psi_14 / edge_spaces: number_mismatch, undeclared_number
- user_o2_15_psi_14 / edge_single_char: undeclared_number
- user_o2_15_psi_14 / edge_numbers_only: quote_mismatch, undeclared_number, unknown_citation
- user_o2_15_psi_14 / edge_portuguese: number_mismatch, quote_mismatch, unknown_citation
- user_o2_15_psi_14 / edge_unicode: undeclared_number

## Retrieved passages for the regions you asked about

**lunar_standard / rank_default** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2, BASS)
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

**lunar_standard / rag_co2** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 11: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 62: ACME/CFI-G Final Report (2022) 21 November 2022 62 varying the concentration ratios of the oxygen/nitrogen mix
- ACME-CFI-G p. 66: ACME/CFI-G Final Report (2022) 21 November 2022 66 fuel was diluted with nitrogen. The other test parameters i

**user_o2_38078 / rank_default** (insufficient_evidence; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI, SAME-R)
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- FLEX p. 9: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 14: analysis of the chamber atmosphere, e.g., for oxygen, nitrogen, carbon dioxide, carbon monoxide, and fuel gase
- ACME-CFI-G p. 78: runs. The CIR includes an optics bench, combustion chamber, fuel, and oxidizer control, and five different cam

**user_o2_38078 / rag_flame_spread** (approved; ranking FLEX, ACME-CFI-G, BASS, BASS-II, CFI)
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

**user_o2_15_psi_14 / rag_co2** (insufficient_evidence; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2, BASS)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 11: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- BASS-II p. 87: NASA/TM-20210011385 79 6.1.4.6 Gas Sensor Results The initial and final O2, CO2, and CO readings were recorded
- BASS-II p. 18: NASA/TM-20210011385 10 Figure 1.7.—O2 consumed, CO2 and CO generated per gram of fuel mass loss for two differ
