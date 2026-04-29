# Atlas PIP Phase 2 Internal Mock API Rollout Procedure — 00:59, 30.04.2026

## Objective

Deploy **PIP Phase 2: Internal Mock API + FEA Integration Readiness** for Atlas Probability Intelligence Platform v1.0 while preserving Football Edge Agent Phase 5 production safety.

Phase 2 adds a protected, server-side, read-only PHP/Domeneshop-compatible mock API layer. It does not introduce database dependency, real-money betting, auto-betting, bookmaker execution, public write endpoints, frontend write tokens, or affiliate/bookmaker funneling.

## Confirmed Phase 1 baseline

Phase 1 remains intact:

- PIP is a separate synchronized technical system.
- FEA remains independently operable.
- PIP integration is disabled by default.
- PIP is fail-soft and optional.
- The probability contract requires `execution_allowed=false` and `compliance_mode=display_only`.
- No database execution is required.

## FEA Phase 5 posture to preserve

Do not alter the existing FEA private `.env` posture:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
FOOTBALL_EDGE_REAL_BETTING_ENABLED=false
FOOTBALL_EDGE_DRY_RUN=true
FOOTBALL_EDGE_AUTO_BETTING_ENABLED=false
```

PIP remains disabled by default:

```env
PIP_INTEGRATION_ENABLED=false
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=
PIP_API_KEY=
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

Controlled Phase 2 server-side integration testing may use:

```env
PIP_INTEGRATION_ENABLED=true
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=https://www.atlas-ai.no
PIP_API_KEY=<SERVER_SIDE_KEY_ONLY>
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

## Phase 2 files added

| File | Purpose |
|---|---|
| `services/pip_api/public/api/v1/pip/health.php` | Protected internal health endpoint. |
| `services/pip_api/public/api/v1/probability/football/fixture.php` | Protected internal mock probability endpoint. |
| `services/pip_api/includes/auth.php` | Server-side API key validation using `X-PIP-API-Key`. |
| `services/pip_api/includes/response_helpers.php` | JSON response, method guard, no-cache, and security headers. |
| `services/pip_api/config/pip_config.example.php` | Server-side config template. |
| `services/pip_api/config/.htaccess` | Denies direct browser access to config directory where supported. |
| `services/pip_api/public/.htaccess` | Optional pretty-route mapping for Apache/Domeneshop if supported. |
| `.env.pip.phase2.example` | Phase 2 environment template. |
| `tools/phase2_endpoint_contract_check.py` | Static endpoint contract checker. |
| `tests/test_phase2_internal_api_static.py` | Phase 2 static unittest coverage. |
| `.github/workflows/pip-phase2-internal-api-tests.yml` | Phase 2 GitHub Actions validation workflow. |

## Endpoint surface

Allowed endpoints only:

```text
GET /api/v1/pip/health
GET /api/v1/probability/football/fixture/{fixture_id}?market=1X2
```

Domeneshop flat-file fallback endpoint:

```text
GET /api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2
```

The API does not support:

- `POST`
- `PUT`
- `PATCH`
- `DELETE`
- real-money betting endpoints
- auto-betting endpoints
- bookmaker execution endpoints
- affiliate/bookmaker funnel endpoints
- frontend token endpoints

## Security behavior

Required request header:

```text
X-PIP-API-Key: <SERVER_SIDE_KEY_ONLY>
```

Rules:

1. The API key must remain server-side only.
2. Do not place the API key in frontend JavaScript.
3. Do not place the API key in static HTML.
4. Do not commit `pip_config.local.php`.
5. Do not expose the key through query strings.
6. Do not use browser-visible configuration.
7. Missing or invalid API key returns HTTP `401 Unauthorized`.
8. If API-key enforcement is enabled but no server-side key is configured, the API returns HTTP `503`.
9. Health responses return no secrets.

## Manual Domeneshop rollout instructions

### 1. Prepare local files

From the repository, use this folder:

```text
services/pip_api/
```

Copy the following subfolders/files to the server:

```text
services/pip_api/public/api/v1/pip/health.php
services/pip_api/public/api/v1/probability/football/fixture.php
services/pip_api/includes/auth.php
services/pip_api/includes/response_helpers.php
services/pip_api/config/pip_config.example.php
services/pip_api/config/.htaccess
services/pip_api/public/.htaccess
```

### 2. Recommended Domeneshop placement

Recommended server-side layout:

```text
/public_html/api/v1/pip/health.php
/public_html/api/v1/probability/football/fixture.php
/pip_api/includes/auth.php
/pip_api/includes/response_helpers.php
/pip_api/config/pip_config.local.php
/pip_api/config/.htaccess
```

This layout keeps `includes` and `config` outside the browser-accessible webroot if Domeneshop allows it.

If the server cannot place `includes` outside webroot, use:

```text
/public_html/pip_api/includes/auth.php
/public_html/pip_api/includes/response_helpers.php
/public_html/pip_api/config/pip_config.local.php
/public_html/pip_api/config/.htaccess
/public_html/api/v1/pip/health.php
/public_html/api/v1/probability/football/fixture.php
```

Then verify that direct browser access to `/pip_api/config/pip_config.local.php` is blocked or returns no sensitive output.

### 3. Create server-side config

On the server:

1. Copy `pip_config.example.php` to `pip_config.local.php`.
2. Replace `CHANGE_ME_SERVER_SIDE_ONLY` with a strong internal key.
3. Confirm `pip_config.local.php` is not committed to Git.
4. Confirm `.gitignore` excludes `services/pip_api/config/pip_config.local.php`.

Recommended `pip_config.local.php` content:

```php
<?php
return [
    'api_key' => 'REPLACE_WITH_STRONG_SERVER_SIDE_KEY',
    'enforce_api_key' => true,
    'platform_version' => '1.0.0',
    'mode' => 'mock',
];
```

### 4. Adjust include paths if deploying outside the repository layout

The committed PHP files assume the repository-style structure:

```text
services/pip_api/public/...
services/pip_api/includes/...
services/pip_api/config/...
```

If deploying to `/public_html/api/...` and `/pip_api/includes/...`, update the two `require_once` lines in each endpoint to point to the final server path.

Example:

```php
require_once $_SERVER['DOCUMENT_ROOT'] . '/../pip_api/includes/response_helpers.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/../pip_api/includes/auth.php';
```

Use this only after confirming the correct Domeneshop server path.

### 5. Browser/Postman/cURL validation

Use cURL with header authentication:

```bash
curl -i -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP/2 200
```

Expected JSON characteristics:

```json
{
  "status": "ok",
  "platform": "atlas_probability_intelligence_platform",
  "mode": "mock",
  "api_surface": "internal_read_only",
  "execution_allowed": false,
  "compliance_mode": "display_only"
}
```

Validate probability endpoint:

```bash
curl -i -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  "https://www.atlas-ai.no/api/v1/probability/football/fixture/982331?market=1X2"
```

If pretty routing is not active, use flat-file fallback:

```bash
curl -i -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  "https://www.atlas-ai.no/api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2"
```

Expected:

- HTTP `200`
- valid JSON
- `execution_allowed=false`
- `compliance_mode=display_only`
- `audit.source=mock`

Validate missing key:

```bash
curl -i https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP/2 401
```

Validate invalid key:

```bash
curl -i -H "X-PIP-API-Key: invalid" https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP/2 401
```

Validate no write methods:

```bash
curl -i -X POST -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP/2 405
```

## GitHub validation commands

Run from repository root:

```bash
python -m unittest discover -s tests
```

Expected:

```text
OK
```

Run the existing probability contract validator:

```bash
python tools/contract_validator.py examples/mock_pip_probability_response.json
```

Expected:

```text
PIP contract validation passed
```

Run the Phase 2 endpoint contract checker:

```bash
python tools/phase2_endpoint_contract_check.py
```

Expected:

```text
PIP Phase 2 endpoint contract check passed
```

## FEA-side optional integration test procedure

1. Confirm FEA remains Phase 5-safe:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
FOOTBALL_EDGE_REAL_BETTING_ENABLED=false
FOOTBALL_EDGE_DRY_RUN=true
FOOTBALL_EDGE_AUTO_BETTING_ENABLED=false
```

