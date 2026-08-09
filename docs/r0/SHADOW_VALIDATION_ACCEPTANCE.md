# Shadow Validation Acceptance — R0

## Immediate functional gate
Before Phase 16I can be technically accepted, preserved/reproducible testing must demonstrate at least one valid non-zero `comparable_consensus` shadow payload traversing provider normalization -> PIP contract -> FEA read-only adapter while all safety locks remain enforced.

## Broader shadow-period gate
A statistically meaningful sample-size target must be approved from actual provider/competition coverage before any predictive-performance claim. R0 does not invent a production sample threshold.

The shadow evidence set must report:
- fixture and competition coverage
- provider availability and comparable-consensus rate
- source/provider counts
- stale/missing-data rate
- fail-soft rate
- Brier score
- log loss
- calibration/reliability results
- consensus dispersion
- model version and calibration version
- prediction timestamp versus data timestamps
- settled outcome provenance
- recommendation quarantine state
- execution and bookmaker-execution lock state

## Leakage control
Predictions must be reconstructed only from information available at the prediction timestamp. Closing odds, later lineups, settled outcomes, or any future-derived feature must never enter the prediction input used for evaluation.

## Failure policy
Missing, stale, incomparable, malformed, or unavailable provider evidence must degrade to `market_only`/`insufficient_consensus` or an FEA fail-soft result. It must never manufacture consensus or relax safety controls.
