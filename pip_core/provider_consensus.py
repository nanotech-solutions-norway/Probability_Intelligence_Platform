"""R0 provider comparability and shadow-consensus primitives.

This module is deliberately read-only and provider-agnostic. It normalizes
complete market snapshots into no-vig probabilities, requires genuinely
comparable observations from at least two providers, and fails soft when the
minimum evidence gate is not met. It does not release recommendations or
create execution actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import median, pstdev
from typing import Iterable

MARKET_SELECTIONS: dict[str, tuple[str, ...]] = {
    "1X2": ("home", "draw", "away"),
    "OVER_UNDER_2_5": ("over_2_5", "under_2_5"),
    "BTTS": ("yes", "no"),
}


@dataclass(frozen=True)
class OddsObservation:
    provider: str
    source: str
    canonical_event_key: str
    market: str
    selection: str
    decimal_odds: float
    observed_at: datetime
    line: str | None = None
    provider_event_id: str | None = None
    provider_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.source.strip():
            raise ValueError("provider and source are required")
        if not self.canonical_event_key.strip():
            raise ValueError("canonical_event_key is required")
        if self.market not in MARKET_SELECTIONS:
            raise ValueError(f"unsupported market: {self.market}")
        if self.selection not in MARKET_SELECTIONS[self.market]:
            raise ValueError(f"invalid selection {self.selection!r} for market {self.market}")
        if self.decimal_odds <= 1.0:
            raise ValueError("decimal_odds must be greater than 1.0")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.provider_timestamp is not None and self.provider_timestamp.tzinfo is None:
            raise ValueError("provider_timestamp must be timezone-aware")


@dataclass(frozen=True)
class ConsensusResult:
    status: str
    canonical_event_key: str
    market: str
    line: str | None
    probabilities: dict[str, float]
    provider_count: int
    source_count: int
    freshness_seconds: int | None
    consensus_dispersion: float | None
    evidence_observation_count: int
    reason: str | None = None


def _as_utc(value: datetime) -> datetime:
    return value.astimezone(timezone.utc)


def _snapshot_key(obs: OddsObservation) -> tuple[str, str]:
    return (obs.provider.strip().lower(), obs.source.strip().lower())


def _deduplicate_latest(observations: Iterable[OddsObservation]) -> list[OddsObservation]:
    latest: dict[tuple[str, str, str], OddsObservation] = {}
    for obs in observations:
        key = (*_snapshot_key(obs), obs.selection)
        previous = latest.get(key)
        if previous is None or _as_utc(obs.observed_at) > _as_utc(previous.observed_at):
            latest[key] = obs
    return list(latest.values())


def _complete_no_vig_snapshots(
    observations: Iterable[OddsObservation],
    *,
    canonical_event_key: str,
    market: str,
    line: str | None,
) -> dict[tuple[str, str], dict[str, tuple[float, datetime]]]:
    required = set(MARKET_SELECTIONS[market])
    candidates = [
        obs
        for obs in observations
        if obs.canonical_event_key == canonical_event_key
        and obs.market == market
        and obs.line == line
    ]
    candidates = _deduplicate_latest(candidates)

    grouped: dict[tuple[str, str], dict[str, OddsObservation]] = {}
    for obs in candidates:
        grouped.setdefault(_snapshot_key(obs), {})[obs.selection] = obs

    complete: dict[tuple[str, str], dict[str, tuple[float, datetime]]] = {}
    for key, selection_map in grouped.items():
        if set(selection_map) != required:
            continue
        implied = {selection: 1.0 / selection_map[selection].decimal_odds for selection in required}
        total = sum(implied.values())
        if total <= 0:
            continue
        complete[key] = {
            selection: (implied[selection] / total, selection_map[selection].observed_at)
            for selection in required
        }
    return complete


def build_comparable_consensus(
    observations: Iterable[OddsObservation],
    *,
    canonical_event_key: str,
    market: str,
    line: str | None = None,
    as_of: datetime | None = None,
    max_snapshot_skew_seconds: int = 180,
    max_age_seconds: int = 900,
    min_provider_count: int = 2,
) -> ConsensusResult:
    """Build deterministic median no-vig consensus or fail soft.

    A complete snapshot requires all canonical selections for the market from
    one provider/source pair. Only snapshots sufficiently close in observation
    time and within the freshness gate are eligible. At least two distinct
    providers are required for `comparable_consensus`.
    """
    if market not in MARKET_SELECTIONS:
        raise ValueError(f"unsupported market: {market}")
    if max_snapshot_skew_seconds < 0 or max_age_seconds < 0:
        raise ValueError("freshness/skew limits cannot be negative")
    if min_provider_count < 2:
        raise ValueError("min_provider_count must be at least 2")
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware")

    snapshots = _complete_no_vig_snapshots(
        observations,
        canonical_event_key=canonical_event_key,
        market=market,
        line=line,
    )
    if not snapshots:
        return ConsensusResult(
            "insufficient_consensus", canonical_event_key, market, line, {}, 0, 0,
            None, None, 0, "no_complete_market_snapshots",
        )

    snapshot_times: dict[tuple[str, str], datetime] = {
        key: max(_as_utc(value[1]) for value in selection_map.values())
        for key, selection_map in snapshots.items()
    }
    freshest = max(snapshot_times.values())
    eligible: dict[tuple[str, str], dict[str, tuple[float, datetime]]] = {}
    for key, snapshot in snapshots.items():
        observed = snapshot_times[key]
        skew = (freshest - observed).total_seconds()
        age = (_as_utc(as_of) - observed).total_seconds()
        if skew <= max_snapshot_skew_seconds and 0 <= age <= max_age_seconds:
            eligible[key] = snapshot

    providers = {key[0] for key in eligible}
    source_count = len(eligible)
    observation_count = source_count * len(MARKET_SELECTIONS[market])
    if len(providers) < min_provider_count:
        status = "market_only" if source_count else "insufficient_consensus"
        reason = "fewer_than_required_comparable_providers" if source_count else "no_fresh_comparable_snapshots"
        freshness = None
        if source_count:
            freshness = int(max(0, (_as_utc(as_of) - max(snapshot_times[key] for key in eligible)).total_seconds()))
        return ConsensusResult(
            status, canonical_event_key, market, line, {}, len(providers), source_count,
            freshness, None, observation_count, reason,
        )

    raw_consensus: dict[str, float] = {}
    dispersions: list[float] = []
    for selection in MARKET_SELECTIONS[market]:
        values = [snapshot[selection][0] for snapshot in eligible.values()]
        raw_consensus[selection] = median(values)
        dispersions.append(pstdev(values) if len(values) > 1 else 0.0)

    total = sum(raw_consensus.values())
    probabilities = {selection: value / total for selection, value in raw_consensus.items()}
    freshest_eligible = max(snapshot_times[key] for key in eligible)
    freshness = int(max(0, (_as_utc(as_of) - freshest_eligible).total_seconds()))
    return ConsensusResult(
        "comparable_consensus",
        canonical_event_key,
        market,
        line,
        probabilities,
        len(providers),
        source_count,
        freshness,
        sum(dispersions) / len(dispersions),
        observation_count,
        None,
    )
