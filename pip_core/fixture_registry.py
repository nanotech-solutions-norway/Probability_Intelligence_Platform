"""Persistent provider-neutral fixture identity registry.

The registry maps provider-owned event identifiers to a positive Atlas/PIP
integer fixture ID. It stores normalized identity metadata only; provider
credentials and raw provider payloads are deliberately out of scope.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_KICKOFF_TOLERANCE_SECONDS = 6 * 60 * 60


class FixtureRegistryError(ValueError):
    """Base class for fail-closed fixture registry errors."""


class FixtureIdentityConflict(FixtureRegistryError):
    """A provider ID was previously mapped to incompatible fixture identity."""


class AmbiguousFixtureMatch(FixtureRegistryError):
    """More than one canonical fixture matched a new provider event."""


@dataclass(frozen=True)
class ProviderFixtureIdentity:
    provider: str
    provider_fixture_id: str
    competition_key: str
    kickoff_at: datetime
    home_team_key: str
    away_team_key: str
    provider_updated_at: datetime | None = None


@dataclass(frozen=True)
class FixtureRecord:
    fixture_id: int
    canonical_event_key: str
    competition_key: str
    kickoff_at: datetime
    home_team_key: str
    away_team_key: str
    status: str


SCHEMA = """
CREATE TABLE IF NOT EXISTS pip_fixtures (
    fixture_id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_event_key TEXT NOT NULL UNIQUE,
    competition_key TEXT NOT NULL,
    kickoff_at TEXT NOT NULL,
    home_team_key TEXT NOT NULL,
    away_team_key TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pip_fixtures_identity
ON pip_fixtures (competition_key, home_team_key, away_team_key, kickoff_at);

CREATE TABLE IF NOT EXISTS pip_provider_fixture_mappings (
    provider TEXT NOT NULL,
    provider_fixture_id TEXT NOT NULL,
    fixture_id INTEGER NOT NULL REFERENCES pip_fixtures(fixture_id) ON DELETE CASCADE,
    provider_updated_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (provider, provider_fixture_id),
    UNIQUE (fixture_id, provider)
);

CREATE INDEX IF NOT EXISTS idx_pip_provider_fixture_internal
ON pip_provider_fixture_mappings (fixture_id);
"""


def _normalize_key(value: str, field: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not normalized:
        raise FixtureRegistryError(f"{field} is required")
    return normalized


def _normalize_provider_fixture_id(value: str | int) -> str:
    if isinstance(value, bool):
        raise FixtureRegistryError("provider_fixture_id must not be boolean")
    normalized = str(value).strip()
    if not normalized or len(normalized) > 128:
        raise FixtureRegistryError("provider_fixture_id must contain 1 to 128 characters")
    return normalized


def _as_utc(value: datetime, field: str) -> datetime:
    if value.tzinfo is None:
        raise FixtureRegistryError(f"{field} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return _as_utc(value, "timestamp").isoformat().replace("+00:00", "Z")


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def canonical_event_key(
    *,
    competition_key: str,
    kickoff_at: datetime,
    home_team_key: str,
    away_team_key: str,
) -> str:
    """Return a stable opaque key from normalized event identity metadata."""
    identity = "|".join(
        (
            _normalize_key(competition_key, "competition_key"),
            _iso(kickoff_at),
            _normalize_key(home_team_key, "home_team_key"),
            _normalize_key(away_team_key, "away_team_key"),
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


class FixtureRegistry:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)

    @classmethod
    def open(cls, path: str | Path) -> "FixtureRegistry":
        return cls(sqlite3.connect(str(path)))

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "FixtureRegistry":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def register_provider_fixture(
        self,
        identity: ProviderFixtureIdentity,
        *,
        kickoff_tolerance_seconds: int = DEFAULT_KICKOFF_TOLERANCE_SECONDS,
    ) -> FixtureRecord:
        if kickoff_tolerance_seconds < 0:
            raise FixtureRegistryError("kickoff_tolerance_seconds cannot be negative")

        provider = _normalize_key(identity.provider, "provider")
        provider_fixture_id = _normalize_provider_fixture_id(identity.provider_fixture_id)
        competition = _normalize_key(identity.competition_key, "competition_key")
        home = _normalize_key(identity.home_team_key, "home_team_key")
        away = _normalize_key(identity.away_team_key, "away_team_key")
        if home == away:
            raise FixtureRegistryError("home and away teams must differ")
        kickoff = _as_utc(identity.kickoff_at, "kickoff_at")
        provider_updated = (
            _as_utc(identity.provider_updated_at, "provider_updated_at")
            if identity.provider_updated_at is not None
            else None
        )
        now = datetime.now(timezone.utc)

        with self.connection:
            mapped = self.connection.execute(
                """
                SELECT f.*
                FROM pip_provider_fixture_mappings AS m
                JOIN pip_fixtures AS f ON f.fixture_id = m.fixture_id
                WHERE m.provider = ? AND m.provider_fixture_id = ?
                """,
                (provider, provider_fixture_id),
            ).fetchone()
            if mapped is not None:
                record = self._record(mapped)
                if (
                    record.competition_key != competition
                    or record.home_team_key != home
                    or record.away_team_key != away
                    or abs((record.kickoff_at - kickoff).total_seconds()) > kickoff_tolerance_seconds
                ):
                    raise FixtureIdentityConflict(
                        "provider fixture ID is already mapped to incompatible event identity"
                    )
                self.connection.execute(
                    """
                    UPDATE pip_provider_fixture_mappings
                    SET provider_updated_at = ?, updated_at = ?
                    WHERE provider = ? AND provider_fixture_id = ?
                    """,
                    (_iso(provider_updated) if provider_updated else None, _iso(now), provider, provider_fixture_id),
                )
                return record

            candidates = self.connection.execute(
                """
                SELECT *
                FROM pip_fixtures
                WHERE competition_key = ?
                  AND home_team_key = ?
                  AND away_team_key = ?
                  AND ABS(strftime('%s', kickoff_at) - strftime('%s', ?)) <= ?
                ORDER BY fixture_id
                """,
                (competition, home, away, _iso(kickoff), kickoff_tolerance_seconds),
            ).fetchall()
            if len(candidates) > 1:
                raise AmbiguousFixtureMatch("multiple canonical fixtures match provider event identity")

            if candidates:
                fixture_id = int(candidates[0]["fixture_id"])
                record = self._record(candidates[0])
            else:
                event_key = canonical_event_key(
                    competition_key=competition,
                    kickoff_at=kickoff,
                    home_team_key=home,
                    away_team_key=away,
                )
                cursor = self.connection.execute(
                    """
                    INSERT INTO pip_fixtures (
                        canonical_event_key, competition_key, kickoff_at,
                        home_team_key, away_team_key, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'scheduled', ?, ?)
                    """,
                    (event_key, competition, _iso(kickoff), home, away, _iso(now), _iso(now)),
                )
                fixture_id = int(cursor.lastrowid)
                record = self.get_by_internal_id(fixture_id)
                if record is None:  # defensive; insert and read happen in one transaction
                    raise FixtureRegistryError("created fixture could not be read back")

            try:
                self.connection.execute(
                    """
                    INSERT INTO pip_provider_fixture_mappings (
                        provider, provider_fixture_id, fixture_id,
                        provider_updated_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        provider,
                        provider_fixture_id,
                        fixture_id,
                        _iso(provider_updated) if provider_updated else None,
                        _iso(now),
                        _iso(now),
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise FixtureIdentityConflict(
                    "provider already has an incompatible mapping for this canonical fixture"
                ) from error
            return record

    def resolve_provider_fixture(self, provider: str, provider_fixture_id: str | int) -> FixtureRecord | None:
        row = self.connection.execute(
            """
            SELECT f.*
            FROM pip_provider_fixture_mappings AS m
            JOIN pip_fixtures AS f ON f.fixture_id = m.fixture_id
            WHERE m.provider = ? AND m.provider_fixture_id = ?
            """,
            (_normalize_key(provider, "provider"), _normalize_provider_fixture_id(provider_fixture_id)),
        ).fetchone()
        return self._record(row) if row is not None else None

    def get_by_internal_id(self, fixture_id: int) -> FixtureRecord | None:
        if isinstance(fixture_id, bool) or fixture_id < 1:
            raise FixtureRegistryError("fixture_id must be a positive integer")
        row = self.connection.execute(
            "SELECT * FROM pip_fixtures WHERE fixture_id = ?",
            (fixture_id,),
        ).fetchone()
        return self._record(row) if row is not None else None

    def provider_mappings(self, fixture_id: int) -> dict[str, str]:
        if self.get_by_internal_id(fixture_id) is None:
            return {}
        rows = self.connection.execute(
            """
            SELECT provider, provider_fixture_id
            FROM pip_provider_fixture_mappings
            WHERE fixture_id = ?
            ORDER BY provider
            """,
            (fixture_id,),
        ).fetchall()
        return {str(row["provider"]): str(row["provider_fixture_id"]) for row in rows}

    @staticmethod
    def _record(row: sqlite3.Row) -> FixtureRecord:
        return FixtureRecord(
            fixture_id=int(row["fixture_id"]),
            canonical_event_key=str(row["canonical_event_key"]),
            competition_key=str(row["competition_key"]),
            kickoff_at=_parse_iso(str(row["kickoff_at"])),
            home_team_key=str(row["home_team_key"]),
            away_team_key=str(row["away_team_key"]),
            status=str(row["status"]),
        )
