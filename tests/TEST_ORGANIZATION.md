# Test Organization

## Overview

Tests are organized into two distinct categories:

1. **Mocked Tests** (default): Use mock data, no API key required
2. **Real API Tests**: Use actual TMDB API, require API key

## Test Structure

```
tests/
├── unit/                    # Unit tests (mocked)
│   ├── test_movie_service.py
│   ├── test_recommendation_service.py
│   └── test_export_service.py
├── integration/             # Integration tests (mocked)
│   ├── test_full_workflow.py
│   ├── test_end_to_end.py
│   └── test_complete_timeline.py
└── api/                     # Real API tests (require API key)
    ├── test_real_tmdb_api.py
    └── conftest.py
```

## Mocked Tests

### Location
- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for complete workflows

### Characteristics
- ✅ Use mock data (no real API calls)
- ✅ Fast execution
- ✅ No API key required
- ✅ Deterministic results
- ✅ Run by default

### Running Mocked Tests

```bash
# Run all mocked tests (default)
pytest
# or
./run_tests.sh all

# Run specific test suites
pytest tests/unit/ -m unit
pytest tests/integration/ -m integration
./run_tests.sh unit
./run_tests.sh integration
```

## Real API Tests

### Location
- `tests/api/`: Tests that use the actual TMDB API

### Characteristics
- ⚠️ Make real API calls to TMDB
- ⚠️ Require valid TMDB API key
- ⚠️ Require internet connection
- ⚠️ Subject to API rate limits
- ⚠️ May be slower
- ⚠️ Excluded by default

### Running Real API Tests

```bash
# Set API key
export TMDB_API_KEY=your_api_key_here

# Run real API tests
pytest tests/api/ -v -m api
# or
./run_tests.sh api
```

### Test Coverage

Real API tests cover:
- ✅ TMDB API client functionality
- ✅ Movie retrieval from real API
- ✅ Movie details and keywords
- ✅ Similar movies and recommendations
- ✅ Complete workflow with real data
- ✅ CSV export with real data
- ✅ Sorting with real movie titles

## Test Markers

### Markers for Mocked Tests
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.e2e`: End-to-end tests (mocked)

### Markers for Real API Tests
- `@pytest.mark.api`: Real API tests
- `@pytest.mark.slow`: Slow tests (real API calls)
- `@pytest.mark.e2e`: End-to-end tests (real API)

## Pytest Configuration

### Default Behavior
- **Excludes API tests by default** (`-m "not api"` in `pytest.ini`)
- Runs only mocked tests unless explicitly requested
- Ensures tests can run without API key

### Running Different Test Types

```bash
# Mocked tests only (default)
pytest

# Real API tests only
pytest -m api

# All tests (mocked + API)
pytest -m ""

# Exclude slow tests
pytest -m "not slow"

# Unit tests only (mocked)
pytest -m unit

# Integration tests only (mocked)
pytest -m integration
```

## Test Runner Script

The `run_tests.sh` script provides convenient commands:

```bash
./run_tests.sh all          # Run all mocked tests (default)
./run_tests.sh unit         # Run unit tests (mocked)
./run_tests.sh integration  # Run integration tests (mocked)
./run_tests.sh e2e          # Run end-to-end tests (mocked)
./run_tests.sh timeline     # Run complete timeline test (mocked)
./run_tests.sh mocked       # Run all mocked tests
./run_tests.sh api          # Run real API tests (requires API key)
./run_tests.sh coverage     # Run with coverage (mocked only)
```

## Best Practices

### For Development
1. **Use mocked tests** during development (faster, no API key needed)
2. Run mocked tests frequently to catch issues early
3. Use real API tests sparingly (slower, requires API key)

### For CI/CD
1. **Run mocked tests** in CI pipeline (fast, reliable)
2. Optionally run real API tests in separate pipeline stage
3. Set up API key as CI secret if running real API tests

### For Testing
1. **Mocked tests**: Test logic, edge cases, error handling
2. **Real API tests**: Verify API integration, test with real data
3. Use real API tests to validate API changes and compatibility

## Fixtures

### Mocked Test Fixtures
- `mock_tmdb_api_response`: Mock API response
- `mock_movie_details_response`: Mock movie details
- `mock_keywords_response`: Mock keywords
- `mock_similar_movies_response`: Mock similar movies
- `sample_movies`: Sample Movie models
- `test_output_dir`: Temporary output directory

### Real API Test Fixtures
- `real_tmdb_client`: Real TMDBClient instance
- `real_movie_service`: Real MovieService instance
- `real_recommendation_service`: Real RecommendationService instance
- `real_export_service`: Real ExportService instance

## Examples

### Example: Running Mocked Tests

```bash
# Run all mocked tests
pytest

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run with coverage
pytest --cov=src --cov-report=html -m "not api"
```

### Example: Running Real API Tests

```bash
# Set API key
export TMDB_API_KEY=your_api_key

# Run all real API tests
pytest tests/api/ -v -m api

# Run specific real API test
pytest tests/api/test_real_tmdb_api.py::TestRealTMDBAPI::test_real_api_get_movies_by_year -v

# Run with verbose output
pytest tests/api/ -v -m api -s
```

## Troubleshooting

### API Tests Skipped
If API tests are skipped, check:
1. Is `TMDB_API_KEY` environment variable set?
2. Is the API key valid?
3. Do you have internet connection?

### Mocked Tests Failing
If mocked tests fail:
1. Check that mock fixtures are properly set up
2. Verify test data matches expected structure
3. Check that side_effect is configured correctly for movie ID-based responses

### Rate Limiting
If you encounter rate limiting with real API tests:
1. Reduce number of API calls in tests
2. Add delays between API calls
3. Use mocked tests for development

