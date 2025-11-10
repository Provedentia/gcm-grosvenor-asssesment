"""
Pytest configuration and fixtures for testing.
"""

import os
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

# Import Movie for type hints (imported inside fixture to avoid circular imports)
from src.models.Movies import Movie


@pytest.fixture
def mock_tmdb_api_response() -> Dict[str, Any]:
    """Mock TMDB API response for discover/movie endpoint."""
    return {
        "page": 1,
        "results": [
            {
                "id": 1,
                "title": "The Matrix",
                "release_date": "1999-03-31",
                "vote_count": 25000,
                "vote_average": 8.7,
                "popularity": 85.5,
                "overview": "A computer hacker learns about the true nature of reality",
                "poster_path": "/poster1.jpg",
                "backdrop_path": "/backdrop1.jpg",
                "adult": False,
                "original_language": "en",
                "original_title": "The Matrix",
                "video": False,
                "genre_ids": [28, 878],
            },
            {
                "id": 2,
                "title": "Inception",
                "release_date": "1999-07-16",  # Changed to 1999 for testing
                "vote_count": 30000,
                "vote_average": 8.8,
                "popularity": 90.2,
                "overview": "A skilled thief is given a chance at redemption",
                "poster_path": "/poster2.jpg",
                "backdrop_path": "/backdrop2.jpg",
                "adult": False,
                "original_language": "en",
                "original_title": "Inception",
                "video": False,
                "genre_ids": [28, 878, 53],
            },
            {
                "id": 3,
                "title": "A Beautiful Mind",
                "release_date": "1999-12-21",  # Changed to 1999 for testing
                "vote_count": 20000,
                "vote_average": 8.2,
                "popularity": 75.3,
                "overview": "A mathematical genius",
                "poster_path": "/poster3.jpg",
                "backdrop_path": "/backdrop3.jpg",
                "adult": False,
                "original_language": "en",
                "original_title": "A Beautiful Mind",
                "video": False,
                "genre_ids": [18, 36],
            },
        ],
        "total_pages": 1,
        "total_results": 3,
    }


