# Test Suite

Comprehensive test suite for the Movie Recommendation System with unit, integration, and end-to-end tests.

## Quick Start

```bash
# Run all tests (default: mocked tests only)
pytest

# Run specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest -m e2e                   # End-to-end tests only

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run real API tests (requires TMDB API key)
export TMDB_API_KEY=your_api_key_here
pytest -m api
```

## Test Structure

```
tests/
├── conftest.py                              # Shared fixtures and test configuration
├── unit/                                    # Unit tests (isolated components)
│   ├── test_movie_service.py                # MovieService tests
│   ├── test_movie_recommendation_engine.py  # MovieRecommendationEngine tests
│   └── test_export_service.py               # ExportService tests
├── integration/                             # Integration tests (service interactions)
│   ├── test_end_to_end.py                   # Complete workflow tests
│   └── test_complete_timeline.py            # Assignment requirements validation
└── api/                                     # Real API integration tests
    ├── conftest.py                          # API test fixtures
    └── test_real_tmdb_api.py                # Real TMDB API tests (deselected by default)
```

## Test Types

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Mocking**: All external dependencies mocked
- **Speed**: Fast (< 1 second)
- **API Key**: Not required

### Integration Tests
- **Purpose**: Test service interactions and complete workflows
- **Mocking**: External APIs mocked, internal services real
- **Speed**: Fast (< 5 seconds)
- **API Key**: Not required

### API Tests
- **Purpose**: Validate real TMDB API integration
- **Mocking**: None (uses real API)
- **Speed**: Slower (network dependent)
- **API Key**: Required
- **Note**: Excluded by default to avoid rate limits

## Test Markers

```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.e2e           # End-to-end workflow tests
@pytest.mark.api           # Real API tests (require key)
@pytest.mark.slow          # Long-running tests
```

## Key Features

- Comprehensive test coverage across all services
- Mock data fixtures for consistent, repeatable tests
- Real API tests for validation (optional)
- Detailed similarity metrics verification
- CSV export validation
- Error handling and edge case testing

## Configuration

Test configuration is managed in `pytest.ini` at the project root. By default:
- Mocked tests run automatically
- Real API tests are excluded (use `-m api` to include)
- Verbose output enabled
- Warnings disabled for cleaner output

## Why Some Tests Are Deselected

When you run the test suite, you may see output like: `47 passed, 15 deselected`

### Deselected Tests Explained

**API tests are deselected by default** for the following reasons:

1. **TMDB API Key Required**: These tests require a valid TMDB API key set in your environment:
   ```bash
   export TMDB_API_KEY=your_api_key_here
   ```

2. **Rate Limiting**: The TMDB API has rate limits. Running these tests frequently could exhaust your quota.

3. **Network Dependency**: API tests depend on external network connectivity and TMDB service availability.

4. **Slower Execution**: Real API calls are much slower than mocked tests (seconds vs milliseconds).

5. **Consistent CI/CD**: Deselecting by default ensures fast, reliable test runs in CI/CD pipelines without requiring API keys.

### Which Tests Are Deselected?

All tests marked with `@pytest.mark.api` in `tests/api/test_real_tmdb_api.py`:
- Real TMDB client initialization tests
- Live API endpoint tests (discover, details, keywords, credits)
- Real movie service integration tests
- Real recommendation service tests
- Complete workflow tests with actual API calls

### Running Deselected Tests

To include API tests in your test run:

```bash
# Run ONLY API tests
pytest -m api

# Run ALL tests (including API tests)
pytest -m "api or not api"

# Or simply remove the deselect marker from pytest.ini
```

**Note**: Make sure you have a `.env` file with your TMDB API key or export it in your shell before running API tests.
