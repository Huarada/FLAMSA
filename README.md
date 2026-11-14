<div align="center">

<img src="src/psi_fire/interface/assets/flamsa.svg" alt="FLAMSA" width="260">

### NASA microgravity combustion data, organized for fire-safety work in crewed habitats

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Pydantic v2](https://img.shields.io/badge/schema-Pydantic%20v2-E92063)
![Data: NASA PSI](https://img.shields.io/badge/data-NASA%20PSI-0B3D91)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)

15 ISS investigations and 1,615 curated records, each traceable to the cell, page or quote it came from.

</div>

<p align="center">
  <img src="docs/screenshots/homepage-lovable-motion-desktop.png" alt="FLAMSA home: interactive combustion chamber" width="88%">
</p>

---

## Contents
1. [Why FLAMSA](#why-flamsa)
2. [The dashboard](#the-dashboard)
3. [The data](#the-data)
4. [Physical consistency rules](#physical-consistency-rules)
5. [The lunar-habitat question](#the-lunar-habitat-question)
6. [Architecture](#architecture)
7. [Quick start](#quick-start)
8. [Known limits](#known-limits)
9. [Repository map](#repository-map)
10. [References](#references)

---

## Why FLAMSA

Fire behaves differently on a spacecraft, a station, a lunar or Martian base or a pressurized rover than it does on Earth. With no buoyancy there is no rising plume, so oxygen reaches the flame by diffusion or through the ventilation flow. Planned exploration habitats also run at lower pressure and higher oxygen than the ISS, and ground screening tests were not designed for that combination.

NASA's [Physical Sciences Informatics (PSI)](https://psi.nasa.gov) archive has years of ISS combustion experiments, spread across spreadsheets, ISA-Tab folders and PDF reports in different formats. We built FLAMSA to make that material usable for fire-safety questions. In practice that meant four jobs:

- **Curation.** Each investigation is mapped to a common schema with canonical units, and the original cell text is kept next to every normalized value.
- **Checks against physics.** Each table is tested against relations stated in its own reports. Values that cannot be physically right are set aside with a note instead of being quietly corrected.
- **Exploration.** The dashboard filters, compares and fits the data, and shows what it excluded and why.
- **Citation.** Claims point to an archived file, a page and a quote that can be found with Ctrl+F.

We do not fill gaps. A missing value stays missing, an inferred one is marked as inferred with the reason, and the source string is always kept.

---

## The dashboard

The workspace has five destinations. One set of research filters drives all of them: investigation, record level, fuel phase, O₂/pressure/flow intervals, review state, hardware, sensors and fire-safety pillar.

| Destination | Contents |
|---|---|
| **Home** | Interactive chamber scene with four entry points (flame behavior, Earth applications, exploration habitats, detection and diagnostics) and live archive counts. |
| **Dashboard** | KPI cards, a scatter of reported tests for any compatible pair of quantities, records per investigation, and reported O₂/pressure/flow envelopes. Every omitted record has a stated reason. |
| **Fire behavior** | Three source-bounded analyses: FLEX burning rate vs O₂ (adjusted slopes with 95% intervals), BASS-II O₂ consumed vs CO₂ produced, and SAFFIRE-II microgravity vs 1 g outcomes. Exports reproducible JSON and CSV. |
| **Investigations** | Catalog, objective, review status, sensors and hardware with quotes, a full TestPoint table and a record inspector showing the raw value and provenance. |
| **Evidence** | Citations with page anchors and downloads of the archived source files, with checksums. |

<table>
<tr>
<td width="50%"><img src="docs/screenshots/fire-behavior-flex.png" alt="FLEX burning rate vs oxygen"><br><sub><b>Fire behavior · FLEX.</b> Burning-rate constant vs O₂ per fuel, colored by diluent, with the adjusted slope and its 95% interval.</sub></td>
<td width="50%"><img src="docs/screenshots/fire-behavior-bass.png" alt="BASS-II gas changes"><br><sub><b>Fire behavior · BASS-II.</b> O₂ consumed vs CO₂ produced in the same burn. The points follow the stoichiometric ratio.</sub></td>
</tr>
<tr>
<td width="50%"><img src="docs/screenshots/filter-integration.png" alt="Dashboard"><br><sub><b>Dashboard.</b> Filters apply to every card. The chart lists the investigations that have no plottable pair and the reason.</sub></td>
<td width="50%"><img src="docs/screenshots/fire-behavior-saffire.png" alt="SAFFIRE-II outcomes"><br><sub><b>Fire behavior · SAFFIRE-II.</b> Raw microgravity and 1 g outcomes side by side. Labels such as "Complete" and "Acceleratory" stay as text.</sub></td>
</tr>
</table>

> The Research copilot panel is in the layout but marked *Not connected*. Scenario ranking and the LLM explanation with checked citations come next (see [Known limits](#known-limits)).

---

## The data

| Investigation | PSI | Phase | Fuels (curated names) | Records |
|---|---|---|---|---:|
| **FLEX** | PSI-69 | liquid droplets | heptane, methanol | 274 |
| **FLEX-2** | PSI-68 | liquid droplets | decane, ethanol, heptane, iso-octane, n-octane and blends | 8 (test matrix) |
| **CFI** | PSI-39 | liquid droplets | n-dodecane, n-dodecane + iso-dodecane | 87 |
| **ACME-CFI-G** | PSI-159 | gas, spherical burner | ethane, propane, butane | 333 |
| **ACME-BRE** | PSI-20 | gas | ethylene, methane | 18 (test days) |
| **ACME-E-FIELD** | PSI-22 | gas, electric field | ethylene, methane | 21 (test days) |
| **SPICE** | PSI-107 | gas jet in coflow | ethylene, methane, propane, propylene (pure and N₂-diluted) | 469 |
| **SLICE** | PSI-106 | gas jet | ethane, ethylene, methane | 12 (test days) |
| **BASS** | PSI-26 | solid | PMMA, SIBAL, Nomex, Ultem, waxes | 122 |
| **BASS-II** | PSI-25 | solid | PMMA, SIBAL, Nomex, Japan wax | 129 |
| **SAFFIRE-I / II / III** | PSI-98 / 99 / 100 | solid, large scale | SIBAL, PMMA, silicone, PMMA + Nomex | 2 / 9 / 2 |
| **SAME** | PSI-102 | solid, smoke | Kapton, Teflon, silicone rubber, lampwick, DBP | 20 |
| **SAME-R** | PSI-101 | solid, smoke | Kapton, Teflon, silicone rubber, lampwick, Pyrell | 109 |
| | | | **Total** | **1,615** |

Curation rules:
- Units are part of the column name: `pressure_psi`, `o2_percent`, `flow_speed_cm_s`, length in `mm`, time in `s`. Conversions are named constants, for example 1 mmHg = 0.0193368 psi.
- `<column>_raw` keeps the source string whenever it differs from the normalized value.
- Each row records its source file (resolved through `data/sources.json`), source row, `provenance_status ∈ {verified, inferred, missing}` and a `provenance_note`.
- Each hand-curated claim cites one printed line or one DOCX paragraph and is verified mechanically against the archived file.
- The output is one folder per investigation, `data/curated/<ID>/test_points.csv` plus `investigation.json`. Both load directly into pandas or any other tool.

---

## Physical consistency rules

Before a table is used on the dashboard, we check it against the physics described in that investigation's own reports. For each rule below you will find the governing relation, what the curated data gives when you test it, the passage in the source that states it, and the test in [`tests/infrastructure/test_physical_consistency.py`](tests/infrastructure/test_physical_consistency.py) that runs it on every curation. The checks also catch pipeline mistakes: a swapped column or a wrong unit conversion breaks at least one of them.

Quotes are copied exactly from the archived file. The numbers in brackets point to the [References](#references).

### R1 · Droplets obey the d² law (FLEX)

In quasi-steady burning, the droplet surface regresses at a constant rate. The square of the diameter therefore falls linearly in time:

```math
d(t)^2 \;=\; d_0^{\,2} \;-\; K\,t
\qquad\Longrightarrow\qquad
t_b \;=\; \frac{d_0^{\,2} - d_e^{\,2}}{K}
```

Here $`d_0`$ is the initial diameter, $`d_e`$ the diameter at flame extinction ($`0`$ if the droplet burned out), $`K`$ the burning-rate constant in mm²/s, and $`t_b`$ the burn time.

FLEX reports $`d_0`$, $`d_e`$, $`K`$ and $`t_b`$ in separate columns, so the law can be tested directly against the table:

```math
\operatorname{median}\!\left(\frac{t_b^{\text{reported}}}{(d_0^{2}-d_e^{2})/K}\right) = 1.04
\qquad (n = 257,\ \text{IQR } 0.99\text{–}1.08)
```

The outliers are flames that went out just after ignition ($`d_e \approx d_0`$); for those the denominator is close to zero.

> "diameter should decrease linearly with time with Ko being constant"
>
> Liu, Trenou, Rah, Hicks and Avedisian, *Effect of Varying the Initial Diameter of n-Octane and n-Decane Droplets over a Wide Range on the Spherically Symmetric Combustion Process* [1], p. 2. The paper measures n-octane and n-decane on the ISS and takes the law from Turns, *An Introduction to Combustion* [2].

### R2 · More oxygen burns a droplet faster (FLEX)

Classical droplet theory links $`K`$ to the Spalding transfer number $`B`$, which grows with the ambient oxygen mass fraction $`Y_{O_2,\infty}`$:

```math
K \;=\; \frac{8\,\lambda_g}{\rho_\ell\,c_{p,g}}\,\ln\!\left(1 + B\right),
\qquad
B \;=\; \frac{c_{p,g}\,(T_\infty - T_s) \;+\; Y_{O_2,\infty}\,\Delta h_c/\nu}{h_{fg}}
\qquad\Longrightarrow\qquad
\frac{\partial K}{\partial Y_{O_2,\infty}} > 0
```

Here $`\lambda_g`$ and $`c_{p,g}`$ are the gas thermal conductivity and heat capacity, $`\rho_\ell`$ the liquid density, $`\Delta h_c`$ the heat of combustion, $`\nu`$ the stoichiometric O₂/fuel mass ratio and $`h_{fg}`$ the latent heat.

On the *Fire behavior → FLEX* tab, each fuel and diluent blend near 1 atm gets its own ordinary least-squares fit:

```math
K_i \;=\; \beta_0 \;+\; \beta_{O_2}\,X_{O_2,i} \;+\; \beta_P\,P_i \;+\; \beta_d\,d_{0,i} \;+\; \varepsilon_i,
\qquad
\hat\beta_{O_2} \;\pm\; t_{0.975,\;n-p}\;\operatorname{SE}\!\big(\hat\beta_{O_2}\big)
```

Pressure and initial diameter are included only when they vary within the group. A group is fitted when it has at least 6 tests, 3 distinct O₂ levels, 3 residual degrees of freedom and a condition number no higher than 10⁴. With the current data:

| Stratum (≈ 1 atm) | n | $`\hat\beta_{O_2}`$ (mm²/s per O₂ point) | 95% interval | Tested O₂ |
|---|---:|---:|---|---|
| heptane · N₂ | 32 | **0.0185** | 0.0062 – 0.0307 | 13–30% |
| methanol · N₂ | 41 | **0.0183** | 0.0157 – 0.0209 | 12–30% |

The diluent matters as well. Helium conducts heat better than nitrogen, and median heptane $`K`$ rises from 0.56 to 0.65 mm²/s with it; CO₂ radiates heat away and gives the lowest values. If the diluents are plotted together the O₂ trend washes out, so the charts keep them apart.

> "The ambient oxygen mole fraction influences the burning rate, extinction diameter, flame chem-"
>
> Williams et al., *Science Requirements Document: Fundamental Studies in Droplet Combustion and Flame Extinguishment in Microgravity (FLEX-2)* [3], p. 42. The document does not give the sign of the effect; that comes from the theory above.

### R3 · Extinction diameter scales with initial diameter (FLEX)

```math
d_e \;\propto\; d_0 \qquad (\text{radiative extinction})
```

Spearman $`\rho(d_e, d_0)`$ is 0.62 for methanol and 0.86 for heptane. Only heptane, which soots, burns more slowly as $`d_0`$ grows; a larger sooty flame loses more heat by radiation.

A droplet that broke apart never reached an extinction diameter, so a `0` recorded for a *disruption* outcome is treated as missing (the raw `0` is kept).

> "Theory1 suggests a linear relationship between extinction diameter, de , and initial droplet diameter, d0"
>
> Hicks, Dietrich, Nayagam and Williams, *Dynamics of Water Absorption and Evaporation During Methanol Droplet Combustion in Microgravity* [4], slide 11. The "1" marks the slide's footnote to Zhang, Card and Williams, *Combustion and Flame* (1996).

### R4 · The stoichiometric mixture fraction follows from the composition (ACME-CFI-G)

For a fuel stream (mass fraction $`Y_F`$, balance N₂) facing an oxidizer stream (mass fraction $`Y_{O_2}`$, balance N₂):

```math
Z_{st} \;=\; \left(1 + \frac{s\,Y_F}{Y_{O_2}}\right)^{-1},
\qquad
s \;=\; \frac{\nu_{O_2}\,W_{O_2}}{W_F}
\quad
\left(\begin{array}{l}
\mathrm{C_2H_6}:\ s = 3.72\\
\mathrm{C_3H_8}:\ s = 3.63\\
\mathrm{C_4H_{10}}:\ s = 3.58
\end{array}\right),
\qquad
Y_k \;=\; \frac{X_k\,W_k}{X_k\,W_k + (1 - X_k)\,W_{N_2}}
```

We recomputed $`Z_{st}`$ from the reported O₂ and fuel mole fractions for all 331 flames, normal and inverse. The largest difference from the reported value is

```math
\max_i \left| Z_{st,i}^{\text{recomputed}} - Z_{st,i}^{\text{reported}} \right| \;=\; 4\times10^{-5}
```

That agreement would not survive a swapped or mis-converted oxygen or fuel column.

> "where Zst and Tad are respectively the stochiometric mixture fraction and adiabatic flame"
>
> Stocker, Sunderland, Axelbaum and Williams, *ACME/CFI-G Final Report: Advanced Combustion via Microgravity Experiments, Cool Flames Investigation with Gases* [5], p. 29.

### R5 · A sealed chamber loses oxygen test after test (ACME-CFI-G)

Mass balance in a closed volume: each flame consumes O₂, and nothing adds O₂ until the chamber is vented and refilled.

```math
X_{O_2}^{\,\text{after}}(n) \;\le\; X_{O_2}^{\,\text{before}}(n),
\qquad
X_{O_2}^{\,\text{before}}(n+1) \;=\; X_{O_2}^{\,\text{after}}(n)
\quad\text{within one chamber fill}
```

The first relation holds for all 179 normal flames. The second holds to $`10^{-6}`$ in 156 of 168 consecutive same-day pairs; the other 12 are new chamber fills. Within a test day, then, O₂ drifts down from test to test and should not be read as a freely chosen condition.

> "recirculation during CFI-G test operations was only conducted prior to venting: (1) at the end of a test day and/or (2) between atmospheres"
>
> Stocker et al., *ACME/CFI-G Final Report* [5], p. 19.

### R6 · Burning consumes O₂ and produces CO₂ in stoichiometric proportion (BASS-II)

PMMA burns as

```math
\mathrm{C_5H_8O_2} \;+\; 6\,\mathrm{O_2} \;\longrightarrow\; 5\,\mathrm{CO_2} \;+\; 4\,\mathrm{H_2O}
\qquad\Longrightarrow\qquad
\frac{\Delta X_{CO_2}}{\Delta X_{O_2}} \;=\; \frac{5}{6} \;\approx\; 0.833
```

For the 24 PMMA burns whose O₂ dropped by more than 0.2 points, the least-squares slope through the origin of CO₂ produced against O₂ consumed (the *Fire behavior → BASS-II* chart) is

```math
\widehat{\left(\frac{\Delta X_{CO_2}}{\Delta X_{O_2}}\right)}_{\mathrm{PMMA}} \;=\; 0.822
\qquad \text{vs. } 0.833 \text{ predicted}
```

CO₂ never falls by more than the 0.1% resolution of the sensor.

The size of the glovebox limits how much O₂ a burn can remove:

```math
m_{O_2} \;=\; \frac{\Delta X_{O_2}\,P\,V}{R\,T}\,W_{O_2}
\;\approx\; 33\ \text{g for }\Delta X_{O_2} = 10\ \text{points in } V = 250\ \text{L}
\;\;\Rightarrow\;\; \approx 17\ \text{g of PMMA}
```

Five final-O₂ readings (1.6, 0.6, 0.9, 39.1 and 40.4%) would require burning more than 30 g of PMMA, or an oxygen source the glovebox does not have. They are treated as missing, with the raw values kept. Negative CO readings come from sensor zero offset and are handled the same way.

> "The O2 decreased during each burn and the CO and CO2 increased accordingly."
>
> Olson, Ferkul, Bhattacharjee, Miller, Fernandez-Pello, Link, T'ien et al., *Burning and Suppression of Solids-II (BASS-II) Summary Report* [6], p. 14. The 250 L work volume is given on p. 87.

### R7 · Spread rate equals burned length over burn time (SAFFIRE-II)

```math
v_f \;=\; \frac{L_b}{t_b}
```

The source lists $`L_b`$, $`t_b`$ and $`v_f`$ in separate columns. $`290\,\text{mm}/145\,\text{s} = 0.20`$ cm/s against 0.21 reported, and $`290/115 = 0.25`$ cm/s against 0.26.

The SAFFIRE-II tab also shows the result the experiment was built to test. Silicone samples burned completely in 1 g but did not spread in microgravity with 20 cm/s of concurrent flow, so the 1 g screening outcome did not carry over to orbit.

### R8 · Mass flow equals volume flow times gas density (SPICE)

```math
\dot m \;=\; \dot V\,\rho,
\qquad
\rho \;=\; \frac{P\,\overline{W}}{R\,T},
\qquad
\overline{W}_{\,75\%\,\mathrm{C_3H_6}/\mathrm{N_2}} \;=\; 0.75\,(42.08) + 0.25\,(28.01) \;=\; 38.56\ \mathrm{g\,mol^{-1}}
```

| Gas (at 101.325 kPa) | $`\rho`$ at 294 K | $`\rho`$ at 300 K | Implied by the SPICE table |
|---|---:|---:|---:|
| propylene | 1.743 | 1.709 | **1.709** |
| 50% propylene / N₂ | 1.452 | 1.424 | **1.423** |
| 75% propylene / N₂ | 1.598 | 1.567 | **1.566** (96 rows), 0.651 (36 rows) |
| methane | 0.665 | 0.652 | **0.651** |

The implied density $`\rho = 60\,\dot m / \dot V`$ (mg/s and sccm) is constant within ±0.2% for each gas and matches the ideal-gas value at about 300 K.

36 rows labeled *75 % Propylene* give methane's density instead, which puts their mass flows about 2.4 times too low. Both mass-flow columns in those rows are treated as missing, with the raw values and a note kept; the volume flow is unchanged. We did not compute a replacement mass flow, since that would put a calculation where a measurement was.

> "75% propylene mixed with 25% nitrogen in moles, and 50% propylene mixed with 50% nitrogen in moles"
>
> Urban, Sunderland and Yuan, *Smoke Point in Co-flow Experiment (SPICE): Laminar Smoke Point Properties of Non-buoyant Round-Jet Diffusion Flames*, Final Report [7], p. 9.

### How violations are handled

| Situation | Action | Example |
|---|---|---|
| Value breaks a physical law | Set to missing, raw kept, row `inferred` with the reason | BASS-II final O₂ of 40.4% |
| Value contradicts another cell, and nothing settles which one is right | Value kept, conflict note added, row stays `verified` | ACME-CFI-G 21106 F4: "no hot ignition" with a 22 s burn |
| Composition does not close | Kept, with a note; never normalized | CFI r13–r16: O₂ + N₂ + He = 0.97 |
| Plausible fix, but the sources disagree | Kept missing until an archived source settles it | SAFFIRE-II thickness `037 mm` (NASA sources give 0.33, 0.36 or 0.37 mm) |

The full review is in [`docs/DATA_QUALITY_REVIEW.md`](docs/DATA_QUALITY_REVIEW.md), and the decisions are in [`docs/ADR.md`](docs/ADR.md) (ADR-0067 and ADR-0080).

---

## The lunar-habitat question

> *"Which microgravity evidence is relevant to a lunar base at ≥ 30% O₂ and ≤ 10.2 psi?"*

Before anything else, the data has to say how much of it applies:

```math
\#\big\{\,\text{tests} : X_{O_2} \ge 30\%\ \wedge\ P \le 10.2\ \text{psi}\,\big\}_{\text{FLEX}} \;=\; 0,
\qquad
\#\big\{\,\cdots\ \wedge\ P \le 10.5\ \text{psi}\,\big\}_{\text{FLEX}} \;=\; 17\ \ (10.33\text{–}10.50\ \text{psi})
```

- Only FLEX and ACME-CFI-G report O₂ and pressure together for each test.
- The near-1 atm slopes from R2 are not extended to 10.2 psi.
- The PSI has no partial-gravity data, so lunar gravity can only be bracketed by the microgravity and 1 g results.

---

## Architecture

The code follows Clean Architecture with domain-driven design, and dependencies point inward. Scores will be computed in the domain layer; the planned LLM step only describes them.

```mermaid
flowchart LR
    KB[("knowledgeBase/<br/>raw PSI files<br/>(read-only)")] --> REG["data/sources.json<br/>registry"]
    REG --> ING["infrastructure/ingestion<br/>adapters · fixups · unit parser"]
    MAN[("data/manual/<br/>quoted metadata")] --> ING
    ING --> CUR[("data/curated/ID/<br/>test_points.csv + investigation.json")]
    CUR --> REPO["CuratedRepository"]
    REPO --> APP["application<br/>explore · chart_data · fire_behavior · statistics"]
    APP --> UI["interface<br/>Streamlit workspace"]
    DOM["domain<br/>model · units · matching<br/>(pure, no I/O)"] -.-> ING
    DOM -.-> APP
```

| Layer | Holds | Must not import |
|---|---|---|
| `domain` | `Investigation`, `TestPoint`, `Quantity`, `Provenance`, unit conversion, interval matching | pandas, Streamlit, LangGraph, I/O |
| `application` | Use cases, ports, chart projections, least-squares statistics | pandas, Streamlit |
| `infrastructure` | Source registry, CSV/ISA-Tab adapters, evidence verifier, repository | no restriction |
| `interface` | Streamlit composition root and views | business rules |

Every architectural decision, trade-off, bug and fix is logged in [`docs/ADR.md`](docs/ADR.md).

---

## Quick start

```bash
git clone https://github.com/Huarada/FLAMSA.git && cd FLAMSA
python -m pip install -e ".[dashboard,dev]"

# Optional: rebuild data/curated from knowledgeBase (the committed output is already up to date)
PYTHONPATH=src python -m psi_fire.interface.curate_cli

# Verify: lint, strict types on the domain, full test suite
ruff check . && mypy src/psi_fire/domain && pytest -q

# Run the dashboard at http://localhost:8501
streamlit run src/psi_fire/interface/app.py
```

No API key or internet connection is needed to explore the data. Python 3.11 or later. Verifying page-anchored quotes in PDFs additionally needs `pdftotext` (poppler).

To use the data in your own models, load `data/curated/*/test_points.csv`. Every column carries its unit, and `<column>_raw` and `provenance_*` let you filter by data quality. *Fire behavior* also exports each analysis as JSON and CSV, with the dataset revision and the record ids.

---

## Known limits

- There is no partial-gravity data in the PSI. E-FIELD uses electric fields to emulate partial gravity, which is not the same as lunar data.
- The slopes and intervals describe associations inside the tested ranges. They are not safety limits, and anything outside those ranges is an extrapolation.
- Not built yet: deterministic relevance ranking for a habitat scenario, citation-validated LLM narration (the copilot is shown as *Not connected*), and the one-click clean-dataset export bundle.
- Source defects we could not repair are documented, not patched: [`docs/DATA_QUALITY_REVIEW.md`](docs/DATA_QUALITY_REVIEW.md), [`docs/zip-removal-report.json`](docs/zip-removal-report.json).
- Rockets and propellants are out of scope.

---

## Repository map

```
knowledgeBase/        raw NASA PSI files (immutable)
data/
  sources.json        investigation id → raw files (the only place raw paths live)
  manual/             hand-curated metadata with 1:1 evidence quotes
  external/           archived external pages (HTML/PDF + SHA-256 + capture time)
  curated/<ID>/       test_points.csv + investigation.json  ← use these
src/psi_fire/
  domain/             entities, value objects, units (pure)
  application/        use cases, chart projections, fire-behavior statistics
  infrastructure/     ingestion adapters, repository, evidence verifier
  interface/          Streamlit workspace (app.py = composition root)
tests/                domain · application · infrastructure (incl. physics) · interface
docs/                 ADR log, data-quality review, dashboard and method notes, specs
```

Further reading: [dashboard guide](docs/dashboard.md) · [fire-behavior methods](docs/fire-behavior.md) · [data-quality review](docs/DATA_QUALITY_REVIEW.md) · [decision log](docs/ADR.md)

---

## References

Every document below is archived in `knowledgeBase/`, so the quotes can be checked against the file.

1. Y. C. Liu, K. N. Trenou, J. Rah, M. C. Hicks, C. T. Avedisian. *Effect of Varying the Initial Diameter of n-Octane and n-Decane Droplets over a Wide Range on the Spherically Symmetric Combustion Process: International Space Station and Ground-based Experiments.* 8th U.S. National Combustion Meeting, paper 070HE-0310, University of Utah, May 2013. `knowledgeBase/suppression/FLEX/2G11-070HE-0310.pdf`
2. S. R. Turns. *An Introduction to Combustion: Concepts and Applications*, 2nd ed. McGraw-Hill, 2000, p. 376. Cited by [1]; not archived here.
3. F. A. Williams (research team lead), D. L. Dietrich, M. C. Hicks, V. Nayagam et al. *Science Requirements Document: Fundamental Studies in Droplet Combustion and Flame Extinguishment in Microgravity (FLEX-2).* NASA. `knowledgeBase/suppression/FLEX2/FLEX-2 SRD Final.pdf`
4. M. C. Hicks, D. L. Dietrich, V. Nayagam, F. A. Williams. *Dynamics of Water Absorption and Evaporation During Methanol Droplet Combustion in Microgravity.* 28th Annual Meeting of the American Society for Space and Gravitational Research (as printed on the cover), Nov.–Dec. 2012. `knowledgeBase/suppression/FLEX/20130010979.pdf`
5. D. P. Stocker, P. B. Sunderland, R. L. Axelbaum, F. A. Williams. *ACME/CFI-G Final Report: Advanced Combustion via Microgravity Experiments (ACME), Cool Flames Investigation with Gases (CFI-G).* NASA Glenn Research Center, 21 November 2022. `knowledgeBase/ACME/CFI-G/PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf`
6. S. L. Olson, P. V. Ferkul, S. Bhattacharjee, F. J. Miller, C. Fernandez-Pello, S. Link, J. S. T'ien, I. Wichman et al. *Burning and Suppression of Solids-II (BASS-II) Summary Report.* NASA/TM-20210011385. `knowledgeBase/Flammable/BASS2/BASS-II Summary Report.pdf`
7. D. L. Urban, P. B. Sunderland, Z.-G. Yuan. *Smoke Point in Co-flow Experiment (SPICE): Laminar Smoke Point Properties of Non-buoyant Round-Jet Diffusion Flames.* Final Report, 2 December 2011. `knowledgeBase/MSG (SolidAndGas)/SPICE/SPICE Final Report 12_2_2012.pdf`

---

<div align="center">
<sub>Built for the NASA Space Apps Challenge. Experimental data: NASA Physical Sciences Informatics (PSI). FLAMSA adds curation, verification and visualization, and makes no fire-safety certification.</sub>
</div>
