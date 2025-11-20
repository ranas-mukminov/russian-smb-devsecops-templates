#!/usr/bin/env bash
set -euo pipefail

start=$(date +%s)
python tools/validate_ci_templates.py >/dev/null 2>&1 || echo "CI validation failed"
python tools/validate_logging_configs.py >/dev/null 2>&1 || echo "Logging validation failed"
end=$(date +%s)

echo "Validation runtime: $((end-start))s" 
