# H1: partial answers versus all-or-nothing validation (decision paper)

Status: proposal, no code changed. To be decided after live run 7 (docs/rag-stress-report-live7.md). Related: docs/rag-failure-hypotheses.md (H1, H2), ADR-0143.

## 1. The rule today

One failing claim rejects the whole answer; after two attempts the user sees only the deterministic ranking ("Insufficient evidence"). This follows CLAUDE.md: "Invalid citation -> answer rejected -> fallback to the deterministic breakdown".

## 2. Evidence for changing it (live run 6, first attempts, replayed with the current validator)

| Measure | Value |
|---|---|
| Drafts with every claim valid | 43% |
| Drafts with some claims valid and some not | 54% |
| Drafts with no valid claim | 3% |
| Drafts with at least 1 / 2 / 3 valid claims | 97% / 92% / 82% |
| Drafts with at least half of their claims valid | 92% |
| Mean claims per draft / per-claim failure rate | 4.6 / 0.33 (before the ADR-0143 rules) |

Reading: the strict rule discards 54% of the drafts that contain several validated claims. Per-claim failure is moderate; answer-level failure is high because failures multiply across about five claims.

## 3. Options

| Option | What the user sees | Main benefit | Main cost |
|---|---|---|---|
| A. Keep strict | Full answer or ranking only | Simplest, strongest guarantee, matches CLAUDE.md | About 55% of answers are lost; the product looks broken |
| B. Partial answer | Only the validated claims, a "Partially validated: k of n claims shown" badge, the ranking and limitations | Recovers most of the lost answers at no extra API cost | Selection effect (see 4), needs an ADR superseding the rejection rule |
| C. Cap the draft at 3 claims | Same as A with fewer claims | Cheap prompt change | Lower coverage; measured gain is unknown |
| D. Per-claim repair (H2), then B as last resort | Repaired claims where possible, partial otherwise | Best quality; fewer withheld claims | Extra API calls and code; more latency |

Recommendation: B with the guardrails below, then D. C alone is weak.

## 4. Impacts of option B

Scientific integrity
- Every claim shown has passed the same checks as today. Nothing unvalidated is displayed. The guarantee per claim is unchanged; the guarantee per answer becomes "each shown claim is valid, the set may be incomplete".
- Selection effect: the claims that fail validation are not random. A claim stating a limitation or a contrary result may be dropped while a favourable one survives, so the remaining text can read more positive than the full draft. Mitigation: the domain-generated limitations and the deterministic breakdown are always shown in full and never depend on the model; the badge states how many claims were withheld.
- Cross-claim references ("as noted above", "in contrast") may point to a withheld claim. Mitigation: the prompt requires each claim to stand alone, and the narrator order is not rewritten.
- Trust: users may read a partial answer as complete. Mitigation: badge wording and colour distinct from "Validated answer"; the withheld text is never shown as an answer (only available to developers in the run trace, as today).

Product
- Fewer "Insufficient evidence" screens: from about 55-60% to about 3% (no valid claim) on this matrix, and the retry still runs first.
- Answers may look shorter and uneven between runs of the same question (already true because of model variance).

Engineering
- Small change: `finalize` keeps claims whose index has no issue, adds `AnswerStatus.PARTIAL`, counts kept and withheld claims, builds traceability and figure traces only for kept claims; the UI badge and a caption change. About a day including tests.
- Issues without a claim index (empty draft, whole-draft failures) keep the strict behaviour.
- The stress harness must report three outcomes (full, partial, insufficient) and keep the invariant that every claim shown has a citation and a source; otherwise the approval rate would silently inflate.
- Contract tests AO-02, AO-03 and the stress invariants need updating: "rejected answer exposes no draft" becomes "withheld claims are never exposed".

Policy and documentation
- CLAUDE.md states the rejection rule; changing it needs an ADR with `Supersedes` and an edit of SPEC-003 section 4 and the XAI rules.

## 5. Guardrails if B is chosen

1. Run the full retry first; partial output only after the last attempt.
2. Minimum evidence for a partial answer: at least 2 validated claims and at least 50% of the draft (named constants). Below that, strict fallback. On the replay this keeps 92% of drafts.
3. Never show withheld claims; show only the count (and the codes in the run trace).
4. Always show limitations and the score breakdown; they do not come from the model.
5. A claim that carries a limitation sentence (partial gravity, extrapolation) is not a special case, because limitations are system-generated; but a plausibility failure (for example an unqualified partial-gravity claim) still withholds that claim and is counted.
6. A configuration switch (strict mode) for evaluation and for anyone who wants the all-or-nothing guarantee.
7. Report the three outcomes separately in every stress report so improvements in model quality are not confused with more tolerant output.

## 6. Questions for the decision

1. Is a partial answer acceptable for the demo, or must every shown answer be complete?
2. Minimum thresholds: 2 claims and 50%, or stricter?
3. Should the badge say "Partially validated" or should the UI label each withheld position ("1 claim withheld")?
4. Strict mode default on or off for the hackathon demo?

## 7. What would change my recommendation

- If run 7 shows that the new validator rules lift the fully valid share above about 70%, the urgency drops and D (repair) alone may suffice.
- If a review of withheld claims shows they are systematically the cautionary ones, B needs a stronger safeguard (for example, withhold the whole answer when a claim containing a negation or a limitation fails).
