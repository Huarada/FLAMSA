# RAG failure attribution (first attempt, offline)

Runs analysed: 279. First-attempt claims: 1299; with an issue: 172 (0.13). Runs whose first attempt had issues: 115; approved after the retry: 41 (0.36).

## Issues by code and stage

| Code | R retrieval | P packaging (payload/schema/prompt) | G generation (model) | V validation (tolerance candidate) | Total |
|---|---|---|---|---|---|
| undeclared_number | 0 | 0 | 98 | 9 | 107 |
| malformed_citation | 0 | 61 | 0 | 0 | 61 |
| quote_mismatch | 0 | 0 | 35 | 1 | 36 |
| number_mismatch | 0 | 2 | 19 | 0 | 21 |
| unknown_citation | 0 | 0 | 8 | 0 | 8 |
| missing_citation | 0 | 0 | 7 | 0 | 7 |
| implausible | 0 | 0 | 6 | 0 | 6 |

## Root-cause breakdown

- **undeclared_number / G** x65: value of a record of an investigation the claim does not cite
  - e.g. The ACME-CFI-G final report concluded that burner oxygen flow rate and oxygen concentration significantly affect inverse flame size and brightness, with chamber oxygen concentration held constant duri
- **malformed_citation / P** x61: the flat citation schema allowed an incomplete or unsupported citation
  - e.g. The FLEX investigation is the highest ranked for the lunar base scenario with oxygen at 30% ambient and pressure near 10.2 psi, making its data most relevant for understanding droplet burning rate con
- **quote_mismatch / G** x32: text not found anywhere in the investigation's documents (paraphrase or invention)
  - e.g. The ACME-CFI-G investigation provides insights into how oxygen concentration influences flame size and radiative heat loss, showing that higher oxidizer flow rates and oxygen concentrations affect fla
- **undeclared_number / G** x28: value of an uncited record of a cited investigation
  - e.g. FLEX's pressure proximity criterion is perfect (value 1.0) because the scenario pressure (10.2 psi) matches closely the nearest test pressures (~10.39-10.46 psi), while ACME-CFI-G's pressure proximity
- **number_mismatch / G** x14: value belongs to a different record of the same investigation
  - e.g. The FLEX investigation addresses the fire-safety pillars of prevention and suppression relevant to a habitat scenario with oxygen concentration near 38% ambient and pressure near 14.7 psi.
- **undeclared_number / V** x9: the number appears in a cited quote (verbatim from the document)
  - e.g. FLEX's oxygen proximity criterion is perfect (value 1.0) because the scenario oxygen (30%) is inside the tested range, whereas ACME-CFI-G's oxygen proximity is lower (0.838) due to a 3.2% difference f
- **missing_citation / G** x7: missing_citation
  - e.g. The curated PSI data contains no technology recommendations for oxygen consumption and CO2 production control during burns in the lunar base scenario. However, the cited investigations provide detaile
- **implausible / G** x6: implausible
  - e.g. The BASS investigation discusses the importance of reduced buoyant flows and low-speed air circulation currents in microgravity environments, which differ significantly from normal Earth gravity, indi
- **undeclared_number / G** x5: not a known fact (model-stated or derived)
  - e.g. ACME-CFI-G investigation includes test points at oxygen concentration and pressure very close to the scenario values, such as test point 21291 J3 with 38.078% oxygen and 14.6967 psi pressure, matching
- **number_mismatch / G** x5: value matches no record of the investigation
  - e.g. The FLEX-2 investigation includes droplet combustion experiments with varying oxygen mole fractions and pressures, including tests at 15% oxygen mole fraction and low pressures in microgravity, provid
- **unknown_citation / G** x4: cited a passage that was not retrieved
  - e.g. The burning rate constant for methanol droplets decreases with increasing oxygen concentration from 15% to 20% ambient at about 1 atm pressure, as shown by FLEX test points with burning rate constants
- **unknown_citation / G** x2: record figure without its record citation
  - e.g. The ACME-CFI-G investigation includes droplet burning rate measurements for alkane fuels at oxygen concentrations higher than the lunar base scenario oxygen level, with tests at about 21% oxygen and p
- **number_mismatch / P** x2: looks like a unit confusion: kPa to psi
  - e.g. The FLEX-2 investigation includes droplet combustion experiments at oxygen mole fractions near 15% and pressures below atmospheric, providing data on droplet interactions and extinction limits in micr
- **unknown_citation / G** x1: cited a test point that does not exist
  - e.g. The ACME-CFI-G investigation includes droplet burning rate measurements for alkane fuels at oxygen concentrations higher than the lunar base scenario oxygen level, with tests at about 21% oxygen and p
- **quote_mismatch / G** x1: quote exists elsewhere (p. 62); the locator is wrong
  - e.g. The ACME-CFI-G investigation includes combustion tests with hydrocarbon fuels at oxygen concentrations near but somewhat higher than the lunar base scenario and at lower pressures. It provides insight
- **quote_mismatch / G** x1: quote exists elsewhere (p. 7); the locator is wrong
  - e.g. The CFI investigation provides data on droplet combustion at oxygen levels near 15% and pressures close to 14 psi, including observations of cool flames and warm flames, which are relevant to understa
- **quote_mismatch / G** x1: quote exists elsewhere (p. 65); the locator is wrong
  - e.g. The ACME-CFI-G investigation is relevant but less closely matched to the lunar base scenario, as its tests are at slightly higher oxygen concentrations (~33-34%) and lower pressures (~7.3 psi), and it
- **quote_mismatch / V** x1: differs only by punctuation or spacing
  - e.g. The BASS-II investigation provides data on solid fuel combustion and flame spread in microgravity-like conditions, which is relevant for habitat fire safety involving solid materials, but it lacks pre
- **unknown_citation / G** x1: FLEX ranking has no 'pillars'. Breakdown fields you may cite: score, rank, oxyge
  - e.g. The FLEX investigation is relevant to a habitat scenario with 15% oxygen and 14 psi pressure because it includes tests with methanol fuel at oxygen levels matching the scenario and pressures close to 
