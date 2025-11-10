"""
Real TMDB API integration tests.
These tests make actual API calls to TMDB and require a valid API key.

To run these tests:
1. Set TMDB_API_KEY environment variable
2. Run: pytest tests/api/ -v -m api
"""

import csv
from pathlib import Path

import pytest

from src.api.TMDB import TMDBClient
from src.services.export_service import ExportService
from src.services.movie_service import MovieService
from src.services.recommendation_service import RecommendationService


@pytest.mark.api
@pytest.mark.slow
class TestRealTMDBAPI:
    """Tests that use the actual TMDB API."""

    def test_real_api_client_initialization(self, real_tmdb_client):
        """Test that the real TMDB client can be initialized."""
        assert real_tmdb_client is not None
        assert real_tmdb_client.api_key is not None
        assert real_tmdb_client.base_url == "https://api.themoviedb.org/3"

    def test_real_api_get_movies_by_year(self, real_tmdb_client):
        """Test getting movies from a real year using the actual API."""
        # Test with a known year with many movies
        year = 2020
        response = real_tmdb_client.get_movies_by_year(
            year=year,
            min_vote_count=100,
            min_vote_average=6.0,
            page=1
        )
        
        assert response is not None
        assert "results" in response
        assert "page" in response
        assert "total_pages" in response
        assert len(response["results"]) > 0
        
        # Verify movie structure
        movie = response["results"][0]
        assert "id" in movie
        assert "title" in movie
        assert "release_date" in movie
        assert "vote_count" in movie
        assert "vote_average" in movie

    def test_real_api_get_movie_details(self, real_tmdb_client):
        """Test getting movie details using the actual API."""
        # Test with a known movie ID (The Matrix)
        movie_id = 603
        response = real_tmdb_client.get_movie_details(movie_id)
        
        assert response is not None
        assert response["id"] == movie_id
        assert "title" in response
        assert "overview" in response
        assert "genres" in response
        assert "release_date" in response

    def test_real_api_get_movie_keywords(self, real_tmdb_client):
        """Test getting movie keywords using the actual API."""
        # Test with a known movie ID (The Matrix)
        movie_id = 603
        response = real_tmdb_client.get_movie_keywords(movie_id)
        
        assert response is not None
        assert "id" in response
        assert "keywords" in response
        assert isinstance(response["keywords"], list)

    def test_real_api_get_similar_movies(self, real_tmdb_client):
        """Test getting similar movies using the actual API."""
        # Test with a known movie ID (The Matrix)
        movie_id = 603
        response = real_tmdb_client.get_similar_movies(movie_id, page=1)
        
        assert response is not None
        assert "results" in response
        assert len(response["results"]) > 0
        
        # Verify similar movie structure
        similar_movie = response["results"][0]
        assert "id" in similar_movie
        assert "title" in similar_movie
        assert similar_movie["id"] != movie_id  # Should be different from original

    def test_real_api_get_movie_recommendations(self, real_tmdb_client):
        """Test getting movie recommendations using the actual API."""
        # Test with a known movie ID (The Matrix)
        movie_id = 603
        response = real_tmdb_client.get_movie_recommendations(movie_id, page=1)
        
        assert response is not None
        assert "results" in response
        # Recommendations may be empty for some movies
        if len(response["results"]) > 0:
            recommended_movie = response["results"][0]
            assert "id" in recommended_movie
            assert "title" in recommended_movie

    def test_real_api_discover_movies_with_genre(self, real_tmdb_client):
        """Test discovering movies with genre filter using the actual API."""
        # Test with Action genre (ID: 28)
        response = real_tmdb_client.discover_movies(
            year=2020,
            min_vote_count=100,
            min_vote_average=6.0,
            with_genres=28,  # Action
            page=1
        )
        
        assert response is not None
        assert "results" in response
        if len(response["results"]) > 0:
            movie = response["results"][0]
            assert "id" in movie
            assert "title" in movie


