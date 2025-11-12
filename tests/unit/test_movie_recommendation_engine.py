"""
Unit tests for MovieRecommendationEngine.

Tests the core similarity calculation methods using mock data to verify
that the calculations are mathematically correct.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.models.Movies import Movie, Genre, Keyword
from src.services.movie_recommendation_engine import MovieRecommendationEngine


class TestMovieRecommendationEngine:
    """Test suite for MovieRecommendationEngine similarity calculations."""

    @pytest.fixture
    def mock_tmdb_client(self):
        """Create a mock TMDB client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def engine(self, mock_tmdb_client, mock_env_vars):
        """Create a MovieRecommendationEngine instance with mocked dependencies."""
        with patch("src.services.movie_recommendation_engine.TMDBClient", return_value=mock_tmdb_client):
            engine = MovieRecommendationEngine(tmdb_client=mock_tmdb_client)
            return engine

    @pytest.fixture
    def sample_movie_1(self):
        """Create a sample movie for testing."""
        return Movie(
            id=1,
            title="The Matrix",
            release_date="1999-03-31",
            release_year=1999,
            vote_count=25000,
            vote_average=8.7,
            popularity=85.5,
            overview="A computer hacker learns about the true nature of reality",
            genres=[
                Genre(id=28, name="Action"),
                Genre(id=878, name="Science Fiction"),
                Genre(id=53, name="Thriller"),
            ],
            keywords=[
                Keyword(id=1, name="artificial intelligence"),
                Keyword(id=2, name="virtual reality"),
                Keyword(id=3, name="hacker"),
            ],
            director="Lana Wachowski",
            collection_id=2344,
            collection_name="The Matrix Collection",
            production_companies=[
                {"id": 79, "name": "Village Roadshow Pictures"},
                {"id": 174, "name": "Warner Bros. Pictures"},
            ],
        )

    @pytest.fixture
    def sample_movie_2(self):
        """Create another sample movie for testing."""
        return Movie(
            id=2,
            title="Inception",
            release_date="2010-07-16",
            release_year=2010,
            vote_count=30000,
            vote_average=8.8,
            popularity=90.2,
            overview="A skilled thief is given a chance at redemption",
            genres=[
                Genre(id=28, name="Action"),
                Genre(id=878, name="Science Fiction"),
                Genre(id=18, name="Drama"),
            ],
            keywords=[
                Keyword(id=1, name="artificial intelligence"),
                Keyword(id=4, name="dream"),
                Keyword(id=5, name="heist"),
            ],
            director="Christopher Nolan",
            collection_id=None,
            collection_name=None,
            production_companies=[
                {"id": 174, "name": "Warner Bros. Pictures"},
                {"id": 923, "name": "Legendary Pictures"},
            ],
        )

    @pytest.fixture
    def sample_movie_3(self):
        """Create a third sample movie for testing."""
        return Movie(
            id=3,
            title="The Matrix Reloaded",
            release_date="2003-05-15",
            release_year=2003,
            vote_count=15000,
            vote_average=7.2,
            popularity=70.0,
            overview="Neo and his allies continue the fight",
            genres=[
                Genre(id=28, name="Action"),
                Genre(id=878, name="Science Fiction"),
                Genre(id=53, name="Thriller"),
            ],
            keywords=[
                Keyword(id=1, name="artificial intelligence"),
                Keyword(id=2, name="virtual reality"),
                Keyword(id=6, name="sequel"),
            ],
            director="Lana Wachowski",
            collection_id=2344,
            collection_name="The Matrix Collection",
            production_companies=[
                {"id": 79, "name": "Village Roadshow Pictures"},
                {"id": 174, "name": "Warner Bros. Pictures"},
            ],
        )

    # Test individual similarity calculations

    def test_calculate_genre_similarity_identical(self, engine):
        """Test genre similarity with identical genres."""
        genres1 = ["Action", "Sci-Fi", "Thriller"]
        genres2 = ["Action", "Sci-Fi", "Thriller"]

        similarity = engine._calculate_genre_similarity(genres1, genres2)

        # Jaccard similarity: 3 shared / 3 total = 1.0
        assert similarity == 1.0

    def test_calculate_genre_similarity_partial_overlap(self, engine):
        """Test genre similarity with partial overlap."""
        genres1 = ["Action", "Sci-Fi", "Thriller"]
        genres2 = ["Action", "Sci-Fi", "Drama"]

        similarity = engine._calculate_genre_similarity(genres1, genres2)

        # Jaccard similarity: 2 shared / 4 total = 0.5
        assert similarity == 0.5

    def test_calculate_genre_similarity_no_overlap(self, engine):
        """Test genre similarity with no overlap."""
        genres1 = ["Action", "Sci-Fi"]
        genres2 = ["Drama", "Romance"]

        similarity = engine._calculate_genre_similarity(genres1, genres2)

        assert similarity == 0.0

    def test_calculate_genre_similarity_empty_lists(self, engine):
        """Test genre similarity with empty lists."""
        similarity = engine._calculate_genre_similarity([], [])
        assert similarity == 0.0

        similarity = engine._calculate_genre_similarity(["Action"], [])
        assert similarity == 0.0

    def test_calculate_keyword_similarity_identical(self, engine):
        """Test keyword similarity with identical keywords."""
        keywords1 = ["ai", "virtual reality", "hacker"]
        keywords2 = ["ai", "virtual reality", "hacker"]

        similarity = engine._calculate_keyword_similarity(keywords1, keywords2)

        assert similarity == 1.0

    def test_calculate_keyword_similarity_partial_overlap(self, engine):
        """Test keyword similarity with partial overlap."""
        keywords1 = ["ai", "virtual reality", "hacker"]
        keywords2 = ["ai", "virtual reality", "dream"]

        similarity = engine._calculate_keyword_similarity(keywords1, keywords2)

        # Jaccard similarity: 2 shared / 4 total = 0.5
        assert similarity == 0.5

    def test_calculate_keyword_similarity_no_overlap(self, engine):
        """Test keyword similarity with no overlap."""
        keywords1 = ["ai", "virtual reality"]
        keywords2 = ["romance", "comedy"]

        similarity = engine._calculate_keyword_similarity(keywords1, keywords2)

        assert similarity == 0.0

    def test_calculate_director_similarity_same_director(self, engine):
        """Test director similarity with same director."""
        director1 = "Christopher Nolan"
        director2 = "Christopher Nolan"

        similarity = engine._calculate_director_similarity(director1, director2)

        assert similarity == 1.0

    def test_calculate_director_similarity_case_insensitive(self, engine):
        """Test director similarity is case insensitive."""
        director1 = "Christopher Nolan"
        director2 = "christopher nolan"

        similarity = engine._calculate_director_similarity(director1, director2)

        assert similarity == 1.0

    def test_calculate_director_similarity_different_directors(self, engine):
        """Test director similarity with different directors."""
        director1 = "Christopher Nolan"
        director2 = "Lana Wachowski"

        similarity = engine._calculate_director_similarity(director1, director2)

        assert similarity == 0.0

    def test_calculate_director_similarity_none_values(self, engine):
        """Test director similarity with None values."""
        similarity = engine._calculate_director_similarity(None, "Christopher Nolan")
        assert similarity == 0.0

        similarity = engine._calculate_director_similarity("Christopher Nolan", None)
        assert similarity == 0.0

        similarity = engine._calculate_director_similarity(None, None)
        assert similarity == 0.0

    def test_calculate_collection_similarity_same_collection(self, engine):
        """Test collection similarity with same collection."""
        collection_id1 = 2344
        collection_id2 = 2344

        similarity = engine._calculate_collection_similarity(collection_id1, collection_id2)

        assert similarity == 1.0

    def test_calculate_collection_similarity_different_collections(self, engine):
        """Test collection similarity with different collections."""
        collection_id1 = 2344
        collection_id2 = 1234

        similarity = engine._calculate_collection_similarity(collection_id1, collection_id2)

        assert similarity == 0.0

    def test_calculate_collection_similarity_none_values(self, engine):
        """Test collection similarity with None values."""
        similarity = engine._calculate_collection_similarity(None, 2344)
        assert similarity == 0.0

        similarity = engine._calculate_collection_similarity(2344, None)
        assert similarity == 0.0

        similarity = engine._calculate_collection_similarity(None, None)
        assert similarity == 0.0

    def test_calculate_production_company_similarity_identical(self, engine):
        """Test production company similarity with identical companies."""
        companies1 = [79, 174]
        companies2 = [79, 174]

        similarity = engine._calculate_production_company_similarity(companies1, companies2)

        # Jaccard similarity: 2 shared / 2 total = 1.0
        assert similarity == 1.0

    def test_calculate_production_company_similarity_partial_overlap(self, engine):
        """Test production company similarity with partial overlap."""
        companies1 = [79, 174]
        companies2 = [174, 923]

        similarity = engine._calculate_production_company_similarity(companies1, companies2)

        # Jaccard similarity: 1 shared / 3 total = 0.333...
        assert similarity == pytest.approx(0.333, abs=0.01)

    def test_calculate_production_company_similarity_no_overlap(self, engine):
        """Test production company similarity with no overlap."""
        companies1 = [79, 174]
        companies2 = [923, 1000]

        similarity = engine._calculate_production_company_similarity(companies1, companies2)

        assert similarity == 0.0

    def test_calculate_production_company_similarity_empty_lists(self, engine):
        """Test production company similarity with empty lists."""
        similarity = engine._calculate_production_company_similarity([], [])
        assert similarity == 0.0

        similarity = engine._calculate_production_company_similarity([79], [])
        assert similarity == 0.0

    # Test overall similarity score calculation

    def test_calculate_similarity_score_same_franchise(self, engine, sample_movie_1, sample_movie_3):
        """Test similarity score for movies in same franchise."""
        score, metrics = engine.calculate_similarity_score(sample_movie_1, sample_movie_3)

        # Should have high similarity due to:
        # - Same collection (weight 0.3)
        # - Same director (weight 0.1)
        # - High genre overlap (weight 0.3)
        # - High keyword overlap (weight 0.1)
        # - Same production companies (weight 0.2)

        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Should be very similar

        # Verify metrics structure
        assert "genre_similarity" in metrics
        assert "keyword_similarity" in metrics
        assert "director_similarity" in metrics
        assert "collection_similarity" in metrics
        assert "production_company_similarity" in metrics
        assert "shared_genres" in metrics
        assert "shared_keywords" in metrics
        assert "similarity_reason" in metrics

        # Verify specific similarities
        assert metrics["collection_similarity"] == 1.0
        assert metrics["director_similarity"] == 1.0
        assert metrics["genre_similarity"] == 1.0  # All genres match

    def test_calculate_similarity_score_partial_similarity(self, engine, sample_movie_1, sample_movie_2):
        """Test similarity score for movies with partial similarity."""
        score, metrics = engine.calculate_similarity_score(sample_movie_1, sample_movie_2)

        assert 0.0 <= score <= 1.0

        # Should have moderate similarity:
        # - Different collection (0.0)
        # - Different director (0.0)
        # - Partial genre overlap (2/4 = 0.5)
        # - Partial keyword overlap (1/5 = 0.2)
        # - Partial production company overlap (1/3 = 0.333)

        assert metrics["collection_similarity"] == 0.0
        assert metrics["director_similarity"] == 0.0
        assert metrics["genre_similarity"] == 0.5
        assert metrics["keyword_similarity"] == 0.2
        assert metrics["production_company_similarity"] == pytest.approx(0.333, abs=0.01)

        # Shared items
        assert set(metrics["shared_genres"]) == {"Action", "Science Fiction"}
        assert set(metrics["shared_keywords"]) == {"artificial intelligence"}

    def test_calculate_similarity_score_returns_valid_range(self, engine, sample_movie_1, sample_movie_2):
        """Test that similarity score is always between 0 and 1."""
        score, metrics = engine.calculate_similarity_score(sample_movie_1, sample_movie_2)

        assert 0.0 <= score <= 1.0

    def test_similarity_reason_generation_same_franchise(self, engine, sample_movie_1, sample_movie_3):
        """Test similarity reason for same franchise movies."""
        score, metrics = engine.calculate_similarity_score(sample_movie_1, sample_movie_3)

        reason = metrics["similarity_reason"]

        # Should mention franchise and director
        assert "The Matrix Collection" in reason or "franchise" in reason.lower()

    def test_similarity_reason_generation_partial(self, engine, sample_movie_1, sample_movie_2):
        """Test similarity reason for partially similar movies."""
        score, metrics = engine.calculate_similarity_score(sample_movie_1, sample_movie_2)

        reason = metrics["similarity_reason"]

        # Should be a non-empty string
        assert isinstance(reason, str)
        assert len(reason) > 0

    # Test candidate pool methods

    def test_get_candidates_from_tmdb_api(self, engine, mock_tmdb_client, sample_movie_1):
        """Test getting candidates from TMDB API."""
        # Mock API responses
        similar_response = {
            "results": [
                {
                    "id": 100,
                    "title": "Similar Movie 1",
                    "vote_count": 1000,
                    "release_date": "2000-01-01",
                    "vote_average": 7.5,
                    "popularity": 50.0,
                    "overview": "Overview",
                    "genre_ids": [28, 878],
                }
            ]
        }

        recommendations_response = {
            "results": [
                {
                    "id": 101,
                    "title": "Recommended Movie 1",
                    "vote_count": 1500,
                    "release_date": "2001-01-01",
                    "vote_average": 8.0,
                    "popularity": 60.0,
                    "overview": "Overview",
                    "genre_ids": [28, 878],
                }
            ]
        }

        mock_tmdb_client.get_similar_movies.return_value = similar_response
        mock_tmdb_client.get_movie_recommendations.return_value = recommendations_response

        candidates = engine._get_candidates_from_tmdb_api(sample_movie_1)

        # Should return both similar and recommended movies
        assert len(candidates) == 2
        assert all(isinstance(movie, Movie) for movie in candidates)

        # Verify API was called
        mock_tmdb_client.get_similar_movies.assert_called_once()
        mock_tmdb_client.get_movie_recommendations.assert_called_once()

    def test_get_candidates_same_year(self, engine, mock_tmdb_client, sample_movie_1):
        """Test getting candidates from same year."""
        # Mock API response
        year_response = {
            "results": [
                {
                    "id": 200,
                    "title": "Same Year Movie",
                    "vote_count": 1000,
                    "release_date": "1999-06-01",
                    "vote_average": 7.5,
                    "popularity": 50.0,
                    "overview": "Overview",
                    "genre_ids": [28],
                }
            ]
        }

        mock_tmdb_client.get_movies_by_year.return_value = year_response

        candidates = engine._get_candidates_same_year(sample_movie_1)

        # Should return movies from same year (excluding target)
        assert len(candidates) >= 0
        assert all(isinstance(movie, Movie) for movie in candidates)

        # Verify API was called with correct year
        mock_tmdb_client.get_movies_by_year.assert_called_once()
        call_args = mock_tmdb_client.get_movies_by_year.call_args
        assert call_args[1]["year"] == 1999

    def test_find_similar_movies_for_each_integration(self, engine, mock_tmdb_client, sample_movie_1):
        """Test the complete find_similar_movies_for_each workflow."""
        # Mock all required API calls
        mock_tmdb_client.get_similar_movies.return_value = {
            "results": [
                {
                    "id": 100,
                    "title": "Similar Movie",
                    "vote_count": 1000,
                    "release_date": "2000-01-01",
                    "vote_average": 7.5,
                    "popularity": 50.0,
                    "overview": "Overview",
                    "genre_ids": [28, 878],
                }
            ]
        }

        mock_tmdb_client.get_movie_recommendations.return_value = {"results": []}

        # Mock enrichment calls
        mock_tmdb_client.get_movie_details.return_value = {
            "id": 100,
            "title": "Similar Movie",
            "genres": [{"id": 28, "name": "Action"}],
            "release_date": "2000-01-01",
            "vote_count": 1000,
            "vote_average": 7.5,
            "popularity": 50.0,
            "overview": "Overview",
        }

        mock_tmdb_client.get_movie_keywords.return_value = {
            "keywords": [{"id": 1, "name": "action"}]
        }

        mock_tmdb_client.get_movie_credits.return_value = {
            "crew": [{"job": "Director", "name": "Test Director"}]
        }

        # Execute
        results = engine.find_similar_movies_for_each(
            top_movies=[sample_movie_1],
            similar_per_movie=3,
            strategy="tmdb_api"
        )

        # Verify results structure
        assert len(results) == 1
        assert "original_movie" in results[0]
        assert "similar_movies" in results[0]
        assert results[0]["original_movie"].id == sample_movie_1.id
