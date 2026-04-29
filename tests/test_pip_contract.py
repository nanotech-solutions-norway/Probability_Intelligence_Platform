import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.contract_validator import validate_pip_response


class PipContractTest(unittest.TestCase):
    def test_mock_probability_response_passes_contract(self):
        payload = json.loads((ROOT / "examples" / "mock_pip_probability_response.json").read_text(encoding="utf-8"))
        self.assertTrue(validate_pip_response(payload))

    def test_execution_allowed_true_is_rejected(self):
        payload = json.loads((ROOT / "examples" / "mock_pip_probability_response.json").read_text(encoding="utf-8"))
        payload["execution_allowed"] = True
        with self.assertRaises(ValueError):
            validate_pip_response(payload)


if __name__ == "__main__":
    unittest.main()
