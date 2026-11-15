# GCP deployment and operations

FLAMSA is deployed publicly on Cloud Run. The latest verified frozen-source release is described below.

- Public URL: https://flamsa-398749245371.us-central1.run.app
- Project: `flamsa-514815` (`398749245371`); billing and project access verified.
- Region/service: `us-central1` / `flamsa`.
- Revision: `flamsa-00002-lis`, serving 100% of traffic.
- Build: `0c6f8fda-4c7b-4ef0-9cd9-e9c3ab524313` (SUCCESS).
- Image: `us-central1-docker.pkg.dev/flamsa-514815/cloud-run-source-deploy/flamsa@sha256:58d55e98ebb1aaccec7172948a06181a014b1bbe6252def382bc202c7832c61e`.

Machine-readable release settings: [gcp-release.json](gcp-release.json).

## Runtime and session behavior

The service uses 1 vCPU, 2 GiB memory, concurrency 10, minimum instances 0, maximum instances 1, a 3,600-second request timeout and session affinity. Public invocation was verified through the service IAM policy and unauthenticated HTTP requests. These settings are capacity controls, not a hard monetary budget.

Cloud Run supports WebSockets, with request timeout and reconnection constraints. Affinity is best effort. Streamlit session state and background Future jobs survive presentation reruns, but are not durable across instance replacement or a new session. Verify changes in the actual hosted environment; local AppTest results alone do not establish cloud behavior.

