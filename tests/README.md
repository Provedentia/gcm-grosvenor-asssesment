# Test Suite

## Quick Start

### Run Mocked Tests (Default)
```bash
# Run all mocked tests
pytest
# or
./run_tests.sh all
```

### Run Real API Tests
```bash
# Set API key first
export TMDB_API_KEY=your_api_key

# Run real API tests
pytest tests/api/ -v -m api
# or
./run_tests.sh api
```

## Test Organization

### Mocked Tests (No API Key Required)
- **Location**: `tests/unit/` and `tests/integration/`
- **Characteristics**: Fast, deterministic, use mock data
- **Run by default**: Yes

### Real API Tests (Requires API Key)
- **Location**: `tests/api/`
- **Characteristics**: Make real API calls, require API key
- **Run by default**: No (excluded by default)

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
└── api/                     # Real API tests
    ├── test_real_tmdb_api.py
    └── README.md
```

## Running Tests

See `TEST_ORGANIZATION.md` for detailed information about test organization and running tests.

## Test Markers

- `@pytest.mark.unit`: Unit tests (mocked)
- `@pytest.mark.integration`: Integration tests (mocked)
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.api`: Real API tests (require API key)
- `@pytest.mark.slow`: Slow tests

## Default Behavior

By default, **only mocked tests run**. Real API tests are excluded unless explicitly requested with `-m api` or `./run_tests.sh api`.

This ensures:
- ✅ Tests run without API key
- ✅ Fast test execution
- ✅ Deterministic results
- ✅ Suitable for CI/CD
