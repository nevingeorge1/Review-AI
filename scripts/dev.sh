#!/usr/bin/env bash
# ReviewAI Local Development Helper Script

set -e

COMMAND="${1:-help}"

case "$COMMAND" in
    "check")
        echo "Running Module 1 foundation verification..."
        python scripts/check_foundation.py
        ;;
    "test")
        echo "Running test suite..."
        pytest backend/tests
        ;;
    "lint")
        echo "Running linter checks..."
        ruff check backend/
        mypy backend/app
        ;;
    "server")
        echo "Starting backend development server..."
        uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    *)
        echo "ReviewAI Dev Commands:"
        echo "  ./scripts/dev.sh check   - Run foundation self-checks"
        echo "  ./scripts/dev.sh test    - Run pytest test suite"
        echo "  ./scripts/dev.sh lint    - Run ruff & mypy checks"
        echo "  ./scripts/dev.sh server  - Launch local FastAPI server"
        ;;
esac
