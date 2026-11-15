# ADR — Continuous decision log

Append-only, **English only**. Never edit existing entries; to change a decision, add a new one with `Supersedes`.
Types: `DECISION` · `TRADEOFF` · `BUG` · `FIX` · `ENHANCEMENT` · `DEBT`
Status: `proposed` · `accepted` · `superseded` · `open` · `resolved` · `deferred`

## Template
```
### ADR-XXXX — <short title>
- Date: YYYY-MM-DD · Type: <type> · Status: <status> · Related: ADR-YYYY · Supersedes: ADR-ZZZZ
- Context: <problem / symptom, with evidence (file, line, output)>
- Options: <A, B, C — DECISION/TRADEOFF only>
- Decision / Root cause / Change: <what was done or decided>
- Consequences: <gains, losses, risks, what becomes harder>
- Review trigger: <when to reopen — mandatory for DEBT/TRADEOFF>
```

---

### ADR-0001 — Stack: Streamlit + LangGraph + Pydantic
- Date: 2026-11-14 · Type: DECISION · Status: accepted
- Context: 48h hackathon, possibly a solo developer; needs a UI with chat and a multi-agent pipeline.
- Options: (A) React + FastAPI; (B) Streamlit + LangGraph.
- Decision: B.
- Consequences: much faster delivery; less visual and front-end state control. Business logic is isolated from the UI (Clean Architecture), so replacing the front end later touches neither domain nor use cases.
- Review trigger: product continues after the hackathon or needs real multi-user support.

### ADR-0002 — Semi-manual curation instead of automatic PDF extraction
- Date: 2026-11-14 · Type: TRADEOFF · Status: accepted
- Context: `knowledgeBase/` holds hundreds of heterogeneous files (PDF, PPT, XLS, ZIP), but every investigation has an `Experimental table` CSV and some have ISA-Tab.
- Decision: parse only CSV + ISA-Tab automatically; objective, sensors and Earth applications are hand-written with per-field provenance.
- Consequences: high quality and traceability; does not scale to new investigations without human work.
- Review trigger: more than 20 investigations in scope, or PSI publishes structured sensor metadata.

### ADR-0003 — Pydantic allowed in domain entities
- Date: 2026-11-14 · Type: TRADEOFF · Status: accepted
- Context: a "pure" domain would require dataclasses plus duplicated mapping for schema/export.
- Decision: entities and VOs are `pydantic.BaseModel(frozen=True)`; it is the only external dependency allowed in `domain/`.
- Consequences: free JSON Schema and validation, no mapping layer; the domain is coupled to a stable library.
- Review trigger: Pydantic forces model compromises (e.g. inheritance, hard cross-field validation).

### ADR-0004 — The LLM narrates, it does not decide
- Date: 2026-11-14 · Type: DECISION · Status: accepted
- Context: the target audience (researchers, engineers) needs auditable, reproducible ranking.
- Options: (A) LLM ranks; (B) deterministic ranking in the domain + LLM explains with validated citations.
- Decision: B, with citation validation and template fallback.
- Consequences: real explainability and reproducibility; criterion weights are human judgment and must be justified here whenever they change.
- Review trigger: expert feedback that the criteria do not capture relevance.

### ADR-0005 — ZIP extraction authorized by the user
- Date: 2026-11-14 · Type: DECISION · Status: accepted
- Context: the user asked to extract every ZIP into its own folder; 37 ZIP files were found in `knowledgeBase/`.
- Options: extract directly into the investigation folder, or preserve/create one subfolder per archive.
- Decision: keep the internal structure when the ZIP already contains a folder with its name; otherwise create a folder named after the ZIP. This session's authorization allows adding extracted files to `knowledgeBase/` while preserving raw data and the original ZIPs. Pre-existing files are accepted only when identical.
- Consequences: 751 files available and verified, including 2 identical pre-existing files; no ZIP modified. Inventory, ZIP SHA-256 hashes and errors recorded in `docs/zip-extraction-report.json`.

### ADR-0006 — Six ZIPs have corrupted content or structure
- Date: 2026-11-14 · Type: BUG · Status: open · Related: ADR-0005
- Context: extracting the 37 ZIPs surfaced errors in 23 entries across 6 archives; messages include invalid CRC, decompression failure and missing headers. Files and entries are itemized in `docs/zip-extraction-report.json`.
- Root cause: inconsistencies between the central directory and local headers, plus invalid or missing compressed data in the source archives. The origin of the corruption was not determined.
- Change: locating local headers allowed adjusting 56 offsets in memory only, without modifying the ZIPs. Every saved file went through decompression, CRC and post-write SHA-256 comparison. Invalid content was not written.
- Consequences: 31 ZIPs fully extracted and 6 partially. 23 entries remain unavailable; intact copies of the affected archives are needed to complete extraction.
- Review trigger: new copies of the affected ZIPs become available.

### ADR-0007 — Curated storage: tidy CSV for test points, JSON for metadata
- Date: 2026-11-14 · Type: DECISION · Status: accepted · Supersedes: the "all curated data as `<id>.json`" layout in the first SKILL.md draft
- Context: consumers are Streamlit (tabular), LangGraph/LangChain (structured objects/JSON) and end users training models (tabular). Raw CSVs are heterogeneous (units in header or value, summary rows, empty cells).
- Options: (A) convert everything to JSON; (B) keep raw CSV and normalize at load time; (C) persist normalized tidy CSV for test points + JSON for nested metadata, joined by one repository.
- Decision: C. Versatility comes from `InvestigationRepository` exposing several views (`all()/get()`, `to_dataframe()`, `to_documents()`), not from the disk format. The LLM receives JSON produced at runtime by `model_dump_json()`.
- Consequences: Streamlit and model users read CSV natively; export equals curated data. Cost: two files per investigation that must stay consistent, mitigated by generating both in the same pipeline run and failing the load on orphan rows.
- Review trigger: data grows beyond what CSV handles comfortably (then Parquet), or metadata becomes tabular.

### ADR-0008 — Fixed-name curated tree + source registry; raw tree not renamed
- Date: 2026-11-14 · Type: DECISION · Status: accepted
- Context: the raw tree has inconsistent names (`supression` typo, `MSG (SolidAndGas)` with spaces, `SAME2` vs SAME-R, `PSI-xx_Experimental table_<name>.csv`, duplicates). Code needs predictable paths.
- Options: (A) rename `knowledgeBase/`; (B) leave raw untouched, map it once in `data/sources.json`, and write curated output to `data/curated/<investigation_id>/{test_points.csv, investigation.json}`.
- Decision: B. Canonical ids are uppercase (`SAFFIRE-III`, `ACME-CFI-G`, `ACME-E-FIELD`). `sources.json` is the only place raw paths appear.
- Consequences: raw data stays immutable and `docs/zip-extraction-report.json` paths stay valid; code reads curated data through fixed names only. Cost: one hand-maintained registry.
- Review trigger: raw data is re-downloaded from PSI with a different layout.

### ADR-0009 — Duplicate raw files resolved by content hash
- Date: 2026-11-14 · Type: DECISION · Status: accepted · Related: ADR-0008
- Context: `SAFFIRE2/PSI-99_Experimental table_SAFFIRE-2.csv` and `... (1).csv`; `BASS/PSI-26_metadata_PSI-102_BASS` and `..._BASS_2`.
- Decision: SHA-256 showed each pair is byte-identical; the registry references the first of each pair. Duplicates are left on disk (raw is immutable).
- Consequences: no data loss; no ambiguity in code.
- Review trigger: a duplicate's hash changes.

### ADR-0010 — English-only repository
- Date: 2026-11-14 · Type: DECISION · Status: accepted
- Context: international project, audience and judges.
- Decision: code, identifiers, comments, data keys, file/folder names (new ones), UI, skills, CLAUDE.md and ADR are English. Existing ADR-0001..0006 were translated from Portuguese once, as an explicit user-requested exception to append-only; content and meaning unchanged. Raw `knowledgeBase/` names are out of scope (ADR-0008).
- Consequences: one language for every reader. Any non-English artifact is logged as a BUG.
- Review trigger: none.

### ADR-0011 — Required experimental metadata is not yet curated
- Date: 2026-11-14 · Type: BUG · Status: open · Related: ADR-0007, ADR-0008
- Context: auditing all 15 registered investigations found no manual metadata files, curated investigation metadata, or curated test-point CSVs. The registry resolves source locations but contains no field-level hardware, sensor or provenance mapping. Evidence: docs/structured-data-coverage.csv and docs/structured-data-audit.json.
- Root cause: the repository currently holds raw sources and a registry; no curation pipeline, domain model or repository implementation has been created. Scientific evidence exists in the sources but has not been transformed into the agreed application representation.
- Consequences: hardware and sensors cannot yet be retrieved as validated domain facts. Nine investigations have explicit hardware declarations in their registered ISA-Tab metadata; the other six require further documentation review. Raw measurement columns must not be treated as verified sensor models.
- Review trigger: manual metadata and the curated CSV/JSON pairs are generated and validated with per-field provenance.

### ADR-0012 — Reproducible structured-source audit
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: accepted · Related: ADR-0011
- Context: the user requested a review of CSVs and structured data for missing hardware, sensor and provenance mappings.
- Change: added scripts/audit_structured_sources.py and the generated docs/structured-data-audit.json and docs/structured-data-coverage.csv, plus a human-readable docs/structured-data-audit.md. Source references resolve through data/sources.json; no raw paths are hardcoded in the audit utility. The audit scans 17 CSV, 317 TXT and 16 XLSX files; 8 legacy XLS files are inventoried only. Physical line ranges, raw field values and spreadsheet cell locators preserve evidence context.
- Consequences: evidence candidates and missing mappings are reviewable per investigation. Before/after SHA-256 snapshots verify all 1,165 raw files remain unchanged. Keywords do not establish deployed hardware, sensor models or scientific validity; no curated facts were generated and architecture remains unchanged. Legacy XLS and nonstructured documentation still require review.
- Review trigger: source data changes or curation begins.

### ADR-0013 — FLEX source table requires an encoding fallback
- Date: 2026-11-14 · Type: BUG · Status: open · Related: ADR-0011, ADR-0012
- Context: UTF-8 decoding fails for the FLEX experimental table referenced by data/sources.json. The audit successfully reads it with cp1252; encoding is recorded alongside its source reference and hash.
- Root cause: raw experimental tables do not all use the same encoding.
- Change: the audit reader explicitly supports utf-8-sig with cp1252 fallback, and UTF-16 BOM detection for structured text. The original bytes remain unchanged.
- Consequences: the audit covers FLEX, but the future ingestion reader must implement the same documented fallback before this issue can be closed for application ingestion.
- Review trigger: the ingestion reader is implemented and verified against the FLEX source file.

### ADR-0014 — Raw folder `supression` renamed to `suppression`
- Date: 2026-11-14 · Type: FIX · Status: resolved · Related: ADR-0008, ADR-0010 · Supersedes: the "raw tree not renamed" clause of ADR-0008 for this folder only
- Context: misspelled raw folder `knowledgeBase/supression/` (FLEX, FLEX-2, CFI) violated the English-only policy.
- Change: user-requested rename to `knowledgeBase/suppression/`; file contents untouched. Paths updated in `data/sources.json` and in the `archive`/`destination` fields of `docs/zip-extraction-report.json` (8 occurrences; JSON re-validated, every `destination` exists). ZIP SHA-256 hashes are unaffected.
- Consequences: raw tree spelled correctly; all other raw names stay as they are (ADR-0008 still applies to them).
- Review trigger: none.

### ADR-0015 — ADR id collision fixed
- Date: 2026-11-14 · Type: FIX · Status: resolved
- Context: two sessions appended concurrently; the folder-rename entry and the metadata-gap BUG were both numbered ADR-0011.
- Change: the folder-rename entry (appended last, by this session) was renumbered to ADR-0014. No content changed.
- Consequences: ids are unique again. Review trigger: none; before appending, always read the file tail for the last id.

### ADR-0016 — CSV normalization pipeline and canonical test_points.csv schema
- Date: 2026-11-14 · Type: DECISION · Status: accepted · Related: ADR-0007, ADR-0008, ADR-0003
- Context: the 16 experimental tables differ in headers, units (in header or in value), granularity (per test, per test day, planned matrix) and notation (ranges, lists, "~", footnotes, continuation rows).
- Decision:
  - Declarative adapter per investigation (`infrastructure/ingestion/adapters.py`, Strategy): every raw header must be mapped (`Num`/`Text`/`Meta`) or explicitly `Skip`ped with a reason; any unmapped or missing header fails curation.
  - Shared pipeline (`pipeline.py`): notes rows → `source_notes`; continuation rows merged; summary rows expanded; identical rows flagged; quantities parsed and converted to canonical units (`domain/units.py`).
  - Flat `TestPoint` entity mirroring one CSV row: fixed core columns + `extras` dict. Supersedes the nested `Atmosphere`/`Fuel`/`Flow` VOs in the first SKILL draft: a flat shape round-trips with the CSV without a mapping layer.
  - Core conditions (`o2_percent`, `pressure_psi`, `flow_speed_cm_s`) are always `_min`/`_max` ranges, because sources report lists and ranges; `_raw` keeps the original text whenever it differs from the canonical number.
  - `record_level` (`test` | `test_day` | `test_matrix`) on every row, so a FLEX-2 matrix row is never mistaken for a test run.
  - `o2_basis` (`ambient` | `oxidizer_stream`) on every row with O2: ACME-CFI-G inverse flames report burner-stream O2, not cabin atmosphere.
  - `investigation.json` carries a column dictionary (kind, canonical unit, source headers, derivation), the ISA-Tab STUDY section as `study_metadata`, source file SHA-256/encoding, and derived `varied` / `held_constant` / `unreported` variables. Core conditions are always assessed, so a missing O2 column is reported, not hidden.
  - Composition root: `python -m psi_fire.interface.curate_cli`; use case `CurateInvestigations`; ports in `application/ports.py`; `CuratedStore` + `CuratedRepository` (with `to_dataframe()`) implement them.
- Consequences: all 15 investigations curate (1,615 test points); 48 tests pass, including real-data integration, repository round-trip and byte-identical regeneration. Cost: many sparse extra columns in a concatenated frame; core columns are the stable contract.
- Review trigger: a new investigation whose rows cannot be expressed as one TestPoint per row.

### ADR-0017 — Source-data defects found during normalization
- Date: 2026-11-14 · Type: BUG · Status: open (source defects; handled, not fixable in raw data)
- Context and handling (raw files untouched; every case is visible in `provenance_note` or `_raw`):
  - BASS "As Run Test #" repeats (24, 85, 89–91); SAME-R test "57" used for two samples; CFI rows 81–88 duplicate rows 24–31 → ids are row-based (`r<row>`), original numbers kept as meta columns. SPICE/E-FIELD contain identical rows (some "Ku LOS" telemetry losses) → kept and flagged "identical to row N", never dropped.
  - ACME-BRE "3400%"/"2100%" are Excel percent-format artifacts → read as 34/21 percent, row `inferred`.
  - SAFFIRE-II thickness "037 mm" is ambiguous (0.37 or 37) → value left empty, raw kept. "See Fig. 5", "Insignificant", "Complete", "Acceleratory" kept as raw text.
  - SAFFIRE-II header "?-g" is a lost "µ" (micro-gravity); "?-g Spread Length" actually holds rates in mm/s → mapped to `microgravity_spread_rate_cm_s`. Header typo "Samle Thickness" mapped by alias.
  - FLEX header subscripts lost (O/N/CO = O2/N2/CO2); "Burning rate; mm" is the d²-law constant in mm²/s → `burning_rate_constant_mm2_s`.
  - SPICE negative air speed (-0.28 cm/s) is a sensor offset near zero flow → value empty, raw kept, row `inferred`.
  - SAFFIRE-I length/width appear swapped relative to SAFFIRE-III (40.6×94 vs 94×40.6 cm) → NOT corrected; needs confirmation from the SAFFIRE documentation.
- Consequences: no invented values; ambiguous cells are empty with their raw text preserved for human review.
- Review trigger: PSI publishes corrected tables, or documentation resolves the SAFFIRE-I dimensions and SAFFIRE-II thickness.

### ADR-0018 — Encoding fallback implemented in the ingestion reader
- Date: 2026-11-14 · Type: FIX · Status: resolved · Related: ADR-0013
- Change: `infrastructure/ingestion/text_source.decode` reads `utf-8-sig` and falls back to `cp1252`; the encoding used is recorded per source file in `investigation.json`. Verified by test (`FLEX` → `cp1252`).
- Consequences: ADR-0013's ingestion condition is met.

### ADR-0019 — Inferred constants and fuel phases
- Date: 2026-11-14 · Type: TRADEOFF · Status: accepted
- Context: some core columns are not in the tables but follow from the investigation design.
- Decision: declared per adapter with a stated reason, recorded as `derivation` in the column dictionary: `fuel_phase` per investigation (SAME "Dibutyl Phthalate" overridden to liquid); `o2_basis` per table; SPICE `flow_direction = coflow` (the experiment is a co-flow burner); `diluent` derived from non-zero N2/CO2/He fractions (FLEX, CFI).
- Consequences: ranking can use these fields; they are design facts, not measurements, and are labelled as such.
- Review trigger: manual metadata curation (pillars, sensors, hardware) contradicts a declared constant.

### ADR-0020 — Export bundle and manual metadata deferred
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: deferred · Related: ADR-0011
- Context: SKILL §1.7 export (`data/export/`: concatenated CSV, JSON, schema, data card) and `data/manual/<id>.json` (pillars, sensors, hardware, Earth applications) are not yet built.
- Consequences: `data/curated/` is already directly consumable (`CuratedRepository.to_dataframe()`); fire-safety pillars and sensors are still missing for ranking (ADR-0011 stays open).
- Review trigger: start of the ranking/XAI step.

### ADR-0021 — FLEX test 114 reports 0 mmHg ambient pressure
- Date: 2026-11-14 · Type: BUG · Status: open · Related: ADR-0017
- Context: coverage check found `pressure_psi = 0` for FLEX test 114 (source row 115, methanol, burn time 18.9 s, extinction). A burning droplet at 0 mmHg is physically impossible; the cell is a source defect.
- Root cause: the pipeline only rejects negative pressures; a zero passes the domain invariant (`pressure_psi ≥ 0`) and the raw "0" equals the canonical text, so no `_raw` was kept either.
- Impact: any pressure-based ranking or plot would include a fake 0 psi point for FLEX.
- Planned fix: FLEX adapter fixup treating 0 mmHg as missing (raw kept, row `inferred`), plus a regression assertion.
- Review trigger: next data-curation change.

### ADR-0022 — Versioned external documentation and capture provenance
- Date: 2026-11-14 · Type: DECISION · Status: accepted · Related: ADR-0008, ADR-0011, ADR-0020
- Context: the user supplied external hardware-reference URLs and two local PDFs and authorized HTML/Markdown acquisition with capture metadata.
- Options: retain live URLs only; duplicate captures per investigation; archive shared sources once per version and link investigations through the existing registry.
- Decision: extend data/sources.json with external_sources and per-investigation external_source_ids. Store versioned captures under data/external/, retaining original HTML or PDF, derived Markdown for HTML only, and metadata with URL, UTC capture time, redirect/status details, title when available, extraction selector/version, and SHA-256/byte length. Preserve failed HTTP responses separately. External archived files are allowed provenance sources alongside original PSI data; CLAUDE.md and the project skill now state this extension.
- Consequences: references remain reproducible without changing existing raw PSI or curated data. One page can support multiple investigations without duplicate downloads. User-supplied associations remain pending scientific review and do not populate verified Hardware/Sensor entities. PDFs require manual review; no automatic PDF parser was introduced. SLICE has no supplied source, not a verified absence of hardware; ACME-CFI-G was not included in the user's batch.
- Review trigger: manual metadata curation or source updates require new captures.

