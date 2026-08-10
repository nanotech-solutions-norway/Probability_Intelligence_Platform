-- PIP provider-neutral fixture registry for Domeneshop MariaDB/MySQL.
-- Additive only: no DROP, TRUNCATE, credentials, provider payloads, or execution tables.

CREATE TABLE IF NOT EXISTS pip_fixtures (
    fixture_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    canonical_event_key CHAR(64) NOT NULL,
    competition_key VARCHAR(100) NOT NULL,
    kickoff_at DATETIME(6) NOT NULL,
    home_team_key VARCHAR(160) NOT NULL,
    away_team_key VARCHAR(160) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'scheduled',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (fixture_id),
    UNIQUE KEY uq_pip_fixture_event (canonical_event_key),
    KEY idx_pip_fixture_identity (competition_key, home_team_key, away_team_key, kickoff_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pip_provider_fixture_mappings (
    provider VARCHAR(64) NOT NULL,
    provider_fixture_id VARCHAR(128) NOT NULL,
    fixture_id BIGINT UNSIGNED NOT NULL,
    provider_updated_at DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (provider, provider_fixture_id),
    UNIQUE KEY uq_pip_fixture_provider (fixture_id, provider),
    KEY idx_pip_provider_fixture_internal (fixture_id),
    CONSTRAINT fk_pip_provider_fixture
        FOREIGN KEY (fixture_id) REFERENCES pip_fixtures (fixture_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
