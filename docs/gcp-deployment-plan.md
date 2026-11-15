# GCP deployment and operations

The first FLAMSA release is deployed publicly on Cloud Run.

- Public URL: https://flamsa-398749245371.us-central1.run.app
- Project: `flamsa-514815` (`398749245371`); billing and project access verified.
- Region/service: `us-central1` / `flamsa`.
- Revision: `flamsa-00001-kk6`, serving 100% of traffic.
- Build: `6e5be84e-1eba-4414-84f5-a17713a4c218` (SUCCESS).
- Image: `us-central1-docker.pkg.dev/flamsa-514815/cloud-run-source-deploy/flamsa@sha256:defb2817f35ff42411e0185e86f154f108542d1c41044d89da57e3348e1c7843`.

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
gcloud builds describe 6e5be84e-1eba-4414-84f5-a17713a4c218 --region us-central1
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

Pre-build local suite: 270 passed, 179 skipped for local Poppler-dependent visual-line checks. Ruff and domain mypy passed. Cloud Build completed successfully with Poppler installed in the Linux image.

Unauthenticated root and health endpoints returned HTTP 200. Native Chrome verified Home, Dashboard (1,615 records and 693 oxygen/pressure dots), Fire behavior, Investigations, the intended filter visibility, source download and a mobile Home viewport without rendered exceptions or horizontal page overflow. A downloaded BASS-II experimental CSV had the same SHA-256 as its original.

A single-click copilot request survived a draft edit while pending and completed in 34.94 seconds. The generic-question test produced an insufficient-evidence outcome due to `quote_mismatch`, with a visible deterministic ranking; no narrator transport error was observed. This is an enforced evidence constraint, not a successful generated explanation. The record-focused question completed in 7.03 seconds with an undeclared-number rejection for 25 and a visible ranking, again without a narrator transport error. No approved model-generated answer was observed in these two samples; model-output validation quality remains a separate follow-up. The strict checks were not relaxed to obtain a passing demonstration.

Evidence: [HTTP smoke](gcp-public-http-smoke.json), [hosted browser observations](gcp-hosted-browser-validation.json), [record-question result](gcp-hosted-record-answer.json), [release metadata](gcp-release.json), screenshots under `docs/screenshots/gcp-*`. No production load, physical-device or full accessibility audit was performed. Build upload size, cold starts, dependency pinning and durable session storage remain considerations before broader production use.
