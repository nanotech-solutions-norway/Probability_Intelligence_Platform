import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.football_edge.pip_client import PipClient
from adapters.football_edge.fea_pip_adapter import enrich_recommendation_with_pip


BASE_ENV = {
    "FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED": "true",
    "FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED": "false",
    "FOOTBALL_EDGE_REAL_BETTING_ENABLED": "false",
    "FOOTBALL_EDGE_DRY_RUN": "true",
    "FOOTBALL_EDGE_AUTO_BETTING_ENABLED": "false",
}


class FeaFallbackTest(unittest.TestCase):
    def test_pip_disabled_returns_fallback_without_error(self):
        env = {**BASE_ENV, "PIP_INTEGRATION_ENABLED": "false"}
        with patch.dict(os.environ, env, clear=True):
            result = PipClient().get_fixture_probability(982331, "1X2")
            self.assertFalse(result.enabled)
            self.assertFalse(result.available)
            self.assertTrue(result.fallback_used)
            self.assertEqual(result.error_code, "PIP_DISABLED")

    def test_pip_unreachable_returns_fallback_without_network_dependency(self):
        env = {
            **BASE_ENV,
            "PIP_INTEGRATION_ENABLED": "true",
            "PIP_FAILSAFE_MODE": "true",
            "PIP_BASE_URL": "https://pip.internal.invalid",
            "PIP_TIMEOUT_SECONDS": "1",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch(
                "adapters.football_edge.pip_client.urllib.request.urlopen",
                side_effect=urllib.error.URLError("simulated unreachable PIP endpoint"),
            ):
                result = PipClient().get_fixture_probability(982331, "1X2")
                self.assertTrue(result.enabled)
                self.assertFalse(result.available)
                self.assertTrue(result.fallback_used)
                self.assertIn(result.error_code, {"PIP_UNREACHABLE", "PIP_CLIENT_EXCEPTION", "PIP_HTTP_ERROR"})

    def test_mock_enrichment_keeps_execution_flags_false(self):
        env = {**BASE_ENV, "PIP_INTEGRATION_ENABLED": "true", "PIP_USE_MOCK": "true"}
        native = {"fixture_id": 982331, "market": "1X2", "recommendation": "NO_BET"}
        with patch.dict(os.environ, env, clear=True):
            enriched = enrich_recommendation_with_pip(native)
            self.assertTrue(enriched["pip_enrichment"]["available"])
            self.assertFalse(enriched["auto_betting_enabled"])
            self.assertFalse(enriched["real_money_betting_enabled"])
            self.assertFalse(enriched["bookmaker_execution_enabled"])
            self.assertEqual(native["recommendation"], "NO_BET")


if __name__ == "__main__":
    unittest.main()
