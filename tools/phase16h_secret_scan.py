#!/usr/bin/env python3
"""Value-aware JSON secret scanner for preserved Phase 16H evidence.

This scanner deliberately does not treat field names such as
`secret_redaction_active` or `api_key_configured` as leaked secrets. It reports
only credential-like string values. It never prints the suspected secret value.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SENSITIVE_KEY = re.compile(r"(?:api[_-]?key|token|secret|password|authorization|credential)", re.I)
OBVIOUS_SECRET_VALUE = [
    re.compile(r"^Bearer\s+[A-Za-z0-9._~+/-]{20,}$", re.I),
    re.compile(r"^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$"),
    re.compile(r"^(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}$"),
    re.compile(r"^sk-[A-Za-z0-9_-]{20,}$"),
    re.compile(r"^AKIA[0-9A-Z]{16}$"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?:api[_-]?key|token|password|secret)\s*[=:]\s*[A-Za-z0-9._~+/-]{16,}", re.I),
]
SAFE_MARKERS = {
    "", "redacted", "masked", "configured", "not_configured", "missing", "none",
    "true", "false", "active", "inactive", "enabled", "disabled", "server_side_only",
    "<redacted>", "***redacted***", "replace_with_api_key", "replace_if_available",
}


def _safe_marker(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in SAFE_MARKERS:
        return True
    if normalized.startswith("${") and normalized.endswith("}"):
        return True
    if normalized.startswith("env:"):
        return True
    return False


def _credential_like(value: str, sensitive_context: bool) -> bool:
    if _safe_marker(value):
        return False
    if any(pattern.search(value) for pattern in OBVIOUS_SECRET_VALUE):
        return True
    if sensitive_context and len(value.strip()) >= 20:
        compact = value.strip()
        classes = sum(bool(re.search(pattern, compact)) for pattern in (r"[a-z]", r"[A-Z]", r"[0-9]", r"[^A-Za-z0-9\s]"))
        return classes >= 2 and " " not in compact
    return False


def scan_json(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            sensitive = bool(SENSITIVE_KEY.search(str(key)))
            if isinstance(child, str) and _credential_like(child, sensitive):
                hits.append(child_path)
            else:
                hits.extend(scan_json(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(scan_json(child, f"{path}[{index}]"))
    elif isinstance(value, str) and _credential_like(value, False):
        hits.append(path)
    return hits


def scan_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    hits = scan_json(payload)
    return {"file": path.name, "credential_value_hit_count": len(hits), "paths": hits}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path, help="JSON file or directory containing preserved evidence JSON")
    args = parser.parse_args()
    files = [args.target] if args.target.is_file() else sorted(args.target.glob("*.json"))
    results = [scan_file(path) for path in files]
    total = sum(item["credential_value_hit_count"] for item in results)
    print(json.dumps({"scanner": "phase16h_value_aware_v1", "files_scanned": len(files), "credential_value_hit_count": total, "results": results}, indent=2))
    return 2 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
