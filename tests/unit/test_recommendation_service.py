"""
Unit tests for RecommendationService.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.models.Movies import Movie
from src.services.recommendation_service import RecommendationService


class TestRecommendationService:
    """Test cases for RecommendationService."""

    @pytest.fixture
    def mock_tmdb_client(self):
        """Create a mock TMDB client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def recommendation_service(self, mock_tmdb_client, mock_env_vars):
        """Create a RecommendationService instance with mocked dependencies."""
        with patch("src.services.recommendation_service.TMDBClient", return_value=mock_tmdb_client):
            service = RecommendationService(tmdb_client=mock_tmdb_client)
            return service

    def test_calculate_genre_similarity(self, recommendation_service):
        """Test genre similarity calculation."""
        genres1 = ["Action", "Sci-Fi", "Thriller"]
        genres2 = ["Action", "Sci-Fi", "Drama"]

        similarity = recommendation_service._calculate_genre_similarity(genres1, genres2)

        # Jaccard similarity: 2 shared / 4 total = 0.5
        assert similarity == 0.5

    def test_calculate_genre_similarity_no_overlap(self, recommendation_service):
        """Test genre similarity with no overlap."""
        genres1 = ["Action", "Sci-Fi"]
        genres2 = ["Drama", "Romance"]

        similarity = recommendation_service._calculate_genre_similarity(genres1, genres2)

        assert similarity == 0.0

    def test_calculate_genre_similarity_identical(self, recommendation_service):
        """Test genre similarity with identical genres."""
        genres1 = ["Action", "Sci-Fi"]
        genres2 = ["Action", "Sci-Fi"]

        similarity = recommendation_service._calculate_genre_similarity(genres1, genres2)

        assert similarity == 1.0

    def test_calculate_keyword_similarity(self, recommendation_service):
        """Test keyword similarity calculation."""
        keywords1 = ["ai", "virtual reality", "hacker"]
        keywords2 = ["ai", "virtual reality", "dream"]

        similarity = recommendation_service._calculate_keyword_similarity(keywords1, keywords2)

        # Jaccard similarity: 2 shared / 4 total = 0.5
        assert similarity == 0.5

    def test_calculate_rating_similarity(self, recommendation_service):
        """Test rating similarity calculation."""
        similarity = recommendation_service._calculate_rating_similarity(8.5, 8.7)

        # Difference: 0.2, Max: 10.0, Similarity: 1.0 - (0.2/10.0) = 0.98
        assert similarity == pytest.approx(0.98, abs=0.01)

    def test_calculate_rating_similarity_identical(self, recommendation_service):
        """Test rating similarity with identical ratings."""
        similarity = recommendation_service._calculate_rating_similarity(8.5, 8.5)

        assert similarity == 1.0

    def test_calculate_year_similarity(self, recommendation_service):
        """Test year similarity calculation."""
        similarity = recommendation_service._calculate_year_similarity(1999, 2001)

        # Difference: 2 years, Max diff: 20, Similarity: 1.0 - (2/20) = 0.9
        assert similarity == pytest.approx(0.9, abs=0.01)

    def test_calculate_year_similarity_same_year(self, recommendation_service):
        """Test year similarity with same year."""
        similarity = recommendation_service._calculate_year_similarity(1999, 1999)

        assert similarity == 1.0

    def test_calculate_similarity_score(self, recommendation_service, sample_movies):
        """Test overall similarity score calculation."""
        movie1 = sample_movies[0]  # The Matrix
        movie2 = sample_movies[1]  # Inception

        score, metrics = recommendation_service.calculate_similarity_score(movie1, movie2)

        assert 0.0 <= score <= 1.0
        assert "genre_similarity" in metrics
        assert "keyword_similarity" in metrics
        assert "rating_similarity" in metrics
        assert "year_similarity" in metrics
        assert "similarity_reason" in metrics
        assert "shared_genres" in metrics

    def test_find_similar_movies(
        self,
        recommendation_service,
        mock_tmdb_client,
        sample_movies,
        mock_similar_movies_response,
        mock_movie_details_response,
        mock_keywords_response,
    ):
        """Test finding similar movies."""
        original_movie = sample_movies[0]

        # Mock API responses
        mock_tmdb_client.get_similar_movies.return_value = mock_similar_movies_response
        mock_tmdb_client.get_movie_details.return_value = mock_movie_details_response
        mock_tmdb_client.get_movie_keywords.return_value = mock_keywords_response

        similar_movies = recommendation_service.find_similar_movies(original_movie, limit=2)

        assert len(similar_movies) <= 2
        if similar_movies:
            assert all("similar_movie" in item for item in similar_movies)
            assert all("similarity_score" in item for item in similar_movies)
            assert all("similarity_reason" in item for item in similar_movies)
            assert all("similarity_metrics" in item for item in similar_movies)

    def test_prepare_similar_movies_for_export(
        self, recommendation_service, sample_movies
    ):
        """Test preparing similar movies data for export."""
        similar_movies_data = [
            {
                "original_movie": sample_movies[0],
                "similar_movies": [
                    {
                        "similar_movie": sample_movies[1],
                        "similarity_score": 0.85,
                        "similarity_reason": "Similar genres",
                        "similarity_metrics": {"genre_similarity": 0.8},
                    }
                ],
            }
        ]

        export_data = recommendation_service.prepare_similar_movies_for_export(
            similar_movies_data
        )

        assert len(export_data) == 1
        assert export_data[0]["original_movie"] == sample_movies[0]
        assert export_data[0]["similar_movie"] == sample_movies[1]
        assert export_data[0]["similarity_score"] == 0.85

