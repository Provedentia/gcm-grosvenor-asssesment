#!/bin/bash

# Test runner script for TMDB Movie Recommendation Application

echo "🧪 Running Tests for TMDB Movie Recommendation Application"
echo "=========================================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest is not installed. Installing..."
    pip install pytest pytest-mock pytest-cov requests-mock
fi

# Run tests based on argument
case "${1:-all}" in
    unit)
        echo "📦 Running Unit Tests..."
        pytest tests/unit/ -v -m unit
        ;;
    integration)
        echo "🔗 Running Integration Tests..."
        pytest tests/integration/ -v -m integration
        ;;
    e2e)
        echo "🚀 Running End-to-End Tests..."
        pytest tests/integration/ -v -m e2e
        ;;
    timeline)
        echo "⏱️  Running Complete Timeline Tests..."
        pytest tests/integration/test_complete_timeline.py -v
        ;;
    coverage)
        echo "📊 Running Tests with Coverage..."
        pytest --cov=src --cov-report=html --cov-report=term-missing -v
        ;;
    all)
        echo "🧪 Running All Tests..."
        pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 [unit|integration|e2e|timeline|coverage|all]"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  e2e         - Run end-to-end tests only"
        echo "  timeline    - Run complete timeline tests"
        echo "  coverage    - Run tests with coverage report"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed!"