### ADR-0023 — ISS National Lab CIR URL blocks capture
- Date: 2026-11-14 · Type: BUG · Status: open · Related: ADR-0022
- Context: the supplied ISS National Lab CIR URL returned HTTP 403 to requests. Its response body and metadata are archived under source id iss-national-lab-cir; no content.md was produced for the failure.
- Root cause: the remote endpoint denied this capture client; the precise server-side policy was not determined.
- Consequences: eight of nine distinct sources were captured successfully (five HTML/Markdown pairs and three PDFs); this CIR source remains unavailable. FLEX/FLEX-2 retain their separately captured MDCA reference. No replacement URL was silently substituted.
- Review trigger: a working official source or an accessible user-supplied snapshot becomes available.

### ADR-0024 — Main-container extraction omitted the MDCA overview
- Date: 2026-11-14 · Type: BUG · Status: resolved · Related: ADR-0022
- Context: review of the initial Markdown showed that MDCA's entry-content contains a link while the substantive MDCA Overview is a separate sidebar widget. The initial ESA conversion also included unrelated article cards and media modals.
- Root cause: a generic main-content selector does not capture all site-specific editorial layouts, and main can include nonarticle interface content.
- Consequences: initial derived Markdown was incomplete or noisy; original HTML remained intact. These first captures are retained in history and are superseded for use by the latest captures documented in docs/external-sources.md.

### ADR-0025 — Source-specific extraction and verified capture bundle
- Date: 2026-11-14 · Type: FIX · Status: resolved · Related: ADR-0024
- Change: the MDCA source declares a selector that includes both entry-content and its overview widget. The converter excludes ESA media modals and related-content blocks. New MDCA/ESA versions preserve earlier snapshots. docs/external-sources.md indexes latest content and metadata; docs/external-source-capture-report.json retains all capture attempts. Capture dependencies are an optional pyproject extra, separate from application dependencies.
- Validation: verified all latest artifact hashes and byte lengths; both local PDF copies are byte-identical to the supplied originals; source/investigation links are reciprocal. Checked heading/table/link conversion, script/navigation exclusion, inclusion of the MDCA overview and exclusion of ESA modal/related text. Ruff and strict domain mypy passed; 48 existing tests passed. Pytest's default temporary/cache directories were inaccessible in this session; rerunning with a unique project-local basetemp and cache disabled passed.
- Consequences: retrieval and conversion are verified, but scientific hardware/sensor claims and PDF contents are not yet curated. No Streamlit run was performed; this change adds source acquisition, not dashboard functionality.

### ADR-0026 — Manual metadata with verifiable evidence (batch 1: SAFFIRE-III, BASS-II, ACME-CFI-G)
- Date: 2026-11-14 · Type: DECISION · Status: accepted · Related: ADR-0011, ADR-0020, ADR-0022
- Context: ranking needs pillars, hardware, gravity regime, sensors and nominal atmosphere that the CSVs do not carry. Reviewers must be able to check each fact without reading whole PDFs.
- Decision:
  - `data/manual/<id>.json` (domain `ManualMetadata`): every fact is a `Claim` = value + status (`verified` | `inferred` | `not_reported`) + `evidence[]` (`source_file`, `locator`, literal `quote`, optional `source_url`) + `note`. `inferred` requires a note; `not_reported` requires an empty value and a note naming what was searched; `verified`/`inferred` require evidence.
  - `EvidenceVerifier` (infrastructure) checks at curation time that each quote appears literally in its file (PDF page via `locator: "p. N"`, DOCX paragraph via `"para N"`, other text whole file) and that the file is under `knowledgeBase/` or `data/external/`. A quote that is not in its source fails curation; it cannot be silently invented.
  - `ManualMetadata` is attached to the aggregate as `Investigation.manual_metadata` and serialized into `investigation.json`; the flat `{value, status, evidence[]}` shape keeps it readable for Streamlit and LLM prompts. `nominal_atmosphere` is optional: `None` means the tables carry O2/pressure per test.
  - `review_status: draft | reviewed`; `reviewed` requires `reviewed_by` and `reviewed_on`. `python -m psi_fire.interface.review_sheet` generates `docs/review/<id>.md` with a checkbox, the quote and a link to the source (PDF links open at `#page=N`).
- Consequences: all 3 batch-1 files are `draft`; the dashboard must show an "unreviewed" badge until reviewed. Cost: quotes must match `pypdf`'s text, so a few were shortened (see ADR-0027). Pillar assignment is the curator's classification and is always `inferred` with a note.
- Review trigger: a source type other than PDF/DOCX/text is cited (e.g. XLSX/PPTX), or reviewers find the quote check too strict.

### ADR-0027 — PDF text extractors disagree; the verifier is the source of truth
- Date: 2026-11-14 · Type: BUG · Status: resolved (handled) · Related: ADR-0026
- Context: `pdftotext` (used to draft quotes) and `pypdf` (used by the verifier) extract different text for the same page. Examples in ACME-CFI-G: "o nly" (p. 68) and "high -definition" (p. 7) in `pypdf`. Two drafted quotes were rejected by the verifier.
- Root cause: font kerning/spacing in the source PDFs; each extractor splits differently.
- Change: quotes were shortened to spans both extractors read identically. The verifier stays strict (no fuzzy matching) so that "verified" keeps its meaning.
- Consequences: a few quotes are fragments; the reviewer still sees the full sentence on the linked page. Drafting must always be followed by the verifier run (`pytest tests/infrastructure/test_evidence.py`).
- Review trigger: many quotes need shortening, then switch the verifier to a layout-aware extractor.

### ADR-0028 — DOCX extraction regex matched non-text tags
- Date: 2026-11-14 · Type: BUG · Status: resolved · Related: ADR-0026
- Context: drafting from `BASS-II data FAQ.docx` showed raw XML inside extracted paragraphs (e.g. para 28). The pattern `<w:t[^>]*>` also matches `<w:tab/>`, `<w:tc>`, `<w:tbl>`.
- Fix: pattern is now `<w:t(?:\s[^>]*)?>` in `evidence_verifier._docx_paragraphs`. Verified: re-extracted text contains no `<w:` tags; evidence tests pass. Paragraph numbering is unaffected (it counts `<w:p>` elements).
- Consequences: DOCX evidence text is clean. DOCX table cells count as paragraphs.

### ADR-0029 — Batch-1 curation findings
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: accepted · Related: ADR-0026
- Findings recorded in the manual files (each with evidence):
  - SAFFIRE-III: no source states the duct atmosphere (O2 or pressure); recorded as `not_reported`, never assumed to be cabin air. This keeps the ranking from scoring O2/pressure for this investigation.
  - BASS-II: pressure is only implied (`P = 1 atm` in the MSG dilution model, p. 19): `inferred`, pressure only. Sources disagree on maximum airflow (ISA-Tab 40 cm/s vs report p. 29: 0 to 50 cm/s); noted, not reconciled.
  - ACME-CFI-G: the final report states that only BRE, not CFI-G, was focused on spacecraft fire safety (p. 68). Pillars are empty on purpose; its relevance comes from its high-O2 data, not a pillar.
- Consequences: `PillarMatch` must treat an empty pillar list as "no direct pillar", not as an error. Remaining ADR-0011 scope: batch 2 (SAFFIRE-I/II, BASS, ACME-BRE) and batch 3 (FLEX, FLEX-2, SAME).

### ADR-0030 — Specify the Streamlit explorer before implementing its consumer contracts
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: proposed · Related: ADR-0016, ADR-0022, ADR-0026, ADR-0029
- Context: the user requested spec-driven development before implementing Streamlit consumption contracts, while another workstream continues data cleaning and manual curation.
- Change: added docs/specs/streamlit-explorer.md (SPEC-001) as a reviewable proposal, without changing application code, schemas or datasets. It specifies current field mappings, proposed read-only application use cases, filter scopes/defaults, catalog and TestPoint columns, evidence access, missing/inferred/draft states, snapshot refresh behavior, implementation sequence and 25 acceptance scenarios. Repository-backed inspection confirmed 15 investigations and 1,615 records with three draft manual-metadata aggregates at the time of writing; the UI must compute changing counts dynamically.
- Consequences: proposed numerical filters use inclusive interval overlap and same-record conjunction, preserve ambient versus oxidizer-stream O2, and never fill TestPoint conditions from nominal metadata. Source-stated claims remain distinguishable from human-reviewed metadata. These UX/contract choices await review; this entry does not approve ranking criteria, implement Streamlit or override curation decisions. Tests and runtime verification are deferred to implementation; this documentation-only task verified the current repository can load the described data.
- Review trigger: user review of SPEC-001 or any curation-facing schema change before dashboard implementation.

### ADR-0031 — Extend explorer specification with challenge-driven data requirements
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: proposed · Related: ADR-0030, ADR-0016, ADR-0026
- Context: the user supplied the full fire-safety challenge brief and requested additional useful data consumption requirements in the spec-driven plan.
- Change: expanded SPEC-001 section 13 with 13 challenge-to-data requirements, inspected optional column mappings by investigation, a source-backed curation backlog, staged views/filters, a future XAI/RAG context envelope and modeling/export readiness requirements. Added AC-26 through AC-36, bringing the specification to 36 acceptance scenarios.
- Consequences: geometry, atmosphere timing/basis, instrument purpose, outcome definitions, hardware configuration, uncertainty, source conflicts and model-data grouping are explicitly considered. Current fields, derived proposals, curation dependencies and later features remain distinct. Stage-1 P0 is unchanged; no data/model/schema/application code was modified. The challenge brief supplies product requirements, not replacement evidence for investigation-specific facts or approval of inferred scientific relationships.
- Validation: checked unique requirement/acceptance ids and representative current-column mappings against curated dictionaries. Scientific truth of proposed additional fields and Streamlit runtime behavior were not tested; these require evidence curation and later implementation respectively.
- Review trigger: user review of the expanded specification or agreement on a proposed curation/schema extension.

### ADR-0032 — Evidence quotes are 1:1 transcriptions of one printed line
- Date: 2026-11-14 · Type: DECISION · Status: accepted · Supersedes: the quote-matching rules of ADR-0026 (whitespace-, typography- and hyphenation-insensitive, whole-page match) · Related: ADR-0027
- Context: the reviewer could not find 9 ACME-CFI-G quotes with Ctrl+F in the PDF. Cause: each quote spanned two printed lines, and a viewer search does not cross a line break. A quote that is correct for the verifier was not usable by a human.
- Decision: `EvidenceVerifier` now enforces that a quote is (a) inside ONE printed line of a PDF page or text file, or ONE DOCX paragraph; (b) character-exact: only whitespace runs are ignored, typographic quotes/dashes are not folded; (c) at least 20 characters; (d) cited with a mandatory locator (`p. N` for PDF, `para N` for DOCX). A sentence that wraps is quoted by the part on one line, or by several evidence entries, one per line. Review sheets print the quote in a code span to copy into Ctrl+F.
- Consequences: quotes are sometimes fragments; the reviewer still reads the whole sentence around the match. The rule is mechanical, so it cannot depend on the curator remembering it. Cost: matching uses `pypdf` text; where `pypdf` differs from the page ("o nly", "high -definition") another span of the line must be chosen (ADR-0027 still applies).
- Review trigger: reviewers report quotes that are on one line in the sheet but still not found in their viewer.

### ADR-0033 — Sensor claims: plain filter labels, and no `measures` the quote does not state
- Date: 2026-11-14 · Type: BUG · Status: resolved · Related: ADR-0026, SPEC-001 §4.2/§6.2
- Context: validating the ACME-CFI-G sensors against SPEC-001 (the Sensor filter uses `sensors[].value.instrument` as its label). Findings in my first drafts: labels with counts and parentheses ("thermocouples (2)"), two instruments in one claim ("intensified video camera and high-definition color camera"), and `measures` text the cited quote did not state ("gas temperature near the flame", "non-imaging flame light emission", "fuel and oxidizer flow", "flame radiation" for radiometers). That is invented content, which the data rules forbid. Smaller over-statements in value strings: BASS-II hardware ("fan-driven", "aboard the ISS" with no quote), SAFFIRE-III hardware ("free-flying").
- Root cause: the verifier checks that a quote exists, not that it supports every word of the claim value; I wrote values from reading, not from the quote.
- Fix: `Sensor.instrument` must be one plain label (no parentheses, commas, ";", "/" or " and ", enforced in the domain); `Sensor.measures` is optional and filled only when a cited quote states it; counts, types and positions go in `Claim.note`, each backed by an evidence entry. All three draft files were corrected and re-verified. Hardware values were cut to what their quotes support.
- Consequences: sensor filters group by instrument across investigations. Several sensors now show `measures: not stated`, which is accurate. A reviewer should still check that each claim value is supported by its quotes: the verifier cannot.
- Review trigger: a stage-2 criterion needs measured-quantity semantics (then add a curated `measurement` vocabulary with evidence).

### ADR-0034 — Sensor specifications richer than `instrument` + `measures` (proposed, not implemented)
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: deferred · Related: ADR-0033, SPEC-001 §13.3
- Context: ACME-CFI-G documents thermocouple type (B nearest the burner, K elsewhere), count, distance from the burner centre (45–200 mm) and a shared 125 samples/s logging rate. None of it fits `instrument`/`measures`; it currently lives in `Claim.note` with evidence.
- Proposal: optional structured fields on `Sensor` (`model_or_type`, `count`, `location`, `sampling_rate_hz`), each only when quoted. Needs schema review with the dashboard workstream before implementation.
- Open question for the reviewer: pillars stay `inferred` (no source states "this is prevention/detection/suppression"); confirm whether the human reviewer, not the curator, should own that classification.
- Review trigger: the dashboard needs to filter or display sensor specifications.

### ADR-0035 — Explorer specification had ambiguous implementation contracts
- Date: 2026-11-14 · Type: BUG · Status: resolved · Related: ADR-0030, ADR-0031
- Context: general QA of SPEC-001 found conflicting P0/P1 evidence/dictionary scope, underspecified query/result/error/port types, ambiguous missing-O2/basis handling, unscoped coverage denominators, incomplete session/source delivery policies, and acceptance cases without stage/task ownership. It also described a coherent refresh guarantee stronger than the current separate JSON/CSV writes can provide.
- Root cause: the first requirements document listed product behavior without fully specifying consumer design, operational prerequisites and verification ownership.
- Consequences: independent implementations could filter different records, leak technical details into the domain/UI or claim unsupported runtime guarantees. Findings QA-01 through QA-15 are recorded individually in docs/specs/streamlit-explorer-qa.md; current runtime defects are recorded separately below.

### ADR-0036 — Complete the spec-driven design and QA traceability
- Date: 2026-11-14 · Type: FIX · Status: resolved · Related: ADR-0035, ADR-0032, ADR-0033, ADR-0034
- Change: revised SPEC-001 to revision 0.3 and added companion DDD/application design, task/acceptance matrix and QA report under docs/specs/. The design keeps Investigation as the existing aggregate, treats catalog results as read projections, assigns pure scientific predicates to the domain and workflow/ports to application, and isolates filesystem/caching/session concerns. Fifty acceptance scenarios and 13 challenge-data requirements map to staged work; no runtime acceptance is claimed passed.
- Validation: checked local companion links, unique ids, complete one-to-one acceptance coverage and current model/repository compatibility. Sensor.measures optionality and plain instrument labels follow the concurrent ADR-0033 change; source quotes remain unaltered/copyable per ADR-0032. More detailed sensor fields remain deferred.
- Consequences: the documentation findings are addressed, but spec/design status remains proposed for review. No production code, model/schema or curated/raw data was modified. Integrated release requires structural integrity fixes and a completed/idle curation checkpoint. Fingerprint retries are explicitly not an atomic producer-generation protocol. Streamlit runtime, performance and browser acceptance were not executed in this documentation task.

### ADR-0037 — CSV-only curated directories are silently omitted by repository discovery
- Date: 2026-11-14 · Type: BUG · Status: open · Related: ADR-0036, ADR-0007
- Context: CuratedRepository.ids in infrastructure/curated_store.py lists only folders containing investigation.json. QA created an isolated workspace-local directory containing only test_points.csv; ids() returned an empty list rather than reporting an incomplete pair (QA-05).
- Root cause: discovery is filtered by metadata presence before get() can validate the required pair, so a CSV-only folder never reaches its missing-file check.
- Consequences: a damaged curated dataset can appear as a smaller valid catalog, contrary to the explicit no-silent-skip contract. No current curated file was altered and the current 15-investigation dataset loaded successfully. The explorer's integration preflight must detect both CSV-only and JSON-only directories without demanding every raw registry entry already be curated.
- Review trigger: repository/preflight owner implements and tests incomplete-pair rejection before integrated explorer release.

### ADR-0038 — Manual metadata identity can disagree with its Investigation
- Date: 2026-11-14 · Type: BUG · Status: open · Related: ADR-0036, ADR-0026
- Context: QA model_validate on an in-memory copy of the ACME-CFI-G aggregate accepted manual_metadata.investigation_id='UNRELATED-INVESTIGATION' while the parent id remained ACME-CFI-G (QA-06).
- Root cause: Investigation validates TestPoint parent identities but does not currently validate its optional ManualMetadata parent identity.
- Consequences: incorrectly attached hardware/sensor/gravity evidence could appear under another investigation. This reproduction did not modify any model, manual JSON or curated data; it demonstrates a missing structural invariant, not evidence that the current dataset contains that mismatch.
- Review trigger: curation/domain integration owner enforces and tests manual-parent identity before integrated explorer release.

### ADR-0044 — SAFFIRE-III nominal-atmosphere note contradicted a source
- Date: 2026-11-14 · Type: BUG · Status: resolved · Related: ADR-0029, ADR-0033
- Context: while drafting SAFFIRE-II I read the 2017 NTRS Saffire paper in full. It states that the Cygnus O2 "will be nearly 21% by volume" (p. 4). My ADR-0029 / SAFFIRE-III note said that paper "states neither O2 nor pressure".
- Root cause: the first search used a truncated grep (`head -30`) and missed the sentence; I then wrote a negative claim without checking the whole document.
- Fix: the SAFFIRE-III claim stays `not_reported` (the sentence concerns the Saffire-II flight, not Saffire-III) but its note now says exactly that. SAFFIRE-II records the O2 as `verified` (~21 percent, O2 only). SAFFIRE-I stays `not_reported`.
- Consequences: negative claims ("not stated anywhere") are the riskiest kind. Rule: a `not_reported` note must list the files searched, and the search must read whole documents, never a truncated grep.
- Review trigger: any new document is added for SAFFIRE-III/I (re-check the not_reported claims).

### ADR-0045 — Batch 2a: BASS, SAFFIRE-I and SAFFIRE-II drafted; visual-line check added
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: accepted · Related: ADR-0032, ADR-0033
- Change: `data/manual/{BASS,SAFFIRE-I,SAFFIRE-II}.json` written with 1:1 single-line quotes and plain sensor labels; BASS-II and SAFFIRE-III already conform. New test `tests/infrastructure/test_evidence_visual_lines.py` checks every PDF quote against `pdftotext -layout` lines (skipped when poppler is absent): `pypdf` can return a whole paragraph as one "line" (e.g. SRD_BASS), so the verifier alone does not guarantee a quote fits on one visible line.
- Findings in the files: SAFFIRE-I/II sensors come from a pre-flight paper ("will be") and BASS sensors from a 2010 requirements document ("the plan is"): all `inferred` with a note. BASS pillars are prevention + suppression (objective 2 is an extinguishing agent). BASS has no O2 in its table; pressure (1 atm) is inferred from slide captions only. SAFFIRE-II nominal O2 (~21 percent) is the only nominal-atmosphere claim backed by a direct statement.
- Remaining: ACME-BRE, FLEX, FLEX-2, SAME (MVP), then SAME-R, CFI, ACME-E-FIELD, SPICE, SLICE.

### ADR-0039 ? First Streamlit research dashboard
- Date: 2026-11-14 ? Type: ENHANCEMENT ? Status: accepted
- Context: the user authorized implementation of the dashboard after SPEC-001 and its QA, with a restrained hackathon presentation and continued ADR updates.
- Change: added pure condition predicates, read-only application queries/use cases, a snapshot adapter and registered evidence reader, plus the Streamlit composition root and native views. The explorer renders live curated counts, granularity-aware coverage charts, catalog filters, record inspectors, column definitions, draft/manual evidence and source downloads. Scientific files and curation models remain untouched. Optional dashboard dependencies and a native light theme are registered.
- Validation: Ruff and strict domain mypy pass; 91 tests pass and 57 visual-PDF evidence tests skip because pdftotext/poppler is absent. AppTest exercises rendering, Test points/Evidence navigation, no-match search and reset; an additional UI check exercised ambient O2 >=30%. HTTP health on 127.0.0.1:8501 returned 200. Source download/checksum and snapshot integration tests pass.
- Consequences: this is the first explorer increment, not completion of all 50 acceptance cases or the ranking/RAG/export MVP. docs/dashboard.md describes startup, actual scope and limitations. The local Streamlit server was started for verification. Full interactive/browser accessibility and performance targets were not certified.

### ADR-0040 ? Generic Pydantic claims cannot be pickled by Streamlit data cache
- Date: 2026-11-14 ? Type: BUG ? Status: resolved
- Context: initial AppTest failed with UnserializableReturnValueError while caching a Snapshot containing generic Claim tuples. Dynamic Pydantic generic classes could not be resolved by pickle.
- Root cause: caching validated domain instances directly depends on pickle compatibility of generated generic classes.
- Fix: cache only revision plus model_dump_json strings, then reconstruct validated models per rerun/session. AppTest now renders without exceptions. This preserves independent mutable dictionaries across sessions rather than sharing domain objects through cache_resource.
- Consequences: JSON reconstruction has a small unmeasured cost; no domain model was changed to accommodate the UI cache.

### ADR-0041 ? Explorer preflight guards incomplete pairs and manual parent identities
- Date: 2026-11-14 ? Type: FIX ? Status: resolved
- Related: ADR-0037, ADR-0038 (consumer safeguards only).
- Change: FileSnapshotProvider checks both curated files, required/unique headers, directory/aggregate/manual parent ids, record granularity and finite conditions/quantities before exposing a snapshot. Regression tests reject CSV-only directories and mismatched manual identities. Registered sources are resolved within approved roots and checked against pinned hashes when available.
- Consequences: the explorer is protected, while the underlying CuratedRepository discovery and generic Investigation invariant still require owner-level fixes if used outside this adapter. Loading uses completed/idle curation checkpoints and before/after fingerprints; no atomic producer-publication claim is made.

### ADR-0042 ? Remaining first-explorer contract refinements
- Date: 2026-11-14 ? Type: DEBT ? Status: open
- Context: an initial working prototype was prioritized over implementing every proposed projection, error variant and secondary control at once.
- Shortcut: application options/source descriptors use plain mappings and documented selection-state labels; interface formats CatalogRows from Match projections. Standalone O2-basis categorical filtering, complete capture-history UI, family presets and the remaining multi-session/accessibility/performance acceptance cases are deferred. Source download preparation is on demand; this is not the clean-dataset export feature.
- Consequences: all scientific filtering remains in domain/application and all file access behind adapters/use cases, but the proposed DTO/error taxonomy is only partially implemented. SPEC-001 implementation status and docs/dashboard.md report these limits explicitly.
- Review trigger: next explorer increment, before declaring all stage-1 acceptance scenarios complete. Replace display-label sentinels with dedicated selection types before adding localized labels or new state categories.

### ADR-0043 ? Concurrent ADR numbering collision remains visible
- Date: 2026-11-14 ? Type: BUG ? Status: open
- Context: concurrent curation appended another ADR-0035 and ADR-0036 after the existing QA entries with those ids. Their titles distinguish the two sets, but id-only references are ambiguous.
- Root cause: independent appenders selected numbers without a shared reservation mechanism.
- Change: this session allocated new ids above the maximum found anywhere in the file. Past entries were not edited because the log is append-only.
- Consequences: earlier duplicate ids remain unresolved; use entry title/context to disambiguate. No silent renumbering of another workstream was performed.
- Review trigger: agree a shared ADR allocation/alias policy with the curation workstream.

### ADR-0046 — Renumbering of two ADR entries; claims in them superseded
- Date: 2026-11-14 · Type: FIX · Status: resolved · Related: ADR-0015, ADR-0044, ADR-0045
- Context: concurrent sessions appended ADR-0035 and ADR-0036 twice (explorer-spec entries and two curation entries). The QA review found the duplicate ids and ambiguous cross-references.
- Change: the two curation entries of this session were renumbered to ADR-0044 (SAFFIRE-III note) and ADR-0045 (batch 2a); the explorer-spec entries keep ADR-0035/0036. Two statements in them are superseded by ADR-0047: "SAFFIRE-I stays not_reported" and "SAFFIRE-II is the only direct nominal-atmosphere statement; BASS sensors are all inferred".
- Consequences: ids are unique. Before appending, always read the last id from the file tail (this was the second collision).

### ADR-0047 — QA review of batch 1 and 2a: findings fixed
- Date: 2026-11-14 · Type: FIX · Status: resolved · Related: ADR-0032, ADR-0033, ADR-0044, ADR-0045
- Context: an independent QA agent re-checked the 6 manual files with a different method (`pdftotext -layout`, DOCX unzip, whole-document searches). All 90 quotes were found; the semantic layer had defects, each confirmed against the source before fixing:
  - BUG (false `not_reported`): SAFFIRE-I O2. The NTRS paper p. 4 says the Saffire-I panel will burn at "the anticipated oxygen mole fraction of the cabin atmosphere (near 0.21 O2 mole fraction)". Now `inferred`, O2 21 percent (pre-flight expectation).
  - BUG (missed direct source): BASS-II pressure. The report p. 46 gives 99.2 to 99.5 kPa monitored in the tests; the earlier 1 atm came from a modelling assumption (p. 19). Now `verified`, 14.3878 to 14.4313 psi, with p. 102 ("Ambient pressure was 1 atm") kept as a secondary quote.
  - SAFFIRE-II nominal O2 was `verified` but is a pre-flight expectation: now `inferred`.
  - CFI-G note cited 85 percent O2 as habitat-relevant; that is the burner stream (o2_basis oxidizer_stream). The ambient maximum is 39.97. Note corrected. CFI-G hardware dropped the weak quotes (p. 7 pre-completion text, p. 4 proposal) for the as-flown p. 29 statement; color camera now cites the CFI-G caption (p. 55).
  - `measures` and notes that went beyond their quotes (radiometer, pressure, thermocouple heights, frame rate, O2 sensor heading, CO over-range, BASS airflow, 22 percent O2 slide, type B thermocouples, "free drift in orbit", "Table 3"): each now has its own evidence entry or was removed.
  - BASS: removed MCA and CSA-CP as experiment sensors (ISS cabin or crew instruments that the requirements document only says "can" measure O2).
  - Earth applications added where the source states one (SAFFIRE-III, ACME-CFI-G).
  - Sensor vocabulary harmonized across investigations: `radiometer`, `anemometer`, `thermocouple`, `O2 sensor`, `CO2 sensor`, `CO sensor`, `pressure sensor`, `video camera`, `still camera`, `color camera`, `intensified video camera`, `gas flow meter`, `photomultiplier tube`. SAFFIRE-III's "solid-state sensor" became three quantity sensors (the solid-state detail stays in the note); "camera" became `video camera` (the same ISA record says "two video cameras").
- Consequences: all 6 files re-verified (113 quotes) with both extractors. Remaining judgement calls for the human reviewer: BASS-II pillars (prevention only although its objective also cites detection and suppression), SAFFIRE-I pillar (weakest), SAFFIRE-III O2 by analogy with SAFFIRE-I/II (left `not_reported`).
- Review trigger: reviewer decisions on the three items above.

### ADR-0048 — Known limits of the evidence verifier
- Date: 2026-11-14 · Type: DEBT · Status: open · Related: ADR-0032
- Context: from the QA review. (1) The verifier also ignores U+00AD soft hyphens in addition to whitespace (documented here; ADR-0032 said whitespace only). (2) ISA-Tab locators (`Comment[...]`) are not validated against the field the quoted line belongs to; the QA agent checked the six files by hand and found them correct. (3) Word has no native paragraph numbering: a DOCX reviewer finds the quote by text, and `para N` is the count of every paragraph element, tables included. (4) Real PDF-viewer search behaviour is not tested, only two extractors (`pypdf` in the verifier, `pdftotext -layout` in the test).
- shortcut: ISA locator not checked, add a field-name check when a mislabeled locator is found.
- Review trigger: a reviewer reports a quote that the checks accept but their viewer cannot find.

