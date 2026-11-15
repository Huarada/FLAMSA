# SPEC-003 — AI orchestration contracts (RAG + validation + retry)

Status: implemented (ADR-0114). Written before the code (spec-driven development, ADR-0110); AO-01..AO-09 pass in tests/application/test_answering_contract.py and tests/infrastructure/. English artifacts; conversation may be Portuguese.
Source: the team's "FLAMSA AI orchestration" diagram (drawio, 2026-11-14). An English adaptation is now retained in [SVG](../diagrams/ai-orchestration-concept.svg) and [editable draw.io](../diagrams/ai-orchestration-concept.drawio), with [source provenance and runtime differences](../diagrams/ai-orchestration-concept.provenance.json). It is a conceptual design; the README's implementation diagrams and current code distinguish TF-IDF retrieval, deterministic validation and the later guarded partial-answer policy.

## 1. Purpose and scope

Answer a user question about a habitat scenario with an evidence-based response in which every factual claim is traceable to a curated record or an archived source passage, and never let a generated claim or score leave the system unvalidated.

In scope: node responsibilities, the data each node receives and returns, the validation and retry policy, the failure output, and the acceptance tests that any implementation must pass.
Out of scope now: choice of LLM provider, embedding model, vector or graph store, prompt wording, server/API layer. LangChain and LangGraph are the preferred implementation (ADR-0111) but are infrastructure details behind the ports below.

## 2. Flow

```
question + HabitatScenario
  -> retrieve        (deterministic; curated data + domain ranking)  -> shortlist (5-6 investigations)
  -> answer          (LLM; may query the PDF knowledge base)          -> draft with claims + citations
  -> map_solutions   (deterministic dictionary lookup)                -> technology suggestions per cited id
  -> validate        (deterministic rules)                            -> approved | rejected(reasons)
  approved                     -> OUTPUT: answer + evidence traceability map + breakdown + limitations
  rejected, attempts < 2       -> attempts += 1, relax retrieval, back to retrieve
  rejected, attempts == 2      -> PARTIAL OUTPUT if >= 2 claims and >= 50% of the draft validated (ADR-0145):
                                  validated claims only, withheld count, breakdown + limitations
                               -> else FAILURE OUTPUT: insufficient_evidence + deterministic breakdown + limitations
```

`MAX_ATTEMPTS = 2` is a named application constant (attempt counting starts at 1).

## 3. Node contracts

Names follow the diagram; the right column is the port that hides the implementation.

| Diagram node | Responsibility | Port (`application/ports.py`, `typing.Protocol`) | Deterministic? |
|---|---|---|---|
| `retrieve_node` | Filter curated investigations/test points for the scenario and question, call the domain ranking, return the top-k shortlist with its `ScoreBreakdown` | `Retriever` (filter) + domain `RelevanceRanker` (score) | Yes |
| `combustion_agent` | Write the answer as structured claims; may fetch passages from the PDF knowledge base | `Narrator`, `PassageSearch` | No (LLM) |
| `new_solutions_agent` | For each cited investigation, look up derived technologies in the key-value dictionary | `SolutionCatalog` | Yes (lookup, not an agent) |
| `double_check_agent` | Check citation coverage, citation validity, numeric agreement, dictionary backing and physical-plausibility rules | `AnswerValidator` (+ domain rules) | Yes |
| `Approved?` / `attempts < 2?` | Retry policy | use case `AnswerScenarioQuestion` | Yes |

Only one node calls an LLM. The diagram's "agents" that check or look things up are deterministic functions; calling them agents does not make them LLM calls.

### 3.1 retrieve
- Input: `HabitatScenario`, question text, `RetrievalSettings` (top_k, O2/pressure tolerance, pillars, fuel phases).
- Output: `Shortlist` = ordered `RankedInvestigation`s, each with its `ScoreBreakdown` (criterion, weight, value, contribution, evidence `TestPoint` ids) and the matching records.
- The shortlist order comes from the domain ranker, never from embedding similarity or the LLM (CLAUDE.md, ADR-0004). Keyword/embedding search over `investigation.json` may only add candidates to the filter; it never sets the score.
- Relaxing on retry widens tolerances and/or top_k by named constants, records the relaxed settings in the trace and never drops the scenario's hard limits from the limitations text.
- Empty shortlist is a valid result and goes straight to the failure output (no LLM call).

