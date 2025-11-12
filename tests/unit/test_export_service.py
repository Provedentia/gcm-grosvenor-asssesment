"""
Unit tests for ExportService.

Tests the ExportService class which handles:
- Converting movie data to CSV format
- Exporting top movies to CSV files
- Exporting similar movies with similarity metrics to CSV files
- Appending data to existing CSV files
"""

import csv
from pathlib import Path
from unittest.mock import patch

import pytest

from src.models.Movies import Movie
from src.services.export_service import ExportService


class TestExportService:
    """Test suite for ExportService functionality."""

    @pytest.fixture
    def export_service(self, test_output_dir):
        """Create an ExportService instance with test output directory."""
        return ExportService(output_dir=str(test_output_dir))

    def test_movie_to_csv_row(self, export_service, sample_movies):
        """Test converting a movie to CSV row."""
        movie = sample_movies[0]
        row = export_service._movie_to_csv_row(movie, sort_method="votes")

        assert row["id"] == "1"
        assert row["title"] == "The Matrix"
        assert row["sort_method"] == "votes"
        assert row["vote_count"] == "25000"
        assert row["vote_average"] == "8.7"

    def test_export_movies_to_csv(self, export_service, sample_movies):
        """Test exporting movies to CSV."""
        movies_data = [
            {"movie": movie, "sort_method": "votes"} for movie in sample_movies
        ]

        filepath = export_service.export_movies_to_csv(
            movies_data=movies_data, filename="test_movies.csv", append=False
        )

        assert Path(filepath).exists()

        # Read and verify CSV
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert rows[0]["title"] == "The Matrix"
        assert rows[0]["sort_method"] == "votes"

    def test_export_movies_to_csv_append(self, export_service, sample_movies):
        """Test appending movies to existing CSV."""
        # First export
        movies_data1 = [{"movie": sample_movies[0], "sort_method": "votes"}]
        filepath = export_service.export_movies_to_csv(
            movies_data=movies_data1, filename="test_append.csv", append=False
        )

        # Append
        movies_data2 = [{"movie": sample_movies[1], "sort_method": "name"}]
        export_service.export_movies_to_csv(
            movies_data=movies_data2, filename="test_append.csv", append=True
        )

        # Verify both entries exist
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["sort_method"] == "votes"
        assert rows[1]["sort_method"] == "name"

    def test_export_similar_movies_to_csv(self, export_service, sample_movies):
        """Test exporting similar movies to CSV."""
        similar_movies_data = [
            {
                "original_movie": sample_movies[0],
                "similar_movie": sample_movies[1],
                "similarity_score": 0.85,
                "similarity_reason": "Similar genres and themes",
                "similarity_metrics": {
                    "genre_similarity": 0.8,
                    "keyword_similarity": 0.6,
                    "content_similarity": 0.7,
                    "rating_similarity": 0.9,
                    "year_similarity": 0.5,
                    "shared_genres": ["Action", "Science Fiction"],
                    "shared_keywords": ["ai"],
                },
            }
        ]

        filepath = export_service.export_similar_movies_to_csv(
            similar_movies_data=similar_movies_data, filename="test_similar.csv"
        )

        assert Path(filepath).exists()

        # Read and verify CSV
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["original_movie_id"] == "1"
        assert rows[0]["similar_movie_id"] == "2"
        assert rows[0]["similarity_score"] == "0.85"
        assert rows[0]["similarity_reason"] == "Similar genres and themes"
        assert "Action" in rows[0]["shared_genres"]

    def test_export_movies_to_csv_empty_data(self, export_service):
        """Test exporting empty movies data raises error."""
        with pytest.raises(ValueError, match="Cannot export empty movies data"):
            export_service.export_movies_to_csv(movies_data=[], filename="test.csv")

    def test_export_similar_movies_to_csv_empty_data(self, export_service):
        """Test exporting empty similar movies data raises error."""
        with pytest.raises(ValueError, match="Cannot export empty similar movies data"):
            export_service.export_similar_movies_to_csv(
                similar_movies_data=[], filename="test.csv"
            )

