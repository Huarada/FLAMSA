# CLAUDE.md — PSI Fire-Safety Explorer (NASA Space Apps)

Web dashboard with **explainable AI (XAI)** that summarizes, ranks and interprets NASA PSI microgravity combustion investigations for fire safety in crewed habitats (spacecraft, station, lunar/Martian base, pressurized rover). Users can also **export the clean dataset** to feed their own models.

- Detailed procedure (data curation + XAI pipeline + dashboard): `.claude/skills/psi-fire-safety/SKILL.md`. **Load it before any data, AI or UI task.**
- Decision log: `docs/ADR.md`. **Read it before changing architecture; append to it at the end of every session.**

## Language policy (enforced)
**English only** for code, identifiers, comments, docstrings, commit messages, JSON/CSV keys, file and folder names, UI text, skills, CLAUDE.md and every ADR entry. Conversation with the user may be in any language; anything written to the repo is English. A non-English artifact in the repo is a bug: fix it and log it in the ADR.

## Non-negotiable MVP (in this order)
1. 8–10 investigations curated into `data/curated/<investigation_id>/`, validated against the schema.
2. One end-to-end demo scenario: *"lunar base, ≥30% O2, ≤10.2 psi"* → ranking + explanation **with citations**.
3. Clean dataset export (tidy CSV + JSON).

Only afterwards: multiple scenarios, Earth applications, UI polish.
**Out of scope:** rockets/propellants. **The PSI has no partial-gravity data** (LUCI/FM2 are future work); E-FIELD only *emulates* partial gravity. Never claim otherwise.

## Stack
Python 3.11+, Pydantic v2, LangGraph, Streamlit, pandas (only in `infrastructure`/`interface`), pytest, ruff, mypy.

## Folder tree (fixed names: code relies on them)
```
knowledgeBase/                    # raw PSI data. IMMUTABLE, read-only, never renamed (ADR-0008)
data/
  sources.json                    # investigation_id → raw files. The ONLY place raw paths live
  external/<source_id>/<capture_id>/ # archived external HTML/PDF, derived Markdown, capture metadata (ADR-0022)
  curated/<investigation_id>/     # one folder per investigation, always the same two files:
    test_points.csv               #   tidy, 1 row per TestPoint, canonical units, provenance columns
    investigation.json            #   nested metadata (objective, sensors, hardware, pillars, DOI, provenance)
  export/                         # generated for users (concatenated CSV, JSON, schema, data card). Never hand-edited
src/psi_fire/
  domain/                         # entities, value objects, domain services, domain errors
  application/                    # use cases + ports (typing.Protocol)
  infrastructure/                 # CSV/ISA-Tab loaders, adapters, repository, LangGraph/LLM adapters
  interface/                      # Streamlit; composition root in app.py
docs/ADR.md
tests/{domain,application,infrastructure,e2e}/
```
`investigation_id` is the canonical uppercase id from `data/sources.json` (e.g. `SAFFIRE-III`, `ACME-CFI-G`). Never hardcode a `knowledgeBase/` path outside `sources.json`.

## Architecture: Clean Architecture + DDD
Dependencies point **inward only**: `interface → application → domain`. `infrastructure` implements ports.

### Layer rules (a violation is a bug; log it in the ADR)
- `domain` imports nothing from `application`, `infrastructure`, `interface`, `pandas`, `langgraph`, `streamlit`, and performs no I/O. Sole exception: `pydantic` (ADR-0003).
- **Ranking is deterministic and lives in the domain.** The LLM **never** computes, alters or invents a score; it only narrates the computed `ScoreBreakdown` (ADR-0004).
- LangGraph and the LLM are infrastructure details behind the `Narrator` port. Swapping providers touches neither `domain` nor `application`.
- Constructor injection, wired only in the composition root. No singletons, no global state, no `st.session_state` outside `interface`.
- One repository, many views: `InvestigationRepository` serves Streamlit (`to_dataframe()`), LangGraph tools (`all()/get()` → `model_dump_json()`), and LangChain (`to_documents()`). Consumers never read files directly (ADR-0007).