@pytest.mark.api
@pytest.mark.slow
@pytest.mark.e2e
class TestRealMovieService:
    """Tests for MovieService using the real TMDB API."""

    def test_real_get_top_movies_by_year(self, real_movie_service):
        """Test getting top movies from a real year using the actual API."""
        year = 2020
        top_n = 5
        
        movies = real_movie_service.get_top_movies_by_year(
            year=year,
            top_n=top_n,
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        assert len(movies) == top_n
        assert all(movie.release_year == year for movie in movies)
        assert all(movie.vote_count >= 100 for movie in movies)
        assert all(movie.vote_average >= 6.0 for movie in movies)
        
        # Verify movies are sorted by vote count (descending)
        vote_counts = [movie.vote_count for movie in movies]
        assert vote_counts == sorted(vote_counts, reverse=True)

    def test_real_export_top_movies_to_csv(self, real_movie_service, tmp_path):
        """Test exporting top movies to CSV using the actual API."""
        year = 2020
        top_n = 3
        filename = "real_api_test_movies.csv"
        
        # Update export service to use tmp_path
        real_movie_service.export_service = ExportService(output_dir=str(tmp_path))
        
        movies, csv_path = real_movie_service.get_and_export_top_movies(
            year=year,
            top_n=top_n,
            filename=filename,
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        assert len(movies) == top_n
        assert Path(csv_path).exists()
        
        # Verify CSV content
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Should have top_n * 3 rows (3 sort methods)
        assert len(rows) == top_n * 3
        
        # Verify all sort methods are present
        sort_methods = {row["sort_method"] for row in rows}
        assert "votes" in sort_methods
        assert "name" in sort_methods
        assert "name_no_articles" in sort_methods
        
        # Verify movies are present
        titles = {row["title"] for row in rows}
        assert len(titles) == top_n

    def test_real_sort_movies_by_name_with_articles(self, real_movie_service):
        """Test sorting movies by name (with articles) using real API data."""
        year = 2020
        movies = real_movie_service.get_top_movies_by_year(
            year=year,
            top_n=5,
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        # Sort by name with articles
        sorted_movies = real_movie_service.sort_movies_by_name(movies, ignore_articles=False)
        
        # Verify sorting
        titles = [movie.title for movie in sorted_movies]
        assert titles == sorted(titles)

    def test_real_sort_movies_by_name_without_articles(self, real_movie_service):
        """Test sorting movies by name (without articles) using real API data."""
        year = 2020
        movies = real_movie_service.get_top_movies_by_year(
            year=year,
            top_n=5,
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        # Sort by name without articles
        sorted_movies = real_movie_service.sort_movies_by_name(movies, ignore_articles=True)
        
        # Verify sorting (normalized titles should be alphabetical)
        normalized_titles = [
            movie.normalize_title_for_sorting(ignore_articles=True).lower()
            for movie in sorted_movies
        ]
        assert normalized_titles == sorted(normalized_titles)


@pytest.mark.api
@pytest.mark.slow
@pytest.mark.e2e
class TestRealRecommendationService:
    """Tests for RecommendationService using the real TMDB API."""

    def test_real_find_similar_movies(self, real_recommendation_service, real_movie_service):
        """Test finding similar movies using the actual API."""
        # Get a real movie first
        year = 2020
        movies = real_movie_service.get_top_movies_by_year(
            year=year,
            top_n=1,
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        if not movies:
            pytest.skip("No movies found for testing")
        
        original_movie = movies[0]
        
        # Find similar movies
        similar_movies = real_recommendation_service.find_similar_movies(
            original_movie=original_movie,
            limit=3,
            min_vote_count=50
        )
        
        # Should find at least some similar movies (may be 0 if API returns none)
        assert isinstance(similar_movies, list)
        
        if len(similar_movies) > 0:
            # Verify structure
            for similar in similar_movies:
                assert "similar_movie" in similar
                assert "similarity_score" in similar
                assert "similarity_reason" in similar
                assert "similarity_metrics" in similar
                
                # Verify similarity score is valid
                assert 0.0 <= similar["similarity_score"] <= 1.0
                
                # Verify similar movie is different from original
                assert similar["similar_movie"].id != original_movie.id

    def test_real_get_similar_movies_for_multiple(self, real_recommendation_service, real_movie_service):
        """Test getting similar movies for multiple movies using the actual API."""
        # Get real movies
        year = 2020
        movies = real_movie_service.get_top_movies_by_year(
            year=year,
            top_n=2,
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        if len(movies) < 2:
            pytest.skip("Not enough movies found for testing")
        
        # Find similar movies for each
        similar_movies_data = real_recommendation_service.get_similar_movies_for_multiple(
            movies=movies,
            limit=2,
            min_vote_count=50
        )
        
        # Should have results for at least some movies
        assert isinstance(similar_movies_data, list)
        assert len(similar_movies_data) <= len(movies)
        
        # Verify structure for each result
        for item in similar_movies_data:
            assert "original_movie" in item
            assert "similar_movies" in item
            assert isinstance(item["similar_movies"], list)


@pytest.mark.api
@pytest.mark.slow
@pytest.mark.e2e
class TestRealCompleteWorkflow:
    """End-to-end tests using the real TMDB API."""

    def test_real_complete_workflow_top_movies(self, real_movie_service, tmp_path):
        """Test complete workflow: get top movies and export to CSV using real API."""
        year = 2020
        top_n = 5
        
        # Update export service to use tmp_path
        real_movie_service.export_service = ExportService(output_dir=str(tmp_path))
        
        # Get and export top movies
        movies, csv_path = real_movie_service.get_and_export_top_movies(
            year=year,
            top_n=top_n,
            filename="real_workflow_test.csv",
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        # Verify results
        assert len(movies) == top_n
        assert Path(csv_path).exists()
        
        # Verify CSV has all three sort methods
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == top_n * 3
        sort_methods = {row["sort_method"] for row in rows}
        assert sort_methods == {"votes", "name", "name_no_articles"}
        
        # Verify votes are sorted correctly
        votes_rows = [r for r in rows if r["sort_method"] == "votes"]
        vote_counts = [int(r["vote_count"]) for r in votes_rows]
        assert vote_counts == sorted(vote_counts, reverse=True)
        
        # Verify name sorting (with articles)
        name_rows = [r for r in rows if r["sort_method"] == "name"]
        titles = [r["title"] for r in name_rows]
        assert titles == sorted(titles)

    def test_real_complete_workflow_with_similar_movies(
        self, real_movie_service, real_recommendation_service, tmp_path
    ):
        """Test complete workflow with similar movies using real API."""
        year = 2020
        top_n = 3
        
        # Update export service to use tmp_path
        real_movie_service.export_service = ExportService(output_dir=str(tmp_path))
        export_service = ExportService(output_dir=str(tmp_path))
        
        # Get top movies
        movies, movies_csv_path = real_movie_service.get_and_export_top_movies(
            year=year,
            top_n=top_n,
            filename="real_workflow_movies.csv",
            min_vote_count=100,
            min_vote_average=6.0
        )
        
        assert len(movies) > 0
        assert Path(movies_csv_path).exists()
        
        # Find similar movies
        similar_movies_data = real_recommendation_service.get_similar_movies_for_multiple(
            movies=movies[:2],  # Use first 2 movies to save API calls
            limit=2,
            min_vote_count=50
        )
        
        # May have 0 results if API doesn't return similar movies
        if len(similar_movies_data) > 0:
            # Prepare for export
            export_data = real_recommendation_service.prepare_similar_movies_for_export(
                similar_movies_data
            )
            
            if len(export_data) > 0:
                # Export similar movies
                similar_csv_path = export_service.export_similar_movies_to_csv(
                    similar_movies_data=export_data,
                    filename="real_workflow_similar.csv",
                )
                
                assert Path(similar_csv_path).exists()
                
                # Verify CSV structure
                with open(similar_csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                
                assert len(rows) > 0
                assert "original_movie_id" in rows[0]
                assert "similar_movie_id" in rows[0]
                assert "similarity_score" in rows[0]

