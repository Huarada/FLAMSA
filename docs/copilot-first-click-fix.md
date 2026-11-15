# Ask copilot: preserve the first submitted request

Date: 2026-11-15. SPEC-001 section 28, AC-101 through AC-103.

## Reproduction and cause

The old implementation used the transient return value of `st.button` late in the full script, after rendering the charts, and ran initialization/answering synchronously on that script run. The result was assigned to session state only after the call returned. A rerun arriving before that branch could consume the click without starting work; a rerun during the synchronous call could abandon the rendering run before its answer was committed. The cached engine could nevertheless be warm for a second click.

A native Chrome reproduction used a fresh Streamlit process and browser profile, a real offline template pipeline and a four-second delay around its answerer. One Ask click was followed by a textarea edit/blur during the wait. Before the fix, the new view settled without a result. The instrumented answerer logged one start and one completion, but no answer or score breakdown appeared in that view. [Before observations](copilot-interrupted-before.json).

A separate first-click sample with the configured provider finished in about 30.52 seconds with an insufficient-evidence outcome. It did not reproduce a UI failure and is not evidence of a transport error. Subsequent interruption experiments explicitly forced the offline template in Python, so validating the race did not depend on provider timing or additional paid calls. [Configured-provider sample](copilot-first-click-before.json).

## Implemented contract

- A keyed button callback records a per-session `CopilotJob` before chart rendering. It reads current widget state rather than scenario/question values captured in an earlier render.
- The job captures the investigations, scenario and question. It starts one daemon worker with a typed Future. Workers do not access Streamlit session state or render UI.
- Engine construction remains deferred until submission. The cached composition-root factory has its automatic spinner disabled so initialization can run without rendering from the worker. A polling fragment provides explicit progress instead.
- Submission is disabled while pending. Draft edits and other reruns reuse the same job; they do not repeat model calls.
- On completion, the UI commits both the answer and actual narrator label, removes the pending job and performs one full rerun to refresh chart highlighting and re-enable submission. Existing answer rendering does not resolve the engine again.
- The response identifies its submitted conditions and question, separately from any draft edited during the wait.
- An operational failure displays a generic retry message without provider secrets and preserves an earlier answer. An explicit retry creates a new job. Citation/number validation and legitimate insufficient-evidence outcomes are unchanged.

This is interface state management, not an alternate ranker, narrator or orchestration pipeline. The existing application use cases and provider adapter remain responsible for answering and validation. It is per live session and does not promise durable recovery after a server restart or a genuinely new browser session.

## Verification

The same native one-click/textarea-edit reproduction completed after the fix in about **7.14 seconds**, including the artificial four-second delay and initialization. The button was disabled while pending and enabled after completion. The original submitted question remained identified even though the editable field had changed. One start and one completion were logged for this attempt; no second click was used. The answer, sources, score breakdown and chart highlighting were rendered with zero visible exceptions. Timing is a local observation, not a latency guarantee. [After observations](copilot-first-click-after.json), [visually inspected screenshot](screenshots/copilot-first-click-fixed.png).

`tests/interface/test_copilot_request_lifecycle.py` covers cold initialization, an interruption before the copilot branch, repeated view reruns, current batched input capture, exactly one answer call, result persistence, operational failure, previous-answer preservation and explicit retry. Existing explorer tests await their offline job before asserting citation/source output. Deferred-initialization tests continue to ensure browsing alone does not construct an engine.

Full suite: **264 passed, 179 skipped** in 285.34 seconds; skips require pdftotext/Poppler PDF visual-line verification. Ruff, domain mypy and strict mypy for the worker/deferred handle passed. The ADR verification entry retains the complete scope. Physical devices, a production load test and all possible provider failure modes were not tested. A live provider was not called again after the fix; the deterministic delayed offline reproduction isolates the UI lifecycle defect.