### 3.2 answer (`Narrator`)
- Input: shortlist, breakdowns, question, scenario, previous rejection reasons on a retry.
- Output (structured, not free text): `Draft{claims: [Claim{text, citations: [Citation]}], limitations_ack: bool}`.
- `Citation` is one of: curated record (`investigation_id`, `test_point_id`, column), curated metadata field (`investigation_id`, JSON path), or knowledge-base passage (`investigation_id`, source file from `data/sources.json`, page/locator, quote, DOI if known).
- Allowed citations are only ids present in the shortlist and passages returned by `PassageSearch` in this attempt.
- The Narrator never produces, changes or reorders a score.

### 3.3 PassageSearch (knowledge base)
- Corpus = explicit allowlist of scientific documents (ADR-0109): engineering drawings and telemetry are excluded by construction.
- Returns passages with file, page and exact text, so the validator can check the quote against the archived source.
- Graph-based retrieval (diagram) and vector retrieval are both implementation options; neither is decided here.

### 3.4 map_solutions (`SolutionCatalog`)
- Input: the investigation ids actually cited in the draft. Output: entries `{investigation_id, technology, status}`.
- The diagram's dictionary is labeled "mock". Every entry therefore carries `status = "illustrative"` until it has an archived source; illustrative entries are shown as such in the UI and never count as evidence for a claim (CLAUDE.md data rule 1 and 3).
- A cited id missing from the dictionary is not an error; it yields no suggestion.

### 3.5 validate (`AnswerValidator`)
Rejects the draft, with machine-readable reasons, if any check fails:
1. Coverage: every claim has at least one citation.
2. Validity: every cited `investigation_id`/`test_point_id` is in the shortlist; every passage was returned in this attempt and its quote matches the archived text.
3. Numeric agreement: every number in a claim matches a cited `Quantity` (value and canonical unit, after rounding stated in the claim).
4. Solutions: every technology mentioned is a `SolutionCatalog` entry for a cited id, and illustrative entries are labeled as such.
5. Plausibility (domain rules, named constants): no O2 outside [0, 100]%, no negative pressure, no claim of partial-gravity PSI data (E-FIELD only emulates it), no extrapolation outside tested O2/pressure without the extrapolation notice.

The validator is code, not a second LLM. An LLM judge may be added later only as an extra, non-blocking signal (would need its own ADR).

## 4. Outputs

Both outputs are always rendered with the deterministic `ScoreBreakdown` table and the domain-generated limitations (partial gravity, extrapolation, oxygen basis such as ACME-CFI-G burner-stream O2).

- **Approved:** claims, their citations and an evidence traceability map (claim -> record/passage -> archived file, locator, checksum), the solution suggestions with their status, the run trace (attempts, relaxed settings).
- **Partial (`partial`, ADR-0145):** the claims that raised no issue (re-validated on their own), the count of withheld claims, the traceability and figure traces of the shown claims only, the breakdown and the limitations. Withheld claims are never exposed as text. Constants `MIN_PARTIAL_CLAIMS` = 2 and `MIN_PARTIAL_SHARE` = 0.5; whole-draft failures (empty draft) and strict mode (`PSI_STRICT_ANSWERS=1`) never produce a partial answer.
- **Failure (`insufficient_evidence`):** status code, the rejection reasons of the last attempt, and the breakdown rendered as text by a template. No LLM text is shown. This reconciles the diagram's failure node with the CLAUDE.md rule "invalid citation -> fallback to the deterministic breakdown"; the user never gets an empty answer.

### 4.1 Claim-level evidence and source access (ADR-0128; handoff: docs/copilot-evidence-handoff.md)

Evidence is not a navigation destination; every approved answer carries it inline.

