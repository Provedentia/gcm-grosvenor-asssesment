# Real TMDB API Tests

This directory contains tests that use the **actual TMDB API** (not mocks).

## Requirements

- **TMDB API Key**: You must have a valid TMDB API key
- Set the `TMDB_API_KEY` environment variable:
  ```bash
  export TMDB_API_KEY=your_api_key_here
  ```

## Running Real API Tests

### Run all API tests:
```bash
pytest tests/api/ -v -m api
```

### Or use the test runner script:
```bash
./run_tests.sh api
```

## Test Structure

- **`test_real_tmdb_api.py`**: Tests for the TMDB API client using real API calls
- **`TestRealMovieService`**: Tests for MovieService using real API
- **`TestRealRecommendationService`**: Tests for RecommendationService using real API
- **`TestRealCompleteWorkflow`**: End-to-end tests using real API

## Important Notes

1. **API Rate Limits**: These tests make real API calls and are subject to TMDB rate limits
2. **API Key Required**: Tests will be skipped if `TMDB_API_KEY` is not set
3. **Slow Tests**: These tests are marked as `@pytest.mark.slow` and may take longer to run
4. **Network Required**: These tests require an active internet connection
5. **Cost**: Free tier TMDB API has rate limits but no monetary cost

## Test Markers

- `@pytest.mark.api`: Marks tests that use the real API
- `@pytest.mark.slow`: Marks tests that take a long time
- `@pytest.mark.e2e`: Marks end-to-end tests

## Excluding API Tests

By default, API tests are **excluded** from the test suite. To run only mocked tests:

```bash
pytest -m "not api"
```

Or use the test runner:
```bash
./run_tests.sh all  # Runs only mocked tests
./run_tests.sh mocked  # Runs all mocked tests
```

## Fixtures

- `real_tmdb_client`: Real TMDBClient instance
- `real_movie_service`: Real MovieService instance
- `real_recommendation_service`: Real RecommendationService instance
- `real_export_service`: Real ExportService instance with temporary output directory

## Example Test Run

```bash
# Set API key
export TMDB_API_KEY=your_api_key

# Run API tests
pytest tests/api/test_real_tmdb_api.py::TestRealTMDBAPI::test_real_api_get_movies_by_year -v

# Run all API tests
pytest tests/api/ -v -m api

# Run with verbose output
pytest tests/api/ -v -m api -s
```

