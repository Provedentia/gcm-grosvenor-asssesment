"""
Export service for exporting movie data to CSV files.
This service only handles CSV conversion and file writing.
All data processing and sorting should be done in other services.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import csv

from src.models.Movies import Movie
from src.utils.logger import get_logger


class ExportService:
    """
    Service for exporting movie data to CSV files.
    Only handles CSV conversion - no data processing or sorting.
    """

    def __init__(self, output_dir: str = "data"):
        """
        Initialize the export service.

        Args:
            output_dir: Directory to save CSV files (default: "data")
        """
        self.logger = get_logger("export_service")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Export service initialized with output directory: {self.output_dir}")

    def _movie_to_csv_row(self, movie: Movie, sort_method: Optional[str] = None) -> Dict[str, str]:
        """
        Convert a Movie model to a CSV row dictionary.

        Args:
            movie: Movie model instance
            sort_method: Optional sort method identifier

        Returns:
            Dictionary representing a CSV row
        """
        return {
            "sort_method": sort_method or "",
            "id": str(movie.id),
            "title": movie.title,
            "release_date": movie.release_date or "",
            "release_year": str(movie.release_year) if movie.release_year else "",
            "vote_count": str(movie.vote_count),
            "vote_average": str(movie.vote_average),
            "popularity": str(movie.popularity),
            "overview": (movie.overview or "")[:500] if movie.overview else "",
            "poster_path": movie.poster_path or "",
            "backdrop_path": movie.backdrop_path or "",
            "genres": ", ".join(movie.genre_names),
            "keywords": ", ".join(movie.keyword_names[:10]),
            "runtime": str(movie.runtime) if movie.runtime else "",
            "tagline": movie.tagline or "",
            "imdb_id": movie.imdb_id or "",
        }

    def _get_movie_csv_fieldnames(self) -> List[str]:
        """
        Get CSV field names for movie export.

        Returns:
            List of field names for CSV header
        """
        return [
            "sort_method",
            "id",
            "title",
            "release_date",
            "release_year",
            "vote_count",
            "vote_average",
            "popularity",
            "overview",
            "poster_path",
            "backdrop_path",
            "genres",
            "keywords",
            "runtime",
            "tagline",
            "imdb_id",
        ]

    def export_movies_to_csv(
        self,
        movies_data: List[Dict[str, Any]],
        filename: str = "top_movies.csv",
        append: bool = False,
    ) -> str:
        """
        Export movies to CSV file.
        The movies_data should contain pre-sorted movies with sort_method information.

        Args:
            movies_data: List of dictionaries containing:
                - "movie": Movie model instance
                - "sort_method": Sort method identifier (e.g., "votes", "name", "name_no_articles")
            filename: Output CSV filename
            append: If True, append to existing file; otherwise overwrite

        Returns:
            Path to the exported CSV file

        Raises:
            ValueError: If movies_data is empty or invalid
        """
        if not movies_data:
            raise ValueError("Cannot export empty movies data")

        filepath = self.output_dir / filename
        fieldnames = self._get_movie_csv_fieldnames()

        # Determine file mode and whether to write header
        mode = "a" if append else "w"
        file_exists = filepath.exists()
        write_header = not append or not file_exists

        self.logger.info(f"Exporting {len(movies_data)} movie entries to {filepath}")

        with open(filepath, mode, newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")

            if write_header:
                writer.writeheader()

            for entry in movies_data:
                if not isinstance(entry, dict):
                    self.logger.warning(f"Invalid entry in movies_data: expected dict, got {type(entry)}. Skipping.")
                    continue

                movie: Any = entry.get("movie")
                sort_method: Optional[str] = entry.get("sort_method")

                if not isinstance(movie, Movie):
                    self.logger.warning(f"Invalid movie in entry: expected Movie, got {type(movie)}. Skipping.")
                    continue

                row = self._movie_to_csv_row(movie, sort_method=sort_method)
                writer.writerow(row)

        self.logger.info(f"Successfully exported movies to {filepath}")
        return str(filepath)

    def export_similar_movies_to_csv(
        self,
        similar_movies_data: List[Dict[str, Any]],
        filename: str = "similar_movies.csv",
    ) -> str:
        """
        Export similar movies data to CSV file.

        Args:
            similar_movies_data: List of dictionaries containing:
                - "original_movie": Movie model instance
                - "similar_movie": Movie model instance
                - "similarity_score": Optional similarity score (float or str)
                - "similarity_reason": Optional reason for similarity (str)
                - Any other similarity metrics
            filename: Output CSV filename

        Returns:
            Path to the exported CSV file

        Raises:
            ValueError: If similar_movies_data is empty
        """
        if not similar_movies_data:
            raise ValueError("Cannot export empty similar movies data")

        filepath = self.output_dir / filename

        fieldnames = [
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
            "genres",
            "keywords",
            "vote_count",
            "vote_average",
            "popularity",
            "release_date",
            "release_year",
            "overview",
            "runtime",
            "imdb_id",
        ]

        self.logger.info(f"Exporting {len(similar_movies_data)} similar movie entries to {filepath}")

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for entry in similar_movies_data:
                if not isinstance(entry, dict):
                    self.logger.warning(f"Invalid entry in similar_movies_data: expected dict, got {type(entry)}. Skipping.")
                    continue

                original_movie: Any = entry.get("original_movie")
                similar_movie: Any = entry.get("similar_movie")
                similarity_score: Any = entry.get("similarity_score")
                similarity_reason: Optional[str] = entry.get("similarity_reason")
                similarity_metrics: Any = entry.get("similarity_metrics", {})

                if not isinstance(original_movie, Movie):
                    self.logger.warning(f"Invalid original_movie: expected Movie, got {type(original_movie)}. Skipping.")
                    continue

                if not isinstance(similar_movie, Movie):
                    self.logger.warning(f"Invalid similar_movie: expected Movie, got {type(similar_movie)}. Skipping.")
                    continue

                # Convert similarity_score to string
                similarity_score_str = ""
                if similarity_score is not None:
                    similarity_score_str = str(similarity_score)

                # Extract detailed metrics
                metrics = similarity_metrics if isinstance(similarity_metrics, dict) else {}
                genre_sim = metrics.get("genre_similarity", "")
                keyword_sim = metrics.get("keyword_similarity", "")
                content_sim = metrics.get("content_similarity", "")
                rating_sim = metrics.get("rating_similarity", "")
                year_sim = metrics.get("year_similarity", "")
                shared_genres = metrics.get("shared_genres", [])
                shared_keywords = metrics.get("shared_keywords", [])

                row = {
                    "original_movie_id": str(original_movie.id),
                    "original_movie_title": original_movie.title,
                    "similar_movie_id": str(similar_movie.id),
                    "similar_movie_title": similar_movie.title,
                    "similarity_score": similarity_score_str,
                    "similarity_reason": similarity_reason or "",
                    "genre_similarity": str(genre_sim) if genre_sim else "",
                    "keyword_similarity": str(keyword_sim) if keyword_sim else "",
                    "content_similarity": str(content_sim) if content_sim else "",
                    "rating_similarity": str(rating_sim) if rating_sim else "",
                    "year_similarity": str(year_sim) if year_sim else "",
                    "shared_genres": ", ".join(shared_genres) if isinstance(shared_genres, list) else "",
                    "shared_keywords": ", ".join(shared_keywords[:10]) if isinstance(shared_keywords, list) else "",
                    "genres": ", ".join(similar_movie.genre_names),
                    "keywords": ", ".join(similar_movie.keyword_names[:10]),
                    "vote_count": str(similar_movie.vote_count),
                    "vote_average": str(similar_movie.vote_average),
                    "popularity": str(similar_movie.popularity),
                    "release_date": similar_movie.release_date or "",
                    "release_year": str(similar_movie.release_year) if similar_movie.release_year else "",
                    "overview": (similar_movie.overview or "")[:500] if similar_movie.overview else "",
                    "runtime": str(similar_movie.runtime) if similar_movie.runtime else "",
                    "imdb_id": similar_movie.imdb_id or "",
                }
                writer.writerow(row)

        self.logger.info(f"Successfully exported similar movies to {filepath}")
        return str(filepath)
