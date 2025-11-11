#!/bin/bash

# Test runner script for TMDB Movie Recommendation Application

echo "🧪 Running Tests for TMDB Movie Recommendation Application"
echo "=========================================================="
echo ""

# Load .env file if it exists (for API key)
if [ -f .env ]; then
    echo "📝 Loading .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest is not installed. Installing..."
    pip install pytest pytest-mock pytest-cov requests-mock
fi

# Run tests based on argument
case "${1:-all}" in
    unit)
        echo "📦 Running Unit Tests (mocked)..."
        pytest tests/unit/ -v -m unit
        ;;
    integration)
        echo "🔗 Running Integration Tests (mocked)..."
        pytest tests/integration/ -v -m integration
        ;;
    e2e)
        echo "🚀 Running End-to-End Tests (mocked)..."
        pytest tests/integration/ -v -m e2e
        ;;
    timeline)
        echo "⏱️  Running Complete Timeline Tests (mocked)..."
        pytest tests/integration/test_complete_timeline.py -v
        ;;
    api)
        echo "🌐 Running Real API Tests..."
        if [ -z "$TMDB_API_KEY" ]; then
            echo "❌ Error: TMDB_API_KEY not found in .env file or environment"
            echo "   Make sure your .env file contains: TMDB_API_KEY=your_api_key"
            echo "   Or set it with: export TMDB_API_KEY=your_api_key"
            exit 1
        fi
        pytest tests/api/ -v -m api -o addopts=""
        ;;
    mocked)
        echo "🎭 Running All Mocked Tests (unit + integration)..."
        pytest tests/unit/ tests/integration/ -v -m "not api"
        ;;
    coverage)
        echo "📊 Running Tests with Coverage (mocked only)..."
        pytest --cov=src --cov-report=html --cov-report=term-missing -v -m "not api"
        ;;
    all)
        echo "🧪 Running All Mocked Tests (excluding API tests)..."
        pytest tests/ -v -m "not api"
        ;;
    *)
        echo "Usage: $0 [unit|integration|e2e|timeline|api|mocked|coverage|all]"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only (mocked)"
        echo "  integration - Run integration tests only (mocked)"
        echo "  e2e         - Run end-to-end tests only (mocked)"
        echo "  timeline    - Run complete timeline tests (mocked)"
        echo "  api         - Run real API tests (requires TMDB_API_KEY)"
        echo "  mocked      - Run all mocked tests (unit + integration)"
        echo "  coverage    - Run tests with coverage report (mocked only)"
        echo "  all         - Run all mocked tests (default, excludes API tests)"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed!"

