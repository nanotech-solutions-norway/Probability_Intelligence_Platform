import unittest

from pip_core.provider_fixture_ids import ProviderPayloadError, extract_provider_fixture_ids


class ProviderFixtureIdTests(unittest.TestCase):
    def test_api_football_fixture_id_path(self):
        document = {"response": [{"fixture": {"id": 1489369}}, {"fixture": {"id": 1489370}}]}
        self.assertEqual(extract_provider_fixture_ids("api_football", document), ["1489369", "1489370"])

    def test_the_odds_api_event_id_path(self):
        document = [{"id": "bda33adca828c09dc3cac3a856aef176"}]
        self.assertEqual(
            extract_provider_fixture_ids("odds_api", document),
            ["bda33adca828c09dc3cac3a856aef176"],
        )

    def test_sportmonks_fixture_and_odds_paths(self):
        fixture = {"data": {"id": 19146701, "starting_at": "2026-08-12 18:00:00"}}
        odds = {"data": [{"id": 1040325, "fixture_id": 18557891}]}
        self.assertEqual(extract_provider_fixture_ids("sportmonks", fixture), ["19146701"])
        self.assertEqual(extract_provider_fixture_ids("sportmonks", odds), ["18557891"])

    def test_statsbomb_match_id_path(self):
        self.assertEqual(extract_provider_fixture_ids("statsbomb", [{"match_id": 3788741}]), ["3788741"])

    def test_duplicate_ids_are_deduplicated(self):
        document = [{"id": "event-1"}, {"id": "event-1"}]
        self.assertEqual(extract_provider_fixture_ids("odds_api", document), ["event-1"])

    def test_missing_identifier_fails_closed(self):
        with self.assertRaises(ProviderPayloadError):
            extract_provider_fixture_ids("sportmonks", {"data": {"name": "fixture"}})


if __name__ == "__main__":
    unittest.main()
