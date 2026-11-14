# SAFFIRE-II: review sheet (draft)

Edit `data/manual/SAFFIRE-II.json` to approve: set `review_status` to `reviewed`, `reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page.

- [ ] **Pillars**: `['prevention']` · _inferred_
  - note: Objectives are fire growth rate and the low-g flammability limit of a material; the second is the prevention pillar (material selection depends on flammability limits). Pillar is the curator's classification, not a source statement.
  - [SAFFIRE-II DoD.docx · para 1](../../knowledgeBase/Flammable/SAFFIRE2/SAFFIRE-II%20DoD.docx): `investigate the low-g flammability limits compared to those obtained in NASA’s normal gravity material flammability screening test`
  - [document.pdf · p. 4](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=4): `Maximum Oxygen Concentration (MOC) flammability limits in long-term low gravity.2 The configuration for these`
- [ ] **Gravity regime**: `microgravity` · _inferred_
  - note: The sources say 'low-gravity'; mapped to the microgravity regime.
  - [document.pdf · p. 4](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=4): `Maximum Oxygen Concentration (MOC) flammability limits in long-term low gravity.2 The configuration for these`
- [ ] **Hardware**: `Saffire experiment unit in the Cygnus vehicle: flow duct with an adjacent avionics bay` · _verified_
  - [SAFFIRE-I Operations.pdf · p. 1](../../knowledgeBase/Flammable/SAFFIRE/SAFFIRE-I%20Operations.pdf#page=1): `The Saffire experiments are conducted in three consecutive flights of the Cygnus vehicle.`
  - [document.pdf · p. 3](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=3): `The experiment package consists of a flow duct and an adjacent avionics bay as shown in`
- [ ] **Nominal atmosphere**: `{'o2_percent_min': 21.0, 'o2_percent_max': 21.0}` · _inferred_
  - note: O2 only, near 21 percent: a pre-flight expectation ('will be nearly 21%', paper p. 4), not a measurement; the experimental table reports 21.5 to 22.1 percent measured. No source gives the pressure.
  - [document.pdf · p. 4](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=4): `nearly 21% by volume—the same as in the ISS when the hatch was closed.`
- [ ] **Sensor**: `{'instrument': 'O2 sensor', 'measures': 'oxygen concentration'}` · _inferred_
  - note: Describes the Saffire experiment package in a pre-flight paper (written 'will be'); the as-flown configuration is not confirmed here. The DoD says the sensor suite is common to Saffire-I, II and III (Table 3, not extractable as text). Measured at the inlet of the avionics bay.
  - [document.pdf · p. 3](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=3): `The oxygen and CO2 concentrations will be measured at the inlet of the avionics bay so that`
- [ ] **Sensor**: `{'instrument': 'CO2 sensor', 'measures': 'CO2 concentration'}` · _inferred_
  - note: Describes the Saffire experiment package in a pre-flight paper (written 'will be'); the as-flown configuration is not confirmed here. The DoD says the sensor suite is common to Saffire-I, II and III (Table 3, not extractable as text). Measured at the inlet of the avionics bay.
  - [document.pdf · p. 3](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=3): `The oxygen and CO2 concentrations will be measured at the inlet of the avionics bay so that`
- [ ] **Sensor**: `{'instrument': 'pressure sensor', 'measures': 'pressure'}` · _inferred_
  - note: Describes the Saffire experiment package in a pre-flight paper (written 'will be'); the as-flown configuration is not confirmed here. The DoD says the suite is common to Saffire-I, II and III (its diagnostics table is an image and cannot be quoted). Called a pressure transducer in the paper.
  - [document.pdf · p. 3](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=3): `A pressure transducer will also measure the pressure`
- [ ] **Sensor**: `{'instrument': 'anemometer', 'measures': 'flow velocity in the duct'}` · _inferred_
  - note: Describes the Saffire experiment package in a pre-flight paper (written 'will be'); the as-flown configuration is not confirmed here. The DoD says the sensor suite is common to Saffire-I, II and III (Table 3, not extractable as text). Two anemometers, one on each side of the sample.
  - [document.pdf · p. 3](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=3): `Two flow anemometers, one on each side of the sample will quantify the flow velocity in the duct and`
- [ ] **Sensor**: `{'instrument': 'video camera'}` · _inferred_
  - note: Describes the Saffire experiment package in a pre-flight paper (written 'will be'); the as-flown configuration is not confirmed here. The DoD says the sensor suite is common to Saffire-I, II and III (Table 3, not extractable as text). Two cameras, located in the avionics bay.
  - [document.pdf · p. 3](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=3): `Two video cameras located in the avionics bay will provide front`
- [ ] **Sensor**: `{'instrument': 'radiometer', 'measures': 'broadband radiative emission from the sample'}` · _inferred_
  - note: Describes the Saffire experiment package in a pre-flight paper (written 'will be'); the as-flown configuration is not confirmed here. The DoD says the sensor suite is common to Saffire-I, II and III (Table 3, not extractable as text). Four radiometers: two viewing the front of the sample, two the back.
  - [document.pdf · p. 4](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=4): `Four calibrated radiometers, two viewing the front of the sample and two viewing the back, will measure the`
  - [document.pdf · p. 4](../../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf#page=4): `broadband radiative emission from the sample to provide an estimate of the radiative flux from the burning zone`
