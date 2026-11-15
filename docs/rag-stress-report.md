# RAG stress report

Narrator: **Template (no language model)**. Runs: 496. Hard failures: **0**. Warnings: 4.

## Per scenario

| Scenario | Runs | Approved | Insufficient | Avg passages | Avg seconds |
|---|---|---|---|---|---|
| lunar_standard (30% / 10.2 psi) | 31 | 31 | 0 | 10.0 | 0.06 |
| user_o2_38078 (38.078% / 14.7 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| user_o2_15_psi_14 (15% / 14 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| earth_cabin (21% / 14.7 psi) | 31 | 31 | 0 | 8.0 | 0.01 |
| well_covered (20% / 16 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| extrap_o2 (40% / 10.2 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| burner_only (50% / 15 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| high_pressure (21% / 50 psi) | 31 | 31 | 0 | 8.0 | 0.01 |
| low_pressure (35% / 8 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| empty_region (5% / 2 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| zero_zero (0% / 0 psi) | 31 | 31 | 0 | 10.0 | 0.01 |
| max_max (100% / 100 psi) | 31 | 31 | 0 | 8.0 | 0.01 |
| tiny_decimals (21.0001% / 14.6999 psi) | 31 | 31 | 0 | 8.0 | 0.01 |
| invalid_negative_o2 (-1% / 14.7 psi) | 31 | 0 | 0 | 0.0 | 0.00 |
| invalid_o2_over_100 (101% / 14.7 psi) | 31 | 0 | 0 | 0.0 | 0.00 |
| invalid_negative_psi (21% / -1 psi) | 31 | 0 | 0 | 0.0 | 0.00 |

## Per question (retrieval relevance proxy)

| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |
|---|---|---|---|---|---|
| rank_default | ranking | 13 | 9.4 | n/a | 0 |
| rank_compare | ranking | 13 | 9.4 | n/a | 0 |
| rank_criterion | ranking | 13 | 9.4 | n/a | 0 |
| rec_ranges | records | 13 | 9.4 | 0.76 | 0 |
| rec_closest | records | 13 | 9.4 | n/a | 0 |
| rec_lowest_psi | records | 13 | 9.4 | 0.60 | 0 |
| rag_flame_spread | passages | 13 | 9.4 | 0.89 | 0 |
| rag_extinction | passages | 13 | 9.4 | 0.96 | 0 |
| rag_burner | passages | 13 | 9.4 | 0.30 | 0 |
| rag_droplet | passages | 13 | 9.4 | 0.84 | 0 |
| rag_co2 | passages | 13 | 9.4 | 0.73 | 0 |
| meta_pillars | metadata | 13 | 9.4 | n/a | 0 |
| meta_hardware | metadata | 13 | 9.4 | 0.75 | 0 |
| lim_safe | limits | 13 | 9.4 | n/a | 0 |
| lim_gravity | limits | 13 | 9.4 | n/a | 0 |
| lim_extrapolate | limits | 13 | 9.4 | n/a | 0 |
| tech | scope | 13 | 9.4 | n/a | 0 |
| out_of_scope | scope | 13 | 9.4 | n/a | 0 |
| trap_exact | trap | 13 | 9.4 | n/a | 0 |
| trap_limit | trap | 13 | 9.4 | n/a | 0 |
| edge_empty | edge | 13 | 9.4 | n/a | 0 |
| edge_spaces | edge | 13 | 9.4 | n/a | 0 |
| edge_single_char | edge | 13 | 9.4 | n/a | 0 |
| edge_numbers_only | edge | 13 | 9.4 | n/a | 0 |
| edge_portuguese | edge | 13 | 9.4 | n/a | 0 |
| edge_unicode | edge | 13 | 9.4 | n/a | 0 |
| edge_markup | edge | 13 | 9.4 | n/a | 0 |
| edge_sql | edge | 13 | 9.4 | n/a | 0 |
| edge_unknown_study | edge | 13 | 9.4 | n/a | 0 |
| edge_injection | edge | 13 | 9.4 | n/a | 0 |
| edge_long | edge | 13 | 9.4 | n/a | 0 |

## Hard failures

None.

## Warnings

- earth_cabin x rag_burner: low retrieval relevance (hit rate 0.25, 8 passages)
- high_pressure x rag_burner: low retrieval relevance (hit rate 0.25, 8 passages)
- max_max x rag_burner: low retrieval relevance (hit rate 0.12, 8 passages)
- tiny_decimals x rag_burner: low retrieval relevance (hit rate 0.25, 8 passages)

## Validator issue codes in rejected runs (runs affected)

None.

## Rejected runs (scenario / question: codes)

None.

## Retrieved passages for the regions you asked about

**lunar_standard / rank_default** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 26: MDC-DOC-1790A October 12, 2010 Reflight Safety Data Package, MDCA/FLEX2 24 FIGURE 14 FLEX2 FIBER ARM AND PROTE
- ACME-CFI-G p. 14: analysis of the chamber atmosphere, e.g., for oxygen, nitrogen, carbon dioxide, carbon monoxide, and fuel gase
- ACME-CFI-G p. 78: runs. The CIR includes an optics bench, combustion chamber, fuel, and oxidizer control, and five different cam

**lunar_standard / rag_flame_spread** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2)
- FLEX p. 10: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- FLEX p. 4: 28th Annual Meeting of the American Society of Space and Gravitational Research Dynamics of Water Absorption a
- ACME-CFI-G p. 65: ACME/CFI-G Final Report (2022) 21 November 2022 65 This composite image shows the effects of the oxidizer flow
- ACME-CFI-G p. 64: ACME/CFI-G Final Report (2022) 21 November 2022 64 Figure 1. CFI-G Inverse Flames at Increasing Oxidizer Flow

**lunar_standard / rag_droplet** (approved; ranking FLEX, ACME-CFI-G, BASS-II, CFI, FLEX-2)
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

**user_o2_15_psi_14 / rag_flame_spread** (approved; ranking FLEX, BASS-II, ACME-CFI-G, CFI, FLEX-2)
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
