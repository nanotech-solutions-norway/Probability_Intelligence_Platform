# PIP Database Layer — Phase 1

Phase 1 does not require a database deployment. The active Phase 1 scope is contract validation, fail-soft FEA integration, and API-boundary governance.

If audit persistence is required during controlled internal validation, use Domeneshop phpMyAdmin's built-in SQL console and paste the optional scaffold from:

```text
db/phpmyadmin/optional_phase1_contract_audit_schema.sql
```

Rules:

- Do not run the SQL unless persistence is explicitly needed.
- Confirm the correct Domeneshop database before executing any statement.
- The optional scaffold creates only `pip_` tables.
- Do not alter existing FEA tables.
- Do not create betting execution, bookmaker, or public write functionality.
