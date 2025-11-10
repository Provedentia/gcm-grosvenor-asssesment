"""
Integration tests for the complete workflow from API to CSV export.
"""

import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.export_service import ExportService
from src.services.movie_service import MovieService
from src.services.recommendation_service import RecommendationService


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for the complete application workflow."""

    @pytest.fixture
    def mock_tmdb_client(self):
        """Create a fully mocked TMDB client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def services(self, mock_tmdb_client, test_output_dir, mock_env_vars):
        """Create service instances with mocked dependencies."""
        with patch("src.services.movie_service.TMDBClient", return_value=mock_tmdb_client), \
             patch("src.services.recommendation_service.TMDBClient", return_value=mock_tmdb_client):
            
            movie_service = MovieService(tmdb_client=mock_tmdb_client)
            recommendation_service = RecommendationService(tmdb_client=mock_tmdb_client)
            export_service = ExportService(output_dir=str(test_output_dir))
            
            return {
                "movie_service": movie_service,
                "recommendation_service": recommendation_service,
                "export_service": export_service,
                "tmdb_client": mock_tmdb_client,
            }

    def test_complete_workflow_top_movies_only(
        self,
        services,
        mock_tmdb_api_response,
        mock_movie_details_response,
        mock_keywords_response,
    ):
        """Test complete workflow: get top movies and export to CSV."""
        movie_service = services["movie_service"]
        export_service = services["export_service"]
        mock_tmdb_client = services["tmdb_client"]

        # Mock API responses - use side_effect to return different data based on movie ID
        from tests.conftest import _get_movie_details_by_id, _get_keywords_by_id
        
        mock_tmdb_client.get_movies_by_year.return_value = mock_tmdb_api_response
        mock_tmdb_client.get_movie_details.side_effect = lambda movie_id: _get_movie_details_by_id(movie_id)
        mock_tmdb_client.get_movie_keywords.side_effect = lambda movie_id: _get_keywords_by_id(movie_id)

        # Step 1: Get top movies
        movies, csv_path = movie_service.get_and_export_top_movies(
            year=1999,
            top_n=3,
            filename="test_top_movies.csv",
        )

        # Verify movies were retrieved
        assert len(movies) == 3
        assert Path(csv_path).exists()

        # Verify CSV content
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Should have 3 movies * 3 sort methods = 9 rows
        assert len(rows) == 9

        # Verify all sort methods are present
        sort_methods = {row["sort_method"] for row in rows}
        assert "votes" in sort_methods
        assert "name" in sort_methods
        assert "name_no_articles" in sort_methods

        # Verify movies are present
        titles = {row["title"] for row in rows}
        assert "The Matrix" in titles
        assert "Inception" in titles
        assert "A Beautiful Mind" in titles

    def test_complete_workflow_with_similar_movies(
        self,
        services,
        mock_tmdb_api_response,
        mock_movie_details_response,
        mock_keywords_response,
        mock_similar_movies_response,
    ):
        """Test complete workflow: get top movies, find similar movies, and export both."""
        movie_service = services["movie_service"]
        recommendation_service = services["recommendation_service"]
        export_service = services["export_service"]
        mock_tmdb_client = services["tmdb_client"]

        # Mock API responses for movie retrieval - use side_effect to return different data based on movie ID
        from tests.conftest import _get_movie_details_by_id, _get_keywords_by_id
        
        mock_tmdb_client.get_movies_by_year.return_value = mock_tmdb_api_response
        mock_tmdb_client.get_movie_details.side_effect = lambda movie_id: _get_movie_details_by_id(movie_id)
        mock_tmdb_client.get_movie_keywords.side_effect = lambda movie_id: _get_keywords_by_id(movie_id)

        # Step 1: Get top movies
        movies, movies_csv_path = movie_service.get_and_export_top_movies(
            year=1999,
            top_n=2,  # Use 2 for faster testing
            filename="test_top_movies.csv",
        )

        assert len(movies) == 2
        assert Path(movies_csv_path).exists()

        # Mock API responses for similar movies - also need to mock details for similar movies
        mock_tmdb_client.get_similar_movies.return_value = mock_similar_movies_response
        # Ensure get_movie_details and get_movie_keywords still work for similar movies (IDs 4, 5)

        # Step 2: Find similar movies
        similar_movies_data = recommendation_service.get_similar_movies_for_multiple(
            movies=movies,
            limit=2,
        )

        assert len(similar_movies_data) > 0

        # Step 3: Prepare for export
        export_data = recommendation_service.prepare_similar_movies_for_export(
            similar_movies_data
        )

        assert len(export_data) > 0

        # Step 4: Export similar movies
        similar_csv_path = export_service.export_similar_movies_to_csv(
            similar_movies_data=export_data,
            filename="test_similar_movies.csv",
        )

        assert Path(similar_csv_path).exists()

        # Verify similar movies CSV content
        with open(similar_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0
        assert "original_movie_id" in rows[0]
        assert "similar_movie_id" in rows[0]
        assert "similarity_score" in rows[0]
        assert "similarity_reason" in rows[0]

    def test_workflow_sorting_verification(
        self,
        services,
        mock_tmdb_api_response,
        mock_movie_details_response,
        mock_keywords_response,
    ):
        """Test that sorting works correctly in the exported CSV."""
        movie_service = services["movie_service"]
        mock_tmdb_client = services["tmdb_client"]

        # Mock API responses - use side_effect to return different data based on movie ID
        from tests.conftest import _get_movie_details_by_id, _get_keywords_by_id
        
        mock_tmdb_client.get_movies_by_year.return_value = mock_tmdb_api_response
        mock_tmdb_client.get_movie_details.side_effect = lambda movie_id: _get_movie_details_by_id(movie_id)
        mock_tmdb_client.get_movie_keywords.side_effect = lambda movie_id: _get_keywords_by_id(movie_id)

        # Get and export movies
        movies, csv_path = movie_service.get_and_export_top_movies(
            year=1999,
            top_n=3,
            filename="test_sorting.csv",
        )

        # Read CSV and verify sorting
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Filter by sort method
        votes_rows = [r for r in rows if r["sort_method"] == "votes"]
        name_rows = [r for r in rows if r["sort_method"] == "name"]
        name_no_articles_rows = [r for r in rows if r["sort_method"] == "name_no_articles"]

        # Verify votes sorting (highest first)
        vote_counts = [int(r["vote_count"]) for r in votes_rows]
        assert vote_counts == sorted(vote_counts, reverse=True)

        # Verify name sorting (alphabetical)
        titles = [r["title"] for r in name_rows]
        assert titles == sorted(titles)

        # Verify name_no_articles sorting
        # "A Beautiful Mind" should come before "The Matrix" when ignoring articles
        titles_no_articles = [r["title"] for r in name_no_articles_rows]
        # Should be sorted: "A Beautiful Mind", "Inception", "The Matrix"
        assert titles_no_articles[0] == "A Beautiful Mind"

    def test_workflow_error_handling(
        self,
        services,
        mock_tmdb_client,
    ):
        """Test error handling in the workflow."""
        movie_service = services["movie_service"]

        # Mock API to return None (simulating failure)
        mock_tmdb_client.get_movies_by_year.return_value = None

        # Should raise ValueError when no movies found
        with pytest.raises(ValueError, match="No movies found"):
            movie_service.get_top_movies_by_year(year=1999, top_n=10)

    def test_workflow_empty_results(
        self,
        services,
        mock_tmdb_client,
    ):
        """Test workflow with empty API results."""
        movie_service = services["movie_service"]

        # Mock API to return empty results
        mock_tmdb_client.get_movies_by_year.return_value = {
            "page": 1,
            "results": [],
            "total_pages": 0,
            "total_results": 0,
        }

        # Should raise ValueError
        with pytest.raises(ValueError, match="No movies found"):
            movie_service.get_top_movies_by_year(year=1999, top_n=10)

