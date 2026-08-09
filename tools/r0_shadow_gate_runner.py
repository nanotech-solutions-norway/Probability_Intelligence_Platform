#!/usr/bin/env python3
"""Offline R0 shadow-gate runner for sanitized provider observations.

No network calls, credentials, deployment actions, recommendations, or execution
capabilities are present. The tool converts a local JSON evidence file into a
PIP v2 shadow payload so the external-data closure gate can be reproduced.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pip_core.provider_consensus import OddsObservation, build_comparable_consensus
from pip_core.shadow_payload import build_shadow_payload


def _dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return parsed


def run_gate(document: dict[str, Any]) -> dict[str, Any]:
    required = {
        "fixture_id",
        "canonical_event_key",
        "market",
        "model_version",
        "calibration_version",
        "evidence_id",
        "data_quality_score",
        "as_of",
        "observations",
    }
    missing = sorted(required - set(document))
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if not isinstance(document["observations"], list):
        raise ValueError("observations must be an array")

    observations = [
        OddsObservation(
            provider=str(row["provider"]),
            source=str(row["source"]),
            canonical_event_key=str(row.get("canonical_event_key", document["canonical_event_key"])),
            market=str(row.get("market", document["market"])),
            selection=str(row["selection"]),
            decimal_odds=float(row["decimal_odds"]),
            observed_at=_dt(str(row["observed_at"])),
            line=row.get("line", document.get("line")),
            provider_event_id=row.get("provider_event_id"),
            provider_timestamp=_dt(row.get("provider_timestamp")),
        )
        for row in document["observations"]
    ]
    consensus = build_comparable_consensus(
        observations,
        canonical_event_key=str(document["canonical_event_key"]),
        market=str(document["market"]),
        line=document.get("line"),
        as_of=_dt(str(document["as_of"])),
        max_snapshot_skew_seconds=int(document.get("max_snapshot_skew_seconds", 180)),
        max_age_seconds=int(document.get("max_age_seconds", 900)),
        min_provider_count=int(document.get("min_provider_count", 2)),
    )
    return build_shadow_payload(
        consensus,
        fixture_id=int(document["fixture_id"]),
        model_version=str(document["model_version"]),
        calibration_version=str(document["calibration_version"]),
        evidence_id=str(document["evidence_id"]),
        data_quality_score=float(document["data_quality_score"]),
        generated_at=_dt(str(document["as_of"])),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="sanitized local R0 provider-evidence JSON")
    parser.add_argument("--output", type=Path, help="optional output path for the v2 shadow payload")
    parser.add_argument("--require-consensus", action="store_true", help="return non-zero if comparable consensus is unavailable")
    args = parser.parse_args()

    document = json.loads(args.input.read_text(encoding="utf-8-sig"))
    payload = run_gate(document)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    if args.require_consensus and payload["data_quality"]["consensus_status"] != "comparable_consensus":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
