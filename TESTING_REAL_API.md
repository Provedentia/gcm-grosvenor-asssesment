# Testing with Real TMDB API

## Quick Start

### Step 1: Set Your API Key

```bash
# Option 1: Set as environment variable (temporary)
export TMDB_API_KEY=your_api_key_here

# Option 2: Add to .env file (persistent)
echo "TMDB_API_KEY=your_api_key_here" >> .env
```

**Get your API key from:** https://www.themoviedb.org/settings/api

### Step 2: Run Real API Tests

```bash
# Run all real API tests
pytest tests/api/ -v -m api

# Or use the test runner script
./run_tests.sh api
```

## Example Commands

### Run All Real API Tests
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/ -v -m api
```

### Run Specific Real API Test
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/test_real_tmdb_api.py::TestRealTMDBAPI::test_real_api_get_movies_by_year -v
```

### Run Real API Tests with Verbose Output
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/ -v -m api -s
```

### Run Real API Tests for Complete Workflow
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/test_real_tmdb_api.py::TestRealCompleteWorkflow -v
```

## What Tests Are Available

### 1. Basic API Client Tests
- `test_real_api_client_initialization` - Test client initialization
- `test_real_api_get_movies_by_year` - Test getting movies by year
- `test_real_api_get_movie_details` - Test getting movie details
- `test_real_api_get_movie_keywords` - Test getting keywords
- `test_real_api_get_similar_movies` - Test getting similar movies
- `test_real_api_get_movie_recommendations` - Test getting recommendations
- `test_real_api_discover_movies_with_genre` - Test genre filtering

### 2. MovieService Tests with Real API
- `test_real_get_top_movies_by_year` - Get top movies from real API
- `test_real_export_top_movies_to_csv` - Export to CSV with real data
- `test_real_sort_movies_by_name_with_articles` - Test sorting with real data
- `test_real_sort_movies_by_name_without_articles` - Test article removal with real data

### 3. RecommendationService Tests with Real API
- `test_real_find_similar_movies` - Find similar movies using real API
- `test_real_get_similar_movies_for_multiple` - Find similar movies for multiple movies

### 4. Complete Workflow Tests with Real API
- `test_real_complete_workflow_top_movies` - Complete workflow with real API
- `test_real_complete_workflow_with_similar_movies` - Complete workflow with similar movies

## Expected Output

When you run real API tests, you'll see:

```
tests/api/test_real_tmdb_api.py::TestRealTMDBAPI::test_real_api_client_initialization PASSED
tests/api/test_real_tmdb_api.py::TestRealTMDBAPI::test_real_api_get_movies_by_year PASSED
tests/api/test_real_tmdb_api.py::TestRealMovieService::test_real_get_top_movies_by_year PASSED
...
```

## Troubleshooting

### Issue: Tests are skipped
**Error:** `SKIPPED [1] tests/api/conftest.py:28: TMDB_API_KEY environment variable not set. Skipping real API tests.`

**Solution:**
```bash
export TMDB_API_KEY=your_api_key
```

### Issue: API rate limiting
**Error:** `429 Too Many Requests` or `Rate limit exceeded`

**Solution:**
- Wait a few seconds between test runs
- Reduce number of API calls in tests
- Use mocked tests for development

### Issue: Invalid API key
**Error:** `401 Unauthorized` or `Invalid API key`

**Solution:**
- Verify your API key is correct
- Check that API key is set: `echo $TMDB_API_KEY`
- Get a new API key from TMDB

### Issue: Network errors
**Error:** `ConnectionError` or `Timeout`

**Solution:**
- Check your internet connection
- Verify TMDB API is accessible
- Check firewall settings

## Testing Specific Functionality

### Test Movie Retrieval
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/test_real_tmdb_api.py::TestRealMovieService::test_real_get_top_movies_by_year -v -s
```

### Test CSV Export
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/test_real_tmdb_api.py::TestRealMovieService::test_real_export_top_movies_to_csv -v -s
```

### Test Similar Movies
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/test_real_tmdb_api.py::TestRealRecommendationService::test_real_find_similar_movies -v -s
```

### Test Complete Workflow
```bash
export TMDB_API_KEY=your_api_key
pytest tests/api/test_real_tmdb_api.py::TestRealCompleteWorkflow -v -s
```

## Example: Testing with Real Data

```bash
# 1. Set API key
export TMDB_API_KEY=your_api_key

# 2. Run a specific test
pytest tests/api/test_real_tmdb_api.py::TestRealMovieService::test_real_get_top_movies_by_year -v -s

# Output will show:
# - Real movies retrieved from TMDB
# - Actual movie titles, years, ratings
# - Real API response data
```

## Performance Notes

- Real API tests are slower than mocked tests
- Each test makes actual HTTP requests to TMDB
- Tests are marked as `@pytest.mark.slow`
- May take 10-30 seconds depending on number of tests

## Best Practices

1. **Use mocked tests for development** - Faster, no API key needed
2. **Use real API tests for validation** - Verify API integration works
3. **Run real API tests before deployment** - Ensure everything works with real data
4. **Don't run real API tests in tight loops** - Respect rate limits

## Verify API Key is Set

```bash
# Check if API key is set
echo $TMDB_API_KEY

# If empty, set it
export TMDB_API_KEY=your_api_key

# Verify it's set
echo $TMDB_API_KEY
```

## Running Tests in Python

You can also test the real API directly in Python:

```python
import os
from src.api.TMDB import TMDBClient

# Set API key
os.environ["TMDB_API_KEY"] = "your_api_key"

# Create client
client = TMDBClient()

# Test API call
response = client.get_movies_by_year(year=2020, page=1)
print(f"Found {len(response['results'])} movies")
```

