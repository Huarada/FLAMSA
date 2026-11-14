# Data quality review: curated values vs. combustion theory

Date: 2026-11-14. Scope: every `data/curated/*/test_points.csv`. Decision log: ADR-0067.

Each rule below states the physics, the source passage that supports it, and what the curated data shows.
Quotes are copied from `pdftotext -layout` output. Where the printed page number differs from the PDF page, both are given.
Rules marked **[CI]** are enforced by `tests/infrastructure/test_physical_consistency.py`.

**Bottom line.** The relations that can be checked hold on the large tables (FLEX, ACME-CFI-G, SAFFIRE-II, SPICE pure fuels, BASS-II CO2).
That rules out column swaps and wrong unit conversions in curation. Seven source-level anomalies were found (section 2); their handling is recorded in ADR-0080.

---

## 1. Rules that hold

### 1.1 FLEX: burn time follows the d² law [CI]
- **Theory.** In quasi-steady droplet burning, d² falls linearly in time: d(t)² = d0² − K·t. A flame that extinguishes at diameter de therefore burns for t_b = (d0² − de²)/K.
- **Source.** `knowledgeBase/suppression/FLEX/2G11-070HE-0310.pdf`, PDF p. 2:
  > "where D is the droplet diameter, t is time, and Ko represents the burning rate value. As suggested, the square of droplet"
  > "diameter should decrease linearly with time with Ko being constant (hence the rationale for scaling the droplet diameter"
- **Data.** For 257 FLEX rows, t_b / ((d0² − de²)/K) has a median of 1.04 (IQR 0.99–1.08). This independently checks three separately reported columns (d0, de, K) against a fourth (burn time).
- **Outliers explained.** Four rows (129, 130, 171, 213) have de ≈ d0: the flame went out right after ignition, so the formula divides by almost zero. Four more rows (10, 19, 48, 239) have no de, so the formula overestimates the burn time.

### 1.2 FLEX: burning-rate constant rises with O₂ [CI]
- **Theory.** The classical result is K = (8λ/ρ_l c_p)·ln(1+B). The transfer number B grows with the ambient O₂ mass fraction, so K rises with O₂. This direction comes from textbook theory (Turns, cited by the paper above). The knowledge-base PDF below only says O₂ *influences* K.
- **Source.** `knowledgeBase/suppression/FLEX2/FLEX-2 SRD Final.pdf`, PDF p. 42:
  > "The ambient oxygen mole fraction influences the burning rate, extinction diameter, flame chem-"
- **Data.** Spearman ρ(K, O₂): heptane/N₂ 0.60, methanol/N₂ 0.89, heptane/CO₂+N₂ 0.72, methanol/CO₂+N₂ 0.81, methanol/He+N₂ 0.57. Heptane/He+N₂ shows no trend (0.04, n = 21) because pressure varies strongly in that subset (ρ(K, P) = −0.61).
- **Dashboard implication.** A K-vs-O₂ scatter should be colored by diluent; mixing diluents hides the trend.

### 1.3 FLEX: helium raises the burning rate
- **Theory.** Helium has a much higher thermal diffusivity than N₂, so heat reaches the droplet faster and K is higher. The same property raises diffusive heat loss.
- **Source.** `knowledgeBase/suppression/FLEX/1G17-070HE-0166.pdf`, PDF p. 6:
  > "mechanism. Figure 7 which summarizes the effect of increasing helium in the ambient shows that"
  > "increasing the diffusive heat loss but increasing the helium concentration to promote increasing diffusive"
- **Data.** Median K (mm²/s): heptane N₂ 0.56 → He+N₂ 0.65; methanol N₂ 0.44 → He+N₂ 0.585. The CO₂+N₂ medians are the lowest (0.50 and 0.43), as expected from the radiative loss of CO₂.

### 1.4 FLEX: extinction diameter scales with initial diameter; sooting fuel burns slower when large
- **Sources.**
  - `knowledgeBase/suppression/FLEX/20130010979.pdf`, PDF p. 11 (methanol, CO₂/N₂):
    > "Theory1 suggests a linear relationship"
    > "between extinction diameter, de , and"
    > "initial droplet diameter, d0"
  - `2G11-070HE-0310.pdf`, PDF p. 1:
    > "Results show that the droplet burning rate decreases with increasing Do throughout the Do range"
