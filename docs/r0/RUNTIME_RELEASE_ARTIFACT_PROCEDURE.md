# Runtime Release Artifact Procedure — R0

This procedure creates a deterministic, reviewed PIP runtime source bundle. It does not deploy or authorize deployment.

## Purpose

The bundle establishes an evidence-backed Git SHA, complete file inventory, per-file hashes, and archive SHA-256 before any later server reconciliation. It packages canonical runtime source and the shared FEA/PIP v2 contract while excluding local configuration and secret-bearing files.

## Build locally

```text
python tools/build_runtime_release.py --git-sha <full-reviewed-commit-sha> --output-dir dist/runtime-release
```

The builder emits only the source SHA, archive hash, file count, artifact paths, and fixed safety-state markers. No provider payload or credential value is read or printed.

## Protected GitHub build

Run `PIP Reproducible Runtime Release Artifact` with `workflow_dispatch` on the reviewed ref. The workflow:

1. checks out the exact Git commit;
2. proves the bundle is byte-for-byte deterministic;
3. verifies every safety lock remains disabled;
4. uploads the bundle and JSON manifest for 30 days.

The resulting manifest may populate a reviewed-source release candidate record. It must not be recorded as the deployed runtime SHA or deployed artifact hash until the host contents are separately reconciled to that exact artifact.

## Safety state

- Deployment authorization: disabled.
- Recommendation release: disabled.
- Execution: disabled.
- Bookmaker execution: disabled.
- Real-money betting automation: disabled.
- Manual review: required.
