"""Fail-soft PIP client for Football Edge Agent.

Design intent:
- disabled by default
- short timeout
- no write endpoints
- no execution capability
- never throws into the FEA recommendation path when failsafe mode is enabled
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PipClientResult:
    enabled: bool
    available: bool
    fallback_used: bool
    data: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None
    latency_ms: int | None = None


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class PipClient:
    def __init__(self) -> None:
        self.integration_enabled = _env_bool("PIP_INTEGRATION_ENABLED", False)
        self.required_for_recommendations = _env_bool("PIP_REQUIRED_FOR_RECOMMENDATIONS", False)
        self.failsafe_mode = _env_bool("PIP_FAILSAFE_MODE", True)
        self.use_mock = _env_bool("PIP_USE_MOCK", False)
        self.base_url = os.getenv("PIP_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("PIP_API_KEY", "")
        try:
            self.timeout_seconds = max(1.0, float(os.getenv("PIP_TIMEOUT_SECONDS", "5")))
        except ValueError:
            self.timeout_seconds = 5.0

    def get_fixture_probability(self, fixture_id: int, market: str = "1X2") -> PipClientResult:
        if not self.integration_enabled:
            return PipClientResult(False, False, True, error_code="PIP_DISABLED", error_message="PIP integration is disabled by configuration.")
        if self.use_mock:
            return self._load_mock_response(fixture_id=fixture_id, market=market)
        if not self.base_url:
            return self._fail("PIP_BASE_URL_MISSING", "PIP_BASE_URL is not configured.")

        endpoint = f"{self.base_url}/api/v1/probability/football/fixture/{int(fixture_id)}?market={market}"
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-PIP-API-Key"] = self.api_key

        start = time.perf_counter()
        try:
            request = urllib.request.Request(endpoint, headers=headers, method="GET")
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                latency_ms = int((time.perf_counter() - start) * 1000)
                if response.status != 200:
                    return self._fail("PIP_HTTP_ERROR", f"PIP returned HTTP {response.status}", latency_ms)
                payload = json.loads(response.read().decode("utf-8"))
                if payload.get("execution_allowed") is not False:
                    return self._fail("PIP_CONTRACT_EXECUTION_FLAG", "PIP response violated execution_allowed=false contract.", latency_ms)
                return PipClientResult(True, True, False, data=payload, latency_ms=latency_ms)
        except urllib.error.HTTPError as exc:
            return self._fail("PIP_HTTP_ERROR", f"PIP HTTP error: {exc.code}")
        except urllib.error.URLError as exc:
            return self._fail("PIP_UNREACHABLE", f"PIP unreachable: {exc.reason}")
        except TimeoutError:
            return self._fail("PIP_TIMEOUT", "PIP request timed out.")
        except Exception as exc:
            return self._fail("PIP_CLIENT_EXCEPTION", str(exc))

    def _load_mock_response(self, fixture_id: int, market: str) -> PipClientResult:
        start = time.perf_counter()
        root = Path(__file__).resolve().parents[2]
        mock_path = root / "examples" / "mock_pip_probability_response.json"
        try:
            payload = json.loads(mock_path.read_text(encoding="utf-8"))
            payload["fixture_id"] = int(fixture_id)
            payload["market"] = market
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PipClientResult(True, True, False, payload, latency_ms=latency_ms)
        except Exception as exc:
            return self._fail("PIP_MOCK_LOAD_FAILED", str(exc))

    def _fail(self, code: str, message: str, latency_ms: int | None = None) -> PipClientResult:
        if not self.failsafe_mode and self.required_for_recommendations:
            raise RuntimeError(f"{code}: {message}")
        return PipClientResult(True, False, True, error_code=code, error_message=message, latency_ms=latency_ms)
