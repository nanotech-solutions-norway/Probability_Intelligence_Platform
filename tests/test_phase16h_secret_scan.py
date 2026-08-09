import unittest

from tools.phase16h_secret_scan import scan_json


class Phase16HSecretScanTests(unittest.TestCase):
    def test_safe_metadata_names_do_not_trigger(self):
        payload = {
            "secret_redaction_active": True,
            "api_key_configured": True,
            "console_token_config_available": True,
            "password_hash_status": "configured",
            "auth_model": "auth_v3_local_php_fallback_or_env",
        }
        self.assertEqual(scan_json(payload), [])

    def test_real_sensitive_value_is_flagged_without_value_echo(self):
        payload = {"api_key": "ExampleSecretValue_1234567890"}
        self.assertEqual(scan_json(payload), ["$.api_key"])

    def test_bearer_value_in_free_text_is_flagged(self):
        payload = {"note": "Bearer ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"}
        self.assertEqual(scan_json(payload), ["$.note"])

    def test_redacted_placeholder_is_safe(self):
        payload = {"provider_token": "<redacted>"}
        self.assertEqual(scan_json(payload), [])


if __name__ == "__main__":
    unittest.main()