2. Temporarily enable PIP server-side integration only:

```env
PIP_INTEGRATION_ENABLED=true
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=https://www.atlas-ai.no
PIP_API_KEY=<SERVER_SIDE_KEY_ONLY>
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

3. Run a controlled FEA recommendation/reporting test.
4. Confirm native FEA behavior still works if PIP is disabled again.
5. Confirm native FEA behavior still works if PIP URL is invalid or unreachable.
6. Confirm no real-money, bookmaker, or auto-betting flag changes occurred.

## Evidence checklist

Capture and archive:

- GitHub Actions screenshot for `PIP Phase 2 Internal API Tests`.
- cURL/Postman output for authorized health endpoint returning HTTP `200`.
- cURL/Postman output for missing key returning HTTP `401`.
- cURL/Postman output for invalid key returning HTTP `401`.
- cURL/Postman output for probability endpoint returning HTTP `200`.
- JSON proof that `execution_allowed=false`.
- JSON proof that `compliance_mode=display_only`.
- cURL proof that `POST` returns HTTP `405`.
- Confirmation that no database SQL was executed.
- Confirmation that FEA `.env` Phase 5 posture remains unchanged.

## Rollback procedure

Use the lowest-risk rollback first:

1. Set `PIP_INTEGRATION_ENABLED=false` in FEA.
2. Clear or remove `PIP_BASE_URL` in FEA.
3. Rename deployed endpoint files on Domeneshop:
   - `health.php` to `health.php.disabled`
   - `fixture.php` to `fixture.php.disabled`
4. Remove or rotate `pip_config.local.php` API key.
5. Remove the optional `.htaccess` routing rule if it causes routing conflicts.
6. Do not alter FEA Phase 5 safety flags.
7. Do not execute SQL as part of rollback.

## Phase 2 completion criteria

Phase 2 is ready when:

1. GitHub Actions passes for `PIP Phase 2 Internal API Tests`.
2. Authorized health endpoint returns HTTP `200` and no secrets.
3. Unauthorized health endpoint returns HTTP `401`.
4. Authorized probability endpoint returns valid JSON.
5. Probability response passes the PIP contract validator.
6. Probability response always includes `execution_allowed=false`.
7. Probability response always includes `compliance_mode=display_only`.
8. POST/PUT/PATCH/DELETE are unavailable or rejected.
9. FEA fallback still works when PIP is disabled.
10. FEA fallback still works when PIP is unreachable.
11. No database dependency is introduced.
12. No FEA Phase 5 production safety variable is changed.
