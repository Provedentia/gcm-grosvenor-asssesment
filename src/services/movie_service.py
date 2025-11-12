"""
Movie service for retrieving, processing, and managing movie data.
Handles business logic for movie operations including sorting and filtering.
"""

from typing import Any, Dict, List, Optional, Tuple

from src.api.TMDB import TMDBClient
from src.models.Movies import Movie, movie_from_tmdb_response, validate_movie_list
from src.services.export_service import ExportService
from src.utils.config import get_config
from src.utils.logger import get_logger


class MovieService:
    """
    Service for movie operations including retrieval, sorting, and export.
    Handles business logic for movie data processing.
    """

    def __init__(self, tmdb_client: Optional[TMDBClient] = None, export_service: Optional[ExportService] = None):
        """
        Initialize the movie service.

        Args:
            tmdb_client: TMDB API client instance (creates new one if not provided)
            export_service: Export service instance (creates new one if not provided)
        """
        self.config = get_config()
        self.logger = get_logger("movie_service")
        self.tmdb_client = tmdb_client or TMDBClient()
        self.export_service = export_service or ExportService()
        self.logger.info("Movie service initialized")

    def _enrich_movies_with_details(self, movies: List[Movie]) -> List[Movie]:
        """
        Enrich movies with detailed information from TMDB API.

        Args:
            movies: List of Movie models with basic information

        Returns:
            List of Movie models with enriched details (genres, keywords, director, collection, etc.)
        """
        enriched_movies: List[Movie] = []

        for movie in movies:
            try:
                # Get detailed movie information (includes collection)
                details_data = self.tmdb_client.get_movie_details(movie.id)
                if not details_data:
                    # If details not available, use the basic movie data
                    enriched_movies.append(movie)
                    continue

                # Get keywords
                keywords_data = self.tmdb_client.get_movie_keywords(movie.id)
                if keywords_data and "keywords" in keywords_data:
                    details_data["keywords"] = keywords_data

                # Get credits to extract director
                credits_data = self.tmdb_client.get_movie_credits(movie.id)
                if credits_data and "crew" in credits_data:
                    # Find director from crew
                    crew = credits_data.get("crew", [])
                    director = None
                    for person in crew:
                        if person.get("job") == "Director":
                            director = person.get("name")
                            break
                    if director:
                        details_data["director"] = director

                # Create enriched movie from detailed data
                enriched_movie = movie_from_tmdb_response(details_data)
                enriched_movies.append(enriched_movie)

            except Exception as e:
                # If enrichment fails, use the original movie data
                self.logger.warning(f"Failed to enrich movie {movie.id}: {e}. Using basic data.")
                enriched_movies.append(movie)

        return enriched_movies

    def get_top_movies_by_year(
        self,
        year: int,
        top_n: int = 10,
        min_vote_count: Optional[int] = None,
        min_vote_average: Optional[float] = None,
    ) -> List[Movie]:
        """
        Get top N movies from a specific year sorted by vote count.

        Args:
            year: Release year
            top_n: Number of top movies to return (default: 10)
            min_vote_count: Minimum number of votes (from config if not provided)
            min_vote_average: Minimum vote average (from config if not provided)

        Returns:
            List of top N Movie models sorted by vote count

        Raises:
            ValueError: If no movies found or invalid parameters
        """
        if min_vote_count is None:
            min_vote_count = self.config.get("recommendation.min_vote_count", 100)
        if min_vote_average is None:
            min_vote_average = self.config.get("recommendation.min_vote_average", 6.0)

        self.logger.info(
            f"Retrieving top {top_n} movies from year {year} "
            f"(min_votes: {min_vote_count}, min_rating: {min_vote_average})"
        )

        all_movies: List[Movie] = []
        page = 1
        max_pages = self.config.get("data.max_pages", 5)

        # Fetch movies from multiple pages until we have enough
        while page <= max_pages and len(all_movies) < top_n * 2:  # Get extra to ensure we have enough after filtering
            data = self.tmdb_client.get_movies_by_year(
                year=year,
                min_vote_count=min_vote_count,
                min_vote_average=min_vote_average,
                sort_by="vote_count.desc",
                page=page,
            )

            if not data or "results" not in data:
                break

            movies_data = data.get("results", [])
            if not movies_data:
                break

            # Convert to Movie models (basic info from discover endpoint)
            validated_movies = validate_movie_list(movies_data)
            all_movies.extend(validated_movies)

            self.logger.debug(f"Retrieved {len(validated_movies)} movies from page {page}")

            # Check if there are more pages
            total_pages = data.get("total_pages", 0)
            if page >= total_pages:
                break

            page += 1

        if not all_movies:
            raise ValueError(f"No movies found for year {year} with the specified criteria")

        # Sort by vote count and get top N
        sorted_movies = sorted(all_movies, key=lambda m: m.vote_count, reverse=True)
        top_movies = sorted_movies[:top_n]

        # Enrich movies with detailed information (genres, keywords, etc.)
        enriched_movies = self._enrich_movies_with_details(top_movies)

        self.logger.info(f"Selected top {len(enriched_movies)} movies from year {year}")
        return enriched_movies

    def sort_movies_by_votes(self, movies: List[Movie]) -> List[Movie]:
        """
        Sort movies by vote count (highest first).

        Args:
            movies: List of Movie models

        Returns:
            Sorted list of Movie models
        """
        return sorted(movies, key=lambda m: m.vote_count, reverse=True)

    def sort_movies_by_name(self, movies: List[Movie], ignore_articles: bool = False) -> List[Movie]:
        """
        Sort movies by name (alphabetically).

        Args:
            movies: List of Movie models
            ignore_articles: If True, ignore articles and common words when sorting.
                Removes: the, a, an, in, on, at, for, with, by, from, to, of, and, or, but

        Returns:
            Sorted list of Movie models
        """
        return sorted(
            movies,
            key=lambda m: m.normalize_title_for_sorting(ignore_articles=ignore_articles).lower(),
        )

    def prepare_movies_for_export(
        self, movies: List[Movie], sort_method: str
    ) -> List[Dict[str, Any]]:
        """
        Prepare movies for CSV export with a single sort method.

        Args:
            movies: List of Movie models to export
            sort_method: Sort method to apply. Options: "votes", "name", "name_no_articles"

        Returns:
            List of dictionaries containing movie and sort_method for export
        """
        if sort_method == "votes":
            sorted_movies = self.sort_movies_by_votes(movies)
            sort_label = "votes"
        elif sort_method == "name":
            sorted_movies = self.sort_movies_by_name(movies, ignore_articles=False)
            sort_label = "name"
        elif sort_method == "name_no_articles":
            sorted_movies = self.sort_movies_by_name(movies, ignore_articles=True)
            sort_label = "name_no_articles"
        else:
            raise ValueError(f"Unknown sort method: {sort_method}")

        # Create export data for this sort method
        export_data: List[Dict[str, Any]] = []
        for movie in sorted_movies:
            export_data.append({"movie": movie, "sort_method": sort_label})

        return export_data

    def get_and_export_top_movies(
        self,
        year: int,
        top_n: int = 10,
        filename: str = "top_movies.csv",
        min_vote_count: Optional[int] = None,
        min_vote_average: Optional[float] = None,
    ) -> Tuple[List[Movie], str]:
        """
        Get top movies from a year and export them to CSV with all sorting methods.

        This method:
        1. Retrieves top N movies from the specified year
        2. Sorts them by votes (highest first) and saves to CSV
        3. Sorts them by name (with articles) and appends to the same CSV
        4. Sorts them by name (without articles) and appends to the same CSV

        Args:
            year: Release year
            top_n: Number of top movies to retrieve (default: 10)
            filename: Output CSV filename
            min_vote_count: Minimum number of votes
            min_vote_average: Minimum vote average

        Returns:
            Tuple of (list of Movie models, path to exported CSV file)

        Raises:
            ValueError: If no movies found or export fails
        """
        self.logger.info(f"Processing top {top_n} movies from year {year} for export")

        # Get top movies
        top_movies = self.get_top_movies_by_year(
            year=year,
            top_n=top_n,
            min_vote_count=min_vote_count,
            min_vote_average=min_vote_average,
        )

        # Export with votes sort (first write, overwrites if exists)
        votes_data = self.prepare_movies_for_export(top_movies, sort_method="votes")
        filepath = self.export_service.export_movies_to_csv(
            movies_data=votes_data, filename=filename, append=False
        )
        self.logger.debug(f"Exported {len(votes_data)} movies sorted by votes")

        # Export with name sort (with articles) - append to file
        name_data = self.prepare_movies_for_export(top_movies, sort_method="name")
        self.export_service.export_movies_to_csv(
            movies_data=name_data, filename=filename, append=True
        )
        self.logger.debug(f"Appended {len(name_data)} movies sorted by name (with articles)")

        # Export with name sort (without articles) - append to file
        name_no_articles_data = self.prepare_movies_for_export(
            top_movies, sort_method="name_no_articles"
        )
        self.export_service.export_movies_to_csv(
            movies_data=name_no_articles_data, filename=filename, append=True
        )
        self.logger.debug(
            f"Appended {len(name_no_articles_data)} movies sorted by name (without articles)"
        )

        self.logger.info(
            f"Successfully exported {len(top_movies)} movies with 3 sort methods to {filepath}"
        )

        return top_movies, filepath

