"""
Unit tests for MovieService.

Tests the MovieService class which handles:
- Fetching top movies by year from TMDB API
- Sorting movies by different criteria (votes, name, name without articles)
- Preparing movie data for export
"""

from unittest.mock import MagicMock, patch

import pytest

from src.models.Movies import Movie
from src.services.movie_service import MovieService


class TestMovieService:
    """Test suite for MovieService functionality."""

    @pytest.fixture
    def mock_tmdb_client(self):
        """Create a mock TMDB client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def movie_service(self, mock_tmdb_client, mock_env_vars):
        """Create a MovieService instance with mocked dependencies."""
        with patch("src.services.movie_service.TMDBClient", return_value=mock_tmdb_client):
            service = MovieService(tmdb_client=mock_tmdb_client)
            return service

    def test_sort_movies_by_votes(self, movie_service, sample_movies):
        """Test sorting movies by vote count."""
        sorted_movies = movie_service.sort_movies_by_votes(sample_movies)

        assert len(sorted_movies) == 3
        assert sorted_movies[0].id == 2  # Inception has highest votes (30000)
        assert sorted_movies[1].id == 1  # The Matrix (25000)
        assert sorted_movies[2].id == 3  # A Beautiful Mind (20000)

    def test_sort_movies_by_name_with_articles(self, movie_service, sample_movies):
        """Test sorting movies by name (with articles)."""
        sorted_movies = movie_service.sort_movies_by_name(sample_movies, ignore_articles=False)

        assert len(sorted_movies) == 3
        # Should sort alphabetically: "A Beautiful Mind", "Inception", "The Matrix"
        assert sorted_movies[0].title == "A Beautiful Mind"
        assert sorted_movies[1].title == "Inception"
        assert sorted_movies[2].title == "The Matrix"

    def test_sort_movies_by_name_without_articles(self, movie_service, sample_movies):
        """Test sorting movies by name (without articles)."""
        sorted_movies = movie_service.sort_movies_by_name(sample_movies, ignore_articles=True)

        assert len(sorted_movies) == 3
        # Should sort ignoring articles: "A Beautiful Mind" -> "Beautiful Mind"
        # "The Matrix" -> "Matrix"
        # So: "Beautiful Mind", "Inception", "Matrix"
        assert sorted_movies[0].title == "A Beautiful Mind"
        assert sorted_movies[1].title == "Inception"
        assert sorted_movies[2].title == "The Matrix"

    def test_get_top_movies_by_year(
        self, movie_service, mock_tmdb_client, mock_tmdb_api_response, mock_movie_details_response, mock_keywords_response
    ):
        """Test getting top movies by year."""
        # Mock API responses
        mock_tmdb_client.get_movies_by_year.return_value = mock_tmdb_api_response
        mock_tmdb_client.get_movie_details.return_value = mock_movie_details_response
        mock_tmdb_client.get_movie_keywords.return_value = mock_keywords_response

        # Get top movies
        movies = movie_service.get_top_movies_by_year(year=1999, top_n=2)

        assert len(movies) == 2
        assert movies[0].id == 1
        assert movies[0].title == "The Matrix"
        mock_tmdb_client.get_movies_by_year.assert_called()

    def test_prepare_movies_for_export_votes(self, movie_service, sample_movies):
        """Test preparing movies for export with votes sort."""
        export_data = movie_service.prepare_movies_for_export(sample_movies, sort_method="votes")

        assert len(export_data) == 3
        assert all(entry["sort_method"] == "votes" for entry in export_data)
        assert all(isinstance(entry["movie"], Movie) for entry in export_data)
        # Should be sorted by votes (highest first)
        assert export_data[0]["movie"].id == 2  # Inception

    def test_prepare_movies_for_export_name(self, movie_service, sample_movies):
        """Test preparing movies for export with name sort."""
        export_data = movie_service.prepare_movies_for_export(sample_movies, sort_method="name")

        assert len(export_data) == 3
        assert all(entry["sort_method"] == "name" for entry in export_data)
        assert all(isinstance(entry["movie"], Movie) for entry in export_data)

    def test_prepare_movies_for_export_name_no_articles(self, movie_service, sample_movies):
        """Test preparing movies for export with name_no_articles sort."""
        export_data = movie_service.prepare_movies_for_export(
            sample_movies, sort_method="name_no_articles"
        )

        assert len(export_data) == 3
        assert all(entry["sort_method"] == "name_no_articles" for entry in export_data)
        assert all(isinstance(entry["movie"], Movie) for entry in export_data)

    def test_prepare_movies_for_export_invalid_method(self, movie_service, sample_movies):
        """Test preparing movies with invalid sort method."""
        with pytest.raises(ValueError, match="Unknown sort method"):
            movie_service.prepare_movies_for_export(sample_movies, sort_method="invalid")

