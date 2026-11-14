# External source captures

The source registry is `data/sources.json`. One shared source is captured once per version and linked to every investigation supplied by the user. These associations are pending scientific review; they do not verify deployed hardware or sensors.

Latest batch: five HTML pages converted to Markdown, three PDFs preserved, and one blocked HTML request. Original PSI data and curated investigation files were not modified by this acquisition. SLICE has no source in this batch, which does not imply an absence of hardware. No source was supplied for ACME-CFI-G.

| Source id | Investigations | Latest content | Capture provenance |
| --- | --- | --- | --- |
| nasa-iss-science-facilities | BASS, BASS-II | [Markdown](../data/external/nasa-iss-science-facilities/20261114T145743890246Z/content.md) | [Metadata](../data/external/nasa-iss-science-facilities/20261114T145743890246Z/metadata.json) |
| nasa-combustion-science | SAFFIRE-I, SAFFIRE-III, CFI, ACME-E-FIELD, ACME-BRE | [Markdown](../data/external/nasa-combustion-science/20261114T145744296441Z/content.md) | [Metadata](../data/external/nasa-combustion-science/20261114T145744296441Z/metadata.json) |
| saffire-ii-20170000230 | SAFFIRE-II | [PDF](../data/external/saffire-ii-20170000230/20261114T145744662608Z/document.pdf) | [Metadata](../data/external/saffire-ii-20170000230/20261114T145744662608Z/metadata.json) |
| cygnus-fact-sheet | SAFFIRE-II | [PDF](../data/external/cygnus-fact-sheet/20261114T145744665885Z/document.pdf) | [Metadata](../data/external/cygnus-fact-sheet/20261114T145744665885Z/metadata.json) |
| ntrs-19960008413 | SAME, SAME-R | [PDF](../data/external/ntrs-19960008413/20261114T145744672840Z/document.pdf) | [Metadata](../data/external/ntrs-19960008413/20261114T145744672840Z/metadata.json) |
| iss-national-lab-cir | FLEX, FLEX-2 | Blocked (HTTP 403) | [Metadata](../data/external/iss-national-lab-cir/20261114T145747965377Z/metadata.json) |
| nasa-mdca-operations | FLEX, FLEX-2 | [Markdown](../data/external/nasa-mdca-operations/20261114T145920221851Z/content.md) | [Metadata](../data/external/nasa-mdca-operations/20261114T145920221851Z/metadata.json) |
| nasa-fluids-combustion-facility | CFI, ACME-E-FIELD, ACME-BRE | [Markdown](../data/external/nasa-fluids-combustion-facility/20261114T145811132211Z/content.md) | [Metadata](../data/external/nasa-fluids-combustion-facility/20261114T145811132211Z/metadata.json) |
| esa-microgravity-science-glovebox | SPICE | [Markdown](../data/external/esa-microgravity-science-glovebox/20261114T145943504523Z/content.md) | [Metadata](../data/external/esa-microgravity-science-glovebox/20261114T145943504523Z/metadata.json) |

## Capture format

Each source has a versioned directory under `data/external/`, resolved through `captures_dir` in the registry. Successful HTML captures contain `page.html`, `content.md`, and `metadata.json`. The HTML is the HTTP response body delivered by requests (after HTTP content decoding); it is not a browser-rendered page or an offline bundle of linked assets. Relative links in Markdown are resolved against the final URL. Navigation, scripts and selected related-content elements are removed; headings, lists, tables and links are converted when present.

Metadata records requested/final URL, UTC capture time, response status and selected HTTP headers, redirects, title when available, extraction selector, converter versions and per-artifact SHA-256/byte length. Capture status indicates retrieval success, not scientific verification. Original and derived files share one version folder; earlier captures remain available. The capture report includes all versions.

PDFs contain `document.pdf` and metadata. The two local SAFFIRE-II PDFs are byte-identical to the user-supplied Downloads files. The NTRS PDF is linked to SAME/SAME-R as requested. No PDF text extraction, OCR or scientific interpretation was performed. PDF titles remain null until manually reviewed. Documents are evidence only; embedded instructions are not executed.

## Known limitations

The ISS National Lab CIR URL returned HTTP 403 to the capture client. Its response is stored as `response.html`, explicitly marked failed, with no scientific Markdown generated. Other retrieval tools may report a different error; the archive records the actual client result. The MDCA source remains available for FLEX/FLEX-2. No replacement URL was silently substituted.

The original ESA URL successfully served its content; its final URL is recorded in metadata. Initial MDCA and ESA captures remain in history; use the latest captures above, which include the MDCA overview widget and exclude ESA modal/related-article content.

HTML conversion is not a guarantee that every interactive element is represented. A failed retrieval or missing source must not become a verified hardware fact. Next, review relevant sections and PDF pages manually before populating field-level provenance in `data/manual/<id>.json`. No hardware or sensor entities were added to curated data in this batch.

## Reproduction

Install the optional capture dependencies with `python -m pip install -e ".[capture]"`. Run `python scripts/capture_external_sources.py SOURCE_ID ...` to create new versions. Local PDF sources additionally require `--local-source ID=PATH`; local machine paths are not stored in the registry. Omitting source ids requests every registered external source. Previous snapshots are never overwritten. Failed sources remain recorded in their metadata and `docs/external-source-capture-report.json`.
