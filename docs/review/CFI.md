# CFI: review sheet (draft)

Edit `data/manual/CFI.json` to approve: set `review_status` to `reviewed`, `reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page.

- [ ] **Pillars**: `[]` · _inferred_
  - note: No direct fire-safety pillar. The five stated objectives are about cool-flame behavior, helium dilution, extinction and soot; the PSI SubResearch Area is 'Droplets'. The Research Impacts text mentions only a general support for 'the design of safer spacecraft systems', and its main applications are engines and fuels. Helium dilution and flame extinction are context for suppression research, but no cited line studies a suppressant. The folder name 'suppression' in knowledgeBase/ is the project's own grouping, not a source statement. Pillar list left empty on purpose; the reviewer should decide.
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `1) Examine the combustion behavior of n-dodecane and mixtures of n-dodecane/iso-dodecane at pressures ranging from 0.25 atm to 5 atm.`
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `2) Analyze the effects of helium dilution on cool flame behavior.`
  - [i_Investigation.txt · Comment[SubResearch Area]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `Comment[SubResearch Area] Droplets`
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `support the design of safer spacecraft systems by refining knowledge of combustion in microgravity environments.`
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `3) Examine the behavior of combustion characteristics.`
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `4) Investigate the relationship between droplet size, pressure, and flame extinction, and (5) understand the consequence of soot formation during cool flame combustion.`
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `A basic understanding of cool flames is important for understanding ignition phenomena of practical fuels and fuel additives.`
- [ ] **Gravity regime**: `microgravity` · _verified_
  - [i_Investigation.txt · Comment[Project Type]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `Microgravity Investigation`
- [ ] **Hardware**: `Multi-User Droplet Combustion Apparatus (MDCA) in the Combustion Integrated Rack (CIR), on the ISS` · _verified_
  - [i_Investigation.txt · Comment[Experiment Hardware]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `Multi-User Droplet Combustion Apparatus (MDCA), Combustion Integrated Rack (CIR)`
  - [i_Investigation.txt · Comment[Flight Platform]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `International Space Station (ISS)`
- [ ] **Nominal atmosphere**: `{'pressure_psi_min': 7.3479, 'pressure_psi_max': 73.4795}` · _verified_
  - note: Pressure only, converted at 14.6959 psi/atm. The Science Final Report lists the experiments performed at 0.5 to 5 atm (p. 6). The PSI record is inconsistent: its Objective says 0.25 to 5 atm and its Approach says the gas system delivers mixtures 'ranging from 0.25 to 0.5 atm'; the 0.25 atm bound is an objective that the flown list does not include, so it is not used. The experimental table carries per-test pressure and the O2/N2/He fractions.
  - [CFI Science Final Report.pdf · p. 6](../../knowledgeBase/suppression/CFI/CFI%20Science%20Final%20Report.pdf#page=6): `Pure n-dodecane at 0.5, 0.75, 1, 1.25, 2, 3, and 5 atm.`
  - [CFI Science Final Report.pdf · p. 6](../../knowledgeBase/suppression/CFI/CFI%20Science%20Final%20Report.pdf#page=6): `N-dodecane/Iso-dodecane mixtures: 75/25% and 60/40% by mass at pressures from 0.5 to 5 atm`
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `1) Examine the combustion behavior of n-dodecane and mixtures of n-dodecane/iso-dodecane at pressures ranging from 0.25 atm to 5 atm.`
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `ranging from 0.25 to 0.5 atm`
- [ ] **Sensor**: `{'instrument': 'black-and-white camera', 'measures': 'droplet size'}` · _verified_
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `Flames were observed with a black-and-white camera for droplet size measurements.`
- [ ] **Sensor**: `{'instrument': 'ultraviolet camera', 'measures': 'OH* radical emissions and flame size'}` · _verified_
  - note: Called a UV camera in the source.
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `A UV camera was used for capturing the OH* radical emissions and flame size.`
- [ ] **Sensor**: `{'instrument': 'high-resolution camera', 'measures': 'monitoring and documentation'}` · _verified_
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `Other high resolution cameras were used for monitoring and documentation.`
- [ ] **Sensor**: `{'instrument': 'radiometer', 'measures': 'flame radiation'}` · _verified_
  - note: Narrow-band and wide-band radiometers.
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `Narrow-band and wide-band radiometers for analyzed flame radiation.`
- [ ] **Earth application**: `Cool-flame reactivity and octane and cetane number of fuels for spark-ignition and diesel engines.` · _verified_
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `including an understanding of how cool flame reactivity determines octane and cetane number for fuels in spark ignition and diesel engines.`
- [ ] **Earth application**: `Design of advanced, clean, high-efficiency HCCI engines.` · _verified_
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/suppression/CFI/PSI-39_metadata_PSI-118_CFI/i_Investigation.txt): `the design of advanced engines such as clean, high-efficiency Homogeneous Charge Compression Ignition (HCCI) engines.`
