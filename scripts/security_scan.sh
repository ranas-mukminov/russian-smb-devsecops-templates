#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip >/dev/null 2>&1 || true
python -m pip install pip-audit bandit >/dev/null 2>&1

pip-audit || true
bandit -q -r tools logging_stack ci_security_templates || true
