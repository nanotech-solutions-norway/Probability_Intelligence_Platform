"""R0-only canonicalization primitives for PIP reconciliation."""

from .provider_consensus import ConsensusResult, OddsObservation, build_comparable_consensus
from .fixture_registry import FixtureRecord, FixtureRegistry, ProviderFixtureIdentity

__all__ = [
    "ConsensusResult",
    "FixtureRecord",
    "FixtureRegistry",
    "OddsObservation",
    "ProviderFixtureIdentity",
    "build_comparable_consensus",
]
