import unittest
from datetime import datetime, timedelta, timezone

from pip_core.provider_consensus import OddsObservation, build_comparable_consensus


NOW = datetime(2026, 8, 8, 20, 0, tzinfo=timezone.utc)
EVENT = "epl:arsenal:chelsea:2026-08-08T20:00Z"


def obs(provider, source, selection, odds, seconds_ago=30, market="1X2", line=None):
    return OddsObservation(
        provider=provider,
        source=source,
        canonical_event_key=EVENT,
        market=market,
        selection=selection,
        decimal_odds=odds,
        observed_at=NOW - timedelta(seconds=seconds_ago),
        line=line,
        provider_event_id=f"{provider}-event",
    )


class ProviderConsensusTests(unittest.TestCase):
    def test_two_provider_complete_snapshots_generate_consensus(self):
        rows = [
            obs("provider_a", "book_a", "home", 2.00),
            obs("provider_a", "book_a", "draw", 3.50),
            obs("provider_a", "book_a", "away", 4.00),
            obs("provider_b", "book_b", "home", 2.10, 50),
            obs("provider_b", "book_b", "draw", 3.40, 50),
            obs("provider_b", "book_b", "away", 3.90, 50),
        ]
        result = build_comparable_consensus(rows, canonical_event_key=EVENT, market="1X2", as_of=NOW)
        self.assertEqual(result.status, "comparable_consensus")
        self.assertEqual(result.provider_count, 2)
        self.assertEqual(result.source_count, 2)
        self.assertEqual(result.evidence_observation_count, 6)
        self.assertAlmostEqual(sum(result.probabilities.values()), 1.0, places=12)
        self.assertIsNotNone(result.consensus_dispersion)

    def test_single_provider_fails_soft_to_market_only(self):
        rows = [
            obs("provider_a", "book_a", "home", 2.00),
            obs("provider_a", "book_a", "draw", 3.50),
            obs("provider_a", "book_a", "away", 4.00),
        ]
        result = build_comparable_consensus(rows, canonical_event_key=EVENT, market="1X2", as_of=NOW)
        self.assertEqual(result.status, "market_only")
        self.assertEqual(result.probabilities, {})
        self.assertEqual(result.provider_count, 1)

    def test_incomplete_snapshot_does_not_count(self):
        rows = [
            obs("provider_a", "book_a", "home", 2.00),
            obs("provider_a", "book_a", "draw", 3.50),
            obs("provider_a", "book_a", "away", 4.00),
            obs("provider_b", "book_b", "home", 2.10),
            obs("provider_b", "book_b", "away", 3.90),
        ]
        result = build_comparable_consensus(rows, canonical_event_key=EVENT, market="1X2", as_of=NOW)
        self.assertEqual(result.status, "market_only")
        self.assertEqual(result.provider_count, 1)

    def test_stale_snapshot_does_not_create_consensus(self):
        rows = [
            obs("provider_a", "book_a", "home", 2.00),
            obs("provider_a", "book_a", "draw", 3.50),
            obs("provider_a", "book_a", "away", 4.00),
            obs("provider_b", "book_b", "home", 2.10, 2000),
            obs("provider_b", "book_b", "draw", 3.40, 2000),
            obs("provider_b", "book_b", "away", 3.90, 2000),
        ]
        result = build_comparable_consensus(rows, canonical_event_key=EVENT, market="1X2", as_of=NOW)
        self.assertEqual(result.status, "market_only")
        self.assertEqual(result.provider_count, 1)

    def test_same_provider_multiple_sources_does_not_satisfy_provider_gate(self):
        rows = []
        for source, home, draw, away in (("book_a", 2.0, 3.5, 4.0), ("book_b", 2.1, 3.4, 3.9)):
            rows.extend([
                obs("provider_a", source, "home", home),
                obs("provider_a", source, "draw", draw),
                obs("provider_a", source, "away", away),
            ])
        result = build_comparable_consensus(rows, canonical_event_key=EVENT, market="1X2", as_of=NOW)
        self.assertEqual(result.status, "market_only")
        self.assertEqual(result.provider_count, 1)
        self.assertEqual(result.source_count, 2)

    def test_market_line_must_match(self):
        rows = [
            obs("provider_a", "book_a", "over_2_5", 1.95, market="OVER_UNDER_2_5", line="2.5"),
            obs("provider_a", "book_a", "under_2_5", 1.95, market="OVER_UNDER_2_5", line="2.5"),
            obs("provider_b", "book_b", "over_2_5", 1.90, market="OVER_UNDER_2_5", line="3.5"),
            obs("provider_b", "book_b", "under_2_5", 2.00, market="OVER_UNDER_2_5", line="3.5"),
        ]
        result = build_comparable_consensus(
            rows,
            canonical_event_key=EVENT,
            market="OVER_UNDER_2_5",
            line="2.5",
            as_of=NOW,
        )
        self.assertEqual(result.status, "market_only")
        self.assertEqual(result.provider_count, 1)

    def test_latest_duplicate_selection_is_used(self):
        rows = [
            obs("provider_a", "book_a", "home", 1.50, 120),
            obs("provider_a", "book_a", "home", 2.00, 20),
            obs("provider_a", "book_a", "draw", 3.50, 20),
            obs("provider_a", "book_a", "away", 4.00, 20),
            obs("provider_b", "book_b", "home", 2.10, 30),
            obs("provider_b", "book_b", "draw", 3.40, 30),
            obs("provider_b", "book_b", "away", 3.90, 30),
        ]
        result = build_comparable_consensus(rows, canonical_event_key=EVENT, market="1X2", as_of=NOW)
        self.assertEqual(result.status, "comparable_consensus")
        self.assertLess(result.probabilities["home"], 0.60)

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            OddsObservation(
                provider="p",
                source="s",
                canonical_event_key=EVENT,
                market="BTTS",
                selection="yes",
                decimal_odds=2.0,
                observed_at=datetime(2026, 8, 8, 20, 0),
            )


if __name__ == "__main__":
    unittest.main()
