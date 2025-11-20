#!/bin/bash
# Format code for router-policy-to-config

set -e

echo "Formatting code for router-policy-to-config..."

cd "$(dirname "$0")/.."

echo "==> Running black..."
black src/ tests/ ai_providers/

echo ""
echo "==> Running isort..."
isort src/ tests/ ai_providers/

echo ""
echo "Code formatting complete!"
