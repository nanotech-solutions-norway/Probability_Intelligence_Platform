import unittest

from tools.r0_shadow_gate_runner import run_gate


class R0ShadowGateRunnerTests(unittest.TestCase):
    def test_sanitized_two_provider_evidence_produces_comparable_v2_payload(self):
        document = {
            "fixture_id": 123,
            "canonical_event_key": "competition:home:away:2026-08-08T20:00Z",
            "market": "1X2",
            "model_version": "r0-shadow-consensus",
            "calibration_version": "r0-none",
            "evidence_id": "test-evidence",
            "data_quality_score": 0.9,
            "as_of": "2026-08-08T20:00:00Z",
            "observations": [
                {"provider": "a", "source": "book_a", "selection": "home", "decimal_odds": 2.0, "observed_at": "2026-08-08T19:59:30Z"},
                {"provider": "a", "source": "book_a", "selection": "draw", "decimal_odds": 3.5, "observed_at": "2026-08-08T19:59:30Z"},
                {"provider": "a", "source": "book_a", "selection": "away", "decimal_odds": 4.0, "observed_at": "2026-08-08T19:59:30Z"},
                {"provider": "b", "source": "book_b", "selection": "home", "decimal_odds": 2.1, "observed_at": "2026-08-08T19:59:20Z"},
                {"provider": "b", "source": "book_b", "selection": "draw", "decimal_odds": 3.4, "observed_at": "2026-08-08T19:59:20Z"},
                {"provider": "b", "source": "book_b", "selection": "away", "decimal_odds": 3.9, "observed_at": "2026-08-08T19:59:20Z"},
            ],
        }
        payload = run_gate(document)
        self.assertEqual(payload["contract_version"], "2.0.0")
        self.assertEqual(payload["data_quality"]["consensus_status"], "comparable_consensus")
        self.assertEqual(payload["data_quality"]["provider_count"], 2)
        self.assertEqual(len(payload["probabilities"]), 3)
        self.assertFalse(payload["safety"]["execution_allowed"])
        self.assertFalse(payload["safety"]["recommendation_release_allowed"])


if __name__ == "__main__":
    unittest.main()
