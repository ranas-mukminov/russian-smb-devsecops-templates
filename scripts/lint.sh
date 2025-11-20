#!/usr/bin/env bash
set -euo pipefail

# Python lint
if command -v ruff >/dev/null 2>&1; then
  ruff tools tests ci_security_templates logging_stack || true
else
  echo "ruff not installed, skipping"
fi

# Optional format check
if command -v black >/dev/null 2>&1; then
  black --check tools tests || true
fi

# YAML sanity
python - <<'PY'
import sys
from pathlib import Path
import yaml

files = list(Path('.').rglob('*.yml')) + list(Path('.').rglob('*.yaml'))
for path in files:
    try:
        yaml.safe_load(path.read_text())
    except Exception as exc:
        sys.exit(f"YAML error in {path}: {exc}")
print(f"YAML validated: {len(files)} files")
PY

# JSON/NDJSON dashboards
python - <<'PY'
import json
from pathlib import Path

def check_json(path: Path):
    with path.open() as f:
        json.load(f)

for path in Path('logging_stack/grafana/dashboards').glob('*.json'):
    check_json(path)
print("Grafana dashboards JSON ok")
PY