def _get_movie_details_by_id(movie_id: int) -> Dict[str, Any]:
    """Helper function to get movie details by ID."""
    movies = {
        1: {
            "id": 1,
            "title": "The Matrix",
            "release_date": "1999-03-31",
            "vote_count": 25000,
            "vote_average": 8.7,
            "popularity": 85.5,
            "overview": "A computer hacker learns about the true nature of reality",
            "poster_path": "/poster1.jpg",
            "backdrop_path": "/backdrop1.jpg",
            "adult": False,
            "original_language": "en",
            "original_title": "The Matrix",
            "video": False,
            "genres": [
                {"id": 28, "name": "Action"},
                {"id": 878, "name": "Science Fiction"},
            ],
            "runtime": 136,
            "status": "Released",
            "tagline": "Welcome to the Real World",
            "budget": 63000000,
            "revenue": 467200000,
            "homepage": "https://www.warnerbros.com/movies/matrix",
            "imdb_id": "tt0133093",
            "production_companies": [],
            "production_countries": [],
            "spoken_languages": [],
        },
        2: {
            "id": 2,
            "title": "Inception",
            "release_date": "1999-07-16",  # Changed to 1999 for testing
            "vote_count": 30000,
            "vote_average": 8.8,
            "popularity": 90.2,
            "overview": "A skilled thief is given a chance at redemption",
            "poster_path": "/poster2.jpg",
            "backdrop_path": "/backdrop2.jpg",
            "adult": False,
            "original_language": "en",
            "original_title": "Inception",
            "video": False,
            "genres": [
                {"id": 28, "name": "Action"},
                {"id": 878, "name": "Science Fiction"},
                {"id": 53, "name": "Thriller"},
            ],
            "runtime": 148,
            "status": "Released",
            "tagline": "Your mind is the scene of the crime",
            "budget": 160000000,
            "revenue": 825500000,
            "homepage": "https://www.warnerbros.com/movies/inception",
            "imdb_id": "tt1375666",
            "production_companies": [],
            "production_countries": [],
            "spoken_languages": [],
        },
        3: {
            "id": 3,
            "title": "A Beautiful Mind",
            "release_date": "1999-12-21",  # Changed to 1999 for testing
            "vote_count": 20000,
            "vote_average": 8.2,
            "popularity": 75.3,
            "overview": "A mathematical genius",
            "poster_path": "/poster3.jpg",
            "backdrop_path": "/backdrop3.jpg",
            "adult": False,
            "original_language": "en",
            "original_title": "A Beautiful Mind",
            "video": False,
            "genres": [
                {"id": 18, "name": "Drama"},
                {"id": 36, "name": "History"},
            ],
            "runtime": 135,
            "status": "Released",
            "tagline": "A Beautiful Mind",
            "budget": 58000000,
            "revenue": 313500000,
            "homepage": "https://www.universalstudios.com/movies/a-beautiful-mind",
            "imdb_id": "tt0268978",
            "production_companies": [],
            "production_countries": [],
            "spoken_languages": [],
        },
        4: {
            "id": 4,
            "title": "The Matrix Reloaded",
            "release_date": "2003-05-15",
            "vote_count": 15000,
            "vote_average": 7.2,
            "popularity": 70.0,
            "overview": "Neo and his allies continue the fight",
            "poster_path": "/poster4.jpg",
            "backdrop_path": "/backdrop4.jpg",
            "adult": False,
            "original_language": "en",
            "original_title": "The Matrix Reloaded",
            "video": False,
            "genres": [
                {"id": 28, "name": "Action"},
                {"id": 878, "name": "Science Fiction"},
            ],
            "runtime": 138,
            "status": "Released",
            "tagline": "Free your mind",
            "budget": 150000000,
            "revenue": 742100000,
            "homepage": "https://www.warnerbros.com/movies/matrix-reloaded",
            "imdb_id": "tt0234215",
            "production_companies": [],
            "production_countries": [],
            "spoken_languages": [],
        },
        5: {
            "id": 5,
            "title": "Blade Runner",
            "release_date": "1982-06-25",
            "vote_count": 18000,
            "vote_average": 8.1,
            "popularity": 65.0,
            "overview": "A blade runner must pursue and terminate replicants",
            "poster_path": "/poster5.jpg",
            "backdrop_path": "/backdrop5.jpg",
            "adult": False,
            "original_language": "en",
            "original_title": "Blade Runner",
            "video": False,
            "genres": [
                {"id": 28, "name": "Action"},
                {"id": 878, "name": "Science Fiction"},
                {"id": 9648, "name": "Mystery"},
            ],
            "runtime": 117,
            "status": "Released",
            "tagline": "Man has made his match... now it's his problem.",
            "budget": 28000000,
            "revenue": 41600000,
            "homepage": "https://www.warnerbros.com/movies/blade-runner",
            "imdb_id": "tt0083658",
            "production_companies": [],
            "production_countries": [],
            "spoken_languages": [],
        },
    }
    return movies.get(movie_id, movies[1])  # Default to movie 1 if not found


def _get_keywords_by_id(movie_id: int) -> Dict[str, Any]:
    """Helper function to get keywords by movie ID."""
    keywords_map = {
        1: {
            "id": 1,
            "keywords": [
                {"id": 100, "name": "artificial intelligence"},
                {"id": 101, "name": "virtual reality"},
                {"id": 102, "name": "hacker"},
            ],
        },
        2: {
            "id": 2,
            "keywords": [
                {"id": 103, "name": "dream"},
                {"id": 104, "name": "subconscious"},
                {"id": 105, "name": "heist"},
            ],
        },
        3: {
            "id": 3,
            "keywords": [
                {"id": 106, "name": "mathematics"},
                {"id": 107, "name": "genius"},
                {"id": 108, "name": "schizophrenia"},
            ],
        },
        4: {
            "id": 4,
            "keywords": [
                {"id": 100, "name": "artificial intelligence"},
                {"id": 101, "name": "virtual reality"},
                {"id": 109, "name": "sequel"},
            ],
        },
        5: {
            "id": 5,
            "keywords": [
                {"id": 110, "name": "dystopia"},
                {"id": 111, "name": "android"},
                {"id": 112, "name": "noir"},
            ],
        },
    }
    return keywords_map.get(movie_id, keywords_map[1])  # Default to movie 1 if not found


