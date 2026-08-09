# Reconciliation & Hardening R0

## Objective
Restore a single reproducible source of truth for the Probability Intelligence Platform (PIP) and its read-only FEA integration before any further capability expansion.

## R0 boundaries
- GitHub is canonical for source code, schemas, tests, configuration templates, and release manifests.
- Google Drive is canonical for validation evidence, archived test outputs, governance records, and historical handoff material.
- Drive code packages are migration evidence until reviewed and reconciled into GitHub.
- No live endpoint overwrite, deployment, provider mutation, execution enablement, recommendation release, bookmaker execution, or real-money betting is authorized by R0.
- PIP remains display/read-only and FEA must remain independently operable when PIP is unavailable.

## Required gates
1. Reconcile GitHub against later Drive Phase 5/16 evidence.
2. Repair and rerun the Phase 16H secret scan against preserved evidence.
3. Inventory environment/configuration artifacts without exposing secret values.
4. Adopt a shared FEA/PIP v2 shadow contract.
5. Reconcile the FEA Phase 3 model scaffold rather than merging it directly.
6. Add contract, fail-soft, safety-invariant, and release-manifest CI.
7. Prove non-zero comparable multi-provider shadow consensus before advancing Phase 16I.

## Acceptance posture
R0 closes only after source, contract, tests, deployment manifest, and archived evidence are traceable to reviewed Git commits and no unresolved safety/source-authority conflict remains.
