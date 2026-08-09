# PIP Subdomain Web-Root Hardening

## Purpose

This package disables Apache directory indexing for the dedicated `pip.atlas-ai.no` document root. It does not deploy application code, credentials, provider configuration, or execution capability.

## Target

Copy `.htaccess` to the verified document root serving `https://pip.atlas-ai.no/`.

Do not infer the document-root path from a Drive filename or from an unverified backup. Confirm the active virtual-host document root through hosting metadata before upload.

## Pre-deployment checks

1. Confirm the current document-root path without opening or copying credential-bearing files.
2. Preserve a recoverable copy of the current root `.htaccess`, if present.
3. Confirm Apache permits `Options -Indexes` in `.htaccess` for this virtual host.
4. Keep `health.php` and `fixture.php` protected by their existing server-side authentication.

## Expected unauthenticated behavior

| Request | Expected result |
|---|---|
| `GET /` | HTTP 403, 404, or an approved non-listing landing response; never an auto-generated file index |
| `GET /health.php` | HTTP 401 |
| `GET /fixture.php` | HTTP 401 |
| `GET /does-not-exist` | HTTP 404 |

## Validation

Verify the four unauthenticated requests above and archive status codes, response headers, timestamp, deployed Git SHA, and artifact SHA-256. Do not capture or archive authentication headers or credential values.

## Rollback

Restore the preserved prior `.htaccess` only if this rule causes an unexpected routing failure. A rollback must not re-enable directory indexing; use a hosting-level `Options -Indexes` equivalent instead.

## Safety boundary

This package does not authorize deployment by itself. Recommendation release, execution, bookmaker execution, real-money betting automation, and public write capability remain disabled.
