# SLICE: review sheet (draft)

Edit `data/manual/SLICE.json` to approve: set `review_status` to `reviewed`, `reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page.

- [ ] **Pillars**: `[]` · _inferred_
  - note: No direct fire-safety pillar stated. The science objectives of the design review are lift-off and blow-out velocity limits of methane and ethylene flames, the hysteresis of lifting and reattachment, and the structure of the flame base. The cited review does not mention fire safety. Pillar list left empty on purpose; the reviewer should decide.
  - [SLICE IP-A SRDR.pdf · p. 7](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=7): `Identify the lift-off velocity limits in air`
  - [SLICE IP-A SRDR.pdf · p. 7](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=7): `Characterize the structure of the flame,`
  - [SLICE IP-A SRDR.pdf · p. 7](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=7): `possible, also identify the blow-out`
  - [SLICE IP-A SRDR.pdf · p. 7](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=7): `Characterize the hysteresis of flame`
- [ ] **Gravity regime**: `microgravity` · _inferred_
  - note: Planned for the ISS in the Microgravity Science Glovebox (design review text, future tense): SLICE reuses the SPICE hardware on the ISS (p. 2) and the acceleration environment is to be measured by SAMS in the MSG work volume (p. 9); mapped to the microgravity regime.
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `SLICE will utilize the SPICE hardware currently on ISS`
  - [SLICE IP-A SRDR.pdf · p. 9](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=9): `The acceleration environment will be measured by SAMS during SLICE`
  - [SLICE IP-A SRDR.pdf · p. 9](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=9): `testing which will be installed into the MSG Work Volume.`
- [ ] **Hardware**: `SPICE hardware re-flown on the ISS (experiment assembly, control box, video camera) with new burner tubes of 2.1 mm and 3.2 mm, an upgraded Nikon still camera and a ceramic pyrometry fiber` · _inferred_
  - note: From the SLICE/BASS System Requirements Design Review of 14 April 2010, written in the future tense ('will'); the as-flown configuration is not confirmed in the cited lines. The SLICE documents sit in the BASS folder of knowledgeBase/, not in the SLICE folder, which holds only the experimental table.
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `SLICE will utilize the SPICE hardware currently on ISS`
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `Experiment Assembly, Cables, Control Box, Video Camera`
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `2.1 mm and 3.2 mm burner tubes`
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `Upgraded Nikon Still Camera`
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `Ceramic Pyrometry Fiber`
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `SLICE will design, fabrication, assemble, test new`
- [ ] **Nominal atmosphere**: `None` · _not_reported_
  - note: The experimental table carries no O2 or pressure. Read for a test atmosphere: the SLICE IP-A SRDR and the two safety assessment reports SLICE ED-04 and ED-05 (SAR-1, SAR-2): they say how O2 (a Compound Specific Analyzer or the Major Constituent Analyzer) and cabin pressure (Columbus transducers) will be measured, but give no value. Not searched: the crew-training slides (IP-C, IP-D), the SPICE video-overlay procedure and the SPICE documents. Do not assume cabin air.
  - [SLICE IP-A SRDR.pdf · p. 8](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=8): `Project will include steps in crew procedures to install a Compound Specific Analyzer`
  - [SLICE IP-A SRDR.pdf · p. 9](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=9): `Cabin pressure will be measured by 4 pressure transducers in the`
- [ ] **Sensor**: `{'instrument': 'still camera', 'measures': 'soot pyrometry or lift-off limits'}` · _inferred_
  - note: From the SLICE/BASS System Requirements Design Review of 14 April 2010, written in the future tense ('will'); the as-flown configuration is not confirmed in the cited lines. The SLICE documents sit in the BASS folder of knowledgeBase/, not in the SLICE folder, which holds only the experimental table. A Nikon D300s with an optional blue-green BG-7 filter.
  - [SLICE IP-A SRDR.pdf · p. 9](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=9): `A Nikon D300s camera with a blue-green BG-7 filter that can installed or`
  - [SLICE IP-A SRDR.pdf · p. 11](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=11): `camera for soot pyrometry or liftoff limits are determined for at`
- [ ] **Sensor**: `{'instrument': 'video camera'}` · _inferred_
  - note: From the SLICE/BASS System Requirements Design Review of 14 April 2010, written in the future tense ('will'); the as-flown configuration is not confirmed in the cited lines. The SLICE documents sit in the BASS folder of knowledgeBase/, not in the SLICE folder, which holds only the experimental table. Part of the reused SPICE hardware.
  - [SLICE IP-A SRDR.pdf · p. 2](../../knowledgeBase/Flammable/BASS/SLICE%20IP-A%20SRDR.pdf#page=2): `Experiment Assembly, Cables, Control Box, Video Camera`
