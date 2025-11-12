"""
End-to-end integration tests simulating the complete application flow.

This module tests:
- Complete workflow from fetching movies to exporting results
- Data consistency across the workflow
- CSV format validation
- Sorting verification
- Error handling scenarios
"""

import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.export_service import ExportService
from src.services.movie_service import MovieService
from src.services.movie_recommendation_engine import RecommendationService


def flatten_similar_movies_for_export(similar_movies_data):
    """Helper function to flatten similar movies data for export."""
    export_data = []
    for item in similar_movies_data:
        original_movie = item.get("original_movie")
        similar_movies = item.get("similar_movies", [])

        for similar_entry in similar_movies:
            export_data.append({
                "original_movie": original_movie,
                "similar_movie": similar_entry.get("similar_movie"),
                "similarity_score": similar_entry.get("similarity_score"),
                "similarity_reason": similar_entry.get("similarity_reason"),
                "similarity_metrics": similar_entry.get("similarity_metrics", {}),
            })

    return export_data


@pytest.mark.integration
@pytest.mark.e2e
class TestEndToEnd:
    """End-to-end tests for the complete application workflow."""

    @pytest.fixture
    def setup_mocked_services(self, test_output_dir, mock_env_vars):
        """Set up all services with mocked TMDB client."""
        mock_tmdb_client = MagicMock()

        # Create comprehensive mock responses
        discover_response = {
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
            ],
            "total_pages": 1,
            "total_results": 2,
        }

        movie_details_response = {
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
        }

        keywords_response = {
            "id": 1,
            "keywords": [
                {"id": 100, "name": "artificial intelligence"},
                {"id": 101, "name": "virtual reality"},
                {"id": 102, "name": "hacker"},
            ],
        }

        similar_movies_response = {
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

        # Configure mock responses - use side_effect to return different data based on movie ID
        from tests.conftest import _get_movie_details_by_id, _get_keywords_by_id
        
        mock_tmdb_client.get_movies_by_year.return_value = discover_response
        mock_tmdb_client.get_movie_details.side_effect = lambda movie_id: _get_movie_details_by_id(movie_id)
        mock_tmdb_client.get_movie_keywords.side_effect = lambda movie_id: _get_keywords_by_id(movie_id)
        mock_tmdb_client.get_similar_movies.return_value = similar_movies_response
        # Also need to mock get_movie_recommendations for the recommendation service
        mock_tmdb_client.get_movie_recommendations.return_value = similar_movies_response

        with patch("src.services.movie_service.TMDBClient", return_value=mock_tmdb_client), \
             patch("src.services.movie_recommendation_engine.TMDBClient", return_value=mock_tmdb_client):
            
            movie_service = MovieService(tmdb_client=mock_tmdb_client)
            recommendation_service = RecommendationService(tmdb_client=mock_tmdb_client)
            export_service = ExportService(output_dir=str(test_output_dir))

            return {
                "movie_service": movie_service,
                "recommendation_service": recommendation_service,
                "export_service": export_service,
                "tmdb_client": mock_tmdb_client,
            }

    def test_complete_application_workflow(self, setup_mocked_services):
        """Test the complete application workflow from start to finish."""
        services = setup_mocked_services
        movie_service = services["movie_service"]
        recommendation_service = services["recommendation_service"]
        export_service = services["export_service"]

        # Step 1: Get top movies for a year
        year = 1999
        top_n = 2

        movies, movies_csv_path = movie_service.get_and_export_top_movies(
            year=year,
            top_n=top_n,
            filename="top_movies_1999.csv",
        )

        # Verify Step 1
        assert len(movies) == top_n
        assert Path(movies_csv_path).exists()

        # Verify CSV has all three sort methods
        with open(movies_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == top_n * 3  # 2 movies * 3 sort methods
        sort_methods = {row["sort_method"] for row in rows}
        assert sort_methods == {"votes", "name", "name_no_articles"}

        # Step 2: Find similar movies for each top movie
        similar_movies_data = recommendation_service.find_similar_movies_for_each(
            top_movies=movies,
            similar_per_movie=2,
            strategy="tmdb_api"
        )

        # Verify Step 2
        assert len(similar_movies_data) == len(movies)
        for item in similar_movies_data:
            assert "original_movie" in item
            assert "similar_movies" in item
            assert len(item["similar_movies"]) > 0

        # Step 3: Prepare similar movies for export
        export_data = flatten_similar_movies_for_export(similar_movies_data)

        # Verify Step 3
        assert len(export_data) > 0
        for entry in export_data:
            assert "original_movie" in entry
            assert "similar_movie" in entry
            assert "similarity_score" in entry
            assert "similarity_reason" in entry
            assert "similarity_metrics" in entry

        # Step 4: Export similar movies to CSV
        similar_csv_path = export_service.export_similar_movies_to_csv(
            similar_movies_data=export_data,
            filename="similar_movies_1999.csv",
        )

        # Verify Step 4
        assert Path(similar_csv_path).exists()

        with open(similar_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0
        assert "original_movie_id" in rows[0]
        assert "similar_movie_id" in rows[0]
        assert "similarity_score" in rows[0]
        assert "similarity_reason" in rows[0]
        assert "genre_similarity" in rows[0]
        assert "keyword_similarity" in rows[0]

        # Verify similarity scores are valid
        for row in rows:
            score = float(row["similarity_score"]) if row["similarity_score"] else 0.0
            assert 0.0 <= score <= 1.0

    def test_workflow_data_consistency(self, setup_mocked_services):
        """Test that data is consistent throughout the workflow."""
        services = setup_mocked_services
        movie_service = services["movie_service"]
        recommendation_service = services["recommendation_service"]
        export_service = services["export_service"]

        # Get top movies
        movies, movies_csv_path = movie_service.get_and_export_top_movies(
            year=1999,
            top_n=2,
            filename="test_consistency.csv",
        )

        # Find similar movies
        similar_movies_data = recommendation_service.find_similar_movies_for_each(
            top_movies=movies,
            similar_per_movie=2,
            strategy="tmdb_api"
        )

        # Export similar movies
        export_data = flatten_similar_movies_for_export(similar_movies_data)
        similar_csv_path = export_service.export_similar_movies_to_csv(
            similar_movies_data=export_data,
            filename="test_similar_consistency.csv",
        )

        # Verify original movies in similar movies CSV match top movies
        with open(similar_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            similar_rows = list(reader)

        original_movie_ids_in_similar = {
            int(row["original_movie_id"]) for row in similar_rows
        }
        top_movie_ids = {movie.id for movie in movies}

        assert original_movie_ids_in_similar == top_movie_ids



    def test_workflow_sorting_verification(self, setup_mocked_services):
        """Test that sorting works correctly in the exported CSV."""
        services = setup_mocked_services
        movie_service = services["movie_service"]
        export_service = services["export_service"]

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

        # Verify votes sorting (highest first)
        vote_counts = [int(r["vote_count"]) for r in votes_rows]
        assert vote_counts == sorted(vote_counts, reverse=True), "Votes should be sorted descending"

        # Verify name sorting (alphabetical)
        titles = [r["title"] for r in name_rows]
        assert titles == sorted(titles), "Names should be sorted alphabetically"

    def test_workflow_error_handling(self, setup_mocked_services):
        """Test error handling in the workflow."""
        services = setup_mocked_services
        movie_service = services["movie_service"]
        tmdb_client = services["tmdb_client"]

        # Mock API to return None (simulating failure)
        tmdb_client.get_movies_by_year.return_value = None

        # Should raise ValueError when no movies found
        with pytest.raises(ValueError, match="No movies found"):
            movie_service.get_top_movies_by_year(year=1999, top_n=10)

    def test_workflow_empty_results(self, setup_mocked_services):
        """Test workflow with empty API results."""
        services = setup_mocked_services
        movie_service = services["movie_service"]
        tmdb_client = services["tmdb_client"]

        # Mock API to return empty results
        tmdb_client.get_movies_by_year.return_value = {
            "page": 1,
            "results": [],
            "total_pages": 0,
            "total_results": 0,
        }

        # Should raise ValueError
        with pytest.raises(ValueError, match="No movies found"):
            movie_service.get_top_movies_by_year(year=1999, top_n=10)

