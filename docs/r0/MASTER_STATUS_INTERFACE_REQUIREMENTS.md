# Master Status Interface Requirements — R0

The existing Atlas/FEA/PIP control-interface concept remains read-only and should be rebuilt only from reconciled canonical release metadata.

## Required display fields
- FEA canonical Git SHA
- PIP canonical Git SHA
- deployed release/artifact hash
- shared contract version
- current phase/gate classification dimensions
- provider health and last successful observation time
- data freshness and comparable-consensus status
- provider-call budget/cap utilization
- last validation archive identifier and hash status
- current model/calibration version
- FEA-without-PIP operability state
- manual-review requirement
- recommendation-release state
- execution state
- bookmaker-execution state
- public-write-endpoint state

## Security
- never display provider credentials, API keys, password hashes, tokens, environment values, or secret-bearing configuration paths that reveal sensitive material;
- no frontend provider token;
- no write or execution action may be exposed by the status interface;
- authentication/session controls remain server-side.

## Source rule
The interface must derive code/release identity from approved Git release metadata and derive evidence state from archived validation manifests. It must not infer canonical version from arbitrary Drive work-folder recency.
