---
name: psi-fire-safety
description: Procedure for the PSI Fire-Safety Explorer. Covers curating raw NASA PSI data (CSV "Experimental table", ISA-Tab, PDFs) into validated per-investigation tidy CSV + JSON, the DDD explainable-ranking domain, the LangGraph pipeline (retrieve → rank → explain → validate) and the Streamlit dashboard with clean-dataset export. Use for any task touching knowledgeBase/, data/, src/psi_fire/ or docs/ADR.md.
---

# PSI Fire-Safety Explorer — Skill

Read `CLAUDE.md` first (language policy, layer rules, ubiquitous language, ADR). This skill is the **how**.
**Everything written to the repo is English**: code, identifiers, comments, column names, JSON keys, UI strings, ADR entries. Non-English output is a bug.

---

## Part 1 — Data curation (knowledgeBase → data/curated)

### 1.1 Source registry
`data/sources.json` is the only mapping from `investigation_id` to raw files. Loaders read it; no code hardcodes a `knowledgeBase/` path. Adding an investigation = one registry entry + one adapter + one manual metadata file.

Source priority: **CSV Experimental table > ISA-Tab `i_Investigation.txt` (Comment[Approach], DOI, Hardware) > PDF/DOCX/PPT** (human reading only for objective/sensors; no PDF parser).

External documentation (ADR-0022): `sources.json.external_sources` registers shared sources and their versioned `captures_dir`; investigation entries link them with `external_source_ids`. Capture HTML as `page.html`, derive `content.md`, and retain URL, UTC capture time, hashes and extraction details in `metadata.json`. PDFs are preserved as `document.pdf` without automatic parsing. Failed HTTP responses are explicitly marked failed and never treated as scientific content. Source association is user-supplied and pending scientific review; only a reviewed statement with a locator supports a hardware/sensor fact. See `docs/external-sources.md` and `scripts/capture_external_sources.py`.

Known facts (verified 2026-11-14):
- `SAFFIRE-2.csv` and `SAFFIRE-2 (1).csv` are byte-identical → registry uses the first.
- `BASS` has two ISA-Tab folders (`..._BASS` and `..._BASS_2`) that are byte-identical → registry uses the first.
- `ACME-CFI-G` has two tables (Normal and Inverse flames) → one investigation, `flame_configuration` column distinguishes them.
- No ISA-Tab for SAFFIRE-I/II, SAME-R, ACME-CFI-G, ACME-E-FIELD, SLICE → metadata comes from manual reading only.

### 1.2 Output layout (fixed names)
```
data/curated/<investigation_id>/test_points.csv     # tidy table
data/curated/<investigation_id>/investigation.json  # nested metadata
```
- Tabular data (one row per test condition) → **CSV**: native for pandas/Streamlit and for users training models.
- Nested, hand-curated metadata → **JSON**: natural shape for objectives, sensor lists and provenance.
- Never convert test points to JSON on disk: the LLM receives JSON produced at runtime by `model_dump_json()` from domain objects, so the disk format is irrelevant to it (ADR-0007).

`test_points.csv` = fixed **core columns** (the stable contract, present in every file, in this order) + investigation-specific **extra columns** (ADR-0016):
`investigation_id, test_point_id, record_level, fuel_name, fuel_phase, o2_basis, o2_percent_{min,max,raw}, pressure_psi_{min,max,raw}, diluent, flow_speed_cm_s_{min,max,raw}, flow_direction, source_file, source_row, provenance_status, provenance_note`
- Core conditions are always `_min`/`_max` (sources give lists and ranges); a single value has min = max.
- Every quantity column has its canonical unit in the name (`burn_time_s`, `sample_thickness_mm`); `x_raw` holds the original text when it differs from the canonical number (`"0.21"` mole fraction, `"~ 21.5"`, `"037 mm"`).
- Empty cell = not reported. Never 0, never guessed.
- `record_level`: `test` | `test_day` | `test_matrix`. Never compare a matrix envelope as if it were a run.
- `o2_basis`: `ambient` | `oxidizer_stream` (CFI-G inverse flames). Ranking must not treat burner-stream O2 as cabin O2.
- `investigation.json` holds the column dictionary (`kind`, `unit`, `source_headers`, `derivation`), ISA-Tab `study_metadata`, source SHA-256/encoding, `source_notes`, and derived `varied_variables` / `held_constant_variables` / `unreported_variables`.

