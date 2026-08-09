import unittest
from datetime import datetime, timezone

from pip_core.provider_consensus import ConsensusResult
from pip_core.shadow_payload import build_shadow_payload


NOW = datetime(2026, 8, 8, 20, 0, tzinfo=timezone.utc)


class ShadowPayloadTests(unittest.TestCase):
    def test_comparable_consensus_builds_probability_payload(self):
        consensus = ConsensusResult(
            status="comparable_consensus",
            canonical_event_key="event-1",
            market="1X2",
            line=None,
            probabilities={"home": 0.50, "draw": 0.25, "away": 0.25},
            provider_count=2,
            source_count=2,
            freshness_seconds=20,
            consensus_dispersion=0.01,
            evidence_observation_count=6,
        )
        payload = build_shadow_payload(
            consensus,
            fixture_id=123,
            model_version="r0-model",
            calibration_version="r0-cal",
            evidence_id="r0-evidence",
            data_quality_score=0.9,
            generated_at=NOW,
        )
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["contract_version"], "2.0.0")
        self.assertEqual(payload["data_quality"]["consensus_status"], "comparable_consensus")
        self.assertEqual(len(payload["probabilities"]), 3)
        self.assertFalse(payload["safety"]["execution_allowed"])
        self.assertFalse(payload["safety"]["recommendation_release_allowed"])
        self.assertFalse(payload["safety"]["bookmaker_execution_enabled"])

    def test_market_only_builds_empty_fail_soft_payload(self):
        consensus = ConsensusResult(
            status="market_only",
            canonical_event_key="event-1",
            market="1X2",
            line=None,
            probabilities={},
            provider_count=1,
            source_count=1,
            freshness_seconds=20,
            consensus_dispersion=None,
            evidence_observation_count=3,
            reason="fewer_than_required_comparable_providers",
        )
        payload = build_shadow_payload(
            consensus,
            fixture_id=123,
            model_version="r0-model",
            calibration_version="r0-cal",
            evidence_id="r0-evidence",
            data_quality_score=0.5,
            generated_at=NOW,
        )
        self.assertEqual(payload["status"], "insufficient_data")
        self.assertEqual(payload["probabilities"], [])
        self.assertEqual(payload["data_quality"]["consensus_status"], "market_only")
        self.assertTrue(payload["safety"]["manual_review_required"])

    def test_invalid_comparable_consensus_is_rejected(self):
        consensus = ConsensusResult(
            status="comparable_consensus",
            canonical_event_key="event-1",
            market="BTTS",
            line=None,
            probabilities={"yes": 0.55},
            provider_count=2,
            source_count=2,
            freshness_seconds=10,
            consensus_dispersion=0.02,
            evidence_observation_count=4,
        )
        with self.assertRaises(ValueError):
            build_shadow_payload(
                consensus,
                fixture_id=123,
                model_version="r0-model",
                calibration_version="r0-cal",
                evidence_id="r0-evidence",
                data_quality_score=0.8,
                generated_at=NOW,
            )

    def test_naive_generated_at_is_rejected(self):
        consensus = ConsensusResult(
            status="insufficient_consensus",
            canonical_event_key="event-1",
            market="BTTS",
            line=None,
            probabilities={},
            provider_count=0,
            source_count=0,
            freshness_seconds=None,
            consensus_dispersion=None,
            evidence_observation_count=0,
        )
        with self.assertRaises(ValueError):
            build_shadow_payload(
                consensus,
                fixture_id=123,
                model_version="r0-model",
                calibration_version="r0-cal",
                evidence_id="r0-evidence",
                data_quality_score=0.0,
                generated_at=datetime(2026, 8, 8, 20, 0),
            )


if __name__ == "__main__":
    unittest.main()
