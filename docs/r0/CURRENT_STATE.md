# Current State — R0 Baseline

## GitHub main
- PIP main baseline SHA: `830be691647a7640964b58fc0da65204866ac9ea`.
- GitHub main remains predominantly the Phase 2 internal mock/API and early FEA-adapter baseline.
- Display-only, fail-soft, and execution-disabled controls remain the required posture.

## Later validated/tested evidence outside GitHub main
Google Drive contains later PIP Phase 5 completion evidence and Phase 16 provider, consensus, shadow-output, and FEA read-only integration work through Phase 16H. These artifacts remain evidence/migration inputs until reconciled into GitHub.

## Current technical blockers
- GitHub/runtime/evidence drift.
- Phase 16H outer acceptance validator has a keyword-based secret-scan false-positive defect.
- Preserved Phase 16G/16H evidence reviewed in R0 contains zero generated comparable consensus shadow payloads.
- FEA/PIP market and selection identifiers have drifted.
- Operational environment/configuration artifacts are duplicated in Drive and require metadata-only inventory plus secret-store consolidation.
- Phase 16I is not technically accepted by R0 without explicit validation/acceptance evidence.

## Safety posture
- Manual review required.
- Execution disabled.
- Recommendation release disabled.
- No public write endpoint authorized.
- No frontend provider token exposure authorized.
- No bookmaker execution authorized.