Commands: `python -m psi_fire.interface.curate_cli [ID ...]` regenerates `data/curated/` (deterministic, byte-identical). Read it with `CuratedRepository(...).all()/get()/to_dataframe()`.

### 1.3 Real pitfalls already seen in the CSVs (handle explicitly)
- **Heterogeneous headers with stray whitespace** (`"Sample Number "`, `"Air Flow "`). Map through a per-investigation alias table, never by position.
- **Unit in the header** (`Ambient pressure; mmHg`, `...; mole fraction`) **or in the value** (`.33 cm`, `30 cm/s`). The `Quantity` parser supports both.
- **Summary rows** (`Kapton: same conditions as 1-4`). Expand into N `TestPoint`s with `provenance.status="inferred"` referencing the source rows. Never drop them.
- **Empty cells** inside valid rows (FLEX test 4, extinction diameter). They become `null`/`missing`, never 0.
- Encoding: `text_source.decode` reads `utf-8-sig`, falls back to `cp1252` (FLEX), records the encoding used.
- **Casing:** every `Text` column is lower-cased by the pipeline (`Yes`/`yes`, `Inverse`/`inverse` are one value). Free-text columns (comments, descriptions) opt out with `free_text=True`.
- **Fuel labels** go through `ingestion/fuel_names.py`: `fuel_name` = lower-case material/species named in the label (`ethylene`, `pmma`, `sibal`), `fuel_geometry` = geometry word in the label, `fuel_label_fraction_percent` = percentage printed in the label (not the measured composition), `fuel_name_raw` = original label, kept whenever it differs. A label naming no material yields `fuel_name = null`: never infer the material.
- **Impossible zeros** (FLEX 0 mmHg) become `null` with the raw value kept and the row `inferred`, through a column `fixup`.
- **Non-unique test numbers** (BASS, SAME-R, CFI): use row-based ids `r<row>`, keep the source number as a meta column.
- **Identical rows**: keep and flag `identical to row N` (they may be real runs with lost telemetry, "Ku LOS"). Never drop.
- **Notes inside tables** (SAFFIRE footnotes, ACME "Notes" column) → `source_notes`, not test points.
- **Continuation rows** (E-FIELD: only "Fuel Conc" filled) → merged into the previous row as a list, row `inferred`.
- **Ambiguous numbers** (`037 mm`), text in numeric columns (`Insignificant`), physically impossible readings (negative speed) → value empty, raw kept, reason in `provenance_note`. Known artifacts are fixed only through a named adapter `fixup` (e.g. Excel `3400%` → 34).
- Full list of source defects: ADR-0017.

### 1.4 Domain model (as implemented, ADR-0016)
```python
# domain/units.py: Unit enum, named conversion constants, to_canonical(), column_name()
# domain/model.py: immutable Pydantic models, no I/O
class TestPoint:      # entity = one CSV row; core fields typed, extras: dict[str, float | str | None]
class ColumnInfo:     # data-dictionary entry: kind (quantity|text|meta|raw), unit, source_headers, derivation
class Investigation:  # aggregate root: id, psi_id, record_level, source_files, study_metadata, source_notes,
                      # columns, test_points (persisted in CSV) + computed varied/held_constant/unreported variables
```
Invariants (Pydantic validators): o2 ∈ [0,100] and requires `o2_basis`; min ≤ max and both-or-neither; pressure/flow ≥ 0; extras never shadow core columns; ≥1 test point; unique `test_point_id`; every extra column documented in `columns`.
Manual metadata (ADR-0026): `Investigation.manual_metadata` holds `pillars`, `gravity_regime`, `hardware`, `nominal_atmosphere` (optional), `sensors`, `earth_applications`, each a `Claim` = `value` + `status` (`verified|inferred|not_reported`) + `evidence[]` (`source_file`, `locator`, literal `quote`) + `note`, plus `review_status` (`draft|reviewed`).