@pytest.fixture
def mock_movie_details_response() -> Dict[str, Any]:
    """Mock TMDB API response for movie details endpoint (returns movie ID 1 by default)."""
    return _get_movie_details_by_id(1)


@pytest.fixture
def mock_keywords_response() -> Dict[str, Any]:
    """Mock TMDB API response for movie keywords endpoint (returns movie ID 1 by default)."""
    return _get_keywords_by_id(1)


@pytest.fixture
def mock_similar_movies_response() -> Dict[str, Any]:
    """Mock TMDB API response for similar movies endpoint."""
    return {
        "page": 1,
        "results": [
            {
                "id": 4,
                "title": "The Matrix Reloaded",
                "release_date": "2003-05-15",
                "vote_count": 15000,
                "vote_average": 7.2,
                "popularity": 70.0,
                "overview": "Neo and his allies continue the fight",
                "poster_path": "/poster4.jpg",
                "backdrop_path": "/backdrop4.jpg",
                "adult": False,
                "original_language": "en",
                "original_title": "The Matrix Reloaded",
                "video": False,
                "genre_ids": [28, 878],
            },
            {
                "id": 5,
                "title": "Blade Runner",
                "release_date": "1982-06-25",
                "vote_count": 18000,
                "vote_average": 8.1,
                "popularity": 65.0,
                "overview": "A blade runner must pursue and terminate replicants",
                "poster_path": "/poster5.jpg",
                "backdrop_path": "/backdrop5.jpg",
                "adult": False,
                "original_language": "en",
                "original_title": "Blade Runner",
                "video": False,
                "genre_ids": [28, 878, 9648],
            },
        ],
        "total_pages": 1,
        "total_results": 2,
    }


@pytest.fixture
def sample_movies() -> List[Movie]:
    """Sample Movie models for testing."""
    from src.models.Movies import Genre, Keyword, Movie

    return [
        Movie(
            id=1,
            title="The Matrix",
            release_date="1999-03-31",
            vote_count=25000,
            vote_average=8.7,
            popularity=85.5,
            overview="A computer hacker learns about the true nature of reality",
            poster_path="/poster1.jpg",
            backdrop_path="/backdrop1.jpg",
            genres=[
                Genre(id=28, name="Action"),
                Genre(id=878, name="Science Fiction"),
            ],
            keywords=[
                Keyword(id=100, name="artificial intelligence"),
                Keyword(id=101, name="virtual reality"),
            ],
            runtime=136,
            tagline="Welcome to the Real World",
            imdb_id="tt0133093",
        ),
        Movie(
            id=2,
            title="Inception",
            release_date="2010-07-16",
            vote_count=30000,
            vote_average=8.8,
            popularity=90.2,
            overview="A skilled thief is given a chance at redemption",
            poster_path="/poster2.jpg",
            backdrop_path="/backdrop2.jpg",
            genres=[
                Genre(id=28, name="Action"),
                Genre(id=878, name="Science Fiction"),
                Genre(id=53, name="Thriller"),
            ],
            keywords=[
                Keyword(id=103, name="dream"),
                Keyword(id=104, name="subconscious"),
            ],
            runtime=148,
            tagline="Your mind is the scene of the crime",
            imdb_id="tt1375666",
        ),
        Movie(
            id=3,
            title="A Beautiful Mind",
            release_date="2001-12-21",
            vote_count=20000,
            vote_average=8.2,
            popularity=75.3,
            overview="A mathematical genius",
            poster_path="/poster3.jpg",
            backdrop_path="/backdrop3.jpg",
            genres=[
                Genre(id=18, name="Drama"),
                Genre(id=36, name="History"),
            ],
            keywords=[],
            runtime=135,
            tagline="",
            imdb_id="tt0268978",
        ),
    ]


@pytest.fixture
def test_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory for tests."""
    output_dir = tmp_path / "test_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("TMDB_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def cleanup_test_files():
    """Cleanup test files after tests."""
    yield
    # Cleanup will be handled by tmp_path fixture
    pass

