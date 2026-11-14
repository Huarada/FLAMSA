# SAME-R: review sheet (draft)

Edit `data/manual/SAME-R.json` to approve: set `review_status` to `reviewed`, `reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page.

- [ ] **Pillars**: `['detection']` · _inferred_
  - note: SAMER is the re-flight of SAME (an extension or continuation, p. 2); its stated purpose is smoke detection: the M-pass two-moment smoke detector and the design of fire detection systems. The report calls the re-flight both SAMER and SAME-2. Pillar is the curator's classification, not a source statement.
  - [SAMER_Final 0602 2014.pdf · p. 6](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=6): `The MPASS was included in SAME-2 to demonstrate the effectiveness of a two-moment smoke detector.`
  - [SAMER_Final 0602 2014.pdf · p. 73](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=73): `design of fire detection systems requires knowledge of both the expected signature of the events to`
- [ ] **Gravity regime**: `microgravity` · _inferred_
  - note: The report says 'low-gravity' and places the flight tests on the ISS (p. 3: thermal precipitators uploaded to the ISS); mapped to the microgravity regime.
  - [SAMER_Final 0602 2014.pdf · p. 9](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=9): `It is important to recognize that this condition is unique to low-gravity scenarios.`
  - [SAMER_Final 0602 2014.pdf · p. 3](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=3): `Six re-assembled Thermal Precipitators, each having 12 TEM grids in it, were uploaded to ISS for SAMER.`
- [ ] **Hardware**: `SAME smoke apparatus re-flown on the ISS with modifications: a new M-pass instrument replaced one of the two Commercial Diagnostic Enclosures` · _verified_
  - note: The SAME flight (2007) was in the Microgravity Science Glovebox (p. 2); the cited lines do not repeat that for SAMER, so it is not stated here.
  - [SAMER_Final 0602 2014.pdf · p. 2](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=2): `Smoke Aerosol Measurement Experiment Re-flight (SAMER) is an extension or continuation of Smoke Aerosol`
  - [SAMER_Final 0602 2014.pdf · p. 2](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=2): `instrument, M-pass, developed in-house GRC, was used to replace one of the two Commercial Diagnostic`
  - [SAMER_Final 0602 2014.pdf · p. 3](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=3): `Six re-assembled Thermal Precipitators, each having 12 TEM grids in it, were uploaded to ISS for SAMER.`
- [ ] **Nominal atmosphere**: `None` · _not_reported_
  - note: The experimental table carries no O2 or pressure. Searched the whole SAMER Final Report (2014) for cabin or ambient pressure and oxygen: the only pressure found is 309 kPa-g of house air for a ground flow test, not the flight atmosphere. The SAME documents searched for SAME (ISA-Tab, Final Science Report, Operations Manual, EIRD, Baseline Concept Description) also state none; the SAME2 folder holds byte-identical copies of the last three. Not searched: presentations, papers, drawings. Do not assume cabin air.
- [ ] **Sensor**: `{'instrument': 'M-pass'}` · _verified_
  - note: A new in-house GRC instrument, called MPASS in a later section; 'to demonstrate the effectiveness of a two-moment smoke detector' (p. 6). Instrument of the SAMER flight apparatus (Final Report, 2014).
  - [SAMER_Final 0602 2014.pdf · p. 2](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=2): `instrument, M-pass, developed in-house GRC, was used to replace one of the two Commercial Diagnostic`
  - [SAMER_Final 0602 2014.pdf · p. 6](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=6): `The MPASS was included in SAME-2 to demonstrate the effectiveness of a two-moment smoke detector.`
- [ ] **Sensor**: `{'instrument': 'P-Trak'}` · _verified_
  - note: Named in the SAMER apparatus flow tests (p. 2); SAME-R reused the SAME hardware already on orbit (p. 3).
  - [SAMER_Final 0602 2014.pdf · p. 2](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=2): `accurate dilution ratio data of the P-trak and Dusttrak so that the accuracy of aerosol concentration can be improved.`
  - [SAMER_Final 0602 2014.pdf · p. 3](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=3): `SAME-R utilized the SAME hardware already on  orbit with reloaded sample carousels, 30  extra loose samples,`
- [ ] **Sensor**: `{'instrument': 'DustTrak'}` · _verified_
  - note: Named in the SAMER apparatus flow tests (p. 2); SAME-R reused the SAME hardware already on orbit (p. 3).
  - [SAMER_Final 0602 2014.pdf · p. 2](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=2): `accurate dilution ratio data of the P-trak and Dusttrak so that the accuracy of aerosol concentration can be improved.`
  - [SAMER_Final 0602 2014.pdf · p. 3](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=3): `SAME-R utilized the SAME hardware already on  orbit with reloaded sample carousels, 30  extra loose samples,`
- [ ] **Sensor**: `{'instrument': 'thermophoretic soot sampler'}` · _inferred_
  - note: Called Thermal Precipitators in the report; the same device is called thermophoretic soot samplers in the SAME record (curator's identification, hence inferred). Six re-assembled Thermal Precipitators were uploaded to the ISS for SAMER (p. 3).
  - [SAMER_Final 0602 2014.pdf · p. 3](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=3): `Six re-assembled Thermal Precipitators, each having 12 TEM grids in it, were uploaded to ISS for SAMER.`
- [ ] **Sensor**: `{'instrument': 'scanning mobility particle sizer', 'measures': 'particle size distribution, as the reference instrument for validation'}` · _verified_
  - note: A post-flight ground instrument, not part of the flight apparatus.
  - [SAMER_Final 0602 2014.pdf · p. 9](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=9): `incorporating the flight aerosol instruments which had been returned to earth.  A Scanning Mobility Particle Sizer`
  - [SAMER_Final 0602 2014.pdf · p. 9](../../knowledgeBase/Detection/SAME2/SAMER_Final%200602%202014.pdf#page=9): `(SMPS) Spectrometer (3936, TSI, Shoreview, MN, USA) was used as the reference instrument in validation`