Writing `data/manual/<id>.json` (procedure):
1. Draft from sources in priority order: ISA-Tab, DoD/Operations docs, final report. Extract text to the scratchpad only to find quotes.
2. Cite the page: `locator` is `p. N` (PDF) or `para N` (DOCX) (mandatory for those types), or a field name (ISA-Tab). **Quotes are 1:1 transcriptions of ONE printed line** (ADR-0032): copy characters exactly (curly quotes included), never cross a line break, at least 20 characters. A wrapped sentence is cited by several entries, one per line. The reviewer must be able to find each quote with Ctrl+F on the cited page.
3. Run `pytest tests/infrastructure/test_evidence.py tests/infrastructure/test_evidence_visual_lines.py`. The second checks each PDF quote against `pdftotext -layout`, because `pypdf` sometimes returns a whole paragraph as one line (ADR-0045). A quote that is not found, spans a line break, or is not character-exact fails. If `pypdf` reads the line differently from the page ("o nly", "high -definition"), choose another span of the same line; never loosen the verifier (ADR-0027). To see the lines the verifier sees, print `_pdf_pages(path)[page-1].split("
")`.
3b. A claim value says only what its quotes say (ADR-0033). Sensor `instrument` is one plain label, lowercase except chemical formulas (`O2 sensor`): no counts, parentheses, commas, "/" or "and"; counts, types and positions go in `note` with their own evidence. Use the shared vocabulary so dashboard filters group across investigations: `thermocouple`, `radiometer`, `anemometer`, `O2 sensor`, `CO2 sensor`, `CO sensor`, `pressure sensor`, `video camera`, `still camera`, `color camera`, `intensified video camera`, `gas flow meter`, `photomultiplier tube`, `temperature sensor`, `heat flux sensor`, `multispectral camera`, `ultraviolet camera`, `black-and-white camera`, `high-resolution camera`, `smoke detector`, `thermophoretic soot sampler`, `transmission electron microscope`, `scanning mobility particle sizer`, `P-Trak`, `DustTrak`, `ion chamber`, `M-pass` (product names keep their case; add a new label only when none fits, and add it here). `measures` stays empty unless a quote states it. Every fact in a `note` or `value` needs its own evidence entry (a table value can cite the experimental CSV line itself). A `not_reported` claim requires reading every listed document in full (never a truncated search; ADR-0044). A pre-flight source ('will be') gives `inferred`, not `verified`; before using a plan or an assumption, search the same report for an as-run statement (ADR-0052).
4. Never guess: not found in any source = `not_reported` with a note listing what was searched (ADR-0029). Pillar is always `inferred`; an empty pillar list means no direct fire-safety pillar.
5. Generate the review sheet: `python -m psi_fire.interface.review_sheet`. The human checks each quote and sets `review_status: reviewed`, `reviewed_by`, `reviewed_on`. Until then the dashboard shows an "unreviewed" badge.

### 1.5 Ingestion pipeline (Pipeline + one Adapter per investigation)
```
SourceRegistry ─► decode ─► header check (every header mapped or Skip) ─► notes / continuation rows
  ─► flag identical rows ─► expand summary rows ─► parse_quantity + to_canonical ─► derive core columns
  ─► TestPoint / Investigation validation ─► CuratedStore ─► data/curated/<id>/
```
- One `AdapterSpec` per investigation in `infrastructure/ingestion/adapters.py` (Strategy): `Num` / `Text` / `Meta` / `Skip` column specs, table constants with a reason, and named quirks (`is_note_row`, `notes_header`, `continuation_header`, `fixup`). Shared logic lives in `pipeline.py`.
- `Text` columns take part in variable analysis; `Meta` columns (ids, dates, camera files) are kept but excluded from it.
- Metadata absent from the CSV (objective, sensors, pillars, Earth applications) is hand-written in `data/manual/<id>.json` from the overview/ISA-Tab, **with `source_file` + page per field**.
- Conversions (named domain constants): `mmHg → psi × 0.0193368`, `kPa → psi × 0.145038`, `atm → psi × 14.6959`, `mole fraction → percent × 100`, `cm → mm × 10`.
- Deterministic output: source row order, sorted JSON keys, `indent=2`, shortest round-trip float text. Rerunning on unchanged input produces byte-identical files (tested).
- Tests run on the real raw files (`tests/infrastructure/test_curation.py`): every quirk above has an assertion. A new quirk = a new assertion.
- Demo order: start with investigations that matter for the lunar scenario (SAFFIRE-*, BASS, ACME-CFI-G), then the rest.

### 1.6 Repository (one source, many views)
```python
class InvestigationRepository(Protocol):
    def all(self) -> list[Investigation]: ...
    def get(self, investigation_id: str) -> Investigation: ...
# infrastructure/CuratedRepository implements it, plus view helpers used only by outer layers:
#   to_dataframe() -> pd.DataFrame       # Streamlit
#   to_documents() -> list[Document]     # LangChain retrieval, if ever needed
```
On load, join `test_points.csv` ↔ `investigation.json` by `investigation_id`; an orphan row or missing folder is a load error, not a warning.

