# Atlas Probability Intelligence Platform v1.0 — Phase 1 Foundation and Contract Layer — 14:57, 29.04.2026

This repository starts **PIP Phase 1: Foundation and Contract Layer** for the Atlas project.

PIP is a separate synchronized technical system. It provides probability scoring contracts, learning-engine readiness, calibration readiness, odds-intelligence boundaries, backtesting scaffolding, model-governance controls, and audit logic. **Football Edge Agent (FEA) remains the football-specific product/interface layer and must remain independently operable.**

## Phase 1 operating position

Phase 1 is a contract-first deployment. It is intentionally lightweight and does not require database deployment unless audit persistence is explicitly needed.

| Area | Phase 1 status |
|---|---|
| Repository/folder scaffold | Active |
| Probability response schema | Active |
| Mock probability response | Active |
| FEA fail-soft adapter | Active |
| OpenAPI read-only patch | Active |
| Contract validator | Active |
| FEA fallback tests | Active |
| SQL/database layer | Optional only; use Domeneshop phpMyAdmin SQL console if needed |
| Real-money betting | Not included |
| Auto-betting | Not included |
| Bookmaker execution | Not included |

## Mandatory FEA Phase 5 posture

The current FEA production/rollout Phase 5 posture must remain unchanged:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
FOOTBALL_EDGE_REAL_BETTING_ENABLED=false
FOOTBALL_EDGE_DRY_RUN=true
FOOTBALL_EDGE_AUTO_BETTING_ENABLED=false
```

PIP integration is disabled by default:

```env
PIP_INTEGRATION_ENABLED=false
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=
PIP_API_KEY=
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

## Phase 1 deliverables

| Deliverable | Location |
|---|---|
| Repository/folder structure | Entire repository tree |
| PIP probability response JSON schema | `api/schemas/pip_probability_response.schema.json` |
| Mock PIP probability response | `examples/mock_pip_probability_response.json` |
| FEA fail-soft PIP client/adapter | `adapters/football_edge/` |
| OpenAPI v1 patch for PIP endpoints | `api/openapi.pip.v1.patch.yaml` |
| Contract validator | `tools/contract_validator.py` |
| Contract validator test | `tests/test_pip_contract.py` |
| FEA fallback test | `tests/test_fea_fallback.py` |
| Domeneshop/GitHub rollout instructions | `docs/Phase_1_Rollout_Procedure.md` |
| Optional phpMyAdmin SQL console scaffold | `db/phpmyadmin/optional_phase1_contract_audit_schema.sql` |
| Governance and boundary notes | `docs/Governance_Policy.md`, `docs/FEA_Integration_Guide.md` |

## Hard boundaries

- No real-money betting.
- No auto-betting.
- No bookmaker execution.
- No public write endpoints.
- No frontend write tokens.
- No bookmaker affiliate funnel without legal review.
- PIP enriches FEA only when enabled.
- FEA continues to function if PIP is disabled, unreachable, malformed, or slow.

## Local validation

Run from the repository root:

```bash
python -m unittest discover -s tests
```

Expected result:

```text
Ran 5 tests
OK
```

## GitHub Actions

The workflow in `.github/workflows/pip-phase1-contract-tests.yml` runs the same standard-library test suite on push and pull request events.

## Implementation policy

Phase 1 does **not** perform production model training, live odds execution, account integration, bookmaker routing, customer PII handling, or real-money recommendations. The optional database scaffold is for future audit/governance persistence only and is not required for Phase 1 contract validation.
