# TMDB Movie Recommendation Application

An application that retrieves top movies from TMDB API for a given year and exports them to CSV files with multiple sorting options.

## Setup

### 1. Install Dependencies

```bash
# Install runtime dependencies only
pip install -r requirements.txt

# Or install with development dependencies (for testing)
pip install -r requirements-dev.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
TMDB_API_KEY=your_tmdb_api_key_here
```

You can get a TMDB API key from: https://www.themoviedb.org/settings/api

### 3. Configure Settings (Optional)

Edit `config/config.yaml` to customize:
- Minimum vote count
- Minimum vote average
- API timeout and retry settings
- Logging configuration

## Usage

### Quick Start

1. **Set up your TMDB API key:**
   ```bash
   # Create .env file
   echo "TMDB_API_KEY=your_api_key_here" > .env
   ```

2. **Run the application:**
   ```bash
   # Get top 10 movies from 2020
   python main.py --year 2020
   ```

### Command Line Interface

Run the application from the command line:

```bash
# Get top 10 movies from 2020
python main.py --year 2020

# Get top 5 movies from 2019 with custom output file
python main.py --year 2019 --top-n 5 --output movies_2019.csv

# Get top 10 movies from 2021 with custom filters
python main.py --year 2021 --min-votes 500 --min-rating 7.0
```

### Getting Similar Movies

To also find and export similar movies:

```bash
# Get top 10 movies from 2020 and find 3 similar movies for each
python main.py --year 2020 --similar-movies --similar-limit 3
```

This will create two CSV files:
- `data/top_movies.csv` - Top movies with 3 sorting methods
- `data/similar_movies.csv` - Similar movies with similarity metrics

### Python API

You can also use the service directly in Python:

```python
from src.services.movie_service import MovieService

# Initialize service
service = MovieService()

# Get and export top movies
movies, csv_path = service.get_and_export_top_movies(
    year=2020,
    top_n=10,
    filename="top_movies.csv"
)

print(f"Exported {len(movies)} movies to {csv_path}")
```

## Output

The application generates CSV files in the `data/` directory with the following columns:

- `sort_method`: How the movies are sorted (votes, name, name_no_articles)
- `id`: TMDB movie ID
- `title`: Movie title
- `release_date`: Release date
- `release_year`: Release year
- `vote_count`: Number of votes
- `vote_average`: Average rating
- `popularity`: Popularity score
- `overview`: Movie description
- `poster_path`: Poster image path
- `backdrop_path`: Backdrop image path
- `genres`: Comma-separated list of genres
- `keywords`: Comma-separated list of keywords
- `runtime`: Runtime in minutes
- `tagline`: Movie tagline
- `imdb_id`: IMDB ID

## Features

- Retrieves top N movies from a specified year
- Sorts movies by votes (highest first)
- Sorts movies by name (including articles like "A", "The")
- Sorts movies by name (ignoring articles)
- Exports all three sorted lists to the same CSV file
- Enriches movies with detailed information (genres, keywords, etc.)
- Finds similar movies using similarity matching algorithm
- Exports similar movies with detailed similarity metrics

## Project Structure

```
.
├── src/
│   ├── api/
│   │   └── TMDB.py          # TMDB API client
│   ├── models/
│   │   └── Movies.py        # Movie data models
│   ├── services/
│   │   ├── movie_service.py # Movie business logic
│   │   ├── recommendation_service.py # Similarity matching and recommendations
│   │   └── export_service.py # CSV export service
│   └── utils/
│       ├── config.py        # Configuration management
│       └── logger.py        # Logging utilities
├── config/
│   └── config.yaml          # Application configuration
├── data/                    # Output directory for CSV files
├── logs/                    # Log files
└── main.py                  # Main entry point
```

## Requirements

- Python 3.8+
- TMDB API key
- See `requirements.txt` for Python dependencies

## Logging

Logs are written to:
- Console (colored output)
- File: `logs/app.log` (with rotation)

## Testing

### Test Organization

Tests are organized into two categories:

1. **Mocked Tests** (default): Use mock data, no API key required
   - `tests/unit/`: Unit tests for individual components
   - `tests/integration/`: Integration tests for complete workflows

2. **Real API Tests**: Use actual TMDB API, require API key
   - `tests/api/`: Tests that make real API calls

**By default, only mocked tests run.** Real API tests are excluded unless explicitly requested.

### Running Tests

#### Mocked Tests (Default)

```bash
# Run all mocked tests (default)
pytest
# or
./run_tests.sh all

# Run unit tests only
pytest tests/unit/ -m unit
# or
./run_tests.sh unit

# Run integration tests only
pytest tests/integration/ -m integration
# or
./run_tests.sh integration

# Run end-to-end tests
pytest tests/integration/ -m e2e
# or
./run_tests.sh e2e

# Run complete timeline test
pytest tests/integration/test_complete_timeline.py -v
# or
./run_tests.sh timeline

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing -m "not api"
# or
./run_tests.sh coverage
```

#### Real API Tests

**Requires TMDB_API_KEY environment variable:**

```bash
# Set API key
export TMDB_API_KEY=your_api_key_here

# Run real API tests
pytest tests/api/ -v -m api
# or
./run_tests.sh api
```

**Note:** Real API tests are excluded by default. They require:
- Valid TMDB API key
- Internet connection
- May be subject to API rate limits

### Using the Test Runner Script

```bash
# Run all mocked tests (default)
./run_tests.sh all

# Run specific test suite (mocked)
./run_tests.sh unit
./run_tests.sh integration
./run_tests.sh e2e
./run_tests.sh timeline
./run_tests.sh mocked  # All mocked tests

# Run real API tests (requires API key)
./run_tests.sh api

# Run with coverage (mocked only)
./run_tests.sh coverage
```

### Test Structure

#### Mocked Tests (No API Key Required)

- **Unit Tests** (`tests/unit/`): Test individual components with mocks
  - `test_movie_service.py`: Movie service tests
  - `test_recommendation_service.py`: Recommendation service tests
  - `test_export_service.py`: Export service tests

- **Integration Tests** (`tests/integration/`): Test complete workflows with mocks
  - `test_full_workflow.py`: Full workflow tests
  - `test_end_to_end.py`: End-to-end tests
  - `test_complete_timeline.py`: Complete timeline test (assignment requirements)

#### Real API Tests (Requires API Key)

- **API Tests** (`tests/api/`): Tests that use the actual TMDB API
  - `test_real_tmdb_api.py`: Real API client tests
  - Tests for MovieService with real API
  - Tests for RecommendationService with real API
  - End-to-end tests with real API

See `tests/api/README.md` for more details on real API tests.

### Test Coverage

Tests cover:
- ✅ Movie retrieval and sorting
- ✅ CSV export with multiple sort methods
- ✅ Similar movie finding
- ✅ Similarity score calculation
- ✅ Complete workflow from API to CSV
- ✅ Error handling
- ✅ Data validation

## Error Handling

The application includes comprehensive error handling:
- API request failures with retry logic
- Invalid movie data validation
- File I/O errors
- Configuration errors

