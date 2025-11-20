#!/bin/bash
# Security scanning for router-policy-to-config

set -e

echo "Running security scans for router-policy-to-config..."

cd "$(dirname "$0")/.."

echo "==> Running bandit..."
bandit -r src/ -f text || true

echo ""
echo "==> Running pip-audit..."
pip-audit --requirement <(pip freeze) || true

echo ""
echo "Security scan complete!"
