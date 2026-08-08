# Source Authority — R0

## Canonical authorities
1. **GitHub main / approved release tag** — source code, schemas, tests, CI, configuration templates, and release definitions.
2. **Google Drive controlled evidence archive** — validation outputs, test archives, manifests, hashes, reports, governance records, and historical transfer material.
3. **Runtime/server configuration** — operational secrets and provider credentials only.

## Conflict resolution
- Newer Drive code does not automatically supersede GitHub. Review, sanitize, test, and reconcile through a controlled branch/PR.
- Technical gate status and operator acceptance are independent dimensions.
- Historical instructions remain historical unless explicitly reclassified.
- Preserve conflicting evidence and resolve it explicitly; do not silently merge states.

## Required phase status dimensions
- technical_gate: PASS | PARTIAL_PASS | BLOCKED | FAIL
- safety_gate: PASS | FAIL
- artifact_state: CREATED | VALIDATED | ARCHIVED
- operator_decision: ACCEPTED | OVERRIDDEN | HELD | NONE
- deployment_state: NOT_DEPLOYED | SHADOW | INTERNAL_LIVE
