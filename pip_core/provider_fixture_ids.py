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


def extract_the_odds_api_event_ids(document: Any) -> list[str]:
    items = document if isinstance(document, list) else [document]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("The Odds API response must be an event object or array")
    return _unique([_identifier(item.get("id"), f"event[{index}].id") for index, item in enumerate(items)])


def extract_sportmonks_fixture_ids(document: Any) -> list[str]:
    if not isinstance(document, dict) or "data" not in document:
        raise ProviderPayloadError("Sportmonks response must contain data")
    data = document["data"]
    items = data if isinstance(data, list) else [data]
    if not items or not all(isinstance(item, dict) for item in items):
        raise ProviderPayloadError("Sportmonks data must be an object or array")
    identifiers = []
    for index, item in enumerate(items):
        field = "fixture_id" if "fixture_id" in item else "id"
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
    "the-odds-api": extract_the_odds_api_event_ids,
    "odds_api": extract_the_odds_api_event_ids,
    "sportmonks": extract_sportmonks_fixture_ids,
    "statsbomb": extract_statsbomb_match_ids,
}


def extract_provider_fixture_ids(provider: str, document: Any) -> list[str]:
    key = provider.strip().lower()
    try:
        extractor = EXTRACTORS[key]
    except KeyError as error:
        raise ProviderPayloadError(f"unsupported provider: {provider}") from error
    return extractor(document)