### ADR-0049 — Manual metadata drafted for all 15 investigations
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: accepted · Related: ADR-0026, ADR-0032, ADR-0033, ADR-0048
- Change: `data/manual/<ID>.json` now exists for ACME-BRE, FLEX, FLEX-2, SAME (MVP) and SAME-R, CFI, ACME-E-FIELD, SPICE, SLICE, besides the six already done. All 15 are `draft`; 249 tests pass; every quote is a 1:1 single-line transcription checked by `pypdf` and, for PDFs, by `pdftotext -layout`.
- Summary (curator's classification, all `inferred`): prevention: ACME-BRE, BASS, BASS-II, SAFFIRE-I/II/III; prevention + suppression: BASS, FLEX; detection: SAME, SAME-R; no direct pillar: ACME-CFI-G, ACME-E-FIELD, CFI, FLEX-2, SLICE, SPICE. Gravity: 14 microgravity, 1 partial_emulated (ACME-E-FIELD). Nominal atmosphere: 3 verified, 6 inferred, 4 not_reported (SAFFIRE-III, SAME, SAME-R, SLICE), 2 absent because the table carries it (ACME-CFI-G, FLEX).
- Source notes worth knowing: the SLICE documents are in the BASS folder, not in `knowledgeBase/MSG (SolidAndGas)/SLICE/` (only the CSV). SAME2 holds byte-identical copies of three SAME documents (SHA-256 checked). PDF text layers differ from the page ("O 2", "high -definition", "o nly", ligatures); quotes avoid those spans.
- Review trigger: reviewer decisions listed in ADR-0050.

### ADR-0050 — Judgement calls left to the human reviewer
- Date: 2026-11-14 · Type: TRADEOFF · Status: open · Related: ADR-0034, ADR-0048, ADR-0049
- Context: no source states a fire-safety pillar, so every pillar is the curator's classification. The cases where the call is least clear:
  - Empty pillar list (no direct pillar) for ACME-CFI-G, ACME-E-FIELD, CFI, FLEX-2, SLICE, SPICE. FLEX-2 and SPICE are tagged 'Spacecraft Fire Safety' / 'Fire Safety' in their PSI records while their own requirements or objectives are basic combustion science; the sources differ and are not reconciled. CFI sits in the project's `suppression` folder, a grouping of this project, not of the sources.
  - BASS-II: prevention only, although its objective also cites detection and suppression system design. SAFFIRE-I: prevention rests on a series-level objective. BASS: suppression from objective 2 (an extinguishing agent).
  - ACME-E-FIELD gravity: `partial_emulated` is inferred from a report sentence that electric fields 'may be a good tool for approximating buoyancy body forces at partial gravity'; the tests ran in microgravity and no partial-gravity measurement exists. The reviewer may prefer `microgravity`.
  - SAFFIRE-III O2 by analogy with SAFFIRE-I/II (left `not_reported`).
  - ACME-BRE nominal atmosphere is an envelope of three planned (pressure, O2) pairs; the pairing cannot be represented (see ADR-0051).
- Consequences: the dashboard must keep the draft badge and show pillars as 'curator classification'. A ranking criterion must treat an empty pillar list as 'no direct pillar', not as an error.
- Review trigger: reviewer decisions.

### ADR-0051 — `NominalAtmosphere` cannot represent paired conditions (proposed)
- Date: 2026-11-14 · Type: ENHANCEMENT · Status: deferred · Related: ADR-0050, SPEC-001 §6.3
- Context: ACME-BRE plans three habitat atmospheres as pairs (14.7 psia with 21 percent O2, 10.2 psia with 26.5, 8.2 psia with 34); FLEX-2, CFI and BASS-II give independent ranges. The model stores min/max per quantity, so a pair becomes an envelope that could be misread as a rectangle (34 percent O2 at 14.7 psia was not planned).
- Proposal: an optional `conditions: tuple[(o2_percent, pressure_psi), ...]` of planned pairs on `NominalAtmosphere`, each with its own evidence. Needs schema review with the dashboard workstream; until then the pairing lives in the claim note and the stage-2 ranking must not combine O2 from one claim with pressure from another.
- Review trigger: the ranking step (`OxygenProximity`/`PressureProximity`) starts.

### ADR-0052 — Second QA round: nominal atmospheres corrected, evidence added to notes
- Date: 2026-11-14 · Type: FIX · Status: resolved · Related: ADR-0033, ADR-0044, ADR-0047, ADR-0049, ADR-0050
- Context: a second independent QA agent re-checked all 15 manual files (257 quotes, 0 mechanical failures). Its semantic findings were confirmed against the sources before fixing. Same class of defect as round 1: an as-run statement existed and the claim used a plan, an assumption or nothing.
- BUG and FIX:
  - ACME-E-FIELD nominal atmosphere was `inferred` from a pre-flight plan; the final report states the as-run conditions: coflow 21 percent O2 with nitrogen balance in all cases (p. 46) and a nominal 100 kPa in the tests of the quoted paper (p. 21). Now `verified`, O2 21 percent and 14.5038 psi.
  - ACME-BRE nominal atmosphere: the report states what was tested (21 percent O2 at 14.7 psia, 27 at 10.2, 34 at 8.2, p. 18) and O2 up to 40 percent (p. 20). The earlier note ('not a statement of what was run') was wrong. Now `verified`, O2 21 to 40 percent and 8.2 to 14.7 psi; the pairing warning stays (ADR-0051).
  - CFI nominal atmosphere used a 0.25 atm bound that is only an objective and `verified` although its two quotes conflict. The Science Final Report lists the flown pressures: 0.5 to 5 atm (p. 6). Now `verified` on that range; the conflict is noted.
  - SPICE nominal atmosphere took 101 kPa from a calculation assumption. Dropped; O2 19 to 24 percent (cabin air) is kept and `verified`.
  - ACME-BRE `color camera`, `radiometer` and the planned burner sizes rest on design text ('will', 'in development'): marked `inferred` or moved into a note; hardware `verified` only on the ISA record.
  - ACME-E-FIELD gravity regime gained the microgravity and ISS evidence its note relied on; the `partial_emulated` label is unchanged and stays a reviewer decision (ADR-0050).
  - SAME and SAME-R sensor claims now cite body text (DustTrak, P-Trak, 'the zeroth-moment instrument is a condensation nuclei counter'); SAME-R `thermophoretic soot sampler` is `inferred` (curator's identification); the SAME not_reported note now states the EIRD instrument pressure range (0.08 to 0.13 'mPa', a typo for MPa) is not a test atmosphere.
  - Facts that sat in notes without evidence now have an evidence entry: table-derived values (the experimental CSV is a valid evidence source: SAFFIRE-I 21.5 to 21.7, ACME-CFI-G 39.97, FLEX-2 matrix), FLEX-2/CFI/SLICE objectives, SLICE hardware and measurement notes, FLEX Earth application.
  - SPICE gained the TSI omni-directional anemometer; ACME-E-FIELD radiometer is `verified` from p. 14.
- Counts (supersede earlier numbers): nominal atmosphere 6 verified, 3 inferred, 4 not_reported, 2 absent (table carries it). 296 evidence entries. ADR-0047 said 113 quotes for the six first-round files; the file counts were 111. ADR-0049 lists BASS under prevention only in its first group; it has prevention and suppression.
- Not done (backlog, no evidence line of 20 characters or more): FLEX-2 ultraviolet and multispectral cameras (its requirements table prints them in short fragments); ACME-E-FIELD intensified monochrome camera (the source says 'available'); SLICE O2 analyzer and pressure transducers (ISS or crew instruments, as for BASS in ADR-0047). A dashboard Sensor filter will therefore miss those on those investigations. Post-flight laboratory instruments (SAME TEM, SAME-R SMPS) sit in the same list as flight sensors and are only flagged in notes: a `role` field would separate them (see ADR-0034).
- Known repo hygiene: a `.test-tmp/` browser-profile directory in the repo root comes from the dashboard workstream, not from curation; the repository is not under git, so nothing is tracked or ignored.
- Review trigger: reviewer decisions (ADR-0050), or any new document for an investigation.

### ADR-0053 ? Detail navigation did not explain the investigation sections
- Date: 2026-11-14 ? Type: BUG ? Status: resolved
- Context: the user reported that the short Investigation view buttons did not make the purpose of each section identifiable.
- Root cause: compact Overview/Test points/Evidence labels lacked explicit subject and action descriptions.
- Fix: replaced the segmented view selector with named peer tabs: Research & scientific context, Experimental records & raw values, and Citations & source downloads, plus an explanatory caption. Existing evidence and record inspectors remain available.
- Validation: AppTest asserts the tab labels and the record/source selectors without UI exceptions.

### ADR-0054 ? BI-style analytic comparison workspace
- Date: 2026-11-14 ? Type: ENHANCEMENT ? Status: accepted
- Context: the user requested Power BI/Salesforce-style dashboards with multi-picklists, scatter plots and comparative lines in addition to existing coverage bars.
- Change: retained global applied multi-select filters and coverage bars; added chart-local investigation multi-selection, canonical-quantity axis selectors, explicit O2 basis, record-tooltipped interactive scatter and selectable comparative line series. BuildChartData in application selects comparable quantities and prepares scalar record pairs without pandas/Streamlit. The interface only formats/chart-renders these results.
- Validation: Ruff and strict domain mypy pass. Full suite: 104 passed, 179 skipped because pdftotext/poppler is absent. New application tests verify range exclusion, basis/granularity filtering and independent fuel-series medians. AppTest covers chart controls, disconnected assistant controls, empty comparison selection, catalog navigation/filter/reset. Local Streamlit health returned HTTP 200. Full browser visual/accessibility review was not certified.
- Consequences: chart controls refine visualizations rather than silently changing the catalog query. Specs and traceability now contain 58 unique acceptance cases; not all are claimed runtime-complete. Source/manual/curated scientific files were not modified.

### ADR-0055 ? Explicit descriptive aggregation for comparative lines
- Date: 2026-11-14 ? Type: DECISION ? Status: accepted
- Context: connecting unrelated experimental records or plotting arbitrary interval midpoints would imply unsupported trends.
- Options: source-order connecting lines; fitted predictive curves; explicitly grouped descriptive summaries alongside raw scatter.
- Decision: lines show median reported vertical values at each reported horizontal value, grouped separately by investigation, fuel, flow direction and O2 basis. Only compatible scalar pairs from individual test records are eligible; missing/nondegenerate ranges, incompatible O2 bases and day/matrix summaries are not treated as paired test observations. Consistent canonical units and original quantity identities are required.
- Consequences: median aggregation is presentation analysis, not a new scientific observation, time series, causal model or flammability boundary. Other conditions can vary and the caveat remains visible. Raw scatter, counts and source rows support interpretation. No imputation, nominal-atmosphere substitution or synthetic midpoint is introduced.
- Review trigger: adding regression, experimental-control matching or scenario/predictive calculations requires its own scientific contract.

### ADR-0056 ? Visible future copilot surface with no simulated AI
- Date: 2026-11-14 ? Type: TRADEOFF ? Status: accepted
- Context: the user explicitly requested a visible AI/dashboard interaction space before SI/LLM integration, superseding SPEC-001 section 3 exclusion of any chat placeholder for this surface only.
- Decision: display a Research copilot panel with Not connected status, disabled question/action controls, actual dataset/query/chart context and a description of future supported actions. It makes no model call, generates no answers and changes no filters. SPEC-001 section 14 defines future revision-scoped validated proposals: filters, axes, series and evidence navigation.
- Consequences: dashboard context is reviewable today, but typed assistant actions, executor and model remain unimplemented. A future LLM must use validated application commands and cannot execute arbitrary code, modify scientific data or calculate/override scores. The panel is a clearly disclosed integration surface, not an operational assistant.
- Review trigger: implementation of the assistant action port, user preview/apply workflow and RAG/Narrator validation.

### ADR-0057 - Screenshot-led research workspace layout
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Context: the user supplied a design image and requested that charts use an optional Research copilot toggle. Figma Dev Mode/code extraction is not available and is not required to implement the supplied reference.
- Change: introduced top Dashboard/Investigations/Evidence navigation, a horizontal multi-select filter panel, four metric cards, a compact chart-settings expander, a profile Lines/Scatter switch, volume bars, a record-level composition donut, experimental coverage intervals and a linked investigation preview. View export delivers JSON settings/revision/result ids only. Theme is white/slate/teal; static CSS is isolated from application/domain rules.
- Consequences: existing scientific filtering, scalar-pair validation, descriptive median grouping, source access and per-record inspection remain intact. Default comparison series include an available series per investigation for readable visual comparison, not relevance ranking. Singleton coverage values have explicit endpoint ticks. The screenshot's illustrative numbers and curves were not imported as scientific data.
- Validation: full suite before final presentation refinements: 104 passed, 179 skipped because pdftotext/poppler is absent. Ruff and strict domain mypy pass; updated UI/application tests cover navigation, reset, empty chart selection, disconnected copilot and filter/axis preservation. A real headless Chrome session verified the desktop dashboard and absence of the former sidebar; desktop screenshot stored under docs/screenshots/. Mobile accessibility and pixel-identical reproduction were not certified.

### ADR-0058 - Copilot panel toggles without changing dashboard analysis
- Date: 2026-11-14 | Type: DECISION | Status: accepted
- Related: ADR-0056; supersedes its always-visible placement only.
- Context: the user wants the chart layout to resemble the supplied reference and keep the Research copilot optional.
- Options: permanently reserve a narrow chart area for the assistant; use an explicit optional panel.
- Decision: the Research copilot toggle defaults off; when enabled, the panel opens to the right of the dashboard, and closing it restores chart width. On investigation/evidence pages the same toggle reveals the panel below the details. Applied filters and selected quantities remain unchanged. No AI model, answers or command executor is simulated.
- Consequences: the full-width reference layout is the default, with an explicit integration surface available on demand. Export view is a configuration artifact, not a clean dataset export or a dashboard screenshot.
- Review trigger: connecting validated assistant commands or changing the responsive panel behavior.

### ADR-0059 - Running server retained stale imported view functions during layout change
- Date: 2026-11-14 | Type: BUG | Status: resolved
- Context: first real-browser inspection showed the new top navigation alongside the previous sidebar filter function, despite the current code using horizontal filters. Automated fresh-process tests rendered the current layout.
- Cause: the long-running Streamlit process retained a previous imported view implementation/theme during this workspace update; the exact file-watcher behavior was not further diagnosed.
- Fix: restarted the owned local Streamlit process after updating views/theme. Fresh browser inspection confirmed sidebar=false, all four chart cards and the optional copilot initially hidden. The startup guide notes the restart requirement for stale layout revisions.
- Consequences: local server is available on 127.0.0.1:8501 with the current layout. Desktop preview is a real rendering; complete automated browser interaction/accessibility certification remains outside this change.

### ADR-0060 - Data-quality review of ACME-CFI-G and cross-investigation gaps (findings only, nothing changed)
- Date: 2026-11-14 | Type: BUG | Status: open | Related: ADR-0021, ADR-0050
- Context: the user reported odd ACME profile charts in the dashboard. Reviewed `data/curated/*/test_points.csv`, the two raw ACME-CFI-G tables and `application/chart_data.py`. No code or data was modified.
- Finding 1 (not a data defect; chart design): `BuildChartData.lines` groups by investigation, fuel, flow direction and O2 basis, but the Streamlit chart colours by investigation. The ACME-CFI-G series "30% butane" (52 tests, 35 distinct O2 values, 21.1 to 39.9 percent) varies pressure (7.3, 14.7, 29.4 psi), burner fuel fraction and fuel mass flow rate at the same time as O2. Burn time is not a function of O2 there (corr 0.22), so a line through medians sorted by O2 zigzags. The 21.5 to 35 percent segment is a straight line across an untested gap (0 tests).
- Finding 2 (BUG, open): 57 of 329 ACME-CFI-G `burn_time_s` values are 0 and 55 of them have `hot_ignition = No` (no ignition), plus control runs with fuel flow 0. Charting a median of burn time mixes "did not burn" with "burned for N seconds".
- Finding 3 (BUG, open): ACME-CFI-G categorical values are not case-normalized: `flame_configuration` Inverse/inverse, `hot_ignition` Yes/yes and No/no, `flame_color` yellow/Yellow and blue/Blue. Also `fuel_name` is a raw label (for example `30% butane`, `100%C2H4`, `75 % Propylene`, `pmma 2 cm`) and splits one fuel into several chart series (fuel-material normalization is still pending).
- Finding 4 (BUG, open, ADR-0021): FLEX test 114 still carries 0 psi, which would plot as a real point.
- Finding 5 (coverage): O2 is absent for BASS, SAME, SAME-R, SPICE, SLICE, SAFFIRE-III and ACME-E-FIELD; pressure is present only for ACME-CFI-G, CFI, FLEX and FLEX-2. The lunar demo scenario (at least 30 percent O2, at most 10.2 psi) has O2 and pressure together only in ACME-CFI-G and FLEX.
- Finding 6: the sensor `intensified video camera` of ACME-CFI-G cites the report abstract (p. 23, "The diagnostics included an / intensified video camera, ..."). The report's own hardware lists (p. 33, p. 86) call it the "CFI intensified camera".
- Planned fix (not applied): case-normalize categorical columns; treat no-ignition burn time as an outcome flag instead of 0; zero FLEX test 114 pressure to missing; normalize fuel names; in the chart, separate series by pressure or colour by series, and break lines across gaps.
- Review trigger: user decision on which of these to apply.

### ADR-0061 - Lower-case categoricals, fuel label normalization, FLEX 0 mmHg fix, scatter-only profile chart
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0021, ADR-0034, ADR-0060
- Context: the user approved the ADR-0060 plan: one casing for categorical values, standardized fuel names, the FLEX test 114 fix, and a scatter-only profile chart.
- Decision 1: the pipeline lower-cases every `Text` column except those declared `free_text=True` (ACME-CFI-G comments, SAME-R test description). Meta columns (ids, dates, video names) keep the source casing. Result: ACME-CFI-G `flame_configuration` is `normal`/`inverse`, `hot_ignition` is `yes`/`no`/`flash`.
- Decision 2: `fuel_name` now holds only the material or species the label literally names, in lower case (`ethylene`, `methane`, `pmma`, `sibal`, `paraffin wax`, `heptane+iso-octane`). New extras: `fuel_geometry` (sphere, rod, slab, film, sheet, candle, fabric), `fuel_label_fraction_percent` (percentage printed in the label, `(pure)` = 100) and `fuel_name_raw` (original label, kept whenever it differs). The implementation is `ingestion/fuel_names.py` with an ordered pattern table; matched spans are consumed so `methane` is not read as `ethane`.
- TRADEOFF: labels that state no material (BASS-II `1/4" clear rod`, `2 cm sphere`, films without PMMA) get `fuel_name = null` (57 of 129 BASS-II rows, 34 of 122 BASS rows, 2 SAFFIRE-II rows with an empty cell), so the dashboard fuel filter groups them under "Not reported". Guessing PMMA would invent a value (data rule 1). The ISA-Tab text has no statement that settles it; the PDFs were not searched for one.
- Decision 3 (FIX of ADR-0021): FLEX test 114 `0 mmHg` is now `null`, raw `0` kept in `pressure_psi_raw`, row `inferred` with a note (column fixup `zero_pressure_as_missing`).
- Decision 4: the profile chart is scatter-only (one translucent outlined dot per reported test, larger plot, richer tooltip). `BuildChartData.lines`, the Lines/Scatter switch and the line-series selector were removed. This also resolves ADR-0060 findings 1 and 2: no median joins tests that differ in pressure or fuel fraction, and no segment crosses an untested gap. Zero burn times are kept as reported (the source states 0 for non-ignition tests); they sit at the bottom of the scatter.
- BUG (ADR-0060 finding 5, not fixable in code): the raw tables of BASS, SAME, SAME-R, SPICE, SLICE, SAFFIRE-III and ACME-E-FIELD carry no O2 column and only BASS-II, FLEX, FLEX-2, CFI, ACME-CFI-G, SAFFIRE-I/II and ACME-BRE report O2; pressure exists only for ACME-CFI-G, CFI, FLEX and FLEX-2. Verified by listing every raw header. Filling these from the manual `nominal_atmosphere` would put a plan or an assumption into a per-test column, so nothing was changed. The lunar scenario has per-test O2 and pressure together only in ACME-CFI-G and FLEX; this must be stated in every ranked answer.
- DEBT: `silicone` (SAME-R) and `silicone rubber` (SAME) and the Nomex variants (`blend`, `natural III`) are left as the sources label them; a reviewer should decide whether they are one material. Fuel size and thickness remain only in `fuel_name_raw`. Payback trigger: a ranking criterion or filter that needs them.
- Verification: ruff clean, `mypy --strict` on the domain clean, 300 tests pass; `data/curated/` regenerated. Not verified: rendering of the new chart in a browser.

### ADR-0062 - Profile chart offers only plottable axis pairs; silicone vs silicone rubber evidence
- Date: 2026-11-14 | Type: BUG | Status: resolved (chart) / open (silicone decision) | Related: ADR-0060, ADR-0061
- Symptom: with filters limited to ACME, BASS or SAFFIRE, or with pressure or flow speed on the horizontal axis, the profile chart showed few or no dots and nothing said why.
- Root cause (verified by running the app headlessly and the chart builder on every investigation): not a rendering failure. (1) The vertical axis stayed on burn time, which exists only for ACME-CFI-G, FLEX, SAFFIRE-I and SAFFIRE-II; with pressure on x the plot has 596 records (ACME-CFI-G, FLEX), with flow speed on x only 7 (SAFFIRE-I/II) because SAME, SAME-R and SPICE have flow speed but no burn time. (2) ACME-BRE, ACME-E-FIELD, SLICE and FLEX-2 are `test_day`/`test_matrix` records and are never plotted by design. (3) BASS has no scalar quantity at all. (4) When the vertical default was missing it fell to the alphabetically first quantity.
- Fix: `BuildChartData.partners` counts plottable records against the chosen x for every other quantity. The vertical selector now lists only quantities with at least one pair, most records first, shows the count, and a stale pick is dropped. A caption lists records plotted per investigation and the investigations with no plottable pair. Test `test_partners_count_only_plottable_pairs`.
- BUG found while fixing (mine, resolved): a closure variable `counts` in `chart_grid` was shadowed by a later `counts = Counter(...)`, which made the option labels show 0 records; renamed `pair_counts`. The headless app test caught it.
- Silicone evidence (no data changed): SAME-R final report (`SAMER_Final 0602 2014.pdf`, p. 3) lists "6 silicone rubber" loose samples and (p. 4) "samples of 6 materials: Teflon, Kapton, Pyrell, silicone rubber, cellulose (lamp wick), and dibutyl-phthalate"; its carousel tables label the same samples "Silicone". The SAME final science report (p. 3) says "silicone rubber, and Teflon". Both programs therefore name the same material, silicone rubber; the SAME-R table label `Silicone` is the short form. Whether the two campaigns used the same formulation is not stated in the cited lines.
- Proposal: map `silicone` to `silicone rubber` for SAME-R, awaiting user confirmation. The raw label stays in `fuel_name_raw`.
- Verification: ruff clean, mypy strict on domain clean, 301 tests pass. Not verified: pixel rendering in a browser.

### ADR-0063 - FLAMSA light-glass presentation and local brand mark
- Date: 2026-11-14 | Type: DECISION | Status: accepted
- Context: the user requested the atmospheric background and glass effects of a new design reference while keeping the current analytic colors and adding FLAMSA identity. No original logo asset was present in the repository.
- Options: adopt the reference's dark/neon palette; preserve the current palette and introduce a restrained light-glass surface treatment.
- Decision: preserve blue/slate/teal series colors and the light workspace. Add cool ambient gradients, a decorative CSS horizon, translucent card backgrounds with backdrop blur, soft edges/shadows, visible focus indicators, reduced-motion handling and a solid-surface fallback. Chart canvases are transparent so they share the card surface. Add a local SVG interpretation of the supplied flame/FLAMSA wordmark and include it in setuptools package data; this is not an extracted original brand asset. The hero and browser title use FLAMSA. No external raster/font dependency was added.
- Validation: Ruff clean, strict domain mypy clean, SVG XML parses; 122 tests passed and 179 visual-PDF checks skipped because pdftotext/poppler is absent. UI tests passed for navigation, filters and copilot state. Real headless Chrome verified the FLAMSA header/logo, computed blur(16px) on the profile card and zero rendered exceptions; desktop screenshot saved in docs/screenshots/flamsa-glass.png. The local server was restarted to apply imported views and theme changes.
- Consequences: presentation only; scientific data, chart semantics, compatible-axis selection and the latest dots-only profile behavior are preserved. Full contrast/accessibility auditing on every viewport/browser and visual inspection of no-backdrop-filter fallbacks were not performed. The current SVG can be replaced with an original brand file later without touching domain/application code.
- Review trigger: original FLAMSA brand asset supplied, a dark-mode request, or further accessibility/performance review.

### ADR-0063 - SAME-R silicone alias; chart counts reconcile to the full record total
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0061, ADR-0062
- Decision 1: the user confirmed that `Silicone` (SAME-R) and `Silicone rubber` (SAME) are one material, consistent with the SAME-R final report (p. 3-4). `AdapterSpec.fuel_aliases` maps the normalized `silicone` to `silicone rubber` for SAME-R only; the raw label stays in `fuel_name_raw`. SAFFIRE-II `silicone` is left unchanged because no source read for it states the formulation. Closes the silicone DEBT of ADR-0061 for SAME and SAME-R.
- BUG (reported by the user, resolved): the chart caption "447 compatible + 1,109 excluded" summed to 1,556, not the 1,615 curated records. Root cause: `BuildChartData` skipped daily (`test_day`: ACME-BRE 18, ACME-E-FIELD 21, SLICE 12) and matrix (`test_matrix`: FLEX-2 8) records before counting them, so the 59 were silently outside both numbers (18+21+12+8 = 59). Fix: `ChartData.summaries` counts them and the caption now reads plotted, tests without a plottable pair, and summary records never plotted; 447 + 1,109 + 59 = 1,615 (checked on the full dataset).
- Note: two interface tests failed once in a full run and passed in isolation and on rerun (305 passed); they use 30 to 45 second AppTest timeouts and are sensitive to machine load. Not diagnosed further.

### ADR-0064 - English FLAMSA homepage adapted from the supplied React concept
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Context: the user supplied Portuguese React/TanStack homepage code and requested an English Home in the existing application.
- Change: added Home as the initial Streamlit destination, retaining Dashboard/Investigations/Evidence and the FLAMSA light-glass design. English introduction, four selectable research themes, a numbered conceptual scene, archive-based counters and navigation calls are implemented with native widgets. GetHomeSummary in application produces snapshot-based counts and source-bounded research ids; Earth-application links require nonempty curated claims. Open related research explicitly selects those ids; ordinary navigation preserves the current query.
- Validation: Ruff and strict domain mypy clean; full suite 126 passed, 179 skipped because pdftotext/poppler is absent. Five final focused homepage/application/UI tests passed. Tests verify current-id bounds, no fabricated Earth applications, unknown-theme rejection, English Home/default navigation, dashboard regressions and research-link routing. Real headless Chrome rendered the English Home, conceptual-illustration label and zero exception elements. Screenshot saved in docs/screenshots/flamsa-home.png. The server was restarted for the current homepage.
- Consequences: this is a native Streamlit adaptation, not a React/Tailwind runtime. Domain/scientific data, curation and ranking scores were not modified. Browser/mobile/accessibility certification across all themes/viewports remains incomplete.

### ADR-0065 - Homepage illustration and relevance claims stay explicit
- Date: 2026-11-14 | Type: TRADEOFF | Status: accepted
- Context: the supplied code imports flamsa-hero.jpg without providing that asset, labels NASA as LIVE, assigns hardcoded illustrative relevance scores and includes investigations beyond the curated registry.
- Decision: retain the four-topic concept with a locally packaged SVG scene labelled conceptual, and native accessible topic controls rather than unsupported image hover handlers. No generated/experimental photograph is claimed. Replace illustrative scores with archive counts, review status and a clear planned-ranking description. Loaded canonical investigation ids are used for links; no live NASA connection is claimed. Introductory copy does not repeat unsupported universal flame/suppression statements from the prototype.
- Consequences: the homepage is usable without a missing raster dependency or extra JavaScript stack. Its topics are navigation starting points, not scored rankings or new source-backed scientific claims. The supplied original hero asset can replace the concept illustration later. Ranking/AI remain unimplemented and clearly described as planned.
- Review trigger: original hero asset supplied, true image-hotspot interactions requested, or deterministic ranking and validated narrative implemented.

### ADR-0066 - Navigation callbacks no longer conflict with widget defaults
- Date: 2026-11-14 | Type: FIX | Status: resolved
- Context: server logs showed a Streamlit warning that workspace_navigation had both an explicit widget default and a Session State value supplied by navigation callbacks.
- Root cause: callback-selected navigation and the segmented control default were competing initialization mechanisms.
- Fix: initialize workspace_navigation to Home once in session state and set the widget default to None. CTA callbacks can select Dashboard/Investigations without conflicting defaults; updated UI tests pass.
- Consequences: first load opens Home and navigation remains per session. No query or dataset mutation was added by the initialization fix.

### ADR-0067 - Physical-consistency review of curated data against the PSI reports
- Date: 2026-11-14 | Type: ENHANCEMENT + BUG (logged, not fixed) | Status: open for the BUG items
- Context: the user asked whether the dashboard data agree with combustion theory, with source passages as evidence. The full review, with page-cited quotes (each checked to exist on its page via pdftotext), is `docs/DATA_QUALITY_REVIEW.md`.
- ENHANCEMENT (done): `tests/infrastructure/test_physical_consistency.py` enforces on the committed curated data: FLEX burn time follows the d-squared law (median ratio 1.04); FLEX K rises with O2 in N2; ACME-CFI-G stoichiometric mixture fraction recomputed from O2 and fuel fraction matches all 331 reported values within 4e-5; ACME-CFI-G O2 after a test never exceeds O2 before; BASS-II CO2 never falls by more than the 0.1% CDM resolution; SAFFIRE-II spread rate equals burn length over burn time within 10%. These guard against column swaps and unit-conversion regressions.
- BUG (source data, not fixed, each needs a user decision because it changes a published value):
  1. SPICE: 36 rows labeled `75 % Propylene` on GMT days 119 and 136 (source rows 270-305) imply a density of 0.651 kg/m3 (methane's) instead of the 1.566 kg/m3 of the other 96 rows with the same label; mass flows are about 2.4x low.
  2. BASS-II: final O2 of 1.6/0.6/0.9% (B2, P22a, T28a) and 39.1/40.4% (P22b, T28b) are physically impossible in the 250 L MSG work volume.
  3. BASS-II: 13 negative initial CO readings (-1 to -3 ppm) kept as numbers.
  4. SAFFIRE-II: thickness `037 mm` (2-4, 2-5, 2-6) curated as missing; 0.37 mm is likely but not stated.
  5. ACME-CFI-G 21106 F4: `hot_ignition = no` contradicts its 22 s burn time and "hot flame" comment.
  6. FLEX rows 39, 43, 52, 93: extinction diameter 0 on `disruption` outcomes.
  7. CFI r13-r16: gas composition sums to 97%.
- Not verified: adiabatic flame temperatures (needs an equilibrium solver); SAME/SAME-R smoke relations; visual check of quotes in a PDF viewer.

### ADR-0068 - Chart omissions looked like missing research-filter results
- Date: 2026-11-14 | Type: BUG | Status: resolved
- Context: the user selected BASS, BASS-II, CFI, FLEX, FLEX-2 and SAFFIRE-II, all record levels and all fuel phases, but saw only FLEX and SAFFIRE-II in the oxygen/burn-time profile legend.
- Reproduction: the inspected snapshot retains all six investigations and 629 records. The plot has FLEX 268 and SAFFIRE-II 3, totaling 271; 350 individual tests lack a valid pair and FLEX-2 contributes eight summary/matrix records. BASS has no O2/burn-time columns, BASS-II and CFI no burn-time values, FLEX six missing burn times, and SAFFIRE-II four missing burn times plus two interval-valued O2 records. These are source availability/granularity limits, not research records dropped by the global query.
- Root cause: the per-investigation omission explanation was hidden inside collapsed Chart settings; the visible profile only listed plotted investigations and global excluded totals. Global filter results and chart eligibility were not visibly distinguished.
- Consequences: users could interpret correct scientific exclusions as a broken multi-select filter. The fix below preserves data rather than adding synthetic points.

### ADR-0069 - Explain profile availability per investigation and retain record access
- Date: 2026-11-14 | Type: FIX | Status: resolved
- Change: BuildChartData uses one plot_exclusion policy for both plotting and typed per-investigation coverage reports. Each omitted record has one primary reason: chart-local deselection, summary granularity, oxygen basis, missing x/y/both, interval-valued quantities or another non-scalar value. Reports reconcile each filtered investigation total with plotted plus omitted records.
- UI: the profile visibly states selected versus plotted investigation counts and names zero-point investigations. Data availability shows retained totals/granularity, plotted counts and primary reasons, plus wrapped selected-investigation details for narrow screens, available scalar fields and an Open retained records action that preserves the global research query. Coverage cards name investigations without the chosen reported interval. The record-level metric caption also derives its labels from filtered data; previously its static three-label caption could accompany a count of two.
- Validation: Ruff and strict domain mypy passed; strict mypy on chart_data also passed after explicitly typing its row projection. Full suite passed 135 tests, with 179 skipped because pdftotext/poppler is absent. Focused chart/application/UI tests passed eight cases, including reason-count reconciliation, local scope, missing/basis/range/summary cases and the reported six-investigation flow. The local server is restarted for the new view modules.
- Consequences: no source/manual/curated values, O2 basis, numeric imputation or plot inclusion policy was changed to manufacture observations. Nominal atmosphere and matrix envelopes remain distinct from scalar test pairs. The underlying measurements remain sparse; the fix makes that explicit and provides access to all retained records. Browser/mobile visual inspection of the new diagnostics remains unverified.

### ADR-0070 - Filter controls and cached data could disagree with the displayed scope
- Date: 2026-11-14 | Type: BUG | Status: resolved
- Context: the user requested an audit of filters and communication between structured data and the dashboard. AppTest reproduced a Home topic link with applied ids FLEX/FLEX-2/CFI while the Investigation widget displayed an empty selection. Home hides filter widgets, so their state was also lost on a return visit. Invalid submissions displayed old results beside changed controls without a readable committed scope.
- Root cause: widgets used empty/default initialization instead of the committed ExplorationQuery. Cached snapshot loading had no current-input comparison, and the reload button reset the query before attempting validation, including on failure. Sensor claims marked not_reported were collapsed into the empty-list state.
- Impact: users could interpret a stale snapshot, staged draft or correct scientific chart exclusion as missing structured data. The row query itself did not drop records in the reproduced six-investigation case.

### ADR-0071 - Synchronize filter controls, applied scope and transactional reload behavior
- Date: 2026-11-14 | Type: FIX | Status: resolved
- Related: ADR-0070, ADR-0068, ADR-0069.
- Change: hydrate absent controls from the applied query while retaining visible form drafts until Apply. Use named query arguments, explicit rejection messages, readable applied summaries and retained-missing-condition counts. On successful reload, reconcile against new options, preserve valid selections, announce removed labels and rehydrate widgets. Failed loading retains the previous snapshot and query. Home topic navigation clears superseded validation errors.
- Verification: AppTest covers topic-link values, numeric settings after Home, unapplied drafts, invalid bounds, successful/failed reloads and freshness warnings. Existing chart/source/navigation tests continue to pass.
- Consequences: changing a control does not silently change results; current and staged scope remain distinct. No source/manual/curated scientific values were edited.

### ADR-0072 - Complete oxygen-basis filtering and distinguish sensor missing states
- Date: 2026-11-14 | Type: ENHANCEMENT + BUG + FIX | Status: accepted
- Context: standalone categorical O2-basis filtering was specified but deferred; the previous selector affected only an enabled numeric range. A not_reported sensor claim was mapped to No entries mapped, the same label as an empty sensor list.
- Change: add actual o2_basis options and an immutable query selection. Without numeric bounds, selected bases match record-level values including unknown basis. With a numeric range, a nonempty categorical selection must match its single explicit basis or Apply fails. Distinguish unavailable manual metadata, empty sensor lists and not_reported sensor claims without inventing domain values. Known sensor labels remain unchanged.
- Verification: application fixtures cover standalone/multiple/missing basis, conflicting numeric basis, reconciliation and all three sensor states. A UI test verifies the conflict keeps the committed query and succeeds after an explicit basis correction.
- Consequences: existing include-missing numeric semantics remain intact; nominal atmosphere never fills a row condition. Spec section 19 and AC-68 through AC-75 describe the updated contracts.

### ADR-0073 - Check curated-input freshness on reruns while retaining explicit publication and reload
- Date: 2026-11-14 | Type: TRADEOFF | Status: accepted
- Context: curation runs independently while the dashboard uses a JSON-serialized cached snapshot. Direct Excel/source/manual edits must pass through curation rather than being read by widgets.
- Options: automatic ingestion/reloading on file changes; explicit validated reload with a byte-level freshness warning.
- Decision: keep explicit reload after the operator confirms curation is idle. Check the current curated-pair/registry fingerprint through an application port on each rerun and warn if changed/unreadable. No background polling or scientific regeneration is performed. A local ten-call sample cost approximately 4 ms per check over about 658 KB of curated inputs.
- Evidence: audit checkpoint 5fa2ee153f3fa0eee6fa2fbb43e9a546b9982b807ab04f582b075a4f3371fc56 has 15 investigations, 1,615 records, 109 categorical options, 16 matching raw-table hashes and 15 matching normalized manual metadata files. Persisted CSV/JSON identity/cell checks and independent SQL numeric queries pass. Details: docs/data-flow-audit.md.
- Verification: Ruff clean; strict mypy on domain and exploration application passes. Full suite: 156 passed, 179 PDF visual-line checks skipped because pdftotext/poppler is absent, using a fresh workspace-local pytest temporary directory.
- Consequences: curated bytes changed while an idle page is open are detected on the next interaction. This is not an atomic publication guarantee or a check of uncurated source edits. Current metadata is draft and still requires human evidence review.
- Review trigger: atomic curation publication becomes available, background updates are requested, or dataset growth makes per-rerun hashing material.

### ADR-0074 - Verify filter synchronization in the running browser
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Related: ADR-0070, ADR-0071, ADR-0072, ADR-0073.
- Verification: restarted the local Streamlit server at http://127.0.0.1:8501 and confirmed health HTTP 200. Headless Chrome at 1440 by 1700 followed Open related research on Home and then Dashboard. After native components completed loading, the visible Investigation chips and accessible combobox label contained FLEX, FLEX-2 and CFI, matching the applied summary and three-investigation result. Record-volume bars retained all three while the profile explained that only FLEX reports its selected scalar pair. No rendered exception was observed. Capture: docs/screenshots/filter-integration.png.
- Consequences: early progressive-render screenshots can contain placeholder widgets and stale elements; validation waits for completed components. The final captured view was visually inspected. Mobile layouts, complete accessibility checks and the 179 PDF visual-line checks requiring missing Poppler were not verified.

### ADR-0075 - Adapt the supplied FLAMSA homepage into the existing Streamlit workspace
- Date: 2026-11-14 | Type: DECISION | Status: accepted
- Context: after the filter integration audit, the user supplied a React/TanStack homepage, Tailwind stylesheet, UI scaffold and the actual hero JPEG to improve Home. The three route copies and two JPEG copies are byte-identical.
- Options: migrate to the exported React scaffold; adapt the supplied composition/assets in the established Streamlit interface.
- Decision: adapt Home with an image-backed introduction, real snapshot counters, a full-aspect research scene and adjacent contextual panel, and compact workflow cards. Keep English copy, the local FLAMSA logo, light glass workspace and blue/slate accents. Package one unmodified JPEG, SHA-256 87735e81a093698d195b49e581d364d800ad75ba4e95c81cf7871bd2b8cc0891, and add JPEGs to package data. SPEC-001 section 20 supersedes the missing-JPEG placeholder choice from section 17.
- Consequences: scene points and native topic choices select the same existing GetHomeSummary themes. Open related research retains the validated query/navigation path. Source data, application projections and dashboard filter semantics are unchanged. Artwork readings are identified as illustrative. Supplied hardcoded rankings, LIVE badge and unsupported scientific claims are not presented as results. The attached Lovable instructions remain reference content and no connector was contacted.
- Verification references: docs/homepage-design.md, SPEC-001 AC-76 through AC-80 and task traceability.

### ADR-0076 - Cached component registration failed across isolated AppTest runtimes
- Date: 2026-11-14 | Type: BUG | Status: resolved
- Symptom: the first Home test rendered, but a later fresh AppTest runtime raised Component research_scene is not registered while the Python interface module remained imported.
- Root cause: an import-time component callable retained registration from a previous runtime. Session-scoped resource caching also retained that callable because AppTest reuses its session identity across fresh runtimes.
- Impact: later navigation/filter tests could fail before Home rendered even though component content and scientific queries were valid. The implementation was corrected rather than skipping or mocking the failing tests.

### ADR-0077 - Register one fixed scene definition in the active runtime through the public API
- Date: 2026-11-14 | Type: FIX | Status: resolved
- Related: ADR-0076.
- Change: register the fixed namespaced inline Custom Components v2 definition when mounting the single Home scene. Streamlit 1.60 registry code confirms identical definitions are idempotent; differing definitions warn. No cached runtime-bound callable, private registry access or test-only bypass remains. Static assets define image/button rendering; dynamic data only supplies the image URI and active topic. Trigger callbacks validate the known topic and update native selector state before rerendering.
- Verification: all eight interface tests pass in the full suite, including independent AppTest runtimes, preserved research filters on topic changes, and related-id hydration. Browser testing exercises every hotspot and native-to-component synchronization.
- Consequences: registration is performed once per Home render rather than at Python module import. The small, fixed template is identical across renders and sessions; widget state remains per session.

### ADR-0078 - Use a small isolated image-hotspot component with native surrounding UI
- Date: 2026-11-14 | Type: TRADEOFF | Status: accepted
- Context: native Streamlit has no clickable image-hotspot selector; the supplied React design uses four numbered scene points.
- Options: static image with only a separate selector; a minimal inline v2 image/button component; a new React application or packaged frontend build.
- Decision: use an inline v2 component limited to the image and four buttons, with isolated CSS, transient topic triggers and controlled active state. Keep all copy, metrics, context, navigation and alternate topic selection native. Buttons expose labels/pressed state, visible focus, 44 px targets and native keyboard activation. The full image aspect ratio keeps marker locations stable, without automatic image motion.
- Verification: focused homepage/application/UI checks passed ten cases. Full suite: 157 passed, 179 PDF layout checks skipped because pdftotext/poppler is absent; fresh workspace-local pytest temporary paths were used. Ruff and strict domain mypy passed. The final headline-only adjustment passed three focused Home tests.
- Consequences: no separate React/Bun build or frontend dependency installation is required. The component and homepage styles are interface details and perform no scientific query/scoring or external requests. Cross-browser, physical-device and full screen-reader/contrast checks remain unverified.
- Review trigger: scene interactions grow beyond topic selection, multiple complex frontend views are required, or the component needs distribution as a standalone package.

### ADR-0079 - Verify the supplied-asset homepage in the running desktop and mobile views
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Related: ADR-0075, ADR-0076, ADR-0077, ADR-0078.
- Verification: restarted the local Streamlit server after the final imported view/style changes. Headless Chrome verified the original 1600 px image, all four hotspot callbacks, native selector synchronization, focus plus Enter activation, and Open related research leading to visible SAME/SAME-R/ACME-CFI-G/SPICE investigation filter chips. No rendered exception occurred. At 390 px both document and main widths were 390 px; all hotspot targets measured 44 by 44 px and the complete image remained visible. Desktop at 1440 by 1600 and mobile at 390 by 900 screenshots were visually inspected.
- Artifacts: docs/screenshots/homepage-supplied-desktop.png, homepage-supplied-mobile.png and homepage-supplied-mobile-scene.png; design/provenance notes in docs/homepage-design.md.
- Consequences: the supplied composition is now interactive within the existing Streamlit session and uses actual archive projections. Chrome emulation is not a physical-device or cross-browser accessibility audit. PDF layout checks remain skipped until Poppler is installed.

### ADR-0080 - Physical-consistency fixups for the source anomalies of ADR-0067
- Date: 2026-11-14 | Type: FIX + DECISION | Status: accepted | Related: ADR-0067, docs/DATA_QUALITY_REVIEW.md section 2
- Context: the user forwarded a second reviewer's policy for the seven anomalies ("correct only with sufficient evidence, preserve the original, keep physically inconsistent values out of analyses and models") and asked to implement it where it agrees with the evidence.
- DECISION: `Fixup` now receives the whole raw row (`(raw, row) -> (corrected raw, note) | None`) so a rule can use physically related cells. A fixup that returns the raw unchanged only attaches a note and keeps the value `verified`; one that changes it marks the row `inferred`. Existing fixups gained an unused row parameter. Rules are physical conditions, not row-id lists, and thresholds are named constants.
- FIX 1 (SPICE): `spice_mass_flow_density_mismatch` - for `75 % Propylene` rows whose implied density (mg/s x 60 / sccm) is below 1.0 kg/m3, both mass-flow columns become missing, raw kept. 36 rows (GMT days 119, 136); `sccm` untouched.
- FIX 2 (BASS-II): `bass_ii_impossible_final_o2` - final O2 that rises more than 0.5 point or drops more than 10 points becomes missing, raw kept (B2, P22a, P22b, T28a, T28b). Legitimate drops in the table are at most 3.2 points. The header ("Calibrated final O2 % by vol") confirms these are concentrations, not differences. CO/CO2 of those tests are untouched.
- FIX 3 (BASS-II): `negative_reading_as_missing` applied to both CO columns (13 negative initial readings); its note is now generic ("sensor offset near zero").
- FIX 6 (FLEX): `zero_extinction_on_disruption` - `0` extinction diameter on a `disruption` outcome becomes missing (tests 39, 43, 52, 93); `0` on `completion` stays.
- FLAG 5 (ACME-CFI-G 21106 F4) and FLAG 7 (CFI r13-r16): `ignition_conflict` and `composition_not_closed` keep the values and add a provenance note. Not normalized, not set to unknown: the source value is the only evidence and no other column resolves the conflict.
- NOT APPLIED 4 (SAFFIRE-II `037 mm`): the second reviewer cited a NASA presentation giving 0.37 mm with "very high" confidence. A web search found NASA sources listing 0.33, 0.36 and 0.37 mm for the Saffire-II silicone and 0.37 mm for the cotton-fiberglass, so the value is not settled. None of them is archived in `data/external` (ADR-0022). Thickness stays missing with raw `037 mm` kept. Payback trigger: archive one primary NASA table that names samples 2-4, 2-5 and 2-6.
- TRADEOFF (rejected proposal): the reviewer's parallel record (`raw_value`, `validated_value`, `quality_status`, `correction_method`) duplicates what each row already carries (`<column>_raw`, the value, `provenance_status`, `provenance_note`). It was not added.
- Tests: `test_physical_consistency.py` gained one density per SPICE gas, a BASS-II O2 bound with an exact set of flagged tests, no negative CO, and checks that the flagged conflicts keep their reported values.

### ADR-0081 - README documents the physical-consistency business rules
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted | Related: ADR-0067, ADR-0080
- Change: added `README.md` (the repository had none) with run commands and a "Physical consistency rules" section. Rules R1-R8 each give the law, why the dashboard behavior is physically coherent, the confirming source passage (same quotes verified in ADR-0067) and the enforcing test. The handling principles are stated there as well: never replace an observation with a calculation; mark a value missing with its raw kept and the row `inferred`; flag, and do not resolve, conflicts that no other cell settles.
- SPICE (R8) now states the ideal-gas computation explicitly: 75/25 C3H6/N2 gives 1.598 kg/m3 at 294 K and 1.567 kg/m3 at 300 K, against the 0.651 kg/m3 (methane) implied by the 36 anomalous rows. No corrected mass flow is derived.
- Not verified: rendering of the README on a Git host. No code or data changed.

### ADR-0082 - Repository .gitignore blocks secrets, browser profiles and caches
- Date: 2026-11-14 | Type: DECISION | Status: accepted
- Context: the user will publish the project to a Git repository manually and asked for an ignore file that blocks security risks, including .env.
- Decision: `.gitignore` excludes env files (only `*.example` templates allowed), Streamlit `secrets.toml`, keys/certificates/cloud credentials, local AI-assistant state (`.claude/settings.local.json`, `.mcp.json`; the project skill and CLAUDE.md stay shared), `.test-tmp/` (headless-browser profiles with cookie and trust-token stores, 180 MB), Python/tool caches, logs, local databases, editor and OS files.
- Validation: a throwaway git index outside the project showed that only caches and `.test-tmp/` are ignored (no source, data, knowledgeBase or docs file), 1,349 files remain, no file name suggests a secret, and no tracked text file contains the user's e-mail or home path. No hardcoded API key in src/scripts/tests.
- Open decision for the user: `knowledgeBase/` is 1.2 GB (37 zip archives, 285 MB). No file exceeds the 100 MB GitHub limit, but the total is above GitHub's recommended repository size. Not ignored because curation and evidence verification read it (ADR-0008).

### ADR-0083 - Remove knowledgeBase zip archives whose content is already extracted in place
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0008, ADR-0082
- Context: the user asked to confirm whether the zip archives in `knowledgeBase/` had already been extracted in their own folder and, if so, to delete those archives, without replacing any file. This is a user-authorized exception to the read-only rule of ADR-0008, limited to deleting redundant archives; no extracted file was written, extracted again or modified.
- Check (read-only): every non-directory entry of each zip must exist in the zip's folder (or `<folder>/<zip stem>/`) with identical size and CRC32. The check ran twice: once as an audit, then again immediately before each deletion.
- Result: 31 of 37 archives passed and were deleted (228.5 MB; `knowledgeBase/` 1.2 GB -> 920 MB). Their SHA-256, size, entry count and extraction folder are recorded in `docs/zip-removal-report.json`. No code, test, `data/sources.json` or manual metadata referenced a zip; 353 tests pass afterwards.
- Kept (not fully extracted in their own folder), 6 archives:
  - ACME-BRE `ACME_drawings_avionics_package.zip` (1 PDF of 26 MB absent everywhere), `ACME_drawings_burners.zip` (11 PDFs absent everywhere), `ACME_drawings_shipping_containers.zip` (5 PDFs absent everywhere).
  - ACME-BRE `ACME_drawings_common_electrical.zip` (2 PDFs), E-FIELDS `ACME_drawings_expt_mounting_structure.zip` (1 PDF) and `ACME_drawings_igniter.zip` (3 PDFs): the missing PDFs exist byte-identical only in the sibling campaign's extracted folder.
- Follow-up for the user: extracting the 6 remaining archives (without overwriting) would allow removing them as well. Not done here, because this step was explicitly limited to verification and deletion.

### ADR-0084 - Six ACME drawing archives are truncated; 23 PDFs cannot be recovered
- Date: 2026-11-14 | Type: BUG (source data, not fixable locally) | Status: open | Related: ADR-0083
- Context: the user asked to extract the 6 remaining zips (ADR-0083) into their folders, then delete them. Extraction ran with no overwrite (new files opened exclusively, existing files only compared) and with a path-traversal guard.
- Symptom: every remaining archive raises "Bad magic number for file header"; central-directory offsets point before the start of the file (-1,048,576 for the first entry).
- Root cause: each archive is exactly 1 MiB shorter than its own central directory describes (avionics 28.0 vs 29.0 MB, burners 13.0 vs 14.0, common_electrical 6.8 vs 7.8, shipping_containers 4.2 vs 5.2, E-FIELDS mounting 1.8 vs 2.8, E-FIELDS igniter 1.8 vs 2.8), i.e. a lost 1 MiB block in the original transfer. Every entry whose bytes survive is already extracted and identical on disk.
- Impact: 23 ACME hardware-drawing PDFs are absent from the project and cannot be rebuilt from these archives; 6 of them exist byte-identical in the sibling campaign folder (ACME-BRE/E-FIELDS). Searching for the local headers found none intact (CRC32 checked). No curated data, evidence quote or test depends on them.
- Action: nothing was written, extracted or deleted in this step. The 6 archives are kept, and the missing file names are listed in `docs/zip-removal-report.json` (`kept_damaged_archives`).
- Payback trigger: re-download the six archives from NASA PSI, then extract them without overwriting and remove them.

### ADR-0085 - Add a source-bounded fire-behavior evidence workspace
- Date: 2026-11-14 | Type: DECISION | Status: accepted
- Context: the user requested FLEX K/O2 fits, BASS-II oxygen/CO2 changes and SAFFIRE-II ground/microgravity comparisons, with controlled groups, uncertainty, citations and continuous ADR contributions.
- Options: extend the generic comparison chart with pooled trend lines; create an explicitly constrained evidence workspace sharing the current snapshot/query.
- Decision: add Fire behavior & safety evidence with three native tabs. SPEC-002 defines consumption, scientific/statistical guards, provenance, exports and FB-01 through FB-12. BuildFireBehavior consumes existing Match projections; numerical calculations live in application/behavior_statistics.py, without I/O, pandas, Streamlit or LLM calls. The interface renders projections and selects settings. Domain, ingestion, curated files and the general point-only dashboard were not modified by this implementation.
- Consequences: all three analyses honor research filters; local settings refine only FLEX. Conditional fitted lines are confined to this explicitly requested evidence view. Source-record actions retain the applied query. No ranking, habitat-safety threshold or direct partial-gravity validation is introduced.

### ADR-0086 - The proposed seventeen-test FLEX scenario did not meet the strict pressure bound
- Date: 2026-11-14 | Type: BUG | Status: resolved
- Context: the user-supplied proposal described seventeen FLEX tests at O2 >=30% and pressure around 10.2 psi. Exact curated-cell checks at revision a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204 found zero records at pressure <=10.2 psi; seventeen instead report 10.331688?10.49601696 psi and meet a separately labelled <=10.5 psi comparison.
- Root cause: an approximate narrative pressure was interpreted as a precise scenario bound. Rounding before filtering or hardcoding seventeen would misrepresent tested coverage.
- Impact: the prototype could falsely advertise direct evidence at the strict lunar-scenario pressure. The discrepancy was reported to the user before implementation; source values were preserved.

### ADR-0087 - Count exact scenario coverage separately from near-atmospheric fitting
- Date: 2026-11-14 | Type: FIX | Status: resolved
- Related: ADR-0086.
- Change: compute O2 >=30% with pressure <=10.2 psi from the same reported scalar ambient-oxygen tests. Compute the distinct <=10.5 psi comparison with its actual pressure range, without rounding before selection. Both use global research scope and retain source references. No lower-pressure test enters a default 1-atm +/-5% fit.
- Verification: synthetic boundary tests distinguish 10.2 from 10.35 and 10.51 psi; independent current-CSV reconciliation verifies exact identities/counts. The interface displays zero strict records and seventeen nearby records for the inspected unfiltered checkpoint, not constants.
- Consequences: near-1-atm coefficients are not silently transferred to the lower-pressure sample or lunar gravity.

### ADR-0088 - Estimate oxygen effects only in identifiable fixed-blend strata
- Date: 2026-11-14 | Type: DECISION | Status: accepted
- Context: shared fuel/diluent labels still mix He or CO2 fractions, and the source review documents diameter and pressure dependence of K. Several diluent/blend strata contain only one or two oxygen levels.
- Options: pooled bivariate slopes; fixed-blend stratification with pressure/diameter-adjusted OLS; scatter only.
- Decision: retain scatter by diluent and separate fuel panels, but fit only within exact fuel/diluent/He-percent/CO2-percent strata in a bounded near-1-atm window. Regress K on an intercept, O2 and varying reported pressure/diameter. Center/scale before solving, then return the O2 coefficient in mm2/s per oxygen percentage point. Require n>=6, >=3 oxygen levels, residual df>=3, full rank and standardized condition number <=10,000. Use round-trip blend labels so close but unequal fractions cannot merge through display rounding.
- Verification: an orthogonal factorial fixture recovers a known coefficient and analytic Student-t interval; a confounding fixture separates the adjusted effect from a misleading pooled slope. Sparse/collinear groups have an explicit no-fit reason. Missing pressure is never replaced by nominal atmosphere.
- Checkpoint: 151 FLEX observations from 274 matched records, 123 explicit exclusions. Only heptane/N2 (n=32) and methanol/N2 (n=41) fit. Their adjusted coefficients are 0.01847212464 and 0.01832299867 mm2/s per O2 point, with 95% intervals [0.00619679206,0.03074745723] and [0.01570562080,0.02094037653]. These checkpoint values are not hardcoded scientific rules.

### ADR-0089 - Use explicit model-based intervals and reproducible numerical projections
- Date: 2026-11-14 | Type: TRADEOFF | Status: accepted
- Context: the user requested a citable slope and interval calculated deterministically in the application, never by an LLM (consistent with ADR-0004).
- Options: omit uncertainty; parametric OLS/Student-t intervals with stated assumptions; bootstrap intervals that introduce additional resampling/model choices.
- Decision: compute Student-t intervals using n minus the actual fitted parameter count, and conditional mean-response bands at group-mean pressure/diameter. Draw only within observed O2 bounds. Record model assumptions and raw within-stratum Spearman rho separately from adjusted slopes. Declare NumPy/SciPy dependencies explicitly and record their versions in analysis identity/export. Reports include settings, policy version, dataset revision, exact observations/exclusions, group ids, reference conditions, source columns and raw-table checksums.
- Consequences: results are deterministic for the same inputs/policy/environment. The intervals assume independent, homoskedastic, approximately normal errors; those assumptions and calibration/model-form uncertainty are not certified by the plot. Reference-condition curves do not mean each reference combination was directly tested. The view does not offer general fire predictions or transfer coefficients to other atmospheres/gravity.
- Method references: NIST least-squares handbook and SciPy regression/Student-t documentation, linked in SPEC-002 and the UI. No model or external scoring service is called.
- Review trigger: independent replication, calibration/error models, stronger nonlinearity/heteroskedasticity evidence, or a request for validated predictive/causal inference.

### ADR-0090 - Preserve measured gas signs and qualitative gravity outcomes
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- BASS-II: compute initial-minus-final O2 and final-minus-initial CO2 from the same complete ambient-oxygen test. At the inspected checkpoint, 121/129 pairs are complete and seven contain a negative difference. Keep and mark signed values, without clamping, missing-value fill or conversion into mass/emission yield. Eight rows have explicit exclusions. Current curated nulls take precedence over the historical data-quality review's old pending-fix inventory.
- SAFFIRE-II: retain nine matching sample rows in a paired outcome matrix/table. Keep numeric fields beside original raw labels, approximate zeros, Complete, Acceleratory, mixed materials, missing material/thickness and source notes. Do not infer a numeric ground burn length from Complete or a zero spread rate from zero length. Source silicone cases have two Complete ground labels, one 7.6 cm value and one approximately-zero ground length; do not generalize them into identical outcomes.
- Verification: synthetic signed/missing-pair and categorical-outcome fixtures; current CSV cell/identity checks; source actions and reproducible CSV/JSON exports. Every record retains investigation/TestPoint/source row/lineage; source checksums and column units are available.

### ADR-0091 - Correct narrow-screen overflow in the new evidence charts
- Date: 2026-11-14 | Type: BUG + FIX | Status: resolved
- Symptom: the first row-faceted Vega-Lite FLEX plot occupied a narrow fixed region on desktop and overflowed its card to 481 px in a 390 px viewport. An initial horizontal metric group also shortened displayed slope values on narrow screens.
- Root cause: faceted charts do not inherit the desired responsive width like standalone native chart elements; two stretched metric containers could shrink below the numeric value width.
- Fix: render a standalone responsive native chart per fuel, with group-detail separation intact. Show coefficients and intervals in native columns that stack at narrow widths. Place gas-quality legends below the BASS-II plot; simplify SAFFIRE-II matrix row labels to sample ids with materials in tooltips/table, horizontal condition headers and a compact vertical legend. Reuse the existing glass card treatment.
- Verification: focused UI tests pass; Chrome at 1440 px and 390 px renders all three tabs and source navigation without exceptions. The corrected FLEX card measures 356 px within the 390 px viewport. Numerical observations, model estimates and query semantics did not change for this presentation fix.

### ADR-0092 - Verify the fire-behavior implementation and document its checkpoint
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Verification: full suite 174 passed, 179 PDF visual-line checks skipped because pdftotext/poppler is absent, using fresh workspace-local pytest temporary paths. Fourteen focused application/infrastructure/UI tests passed after final numerical projection changes; two focused UI cases also passed after the responsive layout update. Ruff clean; strict mypy passed for the domain and both new application modules. Chrome verified the three tabs, plotted graphics, narrow layouts and source-record navigation. The local Streamlit server is restarted for imported module changes.
- Reproducibility: dataset a1c03c208ea71345f81991b2a9ecf3f9fb0e75589ce37220d6bb40e6f7312204; default explicit-all-fuels UI analysis 571d906a625be137609dcdf5f1c38418e714cf29f3f342cdaf3741cec1a3c74e; NumPy 2.5.2, SciPy 1.18.1. Details: docs/fire-behavior.md; acceptance traceability in the Streamlit task spec.
- Artifacts: docs/screenshots/fire-behavior-flex.png, fire-behavior-bass.png, fire-behavior-saffire.png and fire-behavior-mobile.png.
- Not verified: model error assumptions, independent scientific replication, habitat certification, direct partial-gravity behavior, physical-device and full cross-browser/screen-reader accessibility. These limitations are not reasons to invent missing values or safety conclusions.

### ADR-0093 - Delete the six truncated ACME archives
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Supersedes: the "Action" of ADR-0084
- Decision: the user authorized deleting the six truncated archives of ADR-0084, since every intact entry is already extracted and identical on disk. They were deleted; their SHA-256, size and the names of the 23 PDFs that could not be recovered remain in `docs/zip-removal-report.json` (`deleted_damaged_archives`). `knowledgeBase/` now holds no zip archive.
- Consequence: the 23 PDFs (17 absent everywhere, 6 present in the sibling ACME campaign folder) can only be restored by downloading the archives again from NASA PSI.

### ADR-0094 - Re-downloaded ACME archives: 4 PDFs recovered, 4 archives truncated at the source
- Date: 2026-11-14 | Type: FIX (partial) | Status: open for the remaining files | Related: ADR-0084, ADR-0093
- Context: the user re-downloaded 17 ACME archives (Downloads, from 18:38) and asked to add any recoverable PDF to its folder in `knowledgeBase/`. Downloads were handled as untrusted input: read in place with an isolated interpreter, integrity-tested, zip-slip guarded, PDFs only, exclusive create (no overwrite), and CRC32 plus the `%PDF-` signature verified after writing.
- Result: 13 archives are intact and every entry matches the files already on disk (ACME-BRE and E-FIELDS). From the intact `ACME_drawings_expt_mounting_structure.zip` and `ACME_drawings_igniter.zip`, 4 PDFs missing from `ACME/E-FIELDS` were added: `s1101mfa1000_A`, `s1101mfa1300_C`, `s1101mfa1313_F`, `s1101mfa1315_F`. Their SHA-256 values are in `docs/zip-removal-report.json` (`recovered_from_redownload_2026_11_14`).
- BUG (source, not fixable locally): `ACME_drawings_avionics_package`, `_burners`, `_common_electrical` and `_shipping_containers` downloaded byte-identical (same SHA-256) to the truncated copies deleted under ADR-0093. The defect is therefore in the files as published, not in a transfer. 19 PDFs remain absent (17 absent everywhere, 2 `common_electrical` PDFs present in `ACME/E-FIELDS`). Payback trigger: an alternative source (NASA PSI support or another mirror).
- No curated data, evidence or test depends on these drawings; the Downloads folder was left untouched.

### ADR-0095 - Restart Streamlit after the user requested a fresh compilation
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Action: stopped the previously owned Streamlit process and started the current src/psi_fire/interface/app.py on http://127.0.0.1:8501. No source or scientific data was regenerated.
- Verification: python -m compileall -q src/psi_fire completed successfully; the new server health endpoint returned HTTP 200 with body ok. Full tests and browser interaction were not repeated for this operational restart.

### ADR-0096 - Project published as the public GitHub repository FLAMSA
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0082
- Decision: at the user's request, the project was published as a public repository at https://github.com/Huarada/FLAMSA (branch `main`). The initial commit holds 1,325 files, including `knowledgeBase/` (864 MB, no zip archives, no file above 95 MB).
- Pre-publication checks: `.gitignore` (ADR-0082) excludes secrets, browser-test profiles and caches. The staged set contained no env, secret, cache or local-settings file, and no tracked text file contains the user's e-mail or home path. Commit authorship uses the user's own git identity.

### ADR-0097 - README rewritten as the competition entry point
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted | Supersedes: the README content of ADR-0081
- Change: `README.md` now presents the problem, the five workspace destinations with current screenshots, the 15-investigation data table (1,615 records), the curation rules, and the physics business rules R1-R8 as GitHub `math` blocks (d-squared law, Spalding transfer number, the FLEX OLS model with its fitting rules and checkpoint slopes, Zst, closed-chamber O2 balance, PMMA stoichiometry, spread rate, ideal-gas density). It also covers the lunar-scenario coverage counts, a Mermaid architecture diagram, quick start and stated limits.
- New figure: the BASS-II PMMA CO2-produced/O2-consumed slope through the origin is 0.822 (24 burns with an O2 drop above 0.2 points), against the stoichiometric 5/6 = 0.833. Computed from the curated data; not added as a test.
- Honesty constraints: the stale `research-overview.png` (removed line chart) is not used. The copilot, ranking and export bundle are described as not yet implemented. The lunar count is the exact one (0 tests at or below 10.2 psi, 17 at or below 10.5 psi), not a rounded one.
- Not verified: GitHub rendering of the math and Mermaid blocks. Only the balance of the LaTeX delimiters was checked mechanically (51 expressions).

### ADR-0098 - README prose rewritten in a plainer voice; quotes cite their documents
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted | Related: ADR-0095
- Change: the user asked for README text that reads less like generated copy, and for each PDF quote to name its document. Removed emoji, slogan lines, repeated bold labels ("What the data shows", "Rule applied") and most emphasis. Section titles are now "The dashboard", "Physical consistency rules" and "Known limits".
- Every quote now gives authors, title and page, with a numbered References section listing the venue or report series and the archived path. Titles and authors were taken from the cover pages of the archived PDFs. Reference 2 (Turns, *An Introduction to Combustion*, 2nd ed., p. 376) is cited by reference 1 and is not archived. The 2012 meeting name is reproduced as printed on that document's cover.
- Formulas, tables and numbers are unchanged (14 math blocks, LaTeX delimiters re-checked). GitHub rendering is still not verified.

### ADR-0099 - Make the principal analysis destinations prominent and explain their purpose
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Context: the user requested more prominent Dashboard and Fire behavior controls, hover explanations and a differentiated header action. The previous segmented control did not provide separate purpose help for each destination.
- Change: replace it with native Streamlit buttons for all five existing destinations. Dashboard uses a strong blue treatment; Fire behavior uses an amber call to action related to the FLAMSA mark. Each button has individual native help, visible focus, a 44 px minimum height and the current destination is labelled. No duplicate navigation state or external component was added.
- Consequences: the existing workspace_navigation session value and Home/source callbacks remain valid. Header callbacks change only destination; research queries and source selection semantics are preserved. Interface tests now exercise actual header actions rather than the retired segmented control.
- Contract: SPEC-001 section 22, AC-81, AC-82 and AC-85.

### ADR-0100 - Explain fire-behavior physics to students before the research filters
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Context: the user wanted the evidence section's scientific importance and formulas explained clearly at the start, especially for a competition audience.
- Change: add an always-visible opening guide after the Fire behavior title and before filters. Explain the approximate droplet d-squared relationship, K and its units; same-test oxygen/CO2 differences and percentage points; and the paired ground/microgravity length comparison. Define the comparison arrow as a comparison, not a physical law. A progressive disclosure introduces the conditional K regression, coefficients/error term and uncertainty/source trail.
- Scientific framing: explain why microgravity's change in buoyancy is relevant to combustion research. Identify agreement as a physical-consistency check, the oxygen coefficient as a conditional association, and habitat safety as requiring independent environmental evidence. Do not present universal formula proof, numerical safety scores or an additional validation computation. Existing coefficients, data, exclusions and exports were not changed.
- Sources: NASA combustion/fire-safety overview and FLEX requirements document were checked as background, not promoted into new as-run manual claims. Their links are available in the guide. SPEC-001 AC-83/AC-84 and SPEC-002 describe the presentation contract.

### ADR-0101 - Verify the navigation and scientific introduction across session flows and viewports
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Verification: 11 interface tests passed, including purpose help, header/Home/source navigation, query preservation, educational content, source access, filter reset/reload and copilot flows. Full suite: 175 passed, 179 PDF visual-line checks skipped because pdftotext/poppler is absent. Fresh workspace-local temporary directories were used. Ruff passed; strict mypy passed for the domain and new navigation/introduction modules.
- Browser: restarted the owned local Streamlit server. Chrome verified the Dashboard and Fire behavior tooltip texts by actual hover, Enter activation of Fire behavior, four rendered equations and DOM ordering of the introduction before Research filters, with no rendered exception. At 390 px the page remained 390 px wide; header and introduction measured 356 px and learning cards 309 px. Desktop and mobile screenshots were visually inspected.
- Artifacts: docs/screenshots/navigation-fire-tooltip.png, fire-behavior-learning-desktop.png, navigation-mobile.png and fire-behavior-learning-mobile.png. Documentation and acceptance traceability were updated.
- Not verified: physical-device input, screen-reader behavior and a complete cross-browser accessibility/contrast audit. The presentation increment does not establish a new scientific validation result.

### ADR-0102 - Navigation tooltips rewritten to say what each page shows
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Context: the user found the hover text on the Dashboard and Fire behavior buttons to read like generated copy ("Connect physics with evidence", "Explore the dataset").
- Change: the five tooltips in `workspace_navigation.py` now describe concrete content and name the studies (FLEX, BASS-II, SAFFIRE-II) instead of using generic verbs. The test that checked the old wording now checks the new key phrases.
- Not verified: the tooltips were not looked at in a browser; only the AppTest and ruff were run.

### ADR-0103 - Exclude missing extinction diameters from the FLEX physical-consistency check
- Date: 2026-11-14 | Type: BUG / FIX | Status: accepted
- Symptom: the README claimed a 257-observation d-squared checkpoint, while the test silently substituted an unreported extinction diameter with zero through `value(...) or 0.0`.
- Root cause and impact: a missing measurement was treated as complete burnout, contrary to the source-data contract. This changed check eligibility and the denominator of a scientific consistency ratio. The defect was in the test, not the production Fire behavior model.
- Fix: require finite reported diameters, positive K/time, nonnegative extinction diameter and the existing d0 > 1.1 de sensitivity screen. Keep reported zero distinct from missing. Preserve the broad median-agreement assertion and require more than 100 eligible rows rather than the old imputation-dependent 200 threshold.
- Recomputed checkpoint: n=155, median reported/predicted burn time 1.049190953, linear-interpolated IQR 1.029186418-1.077274089. README updated; no raw, manual or curated data changed.

### ADR-0104 - Distinguish physical models, measured differences and documentary context in the formula presentation
- Date: 2026-11-14 | Type: DECISION / ENHANCEMENT | Status: accepted | Related: ADR-0097, ADR-0100
- Context: the user requested an audit of README formulas against Dashboard and Fire behavior and a recommendation on retaining or adding formulas.
- Decision: retain R1-R8 with explicit scope. Keep the three current introductory cards and the existing conditional regression explanation. The ground/flight arrow is a comparison. Recommend the derived burn-time and average length/time equations for optional future technical detail; do not add all README equations to the opening UI or imply a new live validation feature.
- Corrections: d-squared describes squared diameter; eligible strata alone receive OLS fits; Spalding theory requires unmapped thermophysical inputs; conditional extinction-diameter linearity is not proportionality through the origin; chamber mole-fraction observations are not universal mass-balance laws; the PMMA 5/6 reaction ratio concerns molar amounts and does not automatically equal concentration-difference ratios; gas-mass estimates require percentage-point conversion and P/V/T assumptions; SAFFIRE silicone cases differ; SPICE volume flow needs matching reference conditions.
- Independent checkpoints: ACME-CFI-G Zst 331 rows, max absolute error 4.080997963e-5; normal-flame sequence 156 continuous pairs of 168 same-day pairs; exploratory PMMA origin-constrained slope 0.8220215701 for 24 complete pairs. The latter has no reported uncertainty and is not a production chart line or an automated stoichiometric check.
- Tradeoff: keep Spalding, Zst and SPICE ideal-gas relations as technical background/QA rather than inventing new Fire behavior analyses for unmapped inputs or different investigations. No universal safety claim or direct lunar-gravity interpolation is introduced.
- Artifact: docs/formula-audit.md maps every relation to implementation, assumptions, units, checkpoints and a retain/add/defer recommendation; README links it. Numerical computations remain in their existing layers. UI and production scientific calculations were not changed.

### ADR-0105 - Preserve a source quotation while correcting its physical interpretation
- Date: 2026-11-14 | Type: BUG / FIX | Status: accepted | Related: ADR-0104
- Finding: visual inspection of reference [1], page 2 (resolved through the FLEX source registry), confirms that its prose says droplet diameter decreases linearly, whereas the displayed equation and normalized axes use squared diameter. The literal README quotation is accurate but would be misleading without context.
- Fix: preserve the source wording and add an explicit note that the d-squared equation governs the interpretation. No source file or evidence claim was rewritten. Updated the formula audit to distinguish this visually checked page from quotations not rechecked in this session.

### ADR-0106 - Verify the formula audit and corrected consistency check
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted | Related: ADR-0103, ADR-0104, ADR-0105
- Verification: full pytest suite completed with 175 passed and 179 skipped in 196.36 seconds. The skipped tests require pdftotext/Poppler for PDF visual-line checks. Ruff passed, mypy passed for six domain files and git diff --check passed for the changed tracked files. A fresh workspace-local pytest temporary directory avoided existing cache ACL issues.
- Documentation checks: README and formula-audit local Markdown links resolve; 14 display-math blocks and 33 pairs of inline-math delimiters were checked mechanically. The current numerical checkpoints were independently recomputed from repository aggregates, including complete-input FLEX ratios, CFI-G Zst/sequence and the exploratory PMMA slope.
- Not verified: every archived quotation, GitHub/browser math rendering, scientific error assumptions, calibration, experimental replication or habitat certification. Reference [1] page 2 was visually checked as documented in ADR-0105. No UI restart or production computation/data change was needed for this documentation/test increment.

### ADR-0107 - Dashboard centered on O2 x pressure coverage; filtered-records CSV replaces the settings export
- Date: 2026-11-14 | Type: DECISION + BUG/FIX | Status: accepted | Supersedes: the Dashboard card set of ADR-0063 (FLAMSA glass) and the README lunar section of ADR-0095
- Decision (user-approved): the Dashboard keeps the Investigations and Reported records KPIs, now with captions and help text that define an investigation and a record, and splits records into individual tests and daily/matrix summaries. Two KPIs replace "Record levels" and "Selected investigation": tests reporting both O2 and pressure, and lunar-scenario tests. A full-width O2 x pressure coverage map sits directly below the KPIs, with the scenario box (O2 >= 30%, pressure <= 10.2 psi). The comparison scatter follows it at full width. The record-level donut, the records-per-investigation bars and the Dashboard's Open investigation card were removed; that card remains on Investigations and Evidence, where it selects the investigation. The research copilot is unchanged (being implemented separately).
- Decision: "Export view" (a JSON of filters) is replaced by "Download filtered records (CSV)": every record passing the filters, with all curated columns, `_raw` values and provenance, named with the dataset revision. This covers the challenge's data-extraction goal from inside the dashboard.
- Application: `chart_data.condition_map` projects individual tests with scalar O2 and pressure and counts scenario tests by oxygen basis. The scenario constants moved from `fire_behavior.py` to `chart_data.py` (single source, no import cycle); `fire_behavior.py` imports them.
- BUG (mine, documentation): the README lunar section counted only FLEX (0 tests at <= 10.2 psi), implying no evidence for the scenario. ACME-CFI-G has 48 tests in range: 20 normal flames with chamber-atmosphere O2 (14 butane, 6 ethane, 7.35 psi, 33-39% O2) and 28 inverse flames whose O2 is the burner stream, not the atmosphere. An intermediate verbal report to the user gave 48 without that split. Fix: the README section now shows 20 + 28 with a per-investigation table; the Fire behavior FLEX text is labeled as FLEX-only and points to the Dashboard map.
- Tests: new `test_condition_map_counts_the_habitat_scenario_by_oxygen_basis`; new `tests/interface/test_dashboard_overview.py` (KPI labels and help, 20 + 28 scenario counts, removed cards, CSV keeps FLEX test 114 raw "0" and provenance); one explorer AppTest assertion moved from the removed KPI caption to the new one. Full suite: 357 passed; ruff clean; mypy strict on domain clean.
- Not verified: the layout in a browser (only AppTest); obsolete CSS selectors for the removed cards remain in `workspace_style.py`, harmless.

### ADR-0108 - Coverage map polish after the first browser check
- Date: 2026-11-14 | Type: FIX | Status: resolved | Related: ADR-0107
- BUG (mine): in a headless-Chrome capture of the running app, the O2 axis started at 0 (the scenario box and label layers ignored the dots' domain), FLEX dots used a pale palette color that was hard to see, and the scatter notice still mentioned the removed record-count charts.
- Fix: all three layers share one O2 scale (10% to the data maximum), the map uses its own four-color range, and the notice now points to the filtered records and the CSV download. Verified with a second browser capture: no exceptions, KPIs 15/15, 1,615, 693 and 20. Interface tests pass.

### ADR-0109 - Engineering drawings stay in knowledgeBase but never enter the RAG corpus
- Date: 2026-11-14 | Type: DECISION + TRADEOFF | Status: accepted | Related: ADR-0008, ADR-0083
- Context: the planned RAG indexes PSI documents. A 40-file sample of the 504 ACME engineering-drawing PDFs (164 MB) showed 22 with almost no text layer and the rest holding parts lists and manufacturing notes whose columns pdftotext interleaves. They share query vocabulary (burner, igniter, chamber) with the ~70 scientific reports and would crowd them out of the top results; OCR would add dimension fragments, not sentences. The 317 FLEX telemetry .txt files have the same problem.
- Options: (a) delete the drawings from knowledgeBase; (b) keep them and exclude them from the corpus.
- Decision: (b). The RAG corpus is an explicit allowlist of documents (default deny), so drawings and telemetry are excluded by construction, with the reason recorded next to the list.
- Trade-off: deleting would remove 164 MB from the working tree but would not shrink the public repository, because the files are already in the pushed history (commit 16429f5); shrinking it would need a history rewrite and force-push. Deletion would also break the read-only rule of ADR-0008 for files that are valid primary evidence for hardware (the challenge asks for hardware and sensors) and that the Evidence tab can serve. No code, curated data or manual claim references them today, so keeping them costs nothing at runtime.
- Revisit if: repository size becomes a problem for cloning (then move knowledgeBase to Git LFS or an external download rather than deleting selectively).

### ADR-0110 - Spec-driven development for the AI orchestration: contracts before code
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0001, ADR-0004, ADR-0007
- Context: the team agreed an orchestration design (diagram "FLAMSA AI orchestration": retrieve -> combustion agent with PDF RAG -> solutions dictionary -> scientific validation -> approved? -> retry up to 2 attempts -> output or insufficient_evidence). No ranking, Narrator or RAG code exists yet; the Research copilot panel is still separate (ADR-0107).
- Options: (a) implement the LangGraph graph directly from the diagram; (b) write the contracts first (spec, ports, contract tests with fakes), then implement.
- Decision: (b). docs/specs/ai-orchestration-contracts.md (SPEC-003) is the normative English version of the diagram: node responsibilities, ports (Retriever, Narrator, PassageSearch, SolutionCatalog, AnswerValidator), the AnswerScenarioQuestion use case with MAX_ATTEMPTS = 2, both outputs and acceptance tests AO-01..AO-09. Order of work: domain ranking -> ports -> contract tests with fake Narrator -> infrastructure adapters.
- Consequences: validation and retry behavior can be tested without an LLM or network; the LLM provider stays swappable. Cost: a spec to maintain alongside the code.
- Review trigger: SPEC-003 and the implementation disagree; the spec is amended first.

### ADR-0111 - LangChain + LangGraph preferred for the LLM and orchestration layer, adoption deferred
- Date: 2026-11-14 | Type: DECISION | Status: deferred | Related: ADR-0001, ADR-0110
- Context: the user prefers LangChain (LLM/RAG adapters) and LangGraph (graph and retry loop) for the LLM and server side, and agreed they are not needed yet.
- Decision: they are the default choice when SPEC-003 is implemented, confined to infrastructure behind the ports. No dependency is added now. Whether a server/API layer exists at all is an open question in SPEC-003.
- Consequences: no framework lock-in until the contracts are tested; the import-boundary test (AO-09) keeps them out of domain and application.
- Review trigger: implementation of the first LLM-backed node.

### ADR-0112 - Diagram adjustments required by the project rules
- Date: 2026-11-14 | Type: TRADEOFF | Status: accepted | Related: ADR-0004, ADR-0110
- Context: four points of the diagram conflict with CLAUDE.md or the data rules.
- Decisions recorded in SPEC-003: (1) the 5-6 investigation shortlist is ordered by the deterministic domain ranker with its ScoreBreakdown; keyword/embedding search may only add candidates. (2) The failure node returns insufficient_evidence together with the deterministic breakdown and limitations, never an empty answer. (3) The "mock derived technologies" dictionary is illustrative: entries carry status "illustrative", are labeled in the UI and never count as evidence. (4) new_solutions_agent and double_check_agent are deterministic code (lookup and rule checks), not LLM calls; only the answer node uses an LLM. The diagram's Portuguese labels are not committed; the English spec replaces them.
- Consequences: fewer LLM calls and testable validation; the dictionary cannot be presented as a NASA result until it has archived sources.
- Review trigger: an archived source for the solutions dictionary, or a proposal for an LLM judge (needs its own ADR).

### ADR-0113 - Debt: solutions dictionary has no provenance yet
- Date: 2026-11-14 | Type: DEBT | Status: open | Related: ADR-0112
- Shortcut: the investigation -> derived technology dictionary in the diagram is mock data.
- Payback trigger: before it is shown in a demo as anything other than "illustrative", or before it is used in the validator's coverage check. Requires per-entry source file, locator and capture metadata (ADR-0022 rules).

### ADR-0114 - SPEC-003 implemented: one set of steps, two engines, template narrator by default
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0004, ADR-0110, ADR-0111, ADR-0112
- Context: the user asked for the full implementation of SPEC-003 with LangChain/LangGraph.
- Decision: domain/ranking.py (HabitatScenario, five criteria, RelevanceRanker, ScoreBreakdown, domain-written limitations) and domain/answering.py (Citation, Figure, Claim, Draft, plausibility rules). application/answering.py holds every node and routing decision once (`AnsweringSteps`, `MAX_ATTEMPTS = 2`, strict then relaxed `RetrievalSettings`); `AnswerScenarioQuestion` is the plain reference loop and infrastructure/answer_graph.py wires the same steps into a LangGraph StateGraph. The Research copilot panel now calls the pipeline through a composition root (`answering_factory`). LangChain appears only in infrastructure (`LangChainNarrator`, `init_chat_model` from `PSI_LLM_MODEL`); an import-boundary test (AO-09) keeps langchain/langgraph/sklearn/pypdf out of domain and application.
- Decision: with no model configured the `TemplateNarrator` writes claims whose figures are copied from the breakdown and the cited test point, so the dashboard works offline and the text is always checkable. A model, when configured, must pass the same validator.
- Consequences: the retry/failure semantics cannot drift between engines (every contract test runs on both). Cost: `AnswerState` is a TypedDict shared across layers, and the plain loop is kept only as a reference.
- Not decided here: server/API layer (still open in SPEC-003).

### ADR-0115 - RAG corpus allowlist and lexical page retrieval
- Date: 2026-11-14 | Type: DECISION + TRADEOFF | Status: accepted | Related: ADR-0008, ADR-0109
- Context: the knowledge base is ~730 PDFs, mostly engineering drawings; embedding keys are not available offline.
- Decision: `data/rag_corpus.json` lists 20 scientific documents (final/summary reports, SRDs, papers) mapped to investigation ids, default deny. It holds raw `knowledgeBase/` paths outside `data/sources.json`, the same exception manual evidence already uses; the loader rejects any path outside `knowledgeBase/`. The index is generated by `scripts/build_rag_index.py` into `data/rag_index/passages.json` (2,390 chunks of at most 1,200 characters, locator "p. N", fingerprinted on the manifest and file sizes, rebuilt when stale). Retrieval is TF-IDF (unigrams and bigrams) restricted to the shortlisted investigations, ties broken by index order.
- Trade-off: lexical retrieval is deterministic, offline and gives exact page locators, but misses paraphrases and can return running headers (a FLEX hit for an oxygen query was a conference header page). Embeddings or graph retrieval can replace `PdfPassageSearch` behind `PassageSearch` without touching other layers.
- Not covered: scanned PDFs yield almost no text (CFI 28 chunks, SAFFIRE-I and SAFFIRE-III 3 each); no OCR was run, so those studies are thinly represented in passages.
- Review trigger: a quality evaluation of retrieval on real questions, or an embedding provider becoming available.

### ADR-0116 - BUG/FIX: pypdf lone surrogates truncated the index cache
- Date: 2026-11-14 | Type: BUG / FIX | Status: resolved | Related: ADR-0115
- Symptom: the first index build ended with `UnicodeEncodeError: surrogates not allowed` and left a 0-byte `passages.json`.
- Root cause: pypdf can return lone UTF-16 surrogates from broken font maps; `write_text(..., "utf-8")` failed after the file had been opened for writing. Impact: a later run would have read an empty cache.
- Fix: `_clean` drops unencodable characters before chunking, and the cache is written to a temporary file and then replaced. Test: `test_clean_removes_lone_surrogates`.

### ADR-0117 - BUG/FIX: a retry did not hand the rejection reasons to the narrator
- Date: 2026-11-14 | Type: BUG / FIX | Status: resolved | Related: ADR-0114
- Symptom: contract test AO-05 failed: on attempt 2 `NarrationRequest.previous_issues` was empty.
- Root cause: `AnsweringSteps.retrieve` reset `issues`, so the reasons from attempt 1 were erased before the narrator ran. Without them a model cannot repair its draft.
- Fix: `retrieve` keeps `issues`; `validate` overwrites them each attempt. AO-05 now asserts the hand-off on both engines.

### ADR-0118 - Known limits of the answering pipeline
- Date: 2026-11-14 | Type: DEBT | Status: open | Related: ADR-0114, ADR-0115
- Numeric checking parses digit tokens in claim text after removing ids and `[citations]`; spelled-out numbers ("thirty percent") and unit correctness are not checked, and the figure unit is not compared with the record. Pay back before trusting free-text LLM output beyond a demo.
- Passage quotes are checked as substrings of the retrieved chunk (whitespace collapsed), not as the one-printed-line rule of manual evidence; chunks join several lines. Tighten if quotes will be shown as verified evidence.
- The `LangChainNarrator` path is tested with fake runnables only; it was not run against a real provider (no key in this environment). The structured-output schema (flat Citation/Figure models) is untested with OpenAI or Gemini.
- Flow-regime criterion not implemented; weights (0.30/0.20/0.15/0.15/0.20) and scale constants are initial values with no calibration.
- `data/solutions_catalog.json` is empty (ADR-0113): the solutions feature exists but suggests nothing.
- The shortlist is ranked over all curated investigations, not the dashboard's filtered view (stated in the UI).
- Payback trigger: first demo with a real model, or any claim shown to users as "verified".

### ADR-0119 - Local .env for the model key; unusable model settings fall back to the template
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0114
- Decision: `.env` (already blocked by .gitignore) holds `OPENAI_API_KEY` and `PSI_LLM_MODEL`; `.env.example` is the committed template. The Streamlit composition root loads it with python-dotenv, and real environment variables take precedence. Default model `openai:gpt-4.1-mini` (structured-output capable, low cost); changing it is a one-line edit.
- Decision: if the setting is present but unusable (empty key, missing provider package, bad name), `build_answering_pipeline` uses the template narrator and the UI label says "Template (model unavailable: ...; check .env)" instead of crashing.
- Consequences: the pipeline is cached per process, so `.env` changes need an app restart. The default model name was chosen from general knowledge and was not checked against the current provider catalog.

### ADR-0120 - BUG: real-model drafts rejected; retrieval worked but the validator feedback was unusable
- Date: 2026-11-14 | Type: BUG | Status: fixed (ADR-0121) | Related: ADR-0114, ADR-0115
- Symptom: first run with a real OpenAI model showed "Insufficient evidence" for the default question, with issues `unknown_citation: ACME-CFI-G reports no objective`, `quote_mismatch`, and five `A record figure must name a test point that the claim cites`. It looked like "RAG retrieved nothing".
- Root cause: retrieval did return passages. The model (a) cited metadata field `objective` for an investigation without one, (b) quoted passages with paraphrase/ligature/hyphen/case differences, (c) declared record figures without a matching record citation in the same claim. Validator messages did not say what to fix, so the retry repeated the errors. The generic question also had no content words for TF-IDF.
- Impact: no model answer could pass; the user could not see what the model produced or what was retrieved.

### ADR-0121 - FIX for ADR-0120: actionable validation, tolerant quote matching, scenario-enriched retrieval, debug trace
- Date: 2026-11-14 | Type: FIX | Status: accepted | Related: ADR-0120
- Quotes are compared after NFKC normalisation, casefold, soft-hyphen/replacement-char removal and whitespace collapse (words and numbers still must match). Messages now name the failing quote, the figure column and the missing record citation.
- The payload lists `metadata_fields_available` per investigation and the prompt demands a contiguous 20-200 character quote, and a record citation for every record figure.
- Passage search query = question + scenario O2/pressure + fixed fire-safety terms (`retrieval_query`).
- `AttemptRecord` keeps the draft and passages; the UI "Run trace and retrieved passages" expander shows them, labelled as rejected and not an answer.
- TRADEOFF: case/ligature-insensitive matching is slightly more permissive than the one-line rule of manual evidence (see ADR-0118).
- Test fix: the copilot UI test clears the Streamlit resource cache and blanks `PSI_LLM_MODEL` so a developer's `.env` cannot turn it into a paid API call.
- Not verified: behaviour against the real OpenAI model after these changes (needs the user's key).

### ADR-0122 - ENHANCEMENT: citations show the quoted excerpt, the source document name and a DOI link
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: done | Related: ADR-0121
- Each validated citation now renders the passage quote as a blockquote and a caption `<investigation> - <document file name>, <locator>`, linked to `https://doi.org/<doi>` when the investigation's `study_metadata` has a DOI (9 of the curated investigations do).
- DEBT: the link points to the investigation's NASA PSI record, not to the exact PDF page (archived PDFs are local read-only files with no public URL), and the "book name" is the PDF file name; `data/rag_corpus.json` has no titles. Payback: add `title` and `url` per document to the corpus manifest and pass them through `Passage`. ACME-CFI-G and other investigations without a DOI show no link.

### ADR-0123 - ENHANCEMENT: click the coverage chart to set the copilot scenario; copilot on by default
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: done | Related: ADR-0114
- The "Research copilot" toggle defaults to on. Clicking the oxygen/pressure coverage chart sets the copilot's Custom scenario to the nearest grid point (O2 step 0.5 %, pressure step 1 psi), and a dark-cyan marker shows the scenario; editing the inputs by hand moves the marker. Mechanism: an invisible point grid layer with a nearest click selection (`st.altair_chart(on_select="rerun")`); the chart key changes after each pick so the same cell can be clicked again.
- Copilot inputs now use session state instead of `value=` so a chart pick raises no Streamlit warning.
- DEBT: picks snap to a 1 psi grid (not the exact click) and the grid layer sits under the data dots, so a click exactly on a dot may not register. Payback: custom component or finer grid if users need exact coordinates.
- Not verified: the real browser click (only the state path is tested by AppTest; AppTest cannot click a chart).

### ADR-0124 - FIX: chart pick used two reruns and remounted the chart (supersedes the key-bump of ADR-0123)
- Date: 2026-11-14 | Type: FIX | Status: accepted | Related: ADR-0123
- Symptom: after each click the chart refreshed visibly and lost its zoom/pan. Cause: Streamlit delivers chart events only by rerunning the script (platform limit), but ADR-0123 added a second `st.rerun()` and a new chart key per pick, which remounted the chart.
- Fix: `on_select` takes a callback that writes the copilot state; one rerun, stable chart key.
- TRADEOFF: with a stable key the selection persists, so re-clicking the same grid cell after editing the inputs by hand fires no event; click a neighbouring cell. Not verified in a real browser (zoom retention is expected, not confirmed).

### ADR-0125 - ENHANCEMENT: explanatory text, coverage indicators and help tooltips for the chart + copilot step
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: done | Related: ADR-0123
- The coverage chart caption now says what it shows and how to read empty areas; with the copilot on, a "how to use" note explains click -> marker -> Ask copilot. Three indicators sit under the chart: tests near the marker, investigations near, and Coverage (Tested nearby / Extrapolated, inside/outside the lunar box). "Near" = +-5% O2 and +-2 psi (named constants `NEAR_O2_PERCENT`, `NEAR_PRESSURE_PSI`; initial values, not calibrated). Help tooltips added to the toggle, scenario inputs, question box and Ask button, plus a 3-step hint.
- DEBT: the "near" window is a presentation heuristic, not a scientific validity limit; the domain ranking is unchanged. Payback: calibrate with domain experts.

### ADR-0126 - BUG: the oxygen/pressure map empty state hides distinct data-coverage causes
- Date: 2026-11-14 | Type: BUG | Status: open
- Finding: The user reported repeated No test that passes the filters reports both oxygen and pressure messages. The message is local to coverage_map, not a failed research query. At revision a1c03c208ea7, solid-fuel filtering correctly retains 389 rows across seven studies but no scalar O2/pressure pair. FLEX-2 retains eight matrix summaries and zero individual tests. ConditionMap lacks an exclusion-reason breakdown, so the same empty message obscures missing conditions versus summary-only scope. Proposed fix: counts and map-specific reasons, retaining all query records and the existing no-imputation policy.

### ADR-0127 - BUG: inactive numeric filter inputs accept values that Apply filters ignores
- Date: 2026-11-14 | Type: BUG | Status: open
- Finding: Reproduced in AppTest: enter Oxygen minimum 90 with Filter oxygen unchecked, then Apply. oxygen remains None, with 1615 records and 693 map dots; no error is displayed. Pressure and flow use the same pattern. This follows current activation semantics but is a usability defect: active-looking editable bounds can be silently ignored. Proposed fix: explicit activation/disabled-state guidance or a submission warning; do not change missing-value or basis semantics implicitly.

### ADR-0128 - BUG: chart scope can be emptied by a valid research-filter change
- Date: 2026-11-14 | Type: BUG | Status: open
- Finding: Reproduced: select only FLEX in Investigations in comparison charts, then apply Research filters Investigation=BASS-II. The query retains 129 rows but the local chart selection becomes empty when Streamlit drops invalid options. No reconciliation distinguishes this from intentional empty selection. Proposed fix: preserve valid choices and announce/offer recovery after automatic invalidation. Independently the O2/pressure map is empty because BASS-II lacks pressure; these are separate causes. Reset research filters restored the full chart scope in the tested sequence.

### ADR-0129 - BUG: README oxygen/pressure coverage list omits CFI
- Date: 2026-11-14 | Type: BUG | Status: open
- Finding: The lunar-habitat section says only FLEX and ACME-CFI-G report both conditions per test. CFI has 87 scalar pairs, traced to the source Pressure column in atm. At the audited revision, 693 map dots comprise ACME-CFI-G 333, CFI 87 and FLEX 273. Pair availability is distinct from the strict lunar-scenario match. Proposed fix: include CFI in the coverage statement. This finding supplements the earlier formula audit.

### ADR-0130 - Verify Dashboard research filters and document the distinction between records and chart eligibility
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Finding: Audit artifact: docs/dashboard-filter-audit.md includes all 15 study counts, reproducible cases, four issues and proposed fixes. Focused explorer/chart/application/interface suite: 29 passed in 22.52 s. AppTest probes reproduced baseline, inactive numeric bound, solid scope, matrix-only scope, stale chart selection and reset with no exception. Dataset total 1615 records = 1556 tests + 59 summaries; 693 scalar map pairs. Default scenario counts are 20 chamber-atmosphere and 28 burner-stream tests, kept distinct. No production code, curated/raw data or live-model call was changed. The exact user browser selection and physical browser rendering were not verified. Findings are open, not claimed fixed. Use the existing append-only docs/ADR.md; no separate ADR4 file exists in the project.

### ADR-0131 - Review primary navigation against the challenge and the implemented copilot
- Date: 2026-11-14 | Type: ENHANCEMENT / TRADEOFF | Status: proposed, not implemented
- Context: the user asked whether Investigations and Evidence remain essential given the expanded project and a preference for a simpler interface. Re-read the complete supplied challenge and reviewed current specs, architecture, composition root, study/source views and the implemented ranking/RAG/copilot contracts.
- Finding: the challenge requires summarizing, ranking and interpreting investigations; it does not require those two named pages. Investigations provides valuable study context, hardware/sensors, review state, raw rows and column definitions across all 15 studies. Fire behavior analyzes only FLEX, BASS-II and SAFFIRE-II. Evidence currently calls the same detail component and mainly changes its default tab to source downloads, so it has low independent navigation value.
- Recommendation: remove Evidence from primary navigation once contextual source access is complete; retain Sources within study detail and beside chart/copilot claims. Keep Studies discoverable as a secondary catalog/inspector rather than deleting the capability. Suggested primary destinations: Home, Dashboard, Fire behavior. A smaller first step keeps Investigations and removes only the duplicate Evidence header entry.
- Preconditions: preserve source-record callbacks, original values/units/provenance, review status, downloads, query/return behavior and access to all 15 studies. Copilot DOI links currently target investigation records rather than exact PDF pages. Its corpus-wide ranking can cite a study outside Dashboard filters, so contextual inspection needs an explicit labelled path rather than silently changing the query.
- Tradeoff: lower primary-menu complexity at the cost of a secondary inspection step; no measured usability improvement is claimed. Progressive disclosure guidance: https://www.nngroup.com/articles/progressive-disclosure/. Full analysis: docs/navigation-scope-review.md.
- Scope: recommendation only. No navigation, production code, source archive or scientific data was changed. Specs and interface tests must be updated if the user chooses implementation; no new runtime test was needed for this documentary review.

### ADR-0126 - BUG/FIX: coverage chart lost its Y axis title after the pick layers were added
- Date: 2026-11-14 | Type: BUG | Status: fixed | Related: ADR-0123
- Symptom: the pressure axis no longer read "Pressure (psi)". Root cause: the invisible grid and marker layers encoded `psi`/`o2` without titles, and the shared axis took the first layer's untitled field. Impact: users could not tell what the vertical axis meant.
- FIX: both layers set `title="Pressure (psi)"` and `title="Oxygen (%)"`. Not verified visually in a browser; the compiled spec shows the titles on all layers.

### ADR-0132 - Consolidate Evidence into Investigations source inspection
- Date: 2026-11-14 | Type: DECISION / ENHANCEMENT | Status: accepted
- Change: Supersedes: the standalone Evidence navigation in ADR-0099; implements the smaller approved step of ADR-0131. The user authorized removing Evidence while retaining evidence in copilot answers. Remove its header button and dedicated render branch; retain Home, Dashboard, Fire behavior and Investigations. Existing Evidence session values migrate to Investigations and initially open Citations & source downloads without replacing query or investigation selection. Preserve registered sources/downloads, domain evidence, RAG and all Fire behavior source-record actions. Updated README, Dashboard guide, SPEC-001 AC-82/86/87 and acceptance traceability. The orchestration handoff is docs/copilot-evidence-handoff.md; no copilot/orchestration code was edited in this increment.

### ADR-0133 - Concurrent appenders reused ADR-0126
- Date: 2026-11-14 | Type: BUG | Status: open
- Change: The append-only log contains two ADR-0126 headings: the Dashboard coverage-map empty-state finding and the later coverage-chart Y-axis fix. Concurrent writers read different latest states and reused an identifier. Historical entries were preserved; distinguish these references by title until an append-only disambiguation or shared allocation policy is agreed. New entries in this session use the maximum identifier observed at write time; do not rewrite another contributor's entries.

### ADR-0127 - ENHANCEMENT: the copilot answer is linked to the coverage chart
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: done | Related: ADR-0123, ADR-0125
- Problem reported: the chart (individual tests by O2/pressure) and the copilot (ranking of whole investigations on five criteria) looked unrelated, e.g. BASS-II ranked with no dots nearby.
- Change: after an answer, dots of the ranked investigations stay highlighted and others fade; tooltips show "Rank in last answer"; investigations ranked without any plotted dot are listed with the reason; the how-to note states that the ranking weighs five criteria, not only distance.
- Not verified visually. The ranking itself is unchanged; per-criterion weights remain uncalibrated (ADR-0118).

### ADR-0134 - Verify Evidence navigation removal and preserved source access
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted | Related: ADR-0132
- Verification: full suite 224 passed, 179 skipped in 71.44 seconds. Skipped tests require pdftotext/Poppler for PDF visual-line checks. Ruff passed and mypy passed for eight domain files. AppTest asserts that no Evidence header button is rendered, query state survives navigation, Investigations still offers the source tab and prepares a registered download, and an old Evidence session redirects without losing filters. Existing Fire behavior and copilot flows pass.
- Limits: no new physical-browser screenshot/accessibility review, no independent PDF-quotation review, and no real-model call. PSI_LLM_MODEL was blank for the test process. Contextual exact-document copilot actions remain the separate orchestration handoff, not an implementation claim of this change.

### ADR-0128 - Copilot answers keep claim-level evidence, with "View source" and out-of-filter inspection
- Date: 2026-11-14 | Type: DECISION | Status: accepted | Related: ADR-0114, ADR-0122, docs/copilot-evidence-handoff.md
- Context: Evidence left the main navigation; scientific traceability must live in the answers. Ranking covers the whole corpus, so a cited study can be outside the dashboard filters.
- Decision: `TraceEntry` gains `status`; new `FigureTrace` (TestPoint, column, unit, raw text, source row, provenance) on `AnswerResult`; new application use case `ResolveCitationSource` over the existing `SourceReader` port; `RegisteredSources` now also registers the RAG corpus PDFs of each investigation and pins them by SHA-256 (an already-registered PDF without a digest is pinned too). The interface adds `copilot_evidence.py`: citation excerpt/locator/status lines, figure lines and a "View source" dialog. The dialog is a modal inspection context, so filters, scenario and answer are untouched and closing it is the return path. `assistant_panel` receives the `InvestigationSources` built once in `app.py`. No Evidence menu entry was recreated.
- Safety: the model supplies only a path string; it is opened only if it equals a registered file of that investigation (tested with None, unregistered, `../` and absolute paths). Unreadable or changed files are reported as unavailable, not hidden.
- TRADEOFF: passage status says "not human-reviewed" instead of inheriting a verified label; the DOI link stays investigation-level (ADR-0122 debt remains).
- DEBT: no exact-page link or in-app PDF rendering; the PDF is downloaded and opened at the printed locator. Hashing report PDFs happens per app run (cached per instance); revisit if the corpus grows large. Scanned PDFs without text (CFI, SAFFIRE-I/III, ADR-0118) still produce few citable passages.
- Not verified: the dialog in a real browser (AppTest only checks that the click raises no error and leaves the answer and filters in place); a real model answer through the new UI.

### ADR-0129 - BUG (cause not reproduced) and defensive FIX: page lost after Apply filters / Ask copilot
- Date: 2026-11-14 | Type: BUG | Status: mitigated | Related: ADR-0123
- Symptom reported: clicking Apply filters or Ask copilot returned to Home and lost progress. AppTest (nav to Dashboard, Apply filters, Ask copilot) keeps `workspace_navigation` = Dashboard with no exception, so the cause was not reproduced in code. The likely trigger is a new Streamlit session in the browser (reconnect or page reload), which starts with empty session state and therefore Home.
- FIX (mitigation): the current page is mirrored in the URL (`?page=`) and read back when a session starts, so a reload or reconnect returns to the same page. Filters, scenario and the last answer still live in session state and are lost if the session itself is recreated.
- DEBT: persist filters and the last answer across sessions if the root cause is confirmed to be session loss. Server output is now logged to a file in the scratchpad to catch the real cause on the next occurrence.

### ADR-0135 - Home still described implemented ranking as future work
- Date: 2026-11-14 | Type: BUG / FIX | Status: accepted
- Change: The user requested a Home content review against the challenge, ADRs, business rules and implementation. The Home workflow said ranking was Planned and No relevance scores are computed yet, contradicting domain/ranking.py, SPEC-003 and the current copilot. Replaced the stale text with archive-wide scenario ranking, application-computed scores, connected-model or offline-template explanations, criterion breakdown, citations, limits and possible insufficient-evidence output. Supersedes the planned-ranking copy policy of ADR-0065; thematic links remain navigation aids rather than computed rankings.

### ADR-0136 - Align Home purpose, source access and scientific scope with the current challenge workflow
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Change: Home now names NASA PSI rather than limiting the entire archive to ISS experiments; explains comparison, scenario relevance and sources; names prevention/detection/suppression; advertises existing filtered CSV export; and provides Open Fire behavior using the existing query-preserving callback. Earth-application claims are qualified by inference/review status, not presented as proven technology benefits. Replace traceable decisions with cited explanations and make partial-gravity/certification limits common to all themes. Keep the conceptual scene, English copy, source-bounded thematic ids and live counters. At this revision: 15 studies, 1615 records, 0/15 manual metadata files human-reviewed. No ranking weights, scientific calculations, source data, curation or visual design were changed. SPEC-001 section 24 AC-88/89 and task traceability updated; analysis: docs/home-content-audit.md.

### ADR-0137 - Verify Home content alignment and preserved navigation
- Date: 2026-11-14 | Type: ENHANCEMENT | Status: accepted
- Change: Full pytest suite: 238 passed, 179 skipped in 81.25 seconds. Skipped tests require pdftotext/Poppler for PDF visual-line checks. Ruff and domain mypy passed (eight files). The new AppTest covers implemented capability wording, live review counts, scope limitations and Home-to-Fire behavior query preservation; existing theme/source/copilot tests passed. Independently loaded the current snapshot to verify counts and all four thematic link lists. No real model call, new physical-browser/layout review or independent scientific/PDF quote revalidation was performed; PSI_LLM_MODEL was blank for tests. This copy/navigation increment does not claim improved scientific certainty or measured usability performance.

### ADR-0130 - FIX: real-model drafts rejected for figures without citation and undeclared digits; technology questions
- Date: 2026-11-14 | Type: FIX | Status: accepted | Related: ADR-0120, ADR-0121, ADR-0128
- Symptom: the question "which technology should I implement..." ended in insufficient_evidence: record figures named test point 17 without a record citation for it, and the text held digits (29, 39.5, 5) not declared as figures.
- Fix 1 (deterministic completion): before validation, `with_figure_citations` adds the record citation that a record figure's own test_point_id implies, when that test point exists in the shortlist. The number is still checked against the record range, so a wrong value is still rejected (tested). It only completes traceability.
- Fix 2: the undeclared-number message says what to do (declare it with a source, or rewrite without digits); the prompt prefers wording without digits and tells the model that every digit, including counts and ranges, must be a declared figure.
- Fix 3 (honesty): the solutions catalog is empty (ADR-0113), so for "which technology" questions the prompt now forbids naming technologies and asks the model to say the curated PSI data holds no technology recommendations, describing instead what the records show at the scenario's oxygen and pressure. Unbacked technologies stay rejected by the validator.
- DEBT: undeclared digits remain strict by design; a real model may still trip on them. Payback: run the proposed eval set (`data/eval/questions.json`) against the real model and tune from the failure counts. Not verified against the real model after this change.
