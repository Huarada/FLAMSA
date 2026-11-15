# RAG failure attribution (first attempt, offline)

Runs analysed: 279. First-attempt claims: 1277; with an issue: 420 (0.33). Runs whose first attempt had issues: 211; approved after the retry: 49 (0.23).

## Issues by code and stage

| Code | R retrieval | P packaging (payload/schema/prompt) | G generation (model) | V validation (tolerance candidate) | Total |
|---|---|---|---|---|---|
| undeclared_number | 0 | 0 | 245 | 73 | 318 |
| unknown_citation | 0 | 0 | 187 | 0 | 187 |
| malformed_citation | 0 | 80 | 0 | 0 | 80 |
| quote_mismatch | 0 | 0 | 43 | 11 | 54 |
| number_mismatch | 0 | 0 | 48 | 0 | 48 |
| missing_citation | 0 | 0 | 6 | 0 | 6 |
| implausible | 0 | 0 | 1 | 0 | 1 |

## Root-cause breakdown

- **undeclared_number / G** x174: value of a record of an investigation the claim does not cite
  - e.g. The ACME-CFI-G investigation is somewhat relevant to the lunar base scenario, with oxygen proximity of 0.838 and pressure proximity of 0.85, indicating the scenario's oxygen and pressure values are mo
- **unknown_citation / G** x162: cited a test point that does not exist
  - e.g. The FLEX investigation is most relevant to the lunar base scenario because it has test points at oxygen concentration and pressure values very close to the scenario's 30% oxygen and 10.2 psi pressure,
- **malformed_citation / P** x80: the flat citation schema allowed an incomplete or unsupported citation
  - e.g. The FLEX investigation is highly relevant to the habitat scenario with oxygen concentration 38.078% and pressure 14.7 psi because it has extensive data at pressures close to the scenario's pressure an
- **undeclared_number / V** x73: the number appears in a cited quote (verbatim from the document)
  - e.g. The FLEX-2 investigation is relevant as it studies the influence of oxygen mole fraction on burning rate, extinction diameter, flame chemistry and characteristics, covering oxygen mole fractions from 
- **undeclared_number / G** x67: value of an uncited record of a cited investigation
  - e.g. The FLEX investigation includes tests at pressures close to the lunar base scenario pressure of 10.2 psi and oxygen concentration of 30%, using methanol and heptane fuels. These tests provide data on 
- **quote_mismatch / G** x37: text not found anywhere in the investigation's documents (paraphrase or invention)
  - e.g. The ACME-CFI-G investigation provides data on flame size and radiation intensity as oxygen concentration varies, showing that higher oxygen concentration increases flame size and brightness, which is 
- **number_mismatch / G** x29: value belongs to a different record of the same investigation
  - e.g. The ACME-CFI-G final report concluded that the oxygen concentration in the burner stream significantly affects the flame size and brightness in inverse flames, with increased oxidizer flow rate from t
- **number_mismatch / G** x14: figure disagrees with the computed breakdown or the record
  - e.g. The FLEX investigation is most relevant to the habitat scenario with oxygen at 38.078% and pressure at 14.7 psi, ranking first with a score of 0.735. The criterion contributing most to this top result
- **quote_mismatch / V** x11: differs only by punctuation or spacing
  - e.g. The BASS-II investigation focuses on solid fuel combustion (e.g., PMMA) and flame spread in microgravity, with ambient oxygen concentrations around 22% and no reported pressure data. While it addresse
- **unknown_citation / G** x9: ACME-CFI-G has no test point 21291 J3},{.
  - e.g. The ACME-CFI-G investigation includes tests at oxygen concentrations very close to the habitat scenario oxygen concentration of 38.078% ambient and pressure near 14.7 psi. These tests with ethane and 
- **unknown_citation / G** x8: cited a passage that was not retrieved
  - e.g. The FLEX-2 investigation includes test matrices covering oxygen concentrations up to 30% and pressures ranging from about 7.35 psi to over 44 psi, with fuels such as iso-octane, n-octane, heptane, dec
- **missing_citation / G** x6: missing_citation
  - e.g. Partial gravity effects are not directly studied in these investigations, as PSI has no partial-gravity data; the FLEX investigation includes microgravity combustion data but partial gravity is only e
- **number_mismatch / G** x5: value matches no record of the investigation
  - e.g. The FLEX-2 investigation is relevant to habitat scenarios with oxygen near 15% ambient and pressures near 14 psi because it studies droplet combustion at oxygen mole fractions of 0.15 and pressures ar
- **undeclared_number / G** x4: not a known fact (model-stated or derived)
  - e.g. The ACME-CFI-G investigation includes tests closest to the scenario oxygen concentration of 38.078% at approximately 14.7 psi pressure, with test points such as 21291 J3 having an oxygen concentration
- **quote_mismatch / G** x2: quote exists elsewhere (p. 51); the locator is wrong
  - e.g. The ACME-CFI-G investigation includes tests at oxygen concentrations very close to the habitat scenario's 38.078% ambient oxygen and pressure near 14.7 psi, using gaseous fuels such as ethane and buta
- **unknown_citation / G** x2: ACME-CFI-G has no test point 21291 J3}],.
  - e.g. The ACME-CFI-G investigation is highly relevant to the habitat scenario with oxygen concentration close to 38.078% and pressure near 14.7 psi, as it includes tests at oxygen percentages nearly identic
- **unknown_citation / G** x2: ACME-CFI-G has no test point 21088 N1}],.
  - e.g. The ACME-CFI-G investigation, while not matching the scenario oxygen exactly, provides data on inverse flames and flame extinction behavior at pressures close to 14 psi and oxygen concentrations near 
- **quote_mismatch / G** x2: quote exists elsewhere (p. 7); the locator is wrong
  - e.g. The CFI investigation studies droplet combustion and cool flame behavior of liquid fuels at pressures from 0.25 atm to 5 atm and oxygen concentrations near ambient air (21%), which is somewhat differe
- **quote_mismatch / G** x2: quote exists elsewhere (p. 65); the locator is wrong
  - e.g. The ACME-CFI-G investigation is somewhat relevant to the lunar base habitat scenario but less so than FLEX, as its tests are conducted at lower pressures around 7.35 psi and slightly higher oxygen con
- **unknown_citation / G** x1: ACME-CFI-G has no test point 21088 N1},{.
  - e.g. The ACME-CFI-G investigation includes tests at pressures near 14 psi but at higher oxygen concentrations than the scenario's 15%, focusing on gaseous fuels like ethane and butane. It provides no share
- **implausible / G** x1: implausible
  - e.g. The ACME-CFI-G investigation also includes metadata about gravity regime and has tests with oxygen concentrations around 33 to 34 percent ambient and pressures around 7.35 psi, which is somewhat lower
- **unknown_citation / G** x1: ACME-CFI-G has no test point 21153 A5}],.
  - e.g. The ACME-CFI-G investigation has test points near 33.3% oxygen ambient concentration but at a lower pressure of about 7.35 psi, which is somewhat distant from the lunar base pressure of 10.2 psi. It i
- **unknown_citation / G** x1: ACME-CFI-G has no test point 21153 F1},{.
  - e.g. The ACME-CFI-G investigation is somewhat relevant to the lunar base habitat scenario, but its tests are at lower pressures (around 7.35 psi) and slightly higher oxygen concentrations (about 33-34% amb
- **unknown_citation / G** x1: record figure without its record citation
  - e.g. The BASS-II investigation tested solid fuels at oxygen concentrations including 15% and 17.5% ambient oxygen, but did not report pressure values for ambient conditions. This limits direct pressure ran
