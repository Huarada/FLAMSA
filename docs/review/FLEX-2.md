# FLEX-2: review sheet (draft)

Edit `data/manual/FLEX-2.json` to approve: set `review_status` to `reviewed`, `reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page.

- [ ] **Pillars**: `[]` · _inferred_
  - note: No direct fire-safety pillar. The requirements document says FLEX is focused on spacecraft (the words 'fire safety and fire suppression' are on the next printed line, whose ligatures prevent a 1:1 quote) while FLEX-2 returns to the broader objective of improving the fundamental understanding of liquid-fuel combustion (the sentence wraps over the quoted lines, p. 7). The PSI record nevertheless tags the SubResearch Area 'Spacecraft Fire Safety': the two sources differ, not reconciled. Its objective 3 is flame extinction mechanisms and boundaries (ISA), which is context for suppression research, not a suppressant-effectiveness study. Pillar list left empty on purpose; the reviewer should decide.
  - [FLEX-2 SRD Final.pdf · p. 7](../../knowledgeBase/suppression/FLEX2/FLEX-2%20SRD%20Final.pdf#page=7): `paratus, MDCA, in the combustion integrated rack, CIR. While FLEX is focussed on spacecraft`
  - [FLEX-2 SRD Final.pdf · p. 7](../../knowledgeBase/suppression/FLEX2/FLEX-2%20SRD%20Final.pdf#page=7): `FLEX-2 returns to the broader objective of improving the fun-`
  - [FLEX-2 SRD Final.pdf · p. 7](../../knowledgeBase/suppression/FLEX2/FLEX-2%20SRD%20Final.pdf#page=7): `damental understanding of liquid-fuel combustion. The FLEX-2 experiments thus fall in the`
  - [i_Investigation.txt · Comment[SubResearch Area]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `Spacecraft Fire Safety`
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `Study flame extinction mechanisms and their boundaries.`
- [ ] **Gravity regime**: `microgravity` · _verified_
  - [i_Investigation.txt · Comment[Project Type]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `Microgravity Investigation`
- [ ] **Hardware**: `Combustion Integrated Rack (CIR) with the Multi-user Droplet Combustion Apparatus (MDCA), on the ISS` · _verified_
  - note: 'Appartatus' is a typo in the source record.
  - [i_Investigation.txt · Comment[Experiment Hardware]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `Combustion Integrated Rack (CIR), Multi-user Droplet Combustion Appartatus (MDCA)`
  - [i_Investigation.txt · Comment[Flight Platform]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `International Space Station (ISS)`
- [ ] **Nominal atmosphere**: `{'o2_percent_min': 10.0, 'o2_percent_max': 40.0, 'pressure_psi_min': 7.3479, 'pressure_psi_max': 44.0877}` · _verified_
  - note: Envelope from the Approach text (0.5 to 3.0 atm, converted at 14.6959 psi/atm; O2 0.1 to 0.4 mole fraction, balance diluent). The experimental table is a planned matrix with O2 0.17 to 0.30 and the same pressures: the Approach text states a wider O2 range; both are kept. The O2/pressure pairing is not given.
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `which was varied in pressure between 0.5 atm to 3.0 atm and O2 concentration between 0.1 to 0.4 mole fraction`
  - [PSI-68_Experimental table_Flex2.csv · row 2](../../knowledgeBase/suppression/FLEX2/PSI-68_Experimental%20table_Flex2.csv): `IsoOctane (pure),1.5 - 5,O2/N2 or O2/He,0.17; 0.21;0.25; 0.3,0.5; 1.0; 1.5; 2.0; or 3.0 ,25,0.1 - 5`
- [ ] **Sensor**: `{'instrument': 'color camera', 'measures': 'video to verify droplet deployment, ignition and progress'}` · _verified_
  - note: The requirements document table lists 'Flame view with MDCA color' and the word 'camera' is on the next printed line (p. 34).
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `A near real-time download of the color camera video was employed in order to verify successful droplet deployment, ignition, and overall progress of the experiment.`
  - [FLEX-2 SRD Final.pdf · p. 34](../../knowledgeBase/suppression/FLEX2/FLEX-2%20SRD%20Final.pdf#page=34): `- Flame view with MDCA color`
- [ ] **Sensor**: `{'instrument': 'pressure sensor', 'measures': 'chamber pressure'}` · _inferred_
  - note: The source names the recorded quantity, not the instrument.
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `Pressure and temperature data of the chamber environment was also recorded in near real time.`
- [ ] **Sensor**: `{'instrument': 'temperature sensor', 'measures': 'chamber temperature'}` · _inferred_
  - note: The source names the recorded quantity, not the instrument.
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `Pressure and temperature data of the chamber environment was also recorded in near real time.`
- [ ] **Sensor**: `{'instrument': 'radiometer', 'measures': 'wide and narrow band'}` · _inferred_
  - note: A radiometer-calibration record exists among the test-matrix records (DoD para 1, 'Surrotgate' is a typo in the source). The requirements document plans 'wide and narrow band' radiometers: 'radiometers' is on the next printed line (p. 34).
  - [FLEX-2 DoD.docx · para 1](../../knowledgeBase/suppression/FLEX2/FLEX-2%20DoD.docx): `LCTFWavelengths, Quiescent, RadiometerCalibration, SurrotgateFuel`
  - [FLEX-2 SRD Final.pdf · p. 34](../../knowledgeBase/suppression/FLEX2/FLEX-2%20SRD%20Final.pdf#page=34): `- wide and narrow band`
- [ ] **Earth application**: `More efficient and cleaner combustion technologies, reducing pollution and greenhouse gas emissions.` · _verified_
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `Insights gained from these studies can lead to more efficient and cleaner combustion technologies which are crucial for reducing pollution and greenhouse gas emissions.`
- [ ] **Earth application**: `Validation of jet engine models by engine manufacturers.` · _verified_
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/suppression/FLEX2/PSI-68_metadata_PSI-132_FLEX-2/i_Investigation.txt): `4) Validation of jet engine models by engine manufacturers with support from prior droplet results.`