- **Data.** ρ(de, d0) is 0.62 for methanol and 0.86 for heptane. ρ(K, d0) is negative for heptane (−0.23 to −0.44) and about zero for methanol in N₂ (0.04) and CO₂+N₂ (−0.11). The paper attributes the effect to soot and radiation, and only heptane soots, so this is the expected split.
- **Plausibility.** The reference slide (`20130010979.pdf` p. 7) gives K = 0.67 for methanol; it prints "m2/s", a typo for mm²/s. The FLEX methanol range is 0.20–0.74 mm²/s.

### 1.5 ACME-CFI-G: stoichiometric mixture fraction matches the reported composition [CI]
- **Theory.** Zst = 1 / (1 + s·Y_F/Y_O2), where s is the stoichiometric O₂/fuel mass ratio. Y_F is the fuel mass fraction: in the burner stream for normal flames, in the ambient for inverse flames. Y_O2 is the O₂ mass fraction of the other stream, with N₂ as balance in both.
- **Source.** `knowledgeBase/ACME/CFI-G/PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf`, p. 29:
  > "where Zst and Tad are respectively the stochiometric mixture fraction and adiabatic flame"
- **Data.** Zst was recomputed from `o2_percent` and the fuel fraction for all 331 rows. The maximum deviation from the reported value is 4·10⁻⁵. This shows the O₂ and fuel-fraction columns are mapped and converted correctly in both flame configurations.

### 1.6 ACME-CFI-G: O₂ falls test after test in the sealed chamber [CI]
- **Source.** Same report, p. 19:
  > "In contrast to E-FIELD Flames, recirculation during CFI-G test operations was only conducted prior"
  > "to venting: (1) at the end of a test day and/or (2) between atmospheres, where the latter was"
- **Data.** For all 179 normal-flame rows, `o2_after_test_percent` ≤ `o2_percent`. In 156 of 168 consecutive same-day pairs, the O₂ after one test equals the O₂ before the next to 10⁻⁶. The 12 breaks jump to a fresh fill (18–23% or about 39.8%), which are the atmosphere changes the quote describes. In all 154 inverse-flame rows, the ambient fuel fraction also never rises.
- **Dashboard implication.** Within a test day, O₂ is not an independent variable. It drifts down with every test, typically by a few tenths of a point and by up to 1.8 points.

### 1.7 BASS-II: burns consume O₂ and produce CO₂ [CI for CO₂]
- **Source.** `knowledgeBase/Flammable/BASS2/BASS-II Summary Report.pdf`, PDF p. 14:
  > "volume and allowed us to determine when the working volume needed to be purged. The O2 decreased"
  > "during each burn and the CO and CO2 increased accordingly."
  > "was within its calibration window and had a range of 0 to 5 percent and a resolution of 0.1 percent by"
- **Data.** CO₂ never falls by more than the 0.1% resolution (two rows drop 0.01). The median O₂ drop is 0.3 points. The O₂ outliers are in section 2.2.

### 1.8 SAFFIRE-II: spread rate = burned length / burn time [CI]
- **Source.** `knowledgeBase/Flammable/SAFFIRE2/PSI-99_Experimental table_SAFFIRE-2.csv` reports burned length, burn time and spread rate as three separate columns.
- **Data.** Sample 2-5 (SIBAL): 290 mm / 145 s = 0.20 cm/s, reported 0.21. Sample 2-6: 290 / 115 = 0.25 cm/s, reported 0.26.
- **Physics.** The silicone samples did not spread in microgravity at 20 cm/s concurrent flow (burn length ≈ 0), yet burned "Complete" in 1 g. This matches the investigation's goal of comparing low-g limits against the 1-g screening test (SAFFIRE-II DoD, para 1).

### 1.9 SPICE: mass flow = volume flow × gas density (pure fuels)
- **Source.** `knowledgeBase/MSG (SolidAndGas)/SPICE/SPICE Final Report 12_2_2012.pdf`, p. 9:
  > "propylene mixed with 25% nitrogen in moles, and 50% propylene mixed with 50% nitrogen in moles;"
- **Data.** The density implied by `fuel_mass_flow_rate_mg_s × 60 / fuel_volume_flow_rate_sccm` is constant per fuel (± 0.2%): ethylene 1.139, methane 0.651, propane 1.790, propylene 1.709, 50% propylene 1.423 kg/m³. All of these match the ideal-gas density at about 300 K and 1 atm. The hydrocarbon share of the 50% mixture is 0.600 by mass; the expected value is 0.5·42.08 / (0.5·42.08 + 0.5·28.01) = 0.600.
- **Caveat.** The table's reference temperature (about 300 K) is not stated. The flowmeter's standard is 0 °C (Final Report p. 12), while the thesis gives 21 °C as the Sierra standard (PDF p. 37). Absolute mass flows therefore carry an unstated 2–9% reference ambiguity. Relative comparisons are unaffected.

