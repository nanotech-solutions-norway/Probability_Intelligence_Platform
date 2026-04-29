# Atlas PIP Phase 1 Rollout Procedure — 14:57, 29.04.2026

## Objective

Deploy the **Foundation and Contract Layer** for Atlas Probability Intelligence Platform v1.0 while preserving the current Football Edge Agent Phase 5 operating posture.

Phase 1 establishes repository structure, API contracts, fail-soft adapter behavior, mock responses, OpenAPI read-only endpoint definitions, and validation tests. It does not introduce live model training, real-money betting, auto-betting, bookmaker execution, public write endpoints, frontend write tokens, or affiliate funneling.

## FEA posture to preserve

Do not change the current FEA private environment variables:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
FOOTBALL_EDGE_REAL_BETTING_ENABLED=false
FOOTBALL_EDGE_DRY_RUN=true
FOOTBALL_EDGE_AUTO_BETTING_ENABLED=false
```

Add PIP variables separately and keep them disabled by default:

```env
PIP_INTEGRATION_ENABLED=false
PIP_REQUIRED_FOR_RECOMMENDATIONS=false
PIP_BASE_URL=
PIP_API_KEY=
PIP_TIMEOUT_SECONDS=5
PIP_FAILSAFE_MODE=true
PIP_USE_MOCK=false
```

## GitHub rollout

Target repository:

```text
nanotech-solutions-norway/Probability_Intelligence_Platform
```

Run validation after checkout:

```bash
python -m unittest discover -s tests
```

Expected outcome:

```text
Ran 5 tests
OK
```

GitHub Actions also runs this same standard-library test suite on push and pull request events.

## Domeneshop/phpMyAdmin database policy

Phase 1 does **not** strictly require database deployment. The contract layer, mock response, adapter, and tests run without a database.

Only if controlled internal validation requires persistent audit records, use Domeneshop phpMyAdmin's built-in SQL console:

1. Log in to Domeneshop phpMyAdmin.
2. Confirm the correct Atlas/FEA database.
3. Open the built-in SQL console.
4. Paste the content of `db/phpmyadmin/optional_phase1_contract_audit_schema.sql`.
5. Execute only after confirming the SQL creates `pip_` tables only.
6. Confirm no existing FEA table was altered.

Do not import a migration file as a mandatory deployment step. Do not run any SQL if Phase 1 only needs contract validation and GitHub-side tests.

## FEA adapter implementation

Python/FastAPI-style deployments:

```python
from adapters.football_edge.fea_pip_adapter import enrich_recommendation_with_pip

enriched = enrich_recommendation_with_pip(native_fea_recommendation)
```

PHP/Domeneshop-compatible deployments may use `adapters/football_edge/pip_client.php` when that runtime path is required.

Store `PIP_API_KEY` server-side only. Never expose it in frontend code.

## OpenAPI patch

The read-only OpenAPI definitions are stored in:

```text
api/openapi.pip.v1.patch.yaml
```

Phase 1 endpoint definitions:

```text
GET /api/v1/pip/health
GET /api/v1/probability/football/fixture/{fixture_id}?market=1X2
```

There are no POST, PUT, PATCH, or DELETE operations in Phase 1.

## Validation checklist

| Control | Required result |
|---|---|
| FEA Phase 5 env posture unchanged | Pass |
| PIP disabled by default | Pass |
| `PIP_REQUIRED_FOR_RECOMMENDATIONS=false` | Pass |
| `execution_allowed=false` in mock response | Pass |
| Contract test passes | Pass |
| FEA fallback test passes | Pass |
| SQL not required for Phase 1 | Pass |
| Optional SQL creates only `pip_` tables if used | Pass |
| No public write endpoint | Pass |
| No bookmaker execution path | Pass |
| No frontend write token | Pass |
| No affiliate/bookmaker funnel | Pass |

## Phase 1 completion criteria

Phase 1 is complete when:

1. GitHub repository scaffold is committed.
2. Mock response validates against the PIP contract validator.
3. FEA fallback test passes with PIP disabled.
4. FEA fallback test passes with PIP enabled but unreachable.
5. No FEA Phase 5 safety flags have been changed.
6. OpenAPI patch is stored but no public write surface is exposed.
7. Optional database SQL is left unexecuted unless audit persistence is explicitly required.
