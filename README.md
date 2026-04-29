# Atlas Probability Intelligence Platform v1.0 — Phase 2 Internal Mock API + FEA Integration Readiness — 00:59, 30.04.2026

This repository contains **Atlas Probability Intelligence Platform v1.0** (`PIP`) for the Atlas project.

PIP is a separate synchronized technical system. It provides probability scoring contracts, learning-engine readiness, calibration readiness, odds-intelligence boundaries, backtesting scaffolding, model-governance controls, audit logic, and future model/provider upgrade pathways. **Football Edge Agent (`FEA`) remains the football-specific product/interface layer and must remain independently operable.**

## Current operating position

Phase 1 established the foundation and contract layer. Phase 2 adds a protected internal mock API layer and FEA integration-readiness workflow while preserving the existing FEA Phase 5 production posture.

| Area | Current status |
|---|---|
| Repository/folder scaffold | Active |
| Probability response schema | Active |
| Mock probability response | Active |
| FEA fail-soft adapter | Active |
| OpenAPI read-only patch | Active |
| Contract validator | Active |
| FEA fallback tests | Active |
| Phase 2 internal health endpoint | Active in repository; manual Domeneshop upload required |
| Phase 2 internal fixture probability endpoint | Active in repository; manual Domeneshop upload required |
| Server-side API key validation | Active |
| SQL/database layer | Optional only; no database deployment required |
| Real-money betting | Not included |
| Auto-betting | Not included |
| Bookmaker execution | Not included |
| Frontend write token | Not included |

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

Controlled Phase 2 server-side FEA integration testing may use:

```env
PIP_INTEGRATION_ENABLED=true
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=https://www.atlas-ai.no
PIP_API_KEY=<SERVER_SIDE_KEY_ONLY>
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

## Current deliverables

| Deliverable | Location |
|---|---|
| PIP probability response JSON schema | `api/schemas/pip_probability_response.schema.json` |
| Mock PIP probability response | `examples/mock_pip_probability_response.json` |
| FEA fail-soft PIP client/adapter | `adapters/football_edge/` |
| OpenAPI v1 patch for PIP endpoints | `api/openapi.pip.v1.patch.yaml` |
| Contract validator | `tools/contract_validator.py` |
| Phase 2 endpoint static checker | `tools/phase2_endpoint_contract_check.py` |
| Contract and fallback tests | `tests/` |
| Phase 2 health endpoint | `services/pip_api/public/api/v1/pip/health.php` |
| Phase 2 probability endpoint | `services/pip_api/public/api/v1/probability/football/fixture.php` |
| Phase 2 API key auth helper | `services/pip_api/includes/auth.php` |
| Phase 2 response helper | `services/pip_api/includes/response_helpers.php` |
| Phase 2 config example | `services/pip_api/config/pip_config.example.php` |
| Phase 2 rollout procedure | `docs/Phase_2_Internal_Mock_API_Rollout_Procedure.md` |
| Phase 2 transfer pack | `docs/Phase_2_Transfer_Pack.md` |
| Optional phpMyAdmin SQL console scaffold | `db/phpmyadmin/optional_phase1_contract_audit_schema.sql` |

## Phase 2 endpoint surface

Allowed endpoint types only:

```text
GET /api/v1/pip/health
GET /api/v1/probability/football/fixture/{fixture_id}?market=1X2
```

Domeneshop flat-file fallback:

```text
GET /api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2
```

No `POST`, `PUT`, `PATCH`, or `DELETE` endpoint is introduced.

## Security requirements

The internal API uses server-side header validation:

```text
X-PIP-API-Key: <SERVER_SIDE_KEY_ONLY>
```

The API key must never be placed in frontend JavaScript, static HTML, public repo secrets, browser-visible code, or query parameters.

Expected API behavior:

| Scenario | Expected result |
|---|---|
| Authorized health request | HTTP 200 |
| Missing API key | HTTP 401 |
| Invalid API key | HTTP 401 |
| API key enforcement enabled but no server-side key configured | HTTP 503 |
| Non-GET request | HTTP 405 |

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
python tools/contract_validator.py examples/mock_pip_probability_response.json
python tools/phase2_endpoint_contract_check.py
```

Expected result:

```text
OK
PIP contract validation passed
PIP Phase 2 endpoint contract check passed
```

## GitHub Actions

The workflow in `.github/workflows/pip-phase2-internal-api-tests.yml` runs:

```bash
python -m unittest discover -s tests
python tools/contract_validator.py examples/mock_pip_probability_response.json
python tools/phase2_endpoint_contract_check.py
```

The Phase 1 workflow remains available for continuity.

## Database policy

Phase 2 does **not** require database deployment. The optional SQL scaffold under `db/phpmyadmin/` remains optional only and must be executed through Domeneshop/phpMyAdmin built-in SQL console only if persistent audit logging becomes strictly necessary later.

Do not alter existing FEA tables. Do not introduce a required database dependency for Phase 2.

## Manual deployment status

Phase 2 files are implemented in GitHub. Domeneshop deployment remains manual and controlled. Use:

```text
docs/Phase_2_Internal_Mock_API_Rollout_Procedure.md
```

as the operating runbook for upload, validation, rollback, and evidence capture.
