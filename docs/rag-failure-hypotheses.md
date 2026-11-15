# RAG answer failures: hypotheses, tests and fixes by pipeline stage

Status: working document. Written 2026-11-15 from four live stress runs (gpt-4.1-mini, 93 runs each, `docs/rag-stress-report-live*.md`), the quote diagnosis (ADR-0140) and a read of the narrator payload (`request_payload`). A fifth, instrumented run (`--dump`) feeds `scripts/attribute_failures.py`, which fills in the "Measured" column below.

## 1. Why this exists

Rejections were counted by validator code, but a code says where the check fired, not where the fault is. `undeclared_number` can be a model that invents digits, a payload that never gave it the fact, or a validator that is stricter than the evidence needs. Every failure is now attributed to exactly one stage:

| Stage | Question it answers | Typical fix |
|---|---|---|
| R retrieval | Did the text the answer needed exist but not reach the model? | Retrieve by page or neighbour chunks, rerank, more passages |
| P packaging | Did the payload, schema or prompt give the model too little, or an ambiguous, contract? | Richer payload, strict schema, placeholders |
| G generation | Did the model write something the evidence does not support? | Constrain output; repair; stronger model |
| V validation | Is the validator stricter than the evidence requires? | Accept what is provably in the document or computed by the system |
| E retry | Does the second attempt repair anything? | Per-claim repair instead of regenerating |

## 2. What the data says so far

- Approved runs of 93 across four live runs: 36, 35, 41, 34 (about 40%). Spread of about 7 with no relevant code change, so single-run comparisons cannot prove a fix.
- Rejections by code (runs affected, run 4): undeclared_number 50, number_mismatch 17, quote_mismatch 17, unknown_citation 8, malformed_citation 4.
- Quote diagnosis (32 rejected quotes): 30 not contiguous in the cited page (merged sentences, joined spans, text of a chunk that was not retrieved, or invented), 2 near-exact. Normalisation was not the problem.
- Payload read: each record sent to the model carries only fuel, oxygen range, pressure range and record level. It does not carry flow, outcomes, source row, the number of tests, verified counts or tested ranges. The model is asked to avoid unsourced digits yet is not given the digits it would naturally state.
- Structure: one rejected claim rejects the whole answer, and a draft has about three claims.

## 3. Hypotheses

### H1 (E/V policy) All-or-nothing validation amplifies small per-claim errors
- Reasoning: with n claims and per-claim failure p, answer failure is 1-(1-p)^n. p = 0.15 and n = 3 already give 39%, close to what we see.
- Test: `attempts_section` of the stress report (per-claim failure rate versus observed answer failure) and `attribute_failures.py` (claims with an issue / claims).
- Fix options: (a) show the claims that passed validation and state how many were withheld (needs an ADR superseding the "invalid citation, answer rejected" rule in CLAUDE.md); (b) ask for at most 3 claims.
- Decide: if observed answer failure is close to the independent-claims prediction, H1 is structural and (a) is the largest single lever.

### H2 (E) The retry regenerates everything and rarely repairs
- Reasoning: attempt 2 resends the whole task plus the issue list; the model can change correct claims into wrong ones.
- Test: share of runs approved after a first-attempt failure (`attempts_section`, `attribute_failures.py` header).
- Fix: surgical repair: send only the failing claims with their issues and the allowed ids, keep the passed claims, allow up to 3 attempts.
- Decide: recovery below about 25% means the retry is not doing its job.

### H3 (P) The payload does not contain the numbers the model wants to state
- Reasoning: counts, tested ranges and flow are system facts but absent from the payload; the model derives or guesses them.
- Test: undeclared_number explained as "not a known fact (model-stated)" versus "system fact" in the report; stage G versus V in the attribution.
- Fix: add a `facts` block with ready sentences and ids, and let the model write placeholders such as `{fact:FLEX.test_count}`. The application substitutes verified values, so digits never come from the model. This removes undeclared_number and number_mismatch by construction instead of policing them.

### H4 (V) The validator rejects numbers that are provably legitimate
- Reasoning: digits copied from a cited quote are in the document by the quote check; page numbers come from the locator; facts of another shortlisted investigation are system facts.
- Test: V-stage counts for undeclared_number ("appears in a cited quote", "page number").
- Fix: accept those three classes. Each is safe by construction; a wrong value still has no source.
- Decide: ship first, since it only removes false rejections.

### H5 (G) The model paraphrases or merges quotes
- Test: quote_mismatch stage G ("not found anywhere") versus G ("locator is wrong") versus R.
- Fix: extractive citations. Passages are sent with sentence ids; the model returns passage id and sentence ids; the application builds the quote. quote_mismatch and malformed passage citations disappear.

### H6 (R) The right chunk exists on the page but was not retrieved
- Test: quote_mismatch stage R.
- Fix: retrieve the whole page of a hit, or neighbour chunks; raise passages per investigation; add a reranker.

### H7 (P) The flat citation schema allows incomplete citations
- Test: malformed_citation count, always stage P.
- Fix: a discriminated union (record, metadata, passage) so structured output enforces required fields per kind.

### H8 (P) Unit and basis confusion produces number_mismatch
- Reasoning: oxygen as mole fraction versus percent, pressure in kPa or atm versus psi, or ambient versus burner-stream oxygen.
- Test: number_mismatch tagged "looks like a unit confusion", or "value belongs to a different record".
- Fix: name units and basis in every payload field; reject pre-converted statements.

### H9 (G) The model is too small for this contract
- Test: rerun the same cells with a larger model (`PSI_LLM_MODEL`) and compare approval and cost.
- Decide: if a larger model passes about 80% or more without code changes, offer it as a configurable tier; otherwise continue with H3 and H5.

### H10 (P/G) Question type matters
- Reasoning: ranking and score questions invite many numbers and failed 3 of 3 in earlier runs.
- Test: per-question approval table; stage split by question category.
- Fix: generate quantitative sentences deterministically (template) and let the model add only interpretation.

### H11 (measurement) Single runs are noise
- Test: `--repeats 3` variance section (approved per round, mean, std, mixed cells).
- Decide: a change counts as an improvement only if it moves the mean by more than about two standard deviations of the rounds.

## 4. Order of work

1. Measure: the instrumented live run (3 rounds, 279 runs, `--dump`) and `attribute_failures.py`.
2. Safe validator gaps (H4). They only remove false rejections.
3. Structural contract changes (H3 placeholders, H5 extractive quotes, H7 union schema). Each is aimed at the largest stage share found in step 1.
4. Retry and policy (H2 repair; H1 partial answers, which needs a decision from the project owner).
5. Model comparison (H9) once the contract is as strict and as helpful as it can be.

After each step rerun the same matrix and compare using H11. No change may weaken a verification: the negative tests (wrong number, invented quote, unknown citation) must keep failing.

## 5. Reading the result

| If the attribution shows | Root cause is | Next step |
|---|---|---|
| Mostly G on quotes and numbers | The model invents; the contract lets it | H3, H5 |
| Mostly V | Validator stricter than the evidence | H4 |
| Mostly P | Payload or schema | H3, H7, H8 |
| Mostly R | Retrieval | H6 |
| Per-claim p small but answer failure large | Structure | H1 |
| Retry recovery low | Retry design | H2 |
| Large approval gain from a bigger model | Capacity | H9 |