---

## 2. Anomalies found in the source data

Status (ADR-0080): 2.1, 2.2, 2.3 and 2.6 are now missing with the raw value kept and the row `inferred`. 2.5 and 2.7 keep their values with a provenance note. 2.4 is unchanged because the NASA sources disagree on the thickness (0.33, 0.36 or 0.37 mm).

| # | Investigation | Rows | Finding | Why it is physically wrong | Proposed handling |
|---|---|---|---|---|---|
| 2.1 | SPICE | 36 rows labeled `75 % Propylene`, GMT days 119 and 136 (source rows 270–305) | Implied density 0.651 kg/m³ and hydrocarbon share 0.563 | A 75/25 propylene/N₂ mixture (Final Report p. 9) is 1.566 kg/m³, as the other 96 rows with that label show, with share 0.818. The value 0.651 is methane's density. The thesis table (`Dotson_umd_0117N_10980.pdf`, PDF p. 80, printed p. 70: 1.601 mg/s at 49.82 cm/s through 1.6 mm) also implies about 1.6 kg/m³. Mass flows in these rows are about 2.4× too low. | Treat `fuel_mass_flow_rate_mg_s` and `hydrocarbon_mass_flow_rate_mg_s` as missing (raw kept, `inferred` + note) for these rows. `sccm` stays. |
| 2.2 | BASS-II | B2, P22a, T28a (final O₂ 1.6, 0.6, 0.9%); P22b, T28b (final O₂ 39.1, 40.4%) | O₂ collapses to about 1% or doubles to about 40% | Report p. 87: "MSG free work volume of 250 L". Taking O₂ from 21% to 1% would consume about 66 g of O₂, enough to burn about 34 g of PMMA. A 7 g mass-loss test already exceeded the CO sensor range (p. 18). Nothing in the glovebox adds O₂. The a/b pairs sum to about 2× initial and their CO/CO₂ columns are "none" on the same rows, which points to a logging error in the source. FAQ para 22 says the O₂ sensor "was out of calibration". | Treat those five `o2_final_percent` values as missing (`inferred`, "physically impossible in 250 L work volume"). |
| 2.3 | BASS-II | 13 rows | `co_initial_ppm` = −1 to −3 | A concentration cannot be negative; this is zero offset of the CSA-CP sensor | Reuse the `negative_reading_as_missing` fixup already applied to the SPICE air rate. Clamping to 0 is not allowed because it would invent a value. |
| 2.4 | SAFFIRE-II | 2-4, 2-5, 2-6 | Thickness `037 mm` → curated as missing | Almost certainly 0.37 mm (2-7 lists Nomex at 0.37 mm), but the source does not say so | Keep missing (current), or `inferred` 0.37 mm with note: needs user approval. |
| 2.5 | ACME-CFI-G | 21106 F4 | `hot_ignition = no`, yet burn time 22 s, termination FT, comment "hot flame" | Contradictory within the row | Keep as source states; flag in the investigation's notes. |
| 2.6 | FLEX | 39, 43, 52, 93 | `flame_extinction_diameter_mm = 0` on **disruption** outcomes | 0 means burned to completion; a disrupted droplet has no extinction diameter | Treat as missing for `disruption` rows (keep 0 for `completion`). |
| 2.7 | CFI | r13–r16 | O₂ 21% + N₂ 76% + He 0% = 97% | Composition must sum to 100% | Keep (source); add note. |

Minor and expected:
- 29 FLEX rows have a gas composition that sums to 98–101% (rounding).
- BASS-II F2 CO falls from 105 to 82 ppm while CO₂ rises, which is within sensor noise.
- BASS-II O13b final CO is `over` (above 1000 ppm, FAQ para 24) and is curated as missing. It is a censored value, not an absent one.

---

## 3. What was not checked
- ACME-CFI-G `adiabatic_flame_temperature_k` needs an equilibrium solver. Only monotonicity with O₂ was checked (ρ 0.76–0.88, except normal-flame butane, where O₂ and dilution co-vary).
- SAME and SAME-R smoke data (`rt_r0_ratio`, aging times): no physical relation in the curated columns can be checked without the particle-size results.
- ACME-BRE, ACME-E-FIELD, SLICE and FLEX-2 hold daily or matrix summaries and have no relation to test.
- SAFFIRE-I and III have two rows each, with no outcome columns.
- The quotes were located with pdftotext. They were not re-checked visually in a PDF viewer.
