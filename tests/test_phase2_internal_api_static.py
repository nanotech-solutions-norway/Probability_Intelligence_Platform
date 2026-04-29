import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase2InternalApiStaticTest(unittest.TestCase):
    def test_phase2_php_endpoints_exist(self):
        self.assertTrue((ROOT / "services/pip_api/public/api/v1/pip/health.php").is_file())
        self.assertTrue((ROOT / "services/pip_api/public/api/v1/probability/football/fixture.php").is_file())
        self.assertTrue((ROOT / "services/pip_api/includes/auth.php").is_file())
        self.assertTrue((ROOT / "services/pip_api/includes/response_helpers.php").is_file())
        self.assertTrue((ROOT / "services/pip_api/config/pip_config.example.php").is_file())

    def test_api_key_header_is_required_by_auth_helper(self):
        auth = (ROOT / "services/pip_api/includes/auth.php").read_text(encoding="utf-8")
        self.assertIn("HTTP_X_PIP_API_KEY", auth)
        self.assertIn("hash_equals", auth)
        self.assertIn("PIP_UNAUTHORIZED", auth)
        self.assertNotIn("$_GET['api_key']", auth)
        self.assertNotIn('$_GET["api_key"]', auth)

    def test_probability_endpoint_is_display_only(self):
        endpoint = (ROOT / "services/pip_api/public/api/v1/probability/football/fixture.php").read_text(encoding="utf-8")
        self.assertIn("pip_allow_methods(['GET'])", endpoint)
        self.assertIn("'execution_allowed' => false", endpoint)
        self.assertIn("'compliance_mode' => 'display_only'", endpoint)
        self.assertIn("'bookmaker_execution_enabled' => false", endpoint)
        self.assertIn("'frontend_token_exposed' => false", endpoint)
        self.assertIn("'write_endpoint_available' => false", endpoint)

    def test_no_disallowed_http_methods_in_phase2_api_files(self):
        paths = [
            ROOT / "services/pip_api/public/api/v1/pip/health.php",
            ROOT / "services/pip_api/public/api/v1/probability/football/fixture.php",
            ROOT / "api/openapi.pip.v1.patch.yaml",
        ]
        forbidden_patterns = [
            r"\bPOST\b",
            r"\bPUT\b",
            r"\bPATCH\b",
            r"\bDELETE\b",
            r"\bpost:",
            r"\bput:",
            r"\bpatch:",
            r"\bdelete:",
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                self.assertIsNone(re.search(pattern, text), f"Forbidden write method marker {pattern} found in {path}")

    def test_health_endpoint_returns_no_secret_markers(self):
        health = (ROOT / "services/pip_api/public/api/v1/pip/health.php").read_text(encoding="utf-8")
        forbidden_secret_output = ["api_key' =>", 'api_key" =>', "PIP_API_KEY", "CHANGE_ME_SERVER_SIDE_ONLY"]
        for marker in forbidden_secret_output:
            self.assertNotIn(marker, health)


if __name__ == "__main__":
    unittest.main()
