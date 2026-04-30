# Atlas PIP Phase 2 Isolated Domeneshop Package — 01:38, 30.04.2026

## Reason for isolated package

The first deployment target under `/api/v1/...` may be intercepted by the existing Atlas API router. A live test returned:

```json
{
  "status": "error",
  "message": "Route not found",
  "path": "/v1/pip/health"
}
```

This indicates that the request reached the existing `/api` application router instead of the uploaded PHP endpoint.

This isolated package avoids that conflict by placing PIP under:

```text
/pip_phase2/api/v1/...
```

## Upload target

Upload the `pip_phase2` folder to:

```text
/public_html/pip_phase2/
```

Final intended layout:

```text
/public_html/pip_phase2/api/v1/pip/health.php
/public_html/pip_phase2/api/v1/probability/football/fixture.php
/public_html/pip_phase2/pip_api/includes/response_helpers.php
/public_html/pip_phase2/pip_api/includes/auth.php
/public_html/pip_phase2/pip_api/config/.htaccess
/public_html/pip_phase2/pip_api/config/pip_config.example.php
/public_html/pip_phase2/pip_api/config/pip_config.local.php
```

## Required config action

Move or copy the existing server-side config file from:

```text
/public_html/pip_api/config/pip_config.local.php
```

to:

```text
/public_html/pip_phase2/pip_api/config/pip_config.local.php
```

Alternatively, copy `pip_config.example.php` to `pip_config.local.php` and insert the same server-side key.

## FEA base URL for isolated namespace

Use this value for controlled FEA Phase 2 integration testing:

```env
PIP_BASE_URL=https://www.atlas-ai.no/pip_phase2
```

The existing FEA client appends:

```text
/api/v1/probability/football/fixture/{fixture_id}?market=1X2
```

so the isolated endpoint remains compatible.

## Validation URLs

Health endpoint:

```text
https://www.atlas-ai.no/pip_phase2/api/v1/pip/health
```

Probability endpoint, pretty route if rewrite is active:

```text
https://www.atlas-ai.no/pip_phase2/api/v1/probability/football/fixture/982331?market=1X2
```

Probability endpoint, flat-file fallback:

```text
https://www.atlas-ai.no/pip_phase2/api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2
```

## Validation commands

Missing key:

```bash
curl -i https://www.atlas-ai.no/pip_phase2/api/v1/pip/health
```

Expected: HTTP `401` after `pip_config.local.php` is configured.

Authorized health:

```bash
curl -i -H "X-PIP-API-Key: SERVER_SIDE_KEY" https://www.atlas-ai.no/pip_phase2/api/v1/pip/health
```

Expected: HTTP `200`.

Authorized probability:

```bash
curl -i -H "X-PIP-API-Key: SERVER_SIDE_KEY" "https://www.atlas-ai.no/pip_phase2/api/v1/probability/football/fixture.php?fixture_id=982331&market=1X2"
```

Expected: HTTP `200` with `execution_allowed=false` and `compliance_mode=display_only`.

POST rejection:

```bash
curl -i -X POST -H "X-PIP-API-Key: SERVER_SIDE_KEY" https://www.atlas-ai.no/pip_phase2/api/v1/pip/health
```

Expected: HTTP `405`.

## Rollback

Delete or rename:

```text
/public_html/pip_phase2/
```

Then keep FEA set to:

```env
PIP_INTEGRATION_ENABLED=false
PIP_BASE_URL=
```

No SQL/database operation is required.
