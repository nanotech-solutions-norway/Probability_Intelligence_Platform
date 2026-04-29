#!/usr/bin/env python3
"""Self-contained PIP response contract validator.

No third-party package is required. The validator intentionally checks the
runtime invariants that matter to FEA fail-soft integration:
- display-only compliance
- execution disabled
- required fields present
- probability bounds
- probability mass integrity
- recommendation enum integrity
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

VALID_RECOMMENDATIONS = {"BET", "WATCHLIST", "NO_BET"}
VALID_SELECTIONS = {"home", "draw", "away", "over", "under", "yes", "no"}
VALID_MARKETS = {"1X2", "OVER_UNDER", "BTTS", "ASIAN_HANDICAP"}


class PipContractError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PipContractError(message)


def validate_pip_response(payload: dict[str, Any]) -> bool:
    required_top = [
        "status", "platform", "platform_version", "fixture_id", "sport", "market",
        "model_version", "data_timestamp", "selection_probabilities",
        "compliance_mode", "execution_allowed", "audit",
    ]
    for key in required_top:
        _require(key in payload, f"Missing top-level field: {key}")

    _require(payload["status"] in {"ok", "degraded"}, "status must be ok or degraded")
    _require(payload["platform"] == "atlas_probability_intelligence_platform", "invalid platform")
    _require(isinstance(payload["fixture_id"], int) and payload["fixture_id"] > 0, "fixture_id must be positive integer")
    _require(payload["sport"] == "football", "Phase 1 contract supports football only")
    _require(payload["market"] in VALID_MARKETS, "invalid market")
    _require(payload["compliance_mode"] == "display_only", "compliance_mode must be display_only")
    _require(payload["execution_allowed"] is False, "execution_allowed must be false")

    selections = payload["selection_probabilities"]
    _require(isinstance(selections, list) and len(selections) >= 2, "selection_probabilities must contain at least two selections")

    probability_sum = 0.0
    seen = set()
    for idx, item in enumerate(selections):
        for key in [
            "selection", "model_probability", "bookmaker_no_vig_probability", "fair_odds",
            "best_available_odds", "expected_value", "confidence_score", "recommendation",
        ]:
            _require(key in item, f"Missing selection field at index {idx}: {key}")

        selection = item["selection"]
        _require(selection in VALID_SELECTIONS, f"invalid selection: {selection}")
        _require(selection not in seen, f"duplicate selection: {selection}")
        seen.add(selection)

        model_probability = float(item["model_probability"])
        bookmaker_probability = float(item["bookmaker_no_vig_probability"])
        fair_odds = float(item["fair_odds"])
        best_available_odds = float(item["best_available_odds"])
        expected_value = float(item["expected_value"])
        confidence_score = float(item["confidence_score"])

        _require(0.0 <= model_probability <= 1.0, "model_probability out of range")
        _require(0.0 <= bookmaker_probability <= 1.0, "bookmaker_no_vig_probability out of range")
        _require(fair_odds > 1.0, "fair_odds must be greater than 1.0")
        _require(best_available_odds > 1.0, "best_available_odds must be greater than 1.0")
        _require(-1.0 <= expected_value <= 10.0, "expected_value outside controlled contract range")
        _require(0.0 <= confidence_score <= 1.0, "confidence_score out of range")
        _require(item["recommendation"] in VALID_RECOMMENDATIONS, "invalid recommendation")

        implied_ev = (best_available_odds * model_probability) - 1.0
        _require(abs(implied_ev - expected_value) <= 0.01, "expected_value inconsistent with odds/probability")
        probability_sum += model_probability

    if payload["market"] == "1X2":
        _require({"home", "draw", "away"}.issubset(seen), "1X2 market requires home/draw/away selections")
        _require(abs(probability_sum - 1.0) <= 0.01, "1X2 model probabilities must sum approximately to 1.0")

    audit = payload["audit"]
    for key in ["calibration_version", "feature_version", "recommendation_policy_version", "source"]:
        _require(key in audit and str(audit[key]).strip(), f"audit field missing or empty: {key}")
    _require(audit["source"] in {"mock", "live", "backtest", "candidate"}, "invalid audit source")
    return True


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python tools/contract_validator.py <response.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_pip_response(payload)
    print("PIP contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