References: [WebSockets](https://docs.cloud.google.com/run/docs/triggering/websockets), [session affinity](https://docs.cloud.google.com/run/docs/configuring/session-affinity), [container contract](https://docs.cloud.google.com/run/docs/container-contract).

## Identity and model configuration

The project-access account was authorized through Google's browser flow; the original SDK identity did not have access. The SDK now selects `flamsa-514815`. No static Google service-account key was created or copied into the application.

- Build identity: `flamsa-build@flamsa-514815.iam.gserviceaccount.com`, with `roles/run.builder` on this project.
- Runtime identity: `flamsa-runtime@flamsa-514815.iam.gserviceaccount.com`, without broad project roles.
- Model: `openai:gpt-4.1-mini`, preserving the existing provider.
- Runtime secret binding: `OPENAI_API_KEY=flamsa-openai-api-key:1`.

The existing provider key was sent directly through stdin into Secret Manager. Its value was not printed, saved to source, put into an image layer or included in build arguments. Only the runtime identity was granted accessor rights on this specific secret. Cloud Run injects it at startup. A new secret version requires updating the pinned runtime binding.

Reference: [Secret Manager integration](https://docs.cloud.google.com/run/docs/configuring/services/secrets).

## Scientific files and the build snapshot

The image includes registered original documents, curated investigation JSON/CSV pairs, archived external evidence, the corpus manifest, derived passage index, solution catalog, theme and packaged artwork. Source evidence is read-only under the non-root runtime user; the derived passage-index directory can be rebuilt. Source paths and scientific values were not rewritten for deployment.

The first release used a separate source copy: 1,267 files, 917,197,413 bytes. The tested source-manifest SHA-256 is `c7a3c53c59a4bcaf1c88366766866a63854a823f23d52f9ca5e4c2b53ed2ca04`. Relevant source/curated/deployment hashes were unchanged before and after the copy. This preserves the tested package even if the shared working directory changes while a build runs.

The native gcloud upload check exposed directory-pruning differences from the earlier Python Git-style matcher. The shared `.dockerignore`/`.gcloudignore` policy was simplified and the native check repeated successfully: required runtime inputs present; `.env`, Git metadata, browser scratch, tests and unrelated audit assets excluded. All 54 checked science-source references have exact case-sensitive paths for Linux. Do not deploy only the curated tables: that would remove the original-source download and report-backed answering capability.

The complete original archive is about 864 MiB, so source upload and first image construction are substantial. Optimize packaging only with a verified source-access contract. The built image installs dependency versions allowed by pyproject.toml; selected actual versions are retained in the release JSON. The image digest is the immutable release artifact; future rebuilds must be tested because dependency ranges can resolve differently.

## Local CLI access and inspection

Reopen the VS Code terminal after installing Google Cloud CLI if gcloud is not on PATH. The installed Windows CLI is under the user's `AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/` directory.

```powershell
gcloud auth list
gcloud config set project flamsa-514815
gcloud run services describe flamsa --region us-central1
gcloud builds describe 0c6f8fda-4c7b-4ef0-9cd9-e9c3ab524313 --region us-central1
```

This execution environment required a process-scoped custom CA bundle derived from existing Windows-trusted roots plus certifi. HTTPS verification was kept enabled; the machine-local bundle is ignored and is not part of the build. Do not disable TLS verification to work around a certificate problem. If necessary, follow Google's [custom CA configuration](https://docs.cloud.google.com/sdk/docs/proxy-settings).

## Rebuild and redeploy

First run the required project checks and inspect `gcloud meta list-files-for-upload`. Confirm the active account/project and freeze the intended source snapshot before building. The existing dedicated identities, API enablement and secret are already provisioned. A source rebuild can use:

```powershell
gcloud run deploy flamsa --source . --project flamsa-514815 --region us-central1 --build-service-account projects/flamsa-514815/serviceAccounts/flamsa-build@flamsa-514815.iam.gserviceaccount.com --service-account flamsa-runtime@flamsa-514815.iam.gserviceaccount.com --port 8080 --cpu 1 --memory 2Gi --concurrency 10 --timeout 3600 --min-instances 0 --max-instances 1 --session-affinity --allow-unauthenticated --set-env-vars PSI_LLM_MODEL=openai:gpt-4.1-mini --set-secrets OPENAI_API_KEY=flamsa-openai-api-key:1
```

This command creates a new image/revision and can incur build, storage, runtime and provider usage charges. It does not need a local Docker daemon; Cloud Build constructs the Linux image. Keep secret values out of the command line and review the image/revision and actual hosted behavior after each release.

References: [source deployment](https://docs.cloud.google.com/run/docs/deploying-source-code), [custom build identity](https://docs.cloud.google.com/run/docs/configuring/services/build-service-account), [upload exclusions](https://docs.cloud.google.com/sdk/gcloud/reference/topic/gcloudignore).

## Validation and remaining limits

Source commit: `6f745552ab3c549959768b27bfed5211ac7dc97a`. Build `0c6f8fda-4c7b-4ef0-9cd9-e9c3ab524313` succeeded. The candidate was tested with zero production traffic, then promoted to 100 percent; the temporary releasecandidate tag was removed. The previous image/revision remains recorded in [release history](releases/flamsa-00001-kk6.json).

Pre-release checks: 290 passed, 179 skipped for local Poppler-dependent source-line checks; Ruff and domain mypy passed. The Linux image includes Poppler, but the full suite was not repeated inside that image. Both candidate and public root/health endpoints returned HTTP 200. Native Chrome verified Home, Dashboard (1,615 records and 693 scalar oxygen/pressure dots), Fire behavior and Investigations without rendered exceptions. Research filters appeared only on Dashboard. A downloaded BASS-II source CSV matched its original SHA-256, and mobile Home had no horizontal overflow.

The single-click copilot request survived an edit of the draft input, disabled/re-enabled submission and displayed the deterministic ranking after 20.39 seconds. However, the model provider returned HTTP 429 because its credits were exhausted. No generated answer was obtained; this is provider availability, not a scientific evidence-validation rejection. Restore provider credits separately to test live narration. Do not change evidence rules, model configuration or keys merely to manufacture a successful smoke result. Raw provider details and its screenshot remain in ignored local verification files, outside GitHub/build publication.

Security preflight reviewed tracked text and exact local-secret matches, plus the native gcloud upload list: no prohibited local inputs or matching secret values were detected. Excluded editable-install .egg-info metadata along with environment files, credentials, virtualenvs, IDE/assistant state, browser profiles and evaluation dumps. The 1,268-file/917,233,849-byte source snapshot was hash-verified. This is a focused publication audit, not proof against every possible secret in binary/history content.

Evidence: [sanitized security review](release-security-preflight.json), [HTTP checks](gcp-release-http-validation.json), [candidate browser results](gcp-release-browser-validation.json), [public browser results](gcp-release-public-browser.json), [current release metadata](gcp-release.json). Screenshots: docs/screenshots/gcp-release-*. No production load, physical-device or full accessibility audit was performed. Build size, dependency locking, model funding and durable session storage remain operational follow-ups. Work created after the frozen snapshot is not part of this release.

## Daily question limit (cost guard)

The deployment sets `PSI_DAILY_MODEL_LIMIT=4`: at most 4 copilot questions per UTC day in total, across all visitors. The count lives in the memory of the server process, so it starts again at 0 whenever a new revision is released (and also if Cloud Run recycles an idle instance, because `min-instances` is 0). Unset or `0` means no limit (local use). When the limit is spent the "Ask copilot" button is disabled and the panel says when it resets; the previous answer, charts and filters stay visible.

## Rotating the model key (Secret Manager)

The key is never in source, an image or a command line. To store a new key, run this in PowerShell on the machine where gcloud is logged in; it asks for the key without echoing it and writes it without a trailing newline:

```powershell
$secure = Read-Host "New OpenAI key" -AsSecureString
$key = [System.Net.NetworkCredential]::new('', $secure).Password
$file = New-TemporaryFile
[IO.File]::WriteAllText($file, $key)
gcloud secrets versions add flamsa-openai-api-key --data-file="$file" --project flamsa-514815
Remove-Item $file -Force; Remove-Variable key, secure
```

Then point the service at the newest version and retire the revoked one:

```powershell
gcloud run services update flamsa --region us-central1 --project flamsa-514815 --update-secrets OPENAI_API_KEY=flamsa-openai-api-key:latest
gcloud secrets versions disable 1 --secret flamsa-openai-api-key --project flamsa-514815
```

`latest` is resolved when an instance starts, so a new version needs a new revision (the `services update` above creates one). Use a key from a separate provider project with its own monthly budget for the public site.
