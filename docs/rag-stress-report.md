# RAG stress report

Narrator: **Template (no language model)**. Runs: 62. Hard failures: **0**. Warnings: 0.

## Per scenario

| Scenario | Runs | Approved (full) | Partial | Insufficient | Avg passages | Avg seconds |
|---|---|---|---|---|---|---|
| lunar_standard (30% / 10.2 psi) | 62 | 62 | 0 | 0 | 10.0 | 0.06 |

## Per question (retrieval relevance proxy)

| Question | Category | Runs | Avg passages | Avg hit rate | Insufficient |
|---|---|---|---|---|---|
| rank_default | ranking | 2 | 10.0 | n/a | 0 |
| rank_compare | ranking | 2 | 10.0 | n/a | 0 |
| rank_criterion | ranking | 2 | 10.0 | n/a | 0 |
| rec_ranges | records | 2 | 10.0 | 0.80 | 0 |
| rec_closest | records | 2 | 10.0 | n/a | 0 |
| rec_lowest_psi | records | 2 | 10.0 | 0.80 | 0 |
| rag_flame_spread | passages | 2 | 10.0 | 1.00 | 0 |
| rag_extinction | passages | 2 | 10.0 | 1.00 | 0 |
| rag_burner | passages | 2 | 10.0 | 0.40 | 0 |
| rag_droplet | passages | 2 | 10.0 | 0.90 | 0 |
| rag_co2 | passages | 2 | 10.0 | 0.80 | 0 |
| meta_pillars | metadata | 2 | 10.0 | n/a | 0 |
| meta_hardware | metadata | 2 | 10.0 | 0.60 | 0 |
| lim_safe | limits | 2 | 10.0 | n/a | 0 |
| lim_gravity | limits | 2 | 10.0 | n/a | 0 |
| lim_extrapolate | limits | 2 | 10.0 | n/a | 0 |
| tech | scope | 2 | 10.0 | n/a | 0 |
| out_of_scope | scope | 2 | 10.0 | n/a | 0 |
| trap_exact | trap | 2 | 10.0 | n/a | 0 |
| trap_limit | trap | 2 | 10.0 | n/a | 0 |
| edge_empty | edge | 2 | 10.0 | n/a | 0 |
| edge_spaces | edge | 2 | 10.0 | n/a | 0 |
| edge_single_char | edge | 2 | 10.0 | n/a | 0 |
| edge_numbers_only | edge | 2 | 10.0 | n/a | 0 |
| edge_portuguese | edge | 2 | 10.0 | n/a | 0 |
| edge_unicode | edge | 2 | 10.0 | n/a | 0 |
| edge_markup | edge | 2 | 10.0 | n/a | 0 |
| edge_sql | edge | 2 | 10.0 | n/a | 0 |
| edge_unknown_study | edge | 2 | 10.0 | n/a | 0 |
| edge_injection | edge | 2 | 10.0 | n/a | 0 |
| edge_long | edge | 2 | 10.0 | n/a | 0 |

## Hard failures

None.

## Warnings

None.

## Validator issue codes in rejected runs (runs affected)

None.

## Rejected runs (scenario / question: codes)

None.

## Variance across repeated rounds

Answered (full or partial) per round: [31, 31] (mean 31.0, std 0.0).

Cells always approved: 31; never approved: 0; mixed (same input, different outcome): 0.


## Claim-level versus answer-level failure (first attempt)

Drafts: 62; mean claims per draft 3.0; claims with an issue 0 of 186 (per-claim failure rate 0.00).
Answers with at least one failing claim: 0.00. If claims failed independently at that rate, the expected answer failure would be 0.00.
Runs that needed a second attempt: 0; of those approved after the retry: 0 (0.00).

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

