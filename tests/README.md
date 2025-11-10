# Tests

This directory contains tests for the TMDB Movie Recommendation Application.

## Test Structure

```
tests/
├── unit/                  # Unit tests for individual components
│   ├── test_movie_service.py
│   ├── test_recommendation_service.py
│   └── test_export_service.py
├── integration/           # Integration tests
│   ├── test_full_workflow.py
│   └── test_end_to_end.py
├── conftest.py            # Pytest fixtures and configuration
└── README.md              # This file
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/ -m unit
```

### Run Integration Tests Only

```bash
pytest tests/integration/ -m integration
```

### Run End-to-End Tests Only

```bash
pytest tests/integration/ -m e2e
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/unit/test_movie_service.py
```

### Run Specific Test

```bash
pytest tests/unit/test_movie_service.py::TestMovieService::test_sort_movies_by_votes
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Output Capture Disabled

```bash
pytest -s
```

## Test Categories

### Unit Tests

- **test_movie_service.py**: Tests for MovieService
  - Sorting methods (votes, name, name_no_articles)
  - Movie retrieval and enrichment
  - Export data preparation

- **test_recommendation_service.py**: Tests for RecommendationService
  - Similarity calculations (genre, keyword, rating, year)
  - Similarity score computation
  - Similar movie finding

- **test_export_service.py**: Tests for ExportService
  - CSV export functionality
  - File operations
  - Data formatting

### Integration Tests

- **test_full_workflow.py**: Tests for complete workflows
  - Top movies retrieval and export
  - Similar movies finding and export
  - Sorting verification
  - Error handling

- **test_end_to_end.py**: End-to-end tests
  - Complete application workflow
  - Data consistency
  - CSV format validation

## Test Fixtures

Fixtures are defined in `conftest.py`:

- `mock_tmdb_api_response`: Mock TMDB API discover response
- `mock_movie_details_response`: Mock TMDB API movie details response
- `mock_keywords_response`: Mock TMDB API keywords response
- `mock_similar_movies_response`: Mock TMDB API similar movies response
- `sample_movies`: Sample Movie models for testing
- `test_output_dir`: Temporary output directory for test files
- `mock_env_vars`: Mock environment variables

## Writing New Tests

### Unit Test Example

```python
def test_feature_name(service_fixture, sample_data):
    """Test description."""
    # Arrange
    input_data = sample_data
    
    # Act
    result = service_fixture.method(input_data)
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

### Integration Test Example

```python
@pytest.mark.integration
def test_workflow_feature(setup_mocked_services):
    """Test complete workflow."""
    services = setup_mocked_services
    # Test workflow steps
    pass
```

## Test Data

Test data is mocked to avoid making real API calls:
- All TMDB API calls are mocked
- Test data is defined in fixtures
- No real API keys are required for tests

## Continuous Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=src --cov-report=xml
```

## Troubleshooting

### Tests Failing

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify pytest is installed: `pip install pytest pytest-mock pytest-cov`
3. Check test output for specific errors: `pytest -v`

### Mock Issues

1. Verify fixtures are properly set up in `conftest.py`
2. Check that mocks are returning expected data
3. Ensure mock patching is correct

### Environment Variables

Tests use mocked environment variables via the `mock_env_vars` fixture.
No real `.env` file is required for tests.

