# Atlas Probability Intelligence Platform v1.0 — Phase 2 Transfer Pack — 00:59, 30.04.2026

## Authoritative project context

Atlas Probability Intelligence Platform v1.0 (`PIP`) is a separate synchronized technical system, not an embedded feature inside Football Edge Agent (`FEA`). PIP provides probability scoring, learning-engine architecture, calibration/recalibration logic, odds intelligence, backtesting, model-governance controls, audit/contract validation logic, and future model/provider upgrade pathways.

FEA remains the football-specific product/interface layer and must remain independently operable before, during, and after PIP integration.

## Current repository

```text
nanotech-solutions-norway/Probability_Intelligence_Platform
```

Default branch:

```text
main
```

## Phase 1 status

PIP Phase 1: Foundation and Contract Layer has been deployed and validated.

Validated Phase 1 controls:

- Repository initialized.
- GitHub Actions workflow completed successfully.
- PIP probability response contract exists.
- Mock probability response exists.
- Contract validator exists.
- FEA fallback behavior exists and is tested.
- PIP is disabled by default.
- `PIP_REQUIRED_FOR_RECOMMENDATIONS=false`.
- `PIP_FAILSAFE_MODE=true`.
- Python fail-soft adapter exists.
- PHP/Domeneshop fail-soft adapter exists.
- OpenAPI patch is read-only.
- Optional phpMyAdmin SQL scaffold exists but is not mandatory.
- No MariaDB SQL execution is required for Phase 1.
- FEA Phase 5 posture remains preserved.

## Phase 2 status

PIP Phase 2: Internal Mock API + FEA Integration Readiness has been implemented in GitHub.

Phase 2 adds:

- Protected internal PIP API endpoint structure.
- Health endpoint.
- Fixture probability mock endpoint.
- Server-side API key validation using `X-PIP-API-Key`.
- PHP/Domeneshop-compatible endpoint structure.
- Optional `.htaccess` pretty-route notes.
- FEA-side optional integration test procedure.
- FEA environment variable activation checklist.
- Static endpoint contract validation script.
- API security checklist embedded in rollout procedure.
- Phase 2 GitHub Actions workflow.
- Manual Domeneshop upload/placement instructions.
- Rollback instructions.
- Evidence checklist for readiness confirmation.

## Phase 2 files added

```text
.env.pip.phase2.example
.github/workflows/pip-phase2-internal-api-tests.yml
services/pip_api/public/api/v1/pip/health.php
services/pip_api/public/api/v1/probability/football/fixture.php
services/pip_api/includes/auth.php
services/pip_api/includes/response_helpers.php
services/pip_api/config/pip_config.example.php
services/pip_api/config/.htaccess
services/pip_api/public/.htaccess
tools/phase2_endpoint_contract_check.py
tests/test_phase2_internal_api_static.py
docs/Phase_2_Internal_Mock_API_Rollout_Procedure.md
docs/Phase_2_Transfer_Pack.md
```

Updated:

```text
.gitignore
```

## Mandatory FEA private `.env` posture

The existing FEA Phase 5 posture must remain unchanged:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
FOOTBALL_EDGE_REAL_BETTING_ENABLED=false
FOOTBALL_EDGE_DRY_RUN=true
FOOTBALL_EDGE_AUTO_BETTING_ENABLED=false
```

PIP default posture remains disabled:

```env
PIP_INTEGRATION_ENABLED=false
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=
PIP_API_KEY=
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

Controlled Phase 2 FEA-side integration testing may use:

```env
PIP_INTEGRATION_ENABLED=true
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=https://www.atlas-ai.no
PIP_API_KEY=<SERVER_SIDE_KEY_ONLY>
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

## Hard boundaries preserved

The following remain non-negotiable:

- No real-money betting.
- No auto-betting.
- No bookmaker execution.
- No public write endpoints.
- No frontend write tokens.
- No bookmaker affiliate funnel without legal review.
- PIP may enrich FEA only when enabled.
- FEA must continue working when PIP is disabled, unavailable, slow, malformed, or misconfigured.
- PIP must preserve stable API contracts to FEA while allowing future learning-engine upgrades.

## Allowed Phase 2 endpoints only

```text
GET /api/v1/pip/health
GET /api/v1/probability/football/fixture/{fixture_id}?market=1X2
```

Domeneshop flat-file fallback:

```text
GET /api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2
```

Disallowed:

```text
POST
PUT
PATCH
DELETE
real-money endpoints
execution endpoints
bookmaker endpoints
affiliate endpoints
frontend token endpoints
```

## Required security behavior

Header:

```text
X-PIP-API-Key
```

The API key must never be placed in frontend JavaScript, static HTML, public repo secrets, browser-visible code, or query parameters.

Expected failures:

- Missing API key: HTTP `401 Unauthorized`.
- Invalid API key: HTTP `401 Unauthorized`.
- Key enforcement enabled but no server-side key configured: HTTP `503`.
- Non-GET request to endpoint: HTTP `405 Method Not Allowed`.

## Required response controls

The probability endpoint must always include:

```json
"execution_allowed": false
```

and:

```json
"compliance_mode": "display_only"
```

## GitHub validation commands

Run:

```bash
python -m unittest discover -s tests
python tools/contract_validator.py examples/mock_pip_probability_response.json
python tools/phase2_endpoint_contract_check.py
```

Expected:

```text
OK
PIP contract validation passed
PIP Phase 2 endpoint contract check passed
```

## Manual Domeneshop work still required

Phase 2 has been implemented in GitHub, but Domeneshop deployment is manual and controlled.

Manual steps remaining:

1. Upload the Phase 2 PHP endpoint files to Domeneshop.
2. Create `pip_config.local.php` server-side only.
3. Set a strong internal API key.
4. Validate health endpoint with authorized and unauthorized requests.
5. Validate probability endpoint with authorized request.
6. Confirm no frontend token exposure.
7. Confirm no database SQL execution.
8. Confirm FEA Phase 5 `.env` posture remains unchanged.
9. Capture evidence screenshots/logs.

## Evidence required for Phase 2 completion

- GitHub Actions screenshot showing `PIP Phase 2 Internal API Tests` passed.
- Authorized health endpoint returns HTTP `200`.
- Health response contains no secrets.
- Missing API key returns HTTP `401`.
- Invalid API key returns HTTP `401`.
- Authorized probability endpoint returns HTTP `200`.
- Probability response validates against PIP contract.
- Probability response includes `execution_allowed=false`.
- Probability response includes `compliance_mode=display_only`.
- POST request returns HTTP `405` or is unavailable.
- No SQL/database deployment was executed.
- FEA Phase 5 posture remains preserved.

## Rollback summary

1. Set `PIP_INTEGRATION_ENABLED=false` in FEA.
2. Clear `PIP_BASE_URL`.
3. Rename or remove `health.php` and `fixture.php` on Domeneshop.
4. Rotate or remove `pip_config.local.php`.
5. Remove optional `.htaccess` routing if needed.
6. Do not alter FEA safety flags.
7. Do not execute SQL for rollback.

## Recommended next action

Complete GitHub Actions validation for Phase 2, then perform the manual Domeneshop upload using `docs/Phase_2_Internal_Mock_API_Rollout_Procedure.md` as the operating runbook.
