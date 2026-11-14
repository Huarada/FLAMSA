# BASS: review sheet (draft)

Edit `data/manual/BASS.json` to approve: set `review_status` to `reviewed`, `reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page.

- [ ] **Pillars**: `['prevention', 'suppression']` · _inferred_
  - note: Two stated objectives: material flammability in microgravity (prevention) and the effectiveness of an extinguishing agent (suppression). Pillar is the curator's classification, not a source statement.
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `Begin to bridge the gap between the normal gravity NASA-STD-6001 Test#1 method, ground-based microgravity tests, and actual material flammability in microgravity.`
  - [i_Investigation.txt · Comment[Objective]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `Assess the effectiveness of an inert, gaseous extinguishing agent (similar to that used on ISS) in putting out flames over different materials, geometries, preheating, and flow.`
- [ ] **Gravity regime**: `microgravity` · _verified_
  - [i_Investigation.txt · Comment[Project Type]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `Microgravity Investigation`
- [ ] **Hardware**: `Microgravity Science Glovebox (MSG) with a 76 mm x 76 mm flow duct, on the ISS` · _verified_
  - note: The ISA-Tab says airflow up to 40 cm/s; the requirements document plans 5 to 50 cm/s (SRD p. 4). Not reconciled.
  - [i_Investigation.txt · Comment[Experiment Hardware]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `Microgravity Science Glovebox`
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `The experiment was conducted aboard the International Space Station (ISS)`
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `The samples were placed in a small flow duct (76 mm x 76 mm cross section)`
  - [i_Investigation.txt · Comment[Approach]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `airflow speeds reaching as high as 40 cm/s`
  - [SRD_BASS.pdf · p. 4](../../knowledgeBase/Flammable/BASS/SRD_BASS.pdf#page=4): `The airflow speed can be adjusted from 5 to`
  - [SRD_BASS.pdf · p. 4](../../knowledgeBase/Flammable/BASS/SRD_BASS.pdf#page=4): `50 cm/s. Nitrogen is supplied through the nozzle`
- [ ] **Nominal atmosphere**: `{'pressure_psi_min': 14.6959, 'pressure_psi_max': 14.6959}` · _inferred_
  - note: Pressure only (1 atm = 14.6959 psi), taken from slide captions of individual tests; no section states it as a nominal condition for the whole investigation. O2 is not set: the experimental table has no O2 column and the slides show different values (17% in these captions, 22% on p. 31). Do not assume cabin air.
  - [ISS Denver 2013-BASS.pdf · p. 51](../../knowledgeBase/Flammable/BASS/ISS%20Denver%202013-BASS.pdf#page=51): `Atmosphere: 17% O2/N2; 1 atm; Flow speed: 12 cm/s (left to right)`
  - [ISS Denver 2013-BASS.pdf · p. 4](../../knowledgeBase/Flammable/BASS/ISS%20Denver%202013-BASS.pdf#page=4): `More recent tests varying oxygen (below 21%)`
  - [ISS Denver 2013-BASS.pdf · p. 31](../../knowledgeBase/Flammable/BASS/ISS%20Denver%202013-BASS.pdf#page=31): `NOMEX – III, 22% O2, 1 atm`
- [ ] **Sensor**: `{'instrument': 'anemometer', 'measures': 'flow speed'}` · _inferred_
  - note: Stated as the plan in the Science Requirements Document (Feb 2010); the as-flown configuration is not confirmed in the cited documents.
  - [SRD_BASS.pdf · p. 4](../../knowledgeBase/Flammable/BASS/SRD_BASS.pdf#page=4): `to blow air through the duct. An anemometer`
  - [SRD_BASS.pdf · p. 4](../../knowledgeBase/Flammable/BASS/SRD_BASS.pdf#page=4): `is used to measure the actual flow speed.`
- [ ] **Sensor**: `{'instrument': 'radiometer', 'measures': 'flame output'}` · _inferred_
  - note: Stated as the plan in the Science Requirements Document (Feb 2010); the as-flown configuration is not confirmed in the cited documents.
  - [SRD_BASS.pdf · p. 4](../../knowledgeBase/Flammable/BASS/SRD_BASS.pdf#page=4): `A radiometer measures flame output.`
- [ ] **Sensor**: `{'instrument': 'still camera'}` · _verified_
  - note: A digital still camera (2013 ISS R&D slide: it 'provided bulk' of the data, continued on the next printed line); the requirements document also plans still cameras.
  - [ISS Denver 2013-BASS.pdf · p. 10](../../knowledgeBase/Flammable/BASS/ISS%20Denver%202013-BASS.pdf#page=10): `Video and digital still camera provided bulk`
  - [SRD_BASS.pdf · p. 4](../../knowledgeBase/Flammable/BASS/SRD_BASS.pdf#page=4): `still cameras are used to image the flame.`
- [ ] **Sensor**: `{'instrument': 'video camera'}` · _verified_
  - note: Same slide as the still camera: video and digital still camera provided the bulk of the data (continued on the next printed line).
  - [ISS Denver 2013-BASS.pdf · p. 10](../../knowledgeBase/Flammable/BASS/ISS%20Denver%202013-BASS.pdf#page=10): `Video and digital still camera provided bulk`
- [ ] **Earth application**: `Validated combustion models apply to many terrestrial combustion problems.` · _verified_
  - [i_Investigation.txt · Comment[Research Impacts]](../../knowledgeBase/Flammable/BASS/PSI-26_metadata_PSI-102_BASS/i_Investigation.txt): `These models have wide applicability to the general understanding of many terrestrial combustion problems`
