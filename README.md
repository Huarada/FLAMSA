# FLAMSA: PSI Fire-Safety Explorer

FLAMSA is an explainable-AI dashboard for fire safety in crewed habitats. It summarizes, ranks and interprets NASA Physical Sciences Informatics (PSI) microgravity combustion investigations, and it exports the curated dataset for your own models.

- Raw sources: `knowledgeBase/` (read-only). The registry is `data/sources.json`.
- Curated data: `data/curated/<investigation_id>/` (`test_points.csv` and `investigation.json`).
- Decisions: `docs/ADR.md`. Full data-quality review: `docs/DATA_QUALITY_REVIEW.md`.

```
PYTHONPATH=src python -m psi_fire.interface.curate_cli      # rebuild data/curated from knowledgeBase
ruff check . && mypy src/psi_fire/domain && pytest -q
streamlit run src/psi_fire/interface/app.py
```

---

## Physical consistency rules (business rules)

A value shown on the dashboard is trusted only if it obeys the combustion physics stated in the investigation's own reports. Each rule below gives:

- the law;
- why the behavior the dashboard shows is physically coherent;
- the confirming passage, quoted from the archived source;
- the test that enforces the rule on every curation run (`tests/infrastructure/test_physical_consistency.py`).

The rules also guard the pipeline itself. A column swap or a wrong unit conversion breaks at least one of them.

When a source value breaks a rule, we follow three principles:

- **Never replace an observed value with a computed one.** The value becomes missing and the original stays in `<column>_raw`.
- **Record the reason.** The row becomes `provenance_status = inferred` and carries a `provenance_note`.
- **Flag a conflict that no other cell resolves.** The value is kept and only a note is added.

### R1. Droplet burn time follows the d² law (FLEX)
- **Law.** In quasi-steady droplet burning, the square of the diameter falls linearly in time: d(t)² = d0² − K·t. A flame that extinguishes at diameter de therefore burns for t_b = (d0² − de²) / K.
- **Why the data is coherent.** FLEX reports d0, de, K and burn time as separate columns, so the law can be checked independently. Across 257 tests, the median of t_b / ((d0² − de²)/K) is 1.04 (IQR 0.99–1.08). The few outliers are flames that went out right after ignition (de ≈ d0), where the formula divides by almost zero.
- **Evidence.** `knowledgeBase/suppression/FLEX/2G11-070HE-0310.pdf`, PDF p. 2:
  > "diameter should decrease linearly with time with Ko being constant (hence the rationale for scaling the droplet diameter"
- **Test.** `test_flex_burn_time_follows_the_d_squared_law`

### R2. More oxygen burns a droplet faster (FLEX)
- **Law.** Classical theory gives K = (8λ / ρ_l c_p)·ln(1 + B). The transfer number B grows with the ambient O₂ mass fraction, so K rises with O₂.
- **Why the data is coherent.** Within one fuel and one diluent, K rises with O₂: Spearman ρ is 0.60 for heptane in N₂ and 0.89 for methanol in N₂. Helium raises K further because its thermal diffusivity is higher: median heptane 0.56 → 0.65 mm²/s, methanol 0.44 → 0.585 mm²/s. CO₂ lowers K through radiative loss. Charts of K against O₂ must therefore be split by diluent, or the trend disappears.
- **Evidence.** `knowledgeBase/suppression/FLEX2/FLEX-2 SRD Final.pdf`, PDF p. 42:
  > "The ambient oxygen mole fraction influences the burning rate, extinction diameter, flame chem-"

  The SRD gives no direction for the effect; the direction comes from the classical theory above.
- **Test.** `test_flex_burning_rate_rises_with_oxygen_in_nitrogen`

### R3. Extinction diameter scales with initial diameter (FLEX)
- **Law.** Radiative extinction happens at a size that grows with the initial droplet. Sooting fuels also burn slower as the droplet gets larger.
- **Why the data is coherent.** ρ(de, d0) is 0.62 for methanol and 0.86 for heptane. K falls with d0 only for heptane, the sooting fuel; methanol does not soot.
- **Evidence.** `knowledgeBase/suppression/FLEX/20130010979.pdf`, PDF p. 11:
  > "Theory1 suggests a linear relationship" / "between extinction diameter, de , and" / "initial droplet diameter, d0"
- **Rule applied.** A `0` extinction diameter on a `disruption` outcome is treated as missing, because a droplet that broke up has no measurable extinction diameter. A `0` on a `completion` outcome is kept, since the droplet burned away.

### R4. Stoichiometric mixture fraction follows from the reported composition (ACME-CFI-G)
- **Law.** Zst = 1 / (1 + s·Y_F / Y_O₂).
  - s is the stoichiometric O₂/fuel mass ratio: ethane 3.72, propane 3.63, n-butane 3.58.
  - Y_F is the fuel mass fraction, in the burner stream for normal flames and in the ambient for inverse flames.
  - Y_O₂ is the O₂ mass fraction of the other stream. N₂ is the balance in both streams.
- **Why the data is coherent.** Zst was recomputed from `o2_percent` and the fuel fraction for all 331 flames. It matches the reported Zst within 4·10⁻⁵, which proves the O₂ and fuel columns are mapped and converted correctly.
- **Evidence.** `knowledgeBase/ACME/CFI-G/PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf`, p. 29:
  > "where Zst and Tad are respectively the stochiometric mixture fraction and adiabatic flame"
- **Test.** `test_acme_cfi_g_stoichiometric_mixture_fraction_matches_reported_composition`

