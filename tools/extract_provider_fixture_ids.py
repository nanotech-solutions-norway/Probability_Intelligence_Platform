#!/usr/bin/env python3
"""Extract provider fixture IDs from a local JSON response without networking."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pip_core.provider_fixture_ids import extract_provider_fixture_ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=("api_football", "odds_api", "sportmonks", "statsbomb"))
    parser.add_argument("response", type=Path, help="local provider JSON response")
    args = parser.parse_args()
    document = json.loads(args.response.read_text(encoding="utf-8-sig"))
    identifiers = extract_provider_fixture_ids(args.provider, document)
    print(json.dumps({"provider": args.provider, "fixture_ids": identifiers}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
