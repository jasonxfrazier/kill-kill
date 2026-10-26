#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--fix" ]]; then
    echo "Fixing lint issues..."
    uv run ruff check --fix .

    echo "Formatting code..."
    uv run ruff format .
else
    echo "Checking lint..."
    uv run ruff check .

    echo "Checking formatting..."
    uv run ruff format --check .
fi

echo "Ruff completed successfully!"