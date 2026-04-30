# Atlas PIP Phase 2 Domeneshop-Ready Upload Package — 01:18, 30.04.2026

## Purpose

This folder contains a **Domeneshop-ready upload package** for PIP Phase 2 Internal Mock API deployment.

It is structured to be copied directly into the Domeneshop webroot layout without requiring the repository development paths under `services/pip_api/`.

## Upload target

Upload the contents of this folder to the website root for `atlas-ai.no`, normally:

```text
/public_html/
```

After upload, the intended structure is:

```text
/public_html/.htaccess
/public_html/api/v1/pip/health.php
/public_html/api/v1/probability/football/fixture.php
/public_html/pip_api/includes/response_helpers.php
/public_html/pip_api/includes/auth.php
/public_html/pip_api/config/.htaccess
/public_html/pip_api/config/pip_config.example.php
```

## Required manual server-side step

After upload, create:

```text
/public_html/pip_api/config/pip_config.local.php
```

by copying:

```text
/public_html/pip_api/config/pip_config.example.php
```

Then replace:

```text
CHANGE_ME_SERVER_SIDE_ONLY
```

with a strong internal API key.

Recommended file content:

```php
<?php
return [
    'api_key' => 'REPLACE_WITH_STRONG_SERVER_SIDE_KEY',
    'enforce_api_key' => true,
    'platform_version' => '1.0.0',
    'mode' => 'mock',
];
```

## Security requirement

The API key is server-side only.

Do not place the key in:

- frontend JavaScript
- static HTML
- browser-visible configuration
- public repository files
- URL query strings
- GitHub Actions secrets unless a future CI deployment requires it

## Endpoints

Allowed endpoints:

```text
GET /api/v1/pip/health
GET /api/v1/probability/football/fixture/982331?market=1X2
```

Flat-file fallback if rewrite routing is unavailable:

```text
GET /api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2
```

Disallowed methods:

```text
POST
PUT
PATCH
DELETE
```

The endpoint PHP guards reject non-GET methods with HTTP `405`.

## Validation commands

Replace `REPLACE_WITH_SERVER_SIDE_KEY` with the server-side key from `pip_config.local.php`.

### Authorized health check

```bash
curl -i -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP 200
```

Required JSON fields:

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

### Authorized probability check

```bash
curl -i -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  "https://www.atlas-ai.no/api/v1/probability/football/fixture/982331?market=1X2"
```

If pretty routing fails, use:

```bash
curl -i -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  "https://www.atlas-ai.no/api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2"
```

Expected:

```text
HTTP 200
```

Required JSON fields:

```json
{
  "execution_allowed": false,
  "compliance_mode": "display_only"
}
```

### Missing API key check

```bash
curl -i https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP 401
```

### Invalid API key check

```bash
curl -i -H "X-PIP-API-Key: invalid" \
  https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP 401
```

### Write-method rejection check

```bash
curl -i -X POST -H "X-PIP-API-Key: REPLACE_WITH_SERVER_SIDE_KEY" \
  https://www.atlas-ai.no/api/v1/pip/health
```

Expected:

```text
HTTP 405
```

## Rollback

Lowest-risk rollback:

1. Set FEA `PIP_INTEGRATION_ENABLED=false`.
2. Clear FEA `PIP_BASE_URL=`.
3. Rename `/public_html/api/v1/pip/health.php` to `health.php.disabled`.
4. Rename `/public_html/api/v1/probability/football/fixture.php` to `fixture.php.disabled`.
5. Remove or rotate `/public_html/pip_api/config/pip_config.local.php`.
6. Remove `/public_html/.htaccess` only if it creates routing conflicts.

Do not alter FEA Phase 5 safety flags.

Do not execute database SQL.

## Phase 2 operating constraints

- PIP remains optional.
- PIP remains fail-soft.
- PIP remains server-side only.
- PIP remains disabled by default in FEA.
- No real-money betting is introduced.
- No auto-betting is introduced.
- No bookmaker execution is introduced.
- No public write endpoint is introduced.
- No frontend token is introduced.
- No database dependency is introduced.
