# EXP-1 — headroom reproduction

Pre-registered protocol: `../../research/phase3_experiment_protocol.md`
Frozen config: `../../config/experiments/headroom_v1.yaml`

```bash
# 1. build the dataset (deterministic; writes datasets/manifest.json)
python3 build_datasets.py

# 2. run inside an isolated venv holding headroom-ai + tiktoken
python -m venv .venv && ./.venv/bin/pip install headroom-ai httpx tiktoken
./.venv/bin/python run.py          # writes results/raw_results.json

# 3. analyse (pure function of raw_results.json)
python3 analysis.py                # writes ../../outputs/phase3/headroom_*.json
```

Measurement and interpretation are separate steps on purpose: `run.py` produces numbers
and knows nothing about the verdict thresholds; `analysis.py` applies the pre-registered
thresholds and knows nothing about how the numbers were produced.

No paid API is used. No network access is required during measurement.
