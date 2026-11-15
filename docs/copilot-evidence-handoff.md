# Copilot evidence handoff

Context: Evidence has been removed from primary navigation. Study metadata, record inspection and archived source downloads remain in Investigations. The orchestration workstream must preserve evidence in answers; the header change does not remove scientific traceability requirements.

Requested work for the orchestration owner:

1. Retain claim-level citations in every approved answer. Show investigation identity, the faithful source excerpt when available, document name, page/row/field locator and TestPoint/column identity for quantitative claims. Distinguish documentary passages, curated metadata and experimental records.
2. Preserve deterministic scores/calculations, validation/retry behavior, rejection of unsupported claims, uncertainty and scientific limitations. Do not turn a retrieved passage or a matching quote into an assertion of human-reviewed scientific correctness.
3. Provide a contextual View source action using the existing registered source-reader contract. A NASA PSI DOI is a useful investigation link but is not an exact PDF-page link. Do not invent public document URLs or accept arbitrary filesystem paths from the model. Keep source identity/checksum/revision available where the current contracts carry them; extend contracts explicitly if necessary.
4. An inspected citation may belong to a study outside the Dashboard research query because ranking currently covers the complete corpus. Open a labelled source/study inspection context and provide a return path without silently clearing or broadening research filters. Preserve the current selected scenario and answer context.
5. Preserve raw values, canonical units, row lineage, claim status, manual review state and source locators where available. Report missing/unavailable source information rather than inventing it.
6. Cover approved claim traceability, rejection/fallback, missing or unavailable sources, registered source access and out-of-filter citations with appropriate tests. Use fake narrators/models in automated tests; no paid API call is necessary.
7. Update SPEC-003 and the append-only ADR. Coordinate shared app/session changes; navigation now consists of Home, Dashboard, Fire behavior and Investigations. Do not recreate a standalone Evidence header destination.

Status: handoff request, not a claim that contextual source navigation has already been implemented. Existing copilot citations remain in place in this increment.
