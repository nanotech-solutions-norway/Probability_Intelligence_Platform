"""R0-only canonicalization primitives for PIP reconciliation."""

from .provider_consensus import ConsensusResult, OddsObservation, build_comparable_consensus

__all__ = ["ConsensusResult", "OddsObservation", "build_comparable_consensus"]
