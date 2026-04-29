#!/usr/bin/env python3
"""Static Phase 2 internal API contract check.

This tool validates that the Phase 2 PHP endpoint files preserve the required
read-only, display-only, fail-soft integration posture before manual upload to
Domeneshop.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "services/pip_api/public/api/v1/pip/health.php": [
        "pip_allow_methods(['GET'])",
        "pip_require_api_key()",
        "'execution_allowed' => false",
        "'compliance_mode' => 'display_only'",
    ],
    "services/pip_api/public/api/v1/probability/football/fixture.php": [
        "pip_allow_methods(['GET'])",
        "pip_require_api_key()",
        "'execution_allowed' => false",
        "'compliance_mode' => 'display_only'",
        "'bookmaker_execution_enabled' => false",
        "'frontend_token_exposed' => false",
        "'write_endpoint_available' => false",
    ],
    "services/pip_api/includes/auth.php": [
        "HTTP_X_PIP_API_KEY",
        "hash_equals",
        "PIP_UNAUTHORIZED",
    ],
}

FORBIDDEN_OPENAPI_METHODS = [r"\bpost:", r"\bput:", r"\bpatch:", r"\bdelete:"]


def main() -> int:
    for relative_path, required_markers in CHECKS.items():
        path = ROOT / relative_path
        if not path.is_file():
            raise SystemExit(f"Missing required Phase 2 file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in text:
                raise SystemExit(f"Missing required marker in {relative_path}: {marker}")

    openapi_text = (ROOT / "api/openapi.pip.v1.patch.yaml").read_text(encoding="utf-8")
    for pattern in FORBIDDEN_OPENAPI_METHODS:
        if re.search(pattern, openapi_text):
            raise SystemExit(f"Forbidden write operation found in OpenAPI patch: {pattern}")

    print("PIP Phase 2 endpoint contract check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