- **Per citation** (`TraceEntry`): investigation, evidence kind (document passage, curated metadata or experimental record), archived file, locator (page, row or field), the quoted excerpt for passages, and a `status` text. The status states what the evidence is: record provenance (verified/inferred/missing), manual-metadata review state, or "document passage; quote matched mechanically, not human-reviewed". A matching quote is never presented as reviewed scientific correctness.
- **Per number** (`FigureTrace`, record figures only): investigation, TestPoint id, column, canonical unit, raw archived text when kept, source file and row, provenance status. Breakdown figures are computed by the application and are not traced to a source.
- **Source access**: `ResolveCitationSource` (application) matches the citation's file against the investigation's registered sources (`SourceReader`, backed by `data/sources.json`, the raw-data roots, external captures and the RAG corpus allowlist). The model only names a path; an unregistered or arbitrary path is never opened (`SourceStatus.UNREGISTERED`). A registered file that cannot be read or whose checksum changed is reported as `UNAVAILABLE` with the reason; the citation stays visible. Report PDFs from the corpus are pinned by SHA-256.
- **View source** (interface): a per-citation action opens a labelled inspection dialog with the citation, source identity and checksum, a download of the cited document, and the study context. If the study is outside the dashboard filters the dialog says so; the dialog never changes the filters, scenario or answer, and closing it returns to the answer.
- **Not provided**: no public URL to the exact page (the DOI is an investigation-level link and is labelled as such); no in-app PDF page rendering.
- **Rejected / fallback outputs** carry no citations or figure traces, as before.
- Acceptance: tests/application/test_citation_traceability.py (fake narrators), tests/infrastructure/test_explorer_snapshot.py (registered report PDFs, unavailable source), tests/interface/test_explorer_app.py (View source, out-of-filter label).

## 5. Placement (Clean Architecture)

- domain: `HabitatScenario`, `RelevanceCriterion`, `RelevanceRanker`, `ScoreBreakdown`, `Citation`, plausibility rules, limitation texts.
- application: ports above, `AnswerScenarioQuestion` use case (retry loop, `MAX_ATTEMPTS`), `AnswerResult`/`FailureResult` value types.
- infrastructure: LangGraph graph wiring the nodes, LangChain LLM/embedding adapters, `PassageSearch` index, `SolutionCatalog` file reader.
- interface: the existing Research copilot panel calls the use case only.
Swapping LangGraph for a plain loop, or one LLM provider for another, must not touch domain or application.

## 6. Acceptance (contract tests with fakes, before any real LLM)

- AO-01: same scenario and data -> same shortlist order and breakdown (determinism).
- AO-02: a fake Narrator that cites an id outside the shortlist is rejected; after `MAX_ATTEMPTS` the result is `insufficient_evidence` with the breakdown text.
- AO-03: a fake Narrator whose number differs from the cited `Quantity` is rejected with a numeric-agreement reason.
- AO-04: a valid fake draft is approved and every claim maps to an archived file and locator.
- AO-05: the retry relaxes retrieval by the named constants and records it in the trace; the Narrator receives the previous rejection reasons.
- AO-06: an empty shortlist returns the failure output without calling the Narrator.
- AO-07: illustrative dictionary entries are labeled and never satisfy coverage for a claim.
- AO-08: a partial-gravity scenario always carries the partial-gravity limitation, whatever the Narrator writes.
- AO-09: no domain or application module imports LangChain, LangGraph or an LLM SDK (import-boundary test).

## 7. Open questions (decide before implementing the matching node)

1. Source and curation of the solutions dictionary (who writes it, with what provenance) — until then it is illustrative only.
2. Knowledge-base retrieval: vector only, or graph + vector; chunking by page.
3. Exact relaxation steps and the shortlist size (diagram says 5-6; `top_k` constant).
4. Whether the server layer (API) is needed at all, or the Streamlit app calls the use case in-process.

## 8. Implementation notes (ADR-0114, ADR-0115)

- Steps and routing live once in `application/answering.py` (`AnsweringSteps`); `AnswerScenarioQuestion` runs them as a plain loop and `infrastructure/answer_graph.py` wires the same steps into LangGraph. Every contract test runs on both engines.
- Passages are retrieved by the use case before the Narrator is called and handed to it (retrieval-augmented prompt), so the validator can check each quote against what was retrieved in the same attempt. The Narrator does not call tools.
- Retrieval is lexical TF-IDF over page chunks of the allowlist `data/rag_corpus.json` (20 documents); the generated cache is `data/rag_index/passages.json` (`scripts/build_rag_index.py`). Graph or embedding retrieval remains an open question.
- With `PSI_LLM_MODEL` unset the `TemplateNarrator` writes the claims; with it set (e.g. `openai:gpt-4.1-mini`) `LangChainNarrator` uses `init_chat_model(...).with_structured_output(Draft)`. The matching provider package must be installed.
- `data/solutions_catalog.json` ships empty: no technology may be suggested until entries with an author and, for `sourced`, an archived source exist.
- The flow-regime criterion from the skill is not implemented; five criteria are active.
