# Fixture Registry and Provider ID Extraction — R0

## Authority and current provider state

PIP owns canonical fixture identity. FEA remains a read-only consumer and must not create or infer fixture mappings.

The controlled provider setup currently lists API-FOOTBALL, The Odds API, Sportmonks and StatsBomb as **candidates pending credential, licensing and coverage validation**. Their presence in configuration templates does not prove that a paid account, key, competition entitlement or live ingestion job is active.

## Internal fixture ID

`pip_fixtures.fixture_id` is the positive Atlas/PIP integer used by the authenticated PIP endpoint and later stored as `PIP_VALIDATION_FIXTURE_ID`. Provider IDs remain strings because some providers use integers while The Odds API uses opaque string event IDs.

`FixtureRegistry.register_provider_fixture()`:

1. validates normalized competition, kickoff and home/away team identity;
2. returns an existing mapping when the same provider event was already registered;
3. maps a new provider event to one matching canonical fixture inside the kickoff tolerance;
4. creates a new internal fixture only when no canonical match exists;
5. rejects ambiguous matches, reused provider IDs and multiple incompatible IDs from one provider.

The reference implementation uses SQLite for deterministic local/CI validation. `db/phpmyadmin/fixture_registry_schema.sql` supplies the additive MariaDB/MySQL schema for the reviewed Domeneshop database path. MariaDB timestamps must be written in UTC.

## Official provider ID locations

### API-FOOTBALL / API-SPORTS

- List fixtures with `GET https://v3.football.api-sports.io/fixtures` using a league/season/date or other documented filter.
- Extract each provider fixture ID from `response[].fixture.id`.
- Use that value in later API-FOOTBALL fixture, odds, lineup and statistics calls.
- Official reference: https://www.api-football.com/documentation-v3

### The Odds API

- List events with `GET /v4/sports/{sport}/events` or list current odds with `GET /v4/sports/{sport}/odds`.
- Extract the opaque event ID from each top-level event object's `id` field.
- The soccer sport key must also be retained as provider metadata; for example, the official sports catalogue currently includes `soccer_norway_eliteserien`.
- Official reference: https://the-odds-api.com/liveapi/guides/v4/

### Sportmonks Football API v3

- List fixtures with `GET https://api.sportmonks.com/v3/football/fixtures`.
- Extract `data[].id` from fixture entities.
- When processing an odds response, extract `data[].fixture_id`, not the odds row's own `id`.
- Retrieve pre-match odds with `/v3/football/odds/pre-match/fixtures/{fixture_id}`.
- Official fixture reference: https://docs.sportmonks.com/v3/endpoints-and-entities/endpoints/fixtures/get-all-fixtures
- Official odds reference: https://docs.sportmonks.com/v3/endpoints-and-entities/endpoints/standard-odds-feed/pre-match-odds/get-odds-by-fixture-id

### StatsBomb open data

- Matches are listed in the competition/season match files.
- Extract `match_id` from each match object.
- StatsBomb is a candidate analytical/xG source, not an independent bookmaker-odds source for the two-provider consensus gate.
- Official reference: https://github.com/hudl/open-data

## Offline extraction

Save an already-authorized JSON response locally without credentials or request headers, then run:

```text
python tools/extract_provider_fixture_ids.py api_football response.json
python tools/extract_provider_fixture_ids.py odds_api response.json
python tools/extract_provider_fixture_ids.py sportmonks response.json
python tools/extract_provider_fixture_ids.py statsbomb response.json
```

The extractor performs no network call. Do not commit provider payloads unless they are explicitly sanitized and approved as evidence.

## Comparable-consensus boundary

Matching event IDs across providers is necessary but not sufficient. A Phase 16I validation fixture also requires complete same-event/same-market/same-line odds snapshots from at least two distinct providers inside the freshness and skew limits. Missing or ambiguous mappings must fail closed; no ID, odds or provider coverage may be invented.

Recommendation release, execution, auto-betting, real-money betting and bookmaker execution remain disabled.
