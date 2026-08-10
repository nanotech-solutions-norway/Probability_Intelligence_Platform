import unittest

from pip_core.provider_fixture_ids import ProviderPayloadError, extract_provider_fixture_ids


class ProviderFixtureIdTests(unittest.TestCase):
    def test_api_football_fixture_id_path(self):
        document = {"response": [{"fixture": {"id": 1489369}}, {"fixture": {"id": 1489370}}]}
        self.assertEqual(extract_provider_fixture_ids("api_football", document), ["1489369", "1489370"])
        self.assertEqual(extract_provider_fixture_ids("api_sports", document), ["1489369", "1489370"])

    def test_the_odds_api_event_id_path(self):
        document = [{"id": "bda33adca828c09dc3cac3a856aef176"}]
        self.assertEqual(
            extract_provider_fixture_ids("odds_api", document),
            ["bda33adca828c09dc3cac3a856aef176"],
        )

    def test_sportsdata_io_game_id_path(self):
        document = [{"GameId": 12345}, {"GameID": 12346}]
        self.assertEqual(extract_provider_fixture_ids("sportsdata_io", document), ["12345", "12346"])

    def test_soccerdata_api_match_id_paths(self):
        paged = {"count": 2, "results": [{"id": 531585}, {"id": 531586}]}
        single = {"id": 531585, "status": "finished"}
        self.assertEqual(extract_provider_fixture_ids("soccerdata_api", paged), ["531585", "531586"])
        self.assertEqual(extract_provider_fixture_ids("soccerdata_api", single), ["531585"])

    def test_sports_game_odds_event_id_path(self):
        document = {"success": True, "data": [{"eventID": "mXCZTRJnbX8ib64z1h3D"}]}
        self.assertEqual(
            extract_provider_fixture_ids("sports_game_odds", document),
            ["mXCZTRJnbX8ib64z1h3D"],
        )

    def test_sharpapi_event_id_paths(self):
        rest = {"data": [{"id": "soccer-epl-123"}]}
        stream = {"data": {"event_id": "soccer-epl-124"}}
        self.assertEqual(extract_provider_fixture_ids("sharpapi", rest), ["soccer-epl-123"])
        self.assertEqual(extract_provider_fixture_ids("sharpapi", stream), ["soccer-epl-124"])

    def test_statsbomb_match_id_path(self):
        self.assertEqual(extract_provider_fixture_ids("statsbomb", [{"match_id": 3788741}]), ["3788741"])

    def test_duplicate_ids_are_deduplicated(self):
        document = [{"id": "event-1"}, {"id": "event-1"}]
        self.assertEqual(extract_provider_fixture_ids("odds_api", document), ["event-1"])

    def test_missing_identifier_fails_closed(self):
        with self.assertRaises(ProviderPayloadError):
            extract_provider_fixture_ids("sports_game_odds", {"data": {"name": "fixture"}})


if __name__ == "__main__":
    unittest.main()
