"""Build FEA/PIP v2 read-only shadow payloads from R0 consensus results."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .provider_consensus import ConsensusResult, MARKET_SELECTIONS

CONTRACT_VERSION = "2.0.0"
PLATFORM = "atlas_probability_intelligence_platform"


def _iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("generated_at must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _fair_odds(probability: float) -> float | None:
    return None if probability <= 0 else 1.0 / probability


def build_shadow_payload(
    consensus: ConsensusResult,
    *,
    fixture_id: int,
    model_version: str,
    calibration_version: str,
    evidence_id: str,
    data_quality_score: float,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Return a v2 contract-shaped reporting object with hard safety constants."""
    if fixture_id < 1:
        raise ValueError("fixture_id must be positive")
    if consensus.market not in MARKET_SELECTIONS:
        raise ValueError(f"unsupported market: {consensus.market}")
    if not model_version.strip() or not calibration_version.strip() or not evidence_id.strip():
        raise ValueError("model_version, calibration_version, and evidence_id are required")
    if not 0 <= data_quality_score <= 1:
        raise ValueError("data_quality_score must be in [0, 1]")
    generated_at = generated_at or datetime.now(timezone.utc)

    is_consensus = consensus.status == "comparable_consensus"
    if is_consensus:
        expected = set(MARKET_SELECTIONS[consensus.market])
        if set(consensus.probabilities) != expected:
            raise ValueError("comparable consensus must contain the complete canonical market")
        if consensus.provider_count < 2:
            raise ValueError("comparable consensus requires at least two providers")
        probabilities = [
            {
                "selection": selection,
                "probability": consensus.probabilities[selection],
                "fair_odds": _fair_odds(consensus.probabilities[selection]),
            }
            for selection in MARKET_SELECTIONS[consensus.market]
        ]
        status = "ok"
        consensus_status = "comparable_consensus"
    else:
        probabilities = []
        status = "insufficient_data"
        consensus_status = (
            consensus.status
            if consensus.status in {"market_only", "insufficient_consensus"}
            else "insufficient_consensus"
        )

    return {
        "status": status,
        "contract_version": CONTRACT_VERSION,
        "platform": PLATFORM,
        "fixture_id": fixture_id,
        "sport": "football",
        "market": consensus.market,
        "generated_at": _iso_utc(generated_at),
        "probabilities": probabilities,
        "data_quality": {
            "score": data_quality_score,
            "freshness_seconds": consensus.freshness_seconds or 0,
            "provider_count": consensus.provider_count,
            "source_count": consensus.source_count,
            "consensus_status": consensus_status,
            "consensus_dispersion": consensus.consensus_dispersion,
        },
        "safety": {
            "manual_review_required": True,
            "execution_allowed": False,
            "recommendation_release_allowed": False,
            "bookmaker_execution_enabled": False,
        },
        "audit": {
            "model_version": model_version,
            "calibration_version": calibration_version,
            "source": "shadow",
            "evidence_id": evidence_id,
        },
    }