### 1.7 Export (use case `ExportCleanDataset`)
- `data/export/test_points.csv`: all curated CSVs concatenated (same columns).
- `data/export/investigations.json`: all aggregates.
- `data/export/schema.json`: JSON Schema generated from the model.
- `data/export/DATA_CARD.md`: coverage, missing fields per investigation, applied conversions, limitations.

---

## Part 2 — Explainable AI (domain + LangGraph)

### 2.1 Scenario and ranking (domain, deterministic)
```python
class HabitatScenario(VO):  name; o2_percent; pressure_psi; gravity: GravityRegime; pillars_of_interest; fuel_phases_of_interest
class RelevanceCriterion(Protocol):          # Strategy
    name: str; weight: float
    def evaluate(self, inv: Investigation, s: HabitatScenario) -> CriterionResult  # value ∈ [0,1] + rationale + evidence (TestPoint ids)
class RelevanceRanker:                        # Domain Service
    def rank(self, invs, scenario) -> list[RankedInvestigation]   # score = Σ wᵢ·vᵢ, ScoreBreakdown preserved
```
Initial criteria (weights = named constants; changing a weight = `DECISION` in the ADR):
| Criterion | Measures |
|---|---|
| `OxygenProximity` | distance between scenario O2 and tested O2 values (bonus if scenario falls inside the tested range) |
| `PressureProximity` | same for pressure |
| `PillarMatch` | overlap of prevention/detection/suppression |
| `FuelPhaseMatch` | solids (fabrics, plastics) weigh more for habitats |
| `FlowRegimeMatch` | ventilated vs quiescent, per scenario |
| `DataRichness` | number of `TestPoint`s and share of `verified` fields |

Stable tie-break by `investigation_id`. Same input → same output (mandatory test).

### 2.2 LangGraph graph (infrastructure, thin adapters)
```
retrieve ─► rank ─► explain ─► validate_citations ─┬─► END
                                                   └─(invalid, 1 retry)─► explain ─► fallback_template
```
- `State` = `TypedDict` with `scenario`, `question`, `candidates`, `ranked`, `draft`, `citations`, `errors`.
- **retrieve**: structured filter on the repository (pillar, phase, O2 range). Semantic search over `objective`/`approach` only if the filter is not enough (log as `ENHANCEMENT`).
- **rank**: calls the domain `RelevanceRanker`. No LLM here.
- **explain**: LLM with **structured output** `{claims: [{text, investigation_ids, test_point_ids}], limitations: [...]}`. Prompt receives only the top-k with breakdown and provenance. Low temperature.
- **validate_citations**: every cited `investigation_id`/`test_point_id` must exist in `ranked`, and every numeric claim must match a cited `Quantity`. Failure → 1 retry with the error attached → then `fallback_template` (explanation built only from the `ScoreBreakdown`). Every failure goes to `errors` and is visible in the UI.
- Limitations are injected by the domain, not the LLM: `gravity=partial` scenario → fixed notice "PSI has no partial-gravity data; microgravity and 1g bound the interval"; O2/pressure outside tested range → extrapolation notice.

### 2.3 Ports and use cases (application)
```python
class Narrator(Protocol): def explain(self, ranked, scenario, question) -> Explanation
```
Use cases: `RankForScenario`, `ExplainRanking`, `CompareInvestigations` (varied vs held_constant side by side), `ExportCleanDataset`. Each use case is a class with `__call__` and injected dependencies.

---

## Part 3 — Dashboard (interface/Streamlit)
Demo flows, by priority:
1. **Scenario → explained ranking**: preset "Lunar base 30% O2 / 10.2 psi", ranked table, per-criterion breakdown chart, LLM text with clickable citations that open the investigation detail.
2. **Compare**: 2–3 investigations side by side (fuel, O2, pressure, flow, sensors, what varied vs held constant).
3. **Export**: download buttons (JSON, tidy CSV, schema, data card).

Rules: `interface` only calls use cases. `@st.cache_resource` for repository and graph, wired in the composition root. No business rules in widget callbacks. All UI text in English.

---

## Checklist before finishing any task from this skill
- [ ] Layer dependencies respected (grep forbidden imports in `domain/`)
- [ ] Everything written is English (code, comments, keys, UI, ADR)
- [ ] No invented value; `Provenance` on every new fact
- [ ] New/updated tests; `pytest -q` green (or the failure reported with output)
- [ ] `docs/ADR.md` appended with the session's DECISION / TRADEOFF / BUG / FIX / ENHANCEMENT / DEBT
- [ ] Final reply lists what was not verified and the risks
