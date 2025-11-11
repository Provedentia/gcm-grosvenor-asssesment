"""
Pytest configuration for real API tests.
These tests use the actual TMDB API and require a valid API key.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from src.api.TMDB import TMDBClient
from src.services.export_service import ExportService
from src.services.movie_service import MovieService
from src.services.recommendation_service import RecommendationService


# Load .env file before checking for API key
_project_root = Path(__file__).parent.parent.parent
_env_file = _project_root / ".env"
if _env_file.exists():
    load_dotenv(_env_file)


@pytest.fixture(scope="module")
def tmdb_api_key():
    """
    Get TMDB API key from environment variable or .env file.
    
    Returns:
        API key string
        
    Raises:
        pytest.skip: If API key is not available
    """
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        pytest.skip("TMDB_API_KEY not found in environment or .env file. Skipping real API tests.")
    return api_key


@pytest.fixture(scope="module")
def real_tmdb_client(tmdb_api_key):
    """
    Create a real TMDB client instance using the actual API key.
    
    Args:
        tmdb_api_key: TMDB API key from environment
        
    Returns:
        TMDBClient instance
    """
    return TMDBClient(api_key=tmdb_api_key)


@pytest.fixture(scope="module")
def real_movie_service(real_tmdb_client):
    """
    Create a real MovieService instance with real TMDB client.
    
    Args:
        real_tmdb_client: Real TMDBClient instance
        
    Returns:
        MovieService instance
    """
    return MovieService(tmdb_client=real_tmdb_client)


@pytest.fixture(scope="module")
def real_recommendation_service(real_tmdb_client):
    """
    Create a real RecommendationService instance with real TMDB client.
    
    Args:
        real_tmdb_client: Real TMDBClient instance
        
    Returns:
        RecommendationService instance
    """
    return RecommendationService(tmdb_client=real_tmdb_client)


@pytest.fixture
def real_export_service(tmp_path):
    """
    Create a real ExportService instance with temporary output directory.
    
    Args:
        tmp_path: Pytest temporary path fixture
        
    Returns:
        ExportService instance
    """
    output_dir = tmp_path / "api_test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return ExportService(output_dir=str(output_dir))

