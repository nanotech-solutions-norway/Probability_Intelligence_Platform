"""Extract provider-owned fixture IDs from already-authorized JSON responses."""
from __future__ import annotations

from typing import Any, Callable


class ProviderPayloadError(ValueError):
    pass


def _identifier(value: Any, field: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ProviderPayloadError(f"{field} must be a string or integer")
    normalized = str(value).strip()
    if not normalized:
        raise ProviderPayloadError(f"{field} is empty")
    return normalized


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def extract_api_football_fixture_ids(document: Any) -> list[str]:
    if not isinstance(document, dict) or not isinstance(document.get("response"), list):
        raise ProviderPayloadError("API-FOOTBALL response must contain response[]")
    identifiers = []
    for index, item in enumerate(document["response"]):
        if not isinstance(item, dict) or not isinstance(item.get("fixture"), dict):
            raise ProviderPayloadError(f"response[{index}].fixture is required")
        identifiers.append(_identifier(item["fixture"].get("id"), f"response[{index}].fixture.id"))
    return _unique(identifiers)


def extract_sportsdata_io_game_ids(document: Any) -> list[str]:
    items = document if isinstance(document, list) else [document]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("SportsDataIO response must be a game object or array")
    identifiers = []
    for index, item in enumerate(items):
        field = "GameId" if "GameId" in item else "GameID"
        identifiers.append(_identifier(item.get(field), f"game[{index}].{field}"))
    return _unique(identifiers)


def extract_the_odds_api_event_ids(document: Any) -> list[str]:
    items = document if isinstance(document, list) else [document]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("The Odds API response must be an event object or array")
    return _unique([_identifier(item.get("id"), f"event[{index}].id") for index, item in enumerate(items)])


def extract_soccerdata_api_match_ids(document: Any) -> list[str]:
    if not isinstance(document, dict):
        raise ProviderPayloadError("Soccerdata API response must be an object")
    data = document.get("results", document)
    items = data if isinstance(data, list) else [data]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("Soccerdata API results must be an object or array")
    return _unique([_identifier(item.get("id"), f"match[{index}].id") for index, item in enumerate(items)])


def extract_sports_game_odds_event_ids(document: Any) -> list[str]:
    if not isinstance(document, dict) or "data" not in document:
        raise ProviderPayloadError("SportsGameOdds response must contain data")
    data = document["data"]
    items = data if isinstance(data, list) else [data]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("SportsGameOdds data must be an object or array")
    return _unique(
        [_identifier(item.get("eventID"), f"data[{index}].eventID") for index, item in enumerate(items)]
    )


def extract_sharpapi_event_ids(document: Any) -> list[str]:
    if not isinstance(document, dict) or "data" not in document:
        raise ProviderPayloadError("SharpAPI response must contain data")
    data = document["data"]
    items = data if isinstance(data, list) else [data]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("SharpAPI data must be an object or array")
    identifiers = []
    for index, item in enumerate(items):
        field = "event_id" if "event_id" in item else "id"
        identifiers.append(_identifier(item.get(field), f"data[{index}].{field}"))
    return _unique(identifiers)


def extract_statsbomb_match_ids(document: Any) -> list[str]:
    items = document if isinstance(document, list) else [document]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("StatsBomb matches response must be an object or array")
    return _unique(
        [_identifier(item.get("match_id"), f"match[{index}].match_id") for index, item in enumerate(items)]
    )


EXTRACTORS: dict[str, Callable[[Any], list[str]]] = {
    "api-football": extract_api_football_fixture_ids,
    "api_football": extract_api_football_fixture_ids,
    "api-sports": extract_api_football_fixture_ids,
    "api_sports": extract_api_football_fixture_ids,
    "the-odds-api": extract_the_odds_api_event_ids,
    "odds_api": extract_the_odds_api_event_ids,
    "sportsdata-io": extract_sportsdata_io_game_ids,
    "sportsdata_io": extract_sportsdata_io_game_ids,
    "soccerdata-api": extract_soccerdata_api_match_ids,
    "soccerdata_api": extract_soccerdata_api_match_ids,
    "sports-game-odds": extract_sports_game_odds_event_ids,
    "sports_game_odds": extract_sports_game_odds_event_ids,
    "sportsgameodds": extract_sports_game_odds_event_ids,
    "sharpapi": extract_sharpapi_event_ids,
    "statsbomb": extract_statsbomb_match_ids,
}


def extract_provider_fixture_ids(provider: str, document: Any) -> list[str]:
    key = provider.strip().lower()
    try:
        extractor = EXTRACTORS[key]
    except KeyError as error:
        raise ProviderPayloadError(f"unsupported provider: {provider}") from error
    return extractor(document)
