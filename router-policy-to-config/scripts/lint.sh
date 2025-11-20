#!/bin/bash
# Lint and format check for router-policy-to-config

set -e

echo "Running linters for router-policy-to-config..."

cd "$(dirname "$0")/.."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Run this script from router-policy-to-config directory."
    exit 1
fi

echo "==> Running ruff..."
ruff check src/ tests/ ai_providers/ || true

echo ""
echo "==> Running black (check only)..."
black --check src/ tests/ ai_providers/ || true

echo ""
echo "==> Running isort (check only)..."
isort --check-only src/ tests/ ai_providers/ || true

echo ""
echo "==> Running mypy..."
mypy src/router_policy_to_config/ --ignore-missing-imports || true

echo ""
echo "Linting complete!"
