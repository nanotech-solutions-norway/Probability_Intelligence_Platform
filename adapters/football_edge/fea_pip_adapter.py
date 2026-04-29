"""FEA-facing PIP enrichment adapter.

This module deliberately treats PIP output as enrichment metadata only. It does
not place bets, alter environment locks or create provider execution actions.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .pip_client import PipClient, PipClientResult


def enrich_recommendation_with_pip(
    recommendation: dict[str, Any],
    pip_result: PipClientResult | None = None,
    client: PipClient | None = None,
) -> dict[str, Any]:
    """Return an FEA recommendation enriched with PIP data when safely available.

    The original recommendation object is not mutated. Native FEA behavior is
    preserved whenever PIP is disabled, unavailable, slow or malformed.
    """
    enriched = deepcopy(recommendation)
    fixture_id = int(enriched.get("fixture_id", 0) or 0)
    market = str(enriched.get("market", "1X2"))

    if pip_result is None:
        client = client or PipClient()
        pip_result = client.get_fixture_probability(fixture_id=fixture_id, market=market)

    enriched["pip_enrichment"] = {
        "enabled": pip_result.enabled,
        "available": pip_result.available,
        "fallback_used": pip_result.fallback_used,
        "error_code": pip_result.error_code,
        "latency_ms": pip_result.latency_ms,
    }

    if pip_result.available and pip_result.data:
        enriched["pip_probability_intelligence"] = {
            "model_version": pip_result.data.get("model_version"),
            "data_timestamp": pip_result.data.get("data_timestamp"),
            "selection_probabilities": pip_result.data.get("selection_probabilities", []),
            "compliance_mode": pip_result.data.get("compliance_mode"),
            "execution_allowed": pip_result.data.get("execution_allowed"),
            "audit": pip_result.data.get("audit", {}),
        }
    else:
        enriched["pip_probability_intelligence"] = None

    # Hard safety invariant. PIP cannot override FEA's execution posture.
    enriched["auto_betting_enabled"] = False
    enriched["real_money_betting_enabled"] = False
    enriched["bookmaker_execution_enabled"] = False
    return enriched
