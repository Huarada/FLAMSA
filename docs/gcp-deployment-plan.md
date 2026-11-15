# GCP deployment and operations

FLAMSA is publicly deployed at **https://flamsa-398749245371.us-central1.run.app**.

## Current verified release

- Project: `flamsa-514815` (`398749245371`); region/service: `us-central1` / `flamsa`.
- Revision: `flamsa-00013-tiw`, receiving 100% in **latest** traffic mode.
- Source commit: `beba8d54e5268130689792347bab85711ad5a53f`.
- Build: `4aa5eec2-0469-4104-b643-3c17bfd757bc` (SUCCESS).
- Image: `us-central1-docker.pkg.dev/flamsa-514815/cloud-run-source-deploy/flamsa@sha256:01b993c0f6c17ea945f4bd0d164ce3d767d24b86d97ea2aa55a79b3f239aae7c`.
- The temporary candidate tag was removed after hosted verification. Historical snapshots remain under [releases](releases/).

Authoritative release observations: [gcp-release.json](gcp-release.json). A later source/configuration update is a new release; do not assume a local edit or new secret version changed a running instance.

## Browser-title patch release

This revision changes only Streamlit page_title to **FLAMSA**. It uses a three-file incremental build over immutable parent `flamsa-00011-gip` (`us-central1-docker.pkg.dev/flamsa-514815/cloud-run-source-deploy/flamsa@sha256:57fa96b889951b08896cac1d524c6e4df50705c9bf9d4104942157e35f6b332d`), copying only the reviewed entry point. The inherited image retains scientific files, installed dependencies, permissions, non-root user and startup command. The canonical Dockerfile remains the full-rebuild path for other changes.

One targeted Streamlit test and scoped Ruff passed. Native Chrome verified document.title=FLAMSA on Home, Dashboard, Fire behavior and Investigations at both the candidate and public URLs, without exceptions. No model question was submitted; the fresh process showed four questions remaining. The 301-pass/179-skip full suite and the approved 36.14-second narration check described below belong to the validated parent release; they were not repeated for this literal title change. See [parent metadata](releases/flamsa-00011-gip.json), [candidate checks](gcp-tab-title-validation.json) and [public checks](gcp-tab-title-public-validation.json).

## Runtime and usage limits

The service uses 1 vCPU, 2 GiB memory, concurrency 10, min 0/max 1 instances, session affinity and a 3,600-second timeout. These are capacity controls, not a hard monetary budget. Cloud Run WebSocket reconnection and best-effort affinity constraints still apply.

Hosted environment settings are `PSI_DAILY_MODEL_LIMIT=4` and `PSI_DAILY_GLOBAL_LIMIT=100`. Each submitted question consumes one allowance; internal narration retries remain within that question. The visitor key is derived from the forwarded network address, not a login. People sharing a network address share an allowance. Counters live in process memory and reset at 00:00 UTC or process/instance restart, including a new deployment. Idle instance recycling can also reset them; this is a demonstration cost guard rather than persistent per-person accounting.

The hosted smoke check observed four remaining questions initially and three after one completed request. The blocked fifth question, independent visitor keys, global ceiling, UTC rollover, fresh-process reset and concurrency are covered by local tests. The real hosted test used one visitor and one model question, not a multi-network abuse test.

