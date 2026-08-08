# Phase 16H Validator Remediation

## Defect
The preserved outer Phase 16H acceptance validator scans raw JSON text for generic words including `secret`, `api_key`, `password`, and `token`. Safe metadata keys therefore produce false positives even when the evidence records no credential value.

## Corrected rule
Secret scanning must be value-aware:
- field names alone never constitute a leak;
- booleans/status metadata such as `api_key_configured=true` are safe;
- redacted/environment placeholders are safe;
- actual credential-like string values are findings;
- findings report JSON paths only and never echo credential values.

## Rerun requirements
1. Preserve the original Phase 16H archive and original FAIL record unchanged.
2. Run `tools/phase16h_secret_scan.py` against the preserved raw JSON directory.
3. If no credential values are detected, rerun the Phase 16H acceptance classification with the corrected scanner.
4. Archive a new remediation result with hashes and an explicit pointer to the original result.
5. A corrected secret scan does not by itself prove full Phase 16H functional readiness; non-zero comparable shadow consensus remains a separate gate.
