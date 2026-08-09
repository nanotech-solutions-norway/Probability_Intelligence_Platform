# Provider Comparability Gate — R0

## Objective
Produce consensus only from genuinely comparable market observations. Adding providers is not itself a success condition.

## Normalized observation identity
Each candidate observation must resolve to:
- provider
- provider event identifier
- canonical event key
- bookmaker/source
- market
- line where applicable
- selection
- decimal odds
- observed timestamp
- provider/source timestamp when available

## Comparability rules
Observations are comparable only when they describe the same canonical event, market definition, line, and selection inside the approved freshness/timestamp window. Duplicate observations from the same source must not increase consensus source counts.

## Consensus source gate
- comparable provider count must be at least 2 before `comparable_consensus` is emitted;
- otherwise emit `market_only` or `insufficient_consensus` and fail soft;
- provider errors must not be converted into synthetic probability evidence;
- provider-call budget remains enforced;
- all transformations retain source provenance and timestamps.

## Initial shadow aggregation
Use transparent, deterministic no-vig normalization and robust aggregation for shadow testing. Record provider_count, source_count, freshness_seconds, and consensus_dispersion. Production weighting is not authorized until out-of-sample validation justifies it.

## Safety
Consensus generation remains read-only. Manual review is required; recommendation release, execution, public write endpoints, frontend tokens, and bookmaker execution remain disabled.
