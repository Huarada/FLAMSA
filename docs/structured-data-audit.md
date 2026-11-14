# Structured source audit

Audit date: 2026-11-14. Scope: all structured files under the 15 investigation directories resolved through `data/sources.json`.

## Finding

Hardware, sensors and per-field provenance are not yet mapped into curated application data. The repository contains a source registry, but no `data/manual/<id>.json`, `data/curated/<id>/investigation.json`, or `data/curated/<id>/test_points.csv` for any registered investigation. There is no application model, loader or schema to validate these mappings yet.

This is a curation gap rather than a complete absence of source information. Nine investigations have an explicit hardware declaration in their registered ISA-Tab metadata. Instrument evidence is available in descriptions, CSV columns, supporting text and spreadsheets. These sources must be reviewed in context before assigning Sensor entities.

## Coverage

| Investigation | Hardware declaration in registered ISA-Tab | Instrument evidence examples | Remaining work |
| --- | --- | --- | --- |
| BASS | Microgravity Science Glovebox | XLSX camera settings and radiometer gain | Confirm apparatus configuration and instruments |
| BASS-II | Microgravity Science Glovebox (MSG) | CSV radiometer gain; XLSX test matrices | Identify instrument details and preserve setting provenance |
| SAFFIRE-I | Not available | CSV Camera 1 and Camera 2 | Read experiment documentation for hardware and other sensors |
| SAFFIRE-II | Not available | CSV Camera 1 and Camera 2 | Read experiment documentation; do not treat n/a camera references as observations |
| SAFFIRE-III | Saffire III enclosure in Cygnus | Approach: cameras, thermocouples, radiometers, solid state sensors, anemometers | Map each instrument and measured quantity with its own evidence |
| SAME | Comparitive Soot Diagnostic Hardware (source spelling) | Approach: smoke detectors, video cameras, thermophoretic samplers, TEM | Separate in-flight instrumentation from post-flight analysis |
| SAME-R | Not available | No instrument names in the experimental table headers | Read SAME-R documentation; do not inherit SAME instruments automatically |
| FLEX | CIR/FCF and MDCA | Supporting TXT files contain camera settings and radiometer channels | Resolve actual instrument configuration and channels |
| FLEX-2 | CIR and MDCA | Approach: color camera and high speed photography; calibration TXT files | Distinguish calibration records from experiment observations |
| CFI | MDCA and CIR | Approach: black-and-white camera, UV camera, other cameras, narrow-/wide-band radiometers | Preserve instrument purpose and source wording |
| ACME-BRE | CIR and ACME | Approach: heat flux sensor; supporting XLSX thermocouple/radiometer references | Distinguish proposed procedure from actual flight configuration |
| ACME-CFI-G | Not available | Tables report temperatures and flow rates without identifying sensor models | Read final report; distinguish normal and inverse flame configurations |
| ACME-E-FIELD | Not available | Shared ACME XLSX thermocouple/radiometer references | Confirm which shared instruments were actually used |
| SPICE | Microgravity Science Glovebox (MSG) | Approach: still and video cameras | Verify duct identity and instrument configuration |
| SLICE | Not available | Experimental table identifies dates and fuels | Read experiment documentation for apparatus and sensors |

Evidence and precise locators for these findings are stored in `structured-data-audit.json`. Each `source_ref` resolves through `data/sources.json`: find the investigation id, then append `relative_file` to its `raw_dir`. Hardware evidence includes the original ISA-Tab field and physical line range. Spreadsheet examples carry worksheet XML names and cell coordinates; workbook sheet metadata is also included. These are audit references, not a replacement for the application's future Provenance model.

## Files reviewed

- 17 CSV files: all headers, logical record counts, instrument columns, provenance columns and width inconsistencies inspected. This includes 16 registered experimental tables and the duplicate SAFFIRE-II table.
- 317 TXT files: encoding identified, text scanned for hardware/instrument evidence; hardware and approach fields parsed from ISA-Tab with multiline-aware TSV reading.
- 16 XLSX files: workbook sheet metadata and stored cell values inspected for hardware/instrument references. Formulas were not recalculated.
- 8 legacy XLS files: inventoried and hashed; their cell contents were not read because an XLS reader is not installed.
- Raw file hashes compared before and after the audit: 1,165 files unchanged.

No canonical provenance columns (`source_file`, `source_row`, `provenance_status`) were found in the raw CSV headers. This is expected for source files; generating field-level provenance belongs in the ingestion pipeline. A source path alone does not establish a value's locator, status or normalization history.

The FLEX experimental table requires `cp1252` decoding; the audit uses an explicit fallback. This must also be handled by the future ingestion reader. Missing values, ranges, summary rows and measurements have not been normalized or converted into TestPoints by this audit.

## Recommended curation sequence

1. Populate `data/manual/<id>.json` with hardware and sensor facts supported by the reviewed source, preserving original wording and a locator for each fact. Keep unknown values null with missing status. Review instrument candidates before accepting them.
2. For hardware, preserve facility and apparatus separately where the source supports both. MSG alone does not prove the specific MSG-SPICE-duct configuration. Never copy hardware or sensor assignments between investigations solely because they share a project or directory.
3. Read the remaining experiment documentation manually for SAFFIRE-I/II, SAME-R, ACME-CFI-G, ACME-E-FIELD and SLICE. Resolve legacy XLS contents when needed. Do not use automatic PDF extraction under the current project rules.
4. Implement the ingestion pipeline to preserve raw values and per-field source locators, including missing/inferred statuses. Generate the agreed curated CSV and JSON pair and validate it against the domain schema.

## Reproduction and limitations

Run `python scripts/audit_structured_sources.py` to regenerate the detailed JSON and coverage CSV. The script reads raw data and writes only audit artifacts under `docs/`. It does not curate scientific facts or modify the source registry.

Keyword results are evidence candidates and can refer to proposed, ground-based or post-flight instrumentation. Absence of a keyword match does not prove absence of an instrument. No PDFs, DOC/DOCX, PPT/PPTX or PXP contents were reviewed. Existing ZIP corruption documented in ADR-0006 remains unresolved. No application tests, ranking, schema validation or Streamlit execution were possible because application code and tests do not exist yet.
