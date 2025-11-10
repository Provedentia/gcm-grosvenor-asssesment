# Test Summary

## Overview

Comprehensive test suite for the TMDB Movie Recommendation Application covering the complete workflow from API calls to CSV export.

## Test Files

### Unit Tests (`tests/unit/`)

1. **test_movie_service.py**
   - Tests movie sorting (by votes, by name with/without articles)
   - Tests movie retrieval and enrichment
   - Tests export data preparation
   - Tests error handling

2. **test_recommendation_service.py**
   - Tests similarity calculations (genre, keyword, rating, year)
   - Tests overall similarity score computation
   - Tests similar movie finding
   - Tests data preparation for export

3. **test_export_service.py**
   - Tests CSV export functionality
   - Tests file operations (create, append)
   - Tests data formatting
   - Tests error handling for empty data

### Integration Tests (`tests/integration/`)

1. **test_full_workflow.py**
   - Tests complete workflow: get movies → export to CSV
   - Tests workflow with similar movies
   - Tests sorting verification
   - Tests error handling in workflow

2. **test_end_to_end.py**
   - Tests complete application workflow
   - Tests data consistency across workflow
   - Tests CSV format validation
   - Tests all required fields are present

3. **test_complete_timeline.py** ⭐
   - **Main test for assignment requirements**
   - Tests complete timeline from start to finish
   - Verifies all assignment requirements:
     - Top 10 movies from a year
     - Sort by votes and export
     - Sort by name (with articles) and append
     - Sort by name (without articles) and append
     - Find 3 similar movies for each top 10 movie
     - Export 30 similar movies with metrics
   - Validates CSV structure and content
   - Verifies similarity scores and metrics

## Test Fixtures (`conftest.py`)

- `mock_tmdb_api_response`: Mock TMDB discover API response
- `mock_movie_details_response`: Mock TMDB movie details response
- `mock_keywords_response`: Mock TMDB keywords response
- `mock_similar_movies_response`: Mock TMDB similar movies response
- `sample_movies`: Pre-configured Movie models for testing
- `test_output_dir`: Temporary directory for test outputs
- `mock_env_vars`: Mock environment variables

## Running Tests

### Quick Start

```bash
# Install dependencies
pip install pytest pytest-mock pytest-cov requests-mock

# Run all tests
pytest

# Run complete timeline test (assignment requirements)
pytest tests/integration/test_complete_timeline.py -v
```

### Test Categories

```bash
# Unit tests
pytest tests/unit/ -m unit

# Integration tests
pytest tests/integration/ -m integration

# End-to-end tests
pytest tests/integration/ -m e2e

# Complete timeline test
pytest tests/integration/test_complete_timeline.py -v
```

### With Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

## Test Coverage

### What's Tested

✅ **Movie Service**
- Movie retrieval from TMDB API
- Movie sorting (votes, name with/without articles)
- Movie enrichment with details
- Export data preparation

✅ **Recommendation Service**
- Genre similarity calculation
- Keyword similarity calculation
- Rating similarity calculation
- Year similarity calculation
- Overall similarity score computation
- Similar movie finding
- Data preparation for export

✅ **Export Service**
- CSV file creation
- CSV file appending
- Data formatting
- Field validation
- Error handling

✅ **Complete Workflow**
- End-to-end workflow from API to CSV
- Multiple sort methods in same CSV
- Similar movies export with metrics
- Data consistency validation
- CSV format validation

✅ **Error Handling**
- API failures
- Empty results
- Invalid data
- File I/O errors

## Test Data

All tests use mocked data to avoid:
- Real API calls
- Rate limiting issues
- Network dependencies
- API key requirements

Mock data includes:
- 10 sample movies from year 2020
- Movie details with genres and keywords
- Similar movies for each movie
- Realistic vote counts and ratings

## Assignment Requirements Validation

The `test_complete_timeline.py` test validates all assignment requirements:

1. ✅ **Top 10 movies from a year** - Verified
2. ✅ **Sort by votes (highest first)** - Verified
3. ✅ **Sort by name (with articles)** - Verified
4. ✅ **Sort by name (without articles)** - Verified
5. ✅ **All three sorts in same CSV** - Verified
6. ✅ **3 similar movies per top 10 movie** - Verified
7. ✅ **30 similar movies total** - Verified
8. ✅ **Similar movies in separate CSV** - Verified
9. ✅ **Similarity metrics included** - Verified

## Expected Test Output

When running the complete timeline test, you should see:

```
📽️  Step 1: Getting top 10 movies from year 2020...
✅ Step 1 Complete: 10 movies exported to top_movies_2020.csv

🔍 Step 2: Finding 3 similar movies for each movie...
✅ Step 2 Complete: Found 30 similar movies

📊 Step 3: Preparing similar movies data for export...
✅ Step 3 Complete: Prepared 30 entries for export

💾 Step 4: Exporting similar movies to CSV...
✅ Step 4 Complete: Exported 30 similar movie entries to similar_movies_2020.csv

📋 Final Verification:
  - Top movies CSV: top_movies_2020.csv (30 rows)
  - Similar movies CSV: similar_movies_2020.csv (30 rows)
  - Total original movies: 10
  - Total similar movies: 30
  - Average similar movies per original: 3.0

✅ All requirements met! Complete timeline test passed.
```

## Notes

- All tests use mocked TMDB API responses
- No real API keys required for testing
- Tests are isolated and can run in any order
- Test data is cleaned up automatically
- Tests validate both functionality and data integrity