## Ubiquitous language
Use exactly these terms in code, JSON, UI and ADR:
`Investigation`, `TestPoint`, `Fuel` (`FuelPhase: solid|liquid|gas`), `Atmosphere`, `Quantity`, `Flow` (`FlowDirection: concurrent|opposed|quiescent|coflow`), `GravityRegime` (`microgravity|partial_emulated|normal`), `Sensor`, `Hardware`, `FireSafetyPillar` (`prevention|detection|suppression`), `HabitatScenario`, `RelevanceCriterion`, `ScoreBreakdown`, `Citation`, `Provenance`.

## Data rules (non-negotiable)
1. **Never invent a value.** Missing → `null` + `provenance.status = "missing"`. Inferred → `"inferred"` + justification.
2. Raw value **always preserved** next to the normalized one (`Quantity.raw`).
3. Every fact carries `Provenance` (archived file resolved through `data/sources.json` + locator: row/column/page/sheet/section). Sources may be original PSI files in `knowledgeBase/` or versioned external captures in `data/external/` (ADR-0022). External evidence also retains its URL, capture time and artifact SHA-256. A captured page or user-supplied source association alone does not verify an investigation's hardware or sensors.
4. Canonical units: pressure `psi`, O2 `percent` (mole fraction ×100), speed `cm/s`, length `mm`, time `s`. Unit goes in the column name (`o2_percent`).
5. **Evidence quotes are 1:1.** A manual-metadata quote is a character-exact transcription of ONE printed line (PDF/text) or ONE DOCX paragraph, found with Ctrl+F at the cited `p. N` / `para N`; a wrapped sentence is quoted line by line. Claim values may only say what their quotes say (ADR-0032, ADR-0033).

## XAI rules
- Every generated factual sentence cites an `[investigation_id]` present in the retrieved set. A claim that fails validation is withheld and never shown (ADR-0145). After the retries, if at least 2 claims and 50% of the draft validated, the answer is shown as **partial** (badge + count of withheld claims); otherwise → answer rejected → fallback to the deterministic breakdown rendered as text. `PSI_STRICT_ANSWERS=1` restores all-or-nothing.
- The UI **always** shows the breakdown (criterion, weight, value, contribution) next to the LLM text.
- Every answer states relevant limitations (partial gravity, O2/pressure extrapolation outside tested range).

## Clean code
Small single-purpose functions; domain names; full type hints (`mypy --strict` on `domain`); no magic numbers (weights and thresholds are named domain constants); typed domain errors, no bare `except:`; comments only explain *why*. Deliberate shortcut: `# shortcut: <limit>, <when to pay it>` + a `DEBT` ADR entry. Use a pattern only when a concrete problem justifies it (Repository, Strategy, Factory, Value Object, Adapter, Pipeline).

## Continuous ADR (MANDATORY every session)
At the end of **every** response that changed code, data or a decision, **append** entries to `docs/ADR.md`, in English, for each:
`DECISION` (architecture) · `TRADEOFF` · `BUG` (symptom, root cause, impact) · `FIX` (references the BUG) · `ENHANCEMENT` (done or deferred) · `DEBT` (shortcut + payback trigger).
The log is append-only: never edit past entries; a changed decision gets a new entry with `Supersedes: ADR-XXXX`. Format lives in the file itself. A bug seen but not fixed is still logged: hiding bugs is forbidden.

## Verify before saying "done"
```
ruff check . && mypy src/psi_fire/domain && pytest -q
streamlit run src/psi_fire/interface/app.py
```
- Every `data/curated/*/investigation.json` and `test_points.csv` validates.
- Ranking: same scenario → same order (determinism test).
- Demo scenario E2E: output contains ≥1 valid `Citation`.
- Explicitly report what was **not** verified.