### R5. A sealed chamber loses oxygen test after test (ACME-CFI-G)
- **Law.** Mass balance in a closed volume: each flame consumes O₂, and nothing adds O₂ until the chamber is vented and refilled.
- **Why the data is coherent.** O₂ after a test never exceeds O₂ before it (179 of 179 normal flames). In 156 of 168 consecutive same-day pairs, the O₂ after one test equals the O₂ before the next. The 12 exceptions are fresh fills. Within a test day O₂ is therefore not an independent variable; it drifts down.
- **Evidence.** Same report, p. 19:
  > "In contrast to E-FIELD Flames, recirculation during CFI-G test operations was only conducted prior"
  > "to venting: (1) at the end of a test day and/or (2) between atmospheres, where the latter was"
- **Test.** `test_acme_cfi_g_flames_never_add_oxygen_to_the_sealed_chamber`

### R6. Burns consume O₂ and produce CO₂, within the volume's limits (BASS-II)
- **Law.** PMMA burns as C₅H₈O₂ + 6 O₂ → 5 CO₂ + 4 H₂O, which uses 1.92 g of O₂ per gram of fuel. In the 250 L glovebox, a 10-point O₂ drop consumes about 33 g of O₂, which means burning about 17 g of PMMA. That is far more than any burn the report discusses.
- **Why the data is coherent.** CO₂ never falls by more than the sensor's 0.1% resolution. O₂ drops by a median of 0.3 points and by at most 3.2 points.
- **Values outside this range.** Five final-O₂ readings (1.6, 0.6, 0.9, 39.1 and 40.4%) would need either about 34 g of PMMA burned or an oxygen source. They are treated as missing. Negative CO readings are a sensor zero offset and are also treated as missing.
- **Evidence.** `knowledgeBase/Flammable/BASS2/BASS-II Summary Report.pdf`, PDF p. 14:
  > "volume and allowed us to determine when the working volume needed to be purged. The O2 decreased"
  > "during each burn and the CO and CO2 increased accordingly."

  PDF p. 87 gives the "MSG free work volume of 250 L".
- **Tests.** `test_bass_ii_burns_never_remove_carbon_dioxide`, `test_bass_ii_final_o2_never_rises_or_collapses`

### R7. Spread rate equals burned length over burn time (SAFFIRE-II)
- **Law.** v_f = L / t.
- **Why the data is coherent.**
  - The source reports length, time and rate as separate columns. 290 mm / 145 s = 0.20 cm/s against 0.21 reported, and 290 mm / 115 s = 0.25 cm/s against 0.26.
  - Silicone burned completely in 1 g but did not spread in microgravity under 20 cm/s concurrent flow. This is the behavior SAFFIRE exists to expose: 1-g screening does not predict low-g flammability.
- **Test.** `test_saffire_ii_spread_rate_equals_burn_length_over_burn_time`

### R8. Mass flow = volume flow × gas density (SPICE)
- **Law.** ṁ = Q·ρ, with the ideal-gas density ρ = P·M_mix / (R·T).
  - For 75% propylene and 25% N₂ (molar): M_mix = 0.75·42.08 + 0.25·28.01 = 38.56 g/mol.
  - At 101.325 kPa this gives ρ = 1.598 kg/m³ at 294 K, the reference used in the SPICE thesis, and 1.567 kg/m³ at 300 K.
  - Methane gives ρ = 0.652 kg/m³ at 300 K.
- **Why the data is coherent.**
  - The density implied by `fuel_mass_flow_rate_mg_s × 60 / fuel_volume_flow_rate_sccm` is constant within ±0.2% for each gas. It matches the ideal-gas value at about 300 K: ethylene 1.139, methane 0.651, propane 1.790, propylene 1.709, 50% propylene 1.423 kg/m³.
  - The hydrocarbon share of the 50% mixture is 0.600 by mass, exactly 0.5·42.08 / 35.05.
- **Value outside this rule.** 36 rows labeled `75 % Propylene` (GMT days 119 and 136) imply ρ = 0.651 kg/m³, which is methane's density, not the mixture's. Their mass flows are about 2.4× too low.
  - Both mass-flow columns are treated as missing, with the raw value kept and a density-mismatch note.
  - The volumetric flow stays. A corrected mass flow is not computed, because that would replace an observation with a calculation.
- **Evidence.**
  - `knowledgeBase/MSG (SolidAndGas)/SPICE/SPICE Final Report 12_2_2012.pdf`, p. 9:
    > "propylene mixed with 25% nitrogen in moles, and 50% propylene mixed with 50% nitrogen in moles;"
  - `Dotson_umd_0117N_10980.pdf`, PDF p. 80, printed p. 70: 75% C₃H₆, 1.6 mm nozzle, 1.601 mg/s at 49.82 cm/s. That implies about 1.6 kg/m³.
  - Reference temperature: the flowmeter standard is 0 °C (Final Report p. 12) and the Sierra standard is 21 °C (thesis PDF p. 37). The table's own reference (about 300 K) is not stated, so absolute mass flows carry a 2–9% reference ambiguity. Comparisons within SPICE are unaffected.
- **Test.** `test_spice_mass_flow_is_consistent_with_the_labelled_gas_density`

### Conflicts kept as reported
- **ACME-CFI-G 21106 F4.** The row says `hot_ignition = no`, yet it has a 22 s burn and the comment "hot flame". The values are kept, with a conflict note.
- **CFI r13–r16.** O₂ + N₂ + He = 0.97. The missing 3% cannot be assigned to any species, so the values are kept, with a note.
- **SAFFIRE-II 2-4, 2-5, 2-6.** The thickness `037 mm` stays missing. NASA sources disagree between 0.33, 0.36 and 0.37 mm, and none of them is archived yet.

### Limits of these rules
- The PSI has no partial-gravity data.
- The rules hold inside the tested ranges only. Any statement outside them is an extrapolation and must be labeled as one.
