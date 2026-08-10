import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pip_core.fixture_registry import (
    FixtureIdentityConflict,
    FixtureRegistry,
    ProviderFixtureIdentity,
)


KICKOFF = datetime(2026, 8, 12, 18, 0, tzinfo=timezone.utc)


def identity(provider: str, provider_fixture_id: str, **overrides) -> ProviderFixtureIdentity:
    values = {
        "provider": provider,
        "provider_fixture_id": provider_fixture_id,
        "competition_key": "NOR_ELITESERIEN",
        "kickoff_at": KICKOFF,
        "home_team_key": "Home FC",
        "away_team_key": "Away FC",
    }
    values.update(overrides)
    return ProviderFixtureIdentity(**values)


class FixtureRegistryTests(unittest.TestCase):
    def test_two_provider_ids_resolve_to_one_internal_fixture(self):
        registry = FixtureRegistry(sqlite3.connect(":memory:"))
        first = registry.register_provider_fixture(identity("api_football", "1489369"))
        second = registry.register_provider_fixture(identity("odds_api", "abc123"))

        self.assertGreater(first.fixture_id, 0)
        self.assertEqual(second.fixture_id, first.fixture_id)
        self.assertEqual(
            registry.provider_mappings(first.fixture_id),
            {"api-football": "1489369", "odds-api": "abc123"},
        )

    def test_repeat_provider_registration_is_idempotent(self):
        registry = FixtureRegistry(sqlite3.connect(":memory:"))
        first = registry.register_provider_fixture(identity("sportsdata_io", "19146701"))
        repeated = registry.register_provider_fixture(
            identity(
                "sportsdata_io",
                "19146701",
                provider_updated_at=KICKOFF - timedelta(minutes=5),
            )
        )
        self.assertEqual(repeated, first)

    def test_provider_id_cannot_be_reused_for_another_match(self):
        registry = FixtureRegistry(sqlite3.connect(":memory:"))
        registry.register_provider_fixture(identity("api_football", "1489369"))
        with self.assertRaises(FixtureIdentityConflict):
            registry.register_provider_fixture(
                identity("api_football", "1489369", away_team_key="Different FC")
            )

    def test_same_provider_cannot_assign_two_ids_to_one_fixture(self):
        registry = FixtureRegistry(sqlite3.connect(":memory:"))
        registry.register_provider_fixture(identity("sports_game_odds", "19146701"))
        with self.assertRaises(FixtureIdentityConflict):
            registry.register_provider_fixture(identity("sports_game_odds", "19146702"))

    def test_distant_kickoff_creates_a_distinct_fixture(self):
        registry = FixtureRegistry(sqlite3.connect(":memory:"))
        first = registry.register_provider_fixture(identity("api_football", "1"))
        second = registry.register_provider_fixture(
            identity("api_football", "2", kickoff_at=KICKOFF + timedelta(days=7))
        )
        self.assertNotEqual(first.fixture_id, second.fixture_id)

    def test_registry_persists_provider_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixtures.sqlite3"
            with FixtureRegistry.open(path) as registry:
                created = registry.register_provider_fixture(identity("odds_api", "event-1"))
            with FixtureRegistry.open(path) as registry:
                loaded = registry.resolve_provider_fixture("odds_api", "event-1")
                self.assertEqual(loaded, created)

    def test_naive_kickoff_is_rejected(self):
        registry = FixtureRegistry(sqlite3.connect(":memory:"))
        with self.assertRaises(ValueError):
            registry.register_provider_fixture(
                identity("api_football", "1", kickoff_at=datetime(2026, 8, 12, 18, 0))
            )


if __name__ == "__main__":
    unittest.main()