Streamlit session state and background Future jobs survive presentation reruns but are not durable across instance replacement. References: [WebSockets](https://docs.cloud.google.com/run/docs/triggering/websockets), [session affinity](https://docs.cloud.google.com/run/docs/configuring/session-affinity), [container contract](https://docs.cloud.google.com/run/docs/container-contract).

## Identity and secrets

- Build identity: `flamsa-build@flamsa-514815.iam.gserviceaccount.com`, with `roles/run.builder`.
- Runtime identity: `flamsa-runtime@flamsa-514815.iam.gserviceaccount.com`, with accessor rights only on its designated secret.
- Model: `openai:gpt-4.1-mini`.
- Runtime secret binding: **`OPENAI_API_KEY=flamsa-openai-api-key:latest`**.

The secret value is not a source file, build argument or image environment value. Cloud Run injects it at instance startup. Adding a Secret Manager version does not refresh an already running process: create a fresh revision after rotation, and verify that production traffic reaches it. Use a unique revision suffix if necessary to force a new revision.

Preserve **latest traffic mode** after the update. A source release may temporarily stage with no traffic, but its final promotion must return to latest after confirming that latest-ready/latest-created is the reviewed candidate. Pinning an older named revision caused the revoked-key incident recorded in ADR-0154. Do not reapply the historical version-1 binding from old release records.

Reference: [Secret Manager integration](https://docs.cloud.google.com/run/docs/configuring/services/secrets). Google CLI access uses browser-authorized credentials; no static Google service-account key was created for this workflow.

## Review, freeze and rebuild

Run project checks, inspect both Git's intended payload and `gcloud meta list-files-for-upload`, and build from an isolated source snapshot. The current package has 1,269 runtime files and 917,250,760 bytes, preserving registered original sources, curated records, captured external evidence, corpus/passages, catalog, theme and artwork. The scientific archive is read-only for the non-root container user; only the derived passage cache is writable.

The native upload list excludes environment secrets, credentials, virtualenvs, IDE/assistant local state, browser profiles, editable-install metadata and evaluation dumps. The focused pattern/exact-value audit found no matching local secret in the intended payload; this is not proof against every possible secret in binary/history content. See [security preflight](release-security-preflight.json).

Existing-service rebuild, preserving its reviewed environment, quota and secret bindings:

```powershell
gcloud run deploy flamsa --source . --project flamsa-514815 --region us-central1 --build-service-account projects/flamsa-514815/serviceAccounts/flamsa-build@flamsa-514815.iam.gserviceaccount.com --allow-unauthenticated --no-traffic --tag releasecandidate
```

Verify the tagged candidate's pages, source integrity, quotas and secret reference before promotion. Check that no newer concurrent revision appeared; then:

```powershell
gcloud run services update-traffic flamsa --project flamsa-514815 --region us-central1 --to-latest --remove-tags releasecandidate
```

Recheck the public endpoint, revision, traffic mode and runtime settings. A build/source update incurs normal cloud usage; this procedure does not require a local Docker daemon. Source packaging is large because the original archive is retained. Dependencies still use version ranges, so the immutable image digest and recorded built versions identify the release.

This local SDK environment used a process-scoped bundle derived from Windows-trusted roots plus certifi, with HTTPS verification enabled. That ignored local trust bundle is not part of the source/image. Do not disable TLS verification. References: [custom CA configuration](https://docs.cloud.google.com/sdk/docs/proxy-settings), [source deployment](https://docs.cloud.google.com/run/docs/deploying-source-code), [upload exclusions](https://docs.cloud.google.com/sdk/gcloud/reference/topic/gcloudignore).

## Verification and limits

Pre-release checks: **301 passed / 179 skipped**, Ruff and domain mypy passed. Skips require local Poppler-dependent source-line checks. The Linux image installs Poppler, but the full suite was not rerun inside the image.

Candidate and public checks confirmed Home, Dashboard, Fire behavior and Investigations without rendered exceptions. Home displays FLAMSA as its dominant fire-gradient title, with the former headline as subtitle; local visual checks covered 1440/390/320-pixel widths, pause and reduced-motion preference. Dashboard retains its research filters and updated count-bubble map; full-study views remain independent. Public root and health returned HTTP 200. A BASS-II source CSV matched its original SHA-256; mobile Home had no horizontal overflow.

One real hosted copilot request completed in **36.14 seconds**, with a language-model label and an **approved** answer under application checks. Submission was disabled while pending, the submitted question survived a draft edit, and the allowance decreased from four to three. This supersedes the earlier unavailable-provider observation for the old secret/revision; it does not establish a general model-quality rate or scientific correctness beyond the implemented checks.

Evidence: [candidate browser results](gcp-brand-browser-validation.json), [public browser results](gcp-brand-public-browser.json), [public HTTP/traffic checks](gcp-brand-http-validation.json), [branding checks](flamsa-brand-home-validation.json), [release metadata](gcp-release.json). Raw model text remains in ignored local verification files; published observations contain status/counts. No production load, full accessibility, physical-device or multi-network quota audit was performed. Persistent quotas/jobs, dependency locking and more efficient archive packaging remain follow-ups.
