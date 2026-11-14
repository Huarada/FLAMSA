# SPICE: review sheet (draft)

Edit `data/manual/SPICE.json` to approve: set `review_status` to `reviewed`, `reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page.

- [ ] **Pillars**: `[]` · _inferred_
  - note: No pillar-specific statement. The objectives are smoke points and sooting of gas jet diffusion flames; the impact is 'to help design safer spacecraft environments', and the PSI SubResearch Area is 'Fire Safety'. Smoke production could relate to detection, but no cited line says so. Pillar list left empty on purpose; the reviewer should decide.
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `(1) Identify the laminar smoke-point properties of non-buoyant jet diffusion flames under various co-flow conditions in microgravity.`
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `(3) Quantify the sooting propensity of different fuels, such as ethylene, propane, and propylene mixtures.`
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `(1) Will improve our understanding of soot formation mechanisms and help design safer spacecraft environments.`
  - [i_Investigation.txt · Comment[SubResearch Area]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `Comment[SubResearch Area] Fire Safety`
- [ ] **Gravity regime**: `microgravity` · _verified_
  - [i_Investigation.txt · Comment[Project Type]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `Microgravity Investigation`
- [ ] **Hardware**: `Microgravity Science Glovebox (MSG) with a flow duct, integrated nozzles, cameras and a fuel delivery system, on the ISS` · _verified_
  - [i_Investigation.txt · Comment[Experiment Hardware]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `Microgravity Science Glovebox (MSG)`
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `an apparatus with a flow duct with integrated nozzles, cameras, and fuel delivery systems`
  - [i_Investigation.txt · Comment[Flight Platform]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `International Space Station (ISS)`
- [ ] **Nominal atmosphere**: `{'o2_percent_min': 19.0, 'o2_percent_max': 24.0}` · _verified_
  - note: O2 only: the glovebox was flushed with ISS cabin air whose O2 mole fraction is maintained within 19 to 24 percent (p. 19). No pressure is set: the only pressure in the report is a calculation assumption (burner gas properties at 298 K and 101 kPa, p. 20), not a chamber condition. The experimental table has no O2 or pressure column.
  - [SPICE Final Report 12_2_2012.pdf · p. 19](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/SPICE%20Final%20Report%2012_2_2012.pdf#page=19): `such burns the MSG contents were flushed with ISS cabin air. The oxygen mole fraction of this`
  - [SPICE Final Report 12_2_2012.pdf · p. 19](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/SPICE%20Final%20Report%2012_2_2012.pdf#page=19): `cabin air is maintained within 19 – 24%.`
  - [SPICE Final Report 12_2_2012.pdf · p. 20](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/SPICE%20Final%20Report%2012_2_2012.pdf#page=20): `gas properties at 298 K and 101 kPa.`
- [ ] **Sensor**: `{'instrument': 'still camera', 'measures': 'flame lengths'}` · _verified_
  - note: Still and video cameras together.
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `Data such as flame lengths were recorded using still and video cameras.`
- [ ] **Sensor**: `{'instrument': 'video camera', 'measures': 'flame lengths'}` · _verified_
  - note: Still and video cameras together.
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `Data such as flame lengths were recorded using still and video cameras.`
- [ ] **Sensor**: `{'instrument': 'anemometer', 'measures': 'air velocity'}` · _verified_
  - note: An omni-directional TSI model 8475-3-xx anemometer inside the flow duct near the nozzle connector.
  - [SPICE Final Report 12_2_2012.pdf · p. 12](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/SPICE%20Final%20Report%2012_2_2012.pdf#page=12): `An omni-directional anemometer, TSI model 8475-3-xx, is`
  - [SPICE Final Report 12_2_2012.pdf · p. 12](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/SPICE%20Final%20Report%2012_2_2012.pdf#page=12): `located inside the flow duct near the nozzle connecter to measure the air velocity.`
- [ ] **Earth application**: `Possible insights into better fuel formulations and combustion processes.` · _verified_
  - note: Stated as 'could possibly'.
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/MSG%20%28SolidAndGas%29/SPICE/PSI-107_metadata_PSI-176_SPICE/i_Investigation.txt): `Could possibly provide insights to better fuel formulations and combustion processes.`
