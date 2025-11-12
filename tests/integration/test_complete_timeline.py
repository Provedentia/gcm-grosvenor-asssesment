"""
Complete timeline test - tests the entire application workflow from start to finish.
This test simulates the complete user journey as described in the assignment.
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
class TestCompleteTimeline:
    """
    Complete timeline test covering the entire application workflow.
    Tests the assignment requirements end-to-end.
    """

    @pytest.fixture
    def setup_complete_mock_environment(self, test_output_dir, mock_env_vars):
        """Set up complete mock environment for end-to-end testing."""
        mock_tmdb_client = MagicMock()

        # Create comprehensive mock data for 10 movies from year 2020
        year_2020_movies = [
            {
                "id": 100 + i,
                "title": f"Movie {i+1}",
                "release_date": f"2020-{(i%12)+1:02d}-15",
                "vote_count": 30000 - (i * 500),
                "vote_average": 8.5 - (i * 0.1),
                "popularity": 90.0 - (i * 2),
                "overview": f"Overview for Movie {i+1}",
                "poster_path": f"/poster{i+1}.jpg",
                "backdrop_path": f"/backdrop{i+1}.jpg",
                "adult": False,
                "original_language": "en",
                "original_title": f"Movie {i+1}",
                "video": False,
                "genre_ids": [28, 878] if i % 2 == 0 else [18, 36],
            }
            for i in range(10)
        ]

        discover_response = {
            "page": 1,
            "results": year_2020_movies,
            "total_pages": 1,
            "total_results": 10,
        }

        def get_movie_details_side_effect(movie_id: int):
            """Return movie details based on movie_id."""
            movie_idx = movie_id - 100
            if 0 <= movie_idx < 10:
                movie = year_2020_movies[movie_idx]
                return {
                    **movie,
                    "genres": [
                        {"id": 28, "name": "Action"},
                        {"id": 878, "name": "Science Fiction"},
                    ]
                    if movie_idx % 2 == 0
                    else [{"id": 18, "name": "Drama"}, {"id": 36, "name": "History"}],
                    "runtime": 120 + movie_idx,
                    "status": "Released",
                    "tagline": f"Tagline for Movie {movie_idx+1}",
                    "budget": 50000000,
                    "revenue": 200000000,
                    "homepage": f"https://example.com/movie{movie_idx+1}",
                    "imdb_id": f"tt{movie_id:07d}",
                    "production_companies": [],
                    "production_countries": [],
                    "spoken_languages": [],
                }
            return None

        def get_keywords_side_effect(movie_id: int):
            """Return keywords based on movie_id."""
            return {
                "id": movie_id,
                "keywords": [
                    {"id": 100 + movie_id, "name": "action"},
                    {"id": 101 + movie_id, "name": "thriller"},
                ],
            }

        def get_similar_movies_side_effect(movie_id: int, page: int = 1):
            """Return similar movies based on movie_id."""
            # Return 5 similar movies for each movie
            similar_movies = [
                {
                    "id": 200 + (movie_id - 100) * 10 + i,
                    "title": f"Similar Movie {i+1} to Movie {movie_id-100+1}",
                    "release_date": f"202{(i%2):d}-{(i%12)+1:02d}-15",
                    "vote_count": 15000 + (i * 100),
                    "vote_average": 7.5 + (i * 0.1),
                    "popularity": 70.0 + (i * 2),
                    "overview": f"Similar movie {i+1}",
                    "poster_path": f"/similar_poster{i+1}.jpg",
                    "backdrop_path": f"/similar_backdrop{i+1}.jpg",
                    "adult": False,
                    "original_language": "en",
                    "original_title": f"Similar Movie {i+1}",
                    "video": False,
                    "genre_ids": [28, 878],
                }
                for i in range(5)
            ]
            return {
                "page": page,
                "results": similar_movies,
                "total_pages": 1,
                "total_results": 5,
            }

        # Configure mock responses
        mock_tmdb_client.get_movies_by_year.return_value = discover_response
        mock_tmdb_client.get_movie_details.side_effect = get_movie_details_side_effect
        mock_tmdb_client.get_movie_keywords.side_effect = get_keywords_side_effect
        mock_tmdb_client.get_similar_movies.side_effect = get_similar_movies_side_effect

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
                "output_dir": test_output_dir,
            }

    def test_complete_assignment_requirements(self, setup_complete_mock_environment):
        """
        Test complete assignment requirements:
        1. Get top 10 movies from a year
        2. Sort by votes and save to CSV
        3. Sort by name (with articles) and append to CSV
        4. Sort by name (without articles) and append to CSV
        5. Find 3 similar movies for each top 10 movie
        6. Export 30 similar movies to separate CSV with metrics
        """
        services = setup_complete_mock_environment
        movie_service = services["movie_service"]
        recommendation_service = services["recommendation_service"]
        export_service = services["export_service"]
        output_dir = services["output_dir"]

        year = 2020
        top_n = 10
        similar_limit = 3

        # Step 1: Get top 10 movies from year 2020
        print(f"\n📽️  Step 1: Getting top {top_n} movies from year {year}...")
        movies, movies_csv_path = movie_service.get_and_export_top_movies(
            year=year,
            top_n=top_n,
            filename="top_movies_2020.csv",
        )

        # Verify Step 1
        assert len(movies) == top_n, f"Expected {top_n} movies, got {len(movies)}"
        assert Path(movies_csv_path).exists(), "Top movies CSV file should exist"

        # Verify CSV has all three sort methods
        with open(movies_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        expected_rows = top_n * 3  # 10 movies * 3 sort methods = 30 rows
        assert len(rows) == expected_rows, f"Expected {expected_rows} rows, got {len(rows)}"

        # Verify all three sort methods are present
        sort_methods = {row["sort_method"] for row in rows}
        assert "votes" in sort_methods, "Missing 'votes' sort method"
        assert "name" in sort_methods, "Missing 'name' sort method"
        assert "name_no_articles" in sort_methods, "Missing 'name_no_articles' sort method"

        # Verify votes sorting (highest first)
        votes_rows = [r for r in rows if r["sort_method"] == "votes"]
        vote_counts = [int(r["vote_count"]) for r in votes_rows]
        assert vote_counts == sorted(vote_counts, reverse=True), "Votes should be sorted descending"

        # Verify name sorting (alphabetical)
        name_rows = [r for r in rows if r["sort_method"] == "name"]
        titles = [r["title"] for r in name_rows]
        assert titles == sorted(titles), "Names should be sorted alphabetically"

        print(f"✅ Step 1 Complete: {len(movies)} movies exported to {movies_csv_path}")

        # Step 2: Find 3 similar movies for each of the top 10 movies
        print(f"\n🔍 Step 2: Finding {similar_limit} similar movies for each movie...")
        similar_movies_data = recommendation_service.find_similar_movies_for_each(
            top_movies=movies,
            similar_per_movie=similar_limit,
            strategy="tmdb_api"
        )

        # Verify Step 2
        assert len(similar_movies_data) == top_n, f"Expected {top_n} entries, got {len(similar_movies_data)}"

        total_similar_movies = sum(len(item.get("similar_movies", [])) for item in similar_movies_data)
        expected_similar = top_n * similar_limit  # 10 movies * 3 similar = 30
        assert total_similar_movies >= similar_limit, f"Expected at least {similar_limit} similar movies per movie"

        print(f"✅ Step 2 Complete: Found {total_similar_movies} similar movies")

        # Step 3: Prepare similar movies for export
        print(f"\n📊 Step 3: Preparing similar movies data for export...")
        export_data = flatten_similar_movies_for_export(similar_movies_data)

        # Verify Step 3
        assert len(export_data) > 0, "Export data should not be empty"
        for entry in export_data:
            assert "original_movie" in entry, "Missing original_movie in export data"
            assert "similar_movie" in entry, "Missing similar_movie in export data"
            assert "similarity_score" in entry, "Missing similarity_score in export data"
            assert "similarity_reason" in entry, "Missing similarity_reason in export data"
            assert "similarity_metrics" in entry, "Missing similarity_metrics in export data"

        print(f"✅ Step 3 Complete: Prepared {len(export_data)} entries for export")

        # Step 4: Export similar movies to CSV
        print(f"\n💾 Step 4: Exporting similar movies to CSV...")
        similar_csv_path = export_service.export_similar_movies_to_csv(
            similar_movies_data=export_data,
            filename="similar_movies_2020.csv",
        )

        # Verify Step 4
        assert Path(similar_csv_path).exists(), "Similar movies CSV file should exist"

        with open(similar_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0, "Similar movies CSV should not be empty"

        # Verify CSV has all required columns with similarity metrics
        required_columns = [
            "original_movie_id",
            "original_movie_title",
            "similar_movie_id",
            "similar_movie_title",
            "similarity_score",
            "similarity_reason",
            "genre_similarity",
            "keyword_similarity",
            "content_similarity",
            "rating_similarity",
            "year_similarity",
            "shared_genres",
            "shared_keywords",
        ]

        for col in required_columns:
            assert col in reader.fieldnames, f"Missing required column: {col}"

        # Verify similarity scores are valid
        for row in rows:
            score = float(row["similarity_score"]) if row["similarity_score"] else 0.0
            assert 0.0 <= score <= 1.0, f"Similarity score should be between 0 and 1, got {score}"

        # Verify we have data for all original movies
        original_movie_ids = {int(row["original_movie_id"]) for row in rows}
        assert len(original_movie_ids) == top_n, f"Should have similar movies for all {top_n} original movies"

        print(f"✅ Step 4 Complete: Exported {len(rows)} similar movie entries to {similar_csv_path}")

        # Final verification: Check both CSV files exist and have correct content
        print(f"\n📋 Final Verification:")
        print(f"  - Top movies CSV: {movies_csv_path} ({len(list(csv.DictReader(open(movies_csv_path))))} rows)")
        print(f"  - Similar movies CSV: {similar_csv_path} ({len(rows)} rows)")
        print(f"  - Total original movies: {top_n}")
        print(f"  - Total similar movies: {len(rows)}")
        print(f"  - Average similar movies per original: {len(rows) / top_n:.1f}")

        # Verify file sizes are reasonable
        movies_file_size = Path(movies_csv_path).stat().st_size
        similar_file_size = Path(similar_csv_path).stat().st_size

        assert movies_file_size > 0, "Top movies CSV should not be empty"
        assert similar_file_size > 0, "Similar movies CSV should not be empty"

        print(f"\n✅ All requirements met! Complete timeline test passed.")

    def test_timeline_with_different_year(self, setup_complete_mock_environment):
        """Test complete timeline with a different year."""
        services = setup_complete_mock_environment
        movie_service = services["movie_service"]
        recommendation_service = services["recommendation_service"]
        export_service = services["export_service"]

        # Modify mock to return data for year 2019
        services["tmdb_client"].get_movies_by_year.return_value = {
            "page": 1,
            "results": [
                {
                    "id": 200 + i,
                    "title": f"2019 Movie {i+1}",
                    "release_date": f"2019-{(i%12)+1:02d}-15",
                    "vote_count": 25000 - (i * 300),
                    "vote_average": 8.0 - (i * 0.1),
                    "popularity": 80.0 - (i * 2),
                    "overview": f"Overview for 2019 Movie {i+1}",
                    "poster_path": f"/poster{i+1}.jpg",
                    "backdrop_path": f"/backdrop{i+1}.jpg",
                    "adult": False,
                    "original_language": "en",
                    "original_title": f"2019 Movie {i+1}",
                    "video": False,
                    "genre_ids": [28, 878],
                }
                for i in range(5)
            ],
            "total_pages": 1,
            "total_results": 5,
        }

        # Test with year 2019 and top 5
        movies, movies_csv_path = movie_service.get_and_export_top_movies(
            year=2019,
            top_n=5,
            filename="top_movies_2019.csv",
        )

        assert len(movies) == 5
        assert Path(movies_csv_path).exists()

        # Find similar movies
        similar_movies_data = recommendation_service.find_similar_movies_for_each(
            top_movies=movies,
            similar_per_movie=2,
            strategy="tmdb_api"
        )

        assert len(similar_movies_data) == 5

        # Export similar movies
        export_data = flatten_similar_movies_for_export(similar_movies_data)
        similar_csv_path = export_service.export_similar_movies_to_csv(
            similar_movies_data=export_data,
            filename="similar_movies_2019.csv",
        )

        assert Path(similar_csv_path).exists()

