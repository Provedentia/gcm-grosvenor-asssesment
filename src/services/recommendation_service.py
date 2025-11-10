"""
Recommendation service for finding similar movies.
Provides basic similarity matching that can be extended with more complex algorithms.
"""

import time
from typing import Any, Dict, List, Optional, Set, Tuple

from src.api.TMDB import TMDBClient
from src.models.Movies import Movie, movie_from_tmdb_response, validate_movie_list
from src.utils.config import get_config
from src.utils.logger import get_logger


class RecommendationService:
    """
    Service for finding similar movies based on various criteria.
    Uses a basic similarity algorithm that can be extended.
    """

    def __init__(self, tmdb_client: Optional[TMDBClient] = None):
        """
        Initialize the recommendation service.

        Args:
            tmdb_client: TMDB API client instance (creates new one if not provided)
        """
        self.config = get_config()
        self.logger = get_logger("recommendation_service")
        self.tmdb_client = tmdb_client or TMDBClient()
        self.logger.info("Recommendation service initialized")

    def _calculate_genre_similarity(
        self, movie1_genres: List[str], movie2_genres: List[str]
    ) -> float:
        """
        Calculate genre similarity between two movies using Jaccard similarity.

        Args:
            movie1_genres: List of genre names for movie 1
            movie2_genres: List of genre names for movie 2

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not movie1_genres or not movie2_genres:
            return 0.0

        set1 = set(movie1_genres)
        set2 = set(movie2_genres)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        return intersection / union

    def _calculate_keyword_similarity(
        self, movie1_keywords: List[str], movie2_keywords: List[str]
    ) -> float:
        """
        Calculate keyword similarity between two movies using Jaccard similarity.

        Args:
            movie1_keywords: List of keyword names for movie 1
            movie2_keywords: List of keyword names for movie 2

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not movie1_keywords or not movie2_keywords:
            return 0.0

        set1 = set(movie1_keywords)
        set2 = set(movie2_keywords)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        return intersection / union

    def _calculate_rating_similarity(
        self, rating1: float, rating2: float, max_rating: float = 10.0
    ) -> float:
        """
        Calculate rating similarity between two movies.

        Args:
            rating1: Rating of movie 1
            rating2: Rating of movie 2
            max_rating: Maximum possible rating (default: 10.0)

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if max_rating == 0:
            return 0.0

        diff = abs(rating1 - rating2)
        similarity = 1.0 - (diff / max_rating)
        return max(0.0, min(1.0, similarity))

    def _calculate_year_similarity(
        self, year1: Optional[int], year2: Optional[int], max_diff: int = 20
    ) -> float:
        """
        Calculate year similarity between two movies.

        Args:
            year1: Release year of movie 1
            year2: Release year of movie 2
            max_diff: Maximum year difference for full similarity (default: 20)

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if year1 is None or year2 is None:
            return 0.5  # Neutral score if year is unknown

        diff = abs(year1 - year2)
        if diff >= max_diff:
            return 0.0

        similarity = 1.0 - (diff / max_diff)
        return max(0.0, min(1.0, similarity))

    def calculate_similarity_score(
        self, original_movie: Movie, candidate_movie: Movie
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate overall similarity score between two movies.

        Args:
            original_movie: Original movie to compare against
            candidate_movie: Candidate movie to compare

        Returns:
            Tuple of (similarity_score, similarity_metrics)
        """
        # Get weights from config
        weights = self.config.get("recommendation.weights", {})
        genre_weight = weights.get("genre_similarity", 0.4)
        rating_weight = weights.get("rating", 0.3)
        popularity_weight = weights.get("popularity", 0.2)
        year_weight = weights.get("release_year", 0.1)

        # Calculate individual similarity scores
        genre_sim = self._calculate_genre_similarity(
            original_movie.genre_names, candidate_movie.genre_names
        )

        keyword_sim = self._calculate_keyword_similarity(
            original_movie.keyword_names, candidate_movie.keyword_names
        )

        # Combine genre and keyword similarity (average)
        content_sim = (genre_sim + keyword_sim) / 2.0 if (genre_sim + keyword_sim) > 0 else 0.0

        rating_sim = self._calculate_rating_similarity(
            original_movie.vote_average, candidate_movie.vote_average
        )

        year_sim = self._calculate_year_similarity(
            original_movie.release_year, candidate_movie.release_year
        )

        # Normalize popularity (TMDB popularity can vary widely)
        # Use a simple comparison: higher popularity = slightly higher score
        popularity_factor = min(candidate_movie.popularity / 100.0, 1.0) if candidate_movie.popularity > 0 else 0.0

        # Calculate weighted similarity score
        similarity_score = (
            content_sim * genre_weight
            + rating_sim * rating_weight
            + popularity_factor * popularity_weight
            + year_sim * year_weight
        )

        # Create similarity metrics dictionary
        metrics = {
            "genre_similarity": round(genre_sim, 4),
            "keyword_similarity": round(keyword_sim, 4),
            "content_similarity": round(content_sim, 4),
            "rating_similarity": round(rating_sim, 4),
            "year_similarity": round(year_sim, 4),
            "popularity_factor": round(popularity_factor, 4),
            "shared_genres": list(set(original_movie.genre_names).intersection(set(candidate_movie.genre_names))),
            "shared_keywords": list(set(original_movie.keyword_names).intersection(set(candidate_movie.keyword_names))),
        }

        # Generate similarity reason
        reasons = []
        if genre_sim > 0.5:
            reasons.append(f"Similar genres ({', '.join(metrics['shared_genres'][:3])})")
        if keyword_sim > 0.3:
            reasons.append(f"Similar themes ({len(metrics['shared_keywords'])} shared keywords)")
        if rating_sim > 0.7:
            reasons.append("Similar ratings")
        if year_sim > 0.7:
            reasons.append("Similar release period")

        metrics["similarity_reason"] = "; ".join(reasons) if reasons else "General similarity"

        return round(similarity_score, 4), metrics

    def get_similar_movies_from_tmdb(
        self, movie_id: int, limit: int = 10, min_vote_count: Optional[int] = None
    ) -> List[Movie]:
        """
        Get similar movies from TMDB API.

        Args:
            movie_id: TMDB movie ID
            limit: Maximum number of similar movies to retrieve
            min_vote_count: Minimum vote count for similar movies

        Returns:
            List of Movie models
        """
        if min_vote_count is None:
            min_vote_count = self.config.get("recommendation.min_vote_count", 100)

        self.logger.debug(f"Getting similar movies from TMDB for movie ID {movie_id}")

        # Get similar movies from TMDB
        data = self.tmdb_client.get_similar_movies(movie_id, page=1)

        if not data or "results" not in data:
            return []

        similar_movies_data = data.get("results", [])

        # Filter by minimum vote count
        filtered_movies = [
            movie for movie in similar_movies_data
            if movie.get("vote_count", 0) >= min_vote_count
        ]

        # Convert to Movie models
        movies = validate_movie_list(filtered_movies[:limit * 2])  # Get more for filtering

        # Enrich movies with details
        enriched_movies = self._enrich_movies_with_details(movies[:limit * 2])

        return enriched_movies[:limit]

    def _enrich_movies_with_details(self, movies: List[Movie]) -> List[Movie]:
        """
        Enrich movies with detailed information.

        Args:
            movies: List of Movie models

        Returns:
            List of enriched Movie models
        """
        enriched_movies: List[Movie] = []

        for movie in movies:
            try:
                # Get detailed movie information
                details_data = self.tmdb_client.get_movie_details(movie.id)
                if not details_data:
                    enriched_movies.append(movie)
                    continue

                # Get keywords
                keywords_data = self.tmdb_client.get_movie_keywords(movie.id)
                if keywords_data and "keywords" in keywords_data:
                    details_data["keywords"] = keywords_data

                # Create enriched movie
                enriched_movie = movie_from_tmdb_response(details_data)
                enriched_movies.append(enriched_movie)

                # Small delay to avoid rate limiting
                time.sleep(0.1)

            except Exception as e:
                self.logger.warning(f"Failed to enrich movie {movie.id}: {e}")
                enriched_movies.append(movie)

        return enriched_movies

    def find_similar_movies(
        self,
        original_movie: Movie,
        limit: int = 3,
        min_vote_count: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find similar movies for a given movie.

        Args:
            original_movie: Original movie to find similar movies for
            limit: Number of similar movies to return
            min_vote_count: Minimum vote count for similar movies

        Returns:
            List of dictionaries containing:
                - "similar_movie": Movie model
                - "similarity_score": float
                - "similarity_reason": str
                - "similarity_metrics": dict with detailed metrics
        """
        self.logger.info(f"Finding {limit} similar movies for: {original_movie.title}")

        # Get candidate movies from TMDB
        candidate_movies = self.get_similar_movies_from_tmdb(
            movie_id=original_movie.id,
            limit=limit * 3,  # Get more candidates to filter
            min_vote_count=min_vote_count,
        )

        if not candidate_movies:
            self.logger.warning(f"No similar movies found for {original_movie.title}")
            return []

        # Calculate similarity scores for all candidates
        scored_movies: List[Tuple[Movie, float, Dict[str, Any]]] = []

        for candidate in candidate_movies:
            # Skip if it's the same movie
            if candidate.id == original_movie.id:
                continue

            score, metrics = self.calculate_similarity_score(original_movie, candidate)
            scored_movies.append((candidate, score, metrics))

        # Sort by similarity score (highest first)
        scored_movies.sort(key=lambda x: x[1], reverse=True)

        # Get top N similar movies
        top_similar = scored_movies[:limit]

        # Format results
        results: List[Dict[str, Any]] = []
        for movie, score, metrics in top_similar:
            results.append({
                "similar_movie": movie,
                "similarity_score": score,
                "similarity_reason": metrics.get("similarity_reason", "General similarity"),
                "similarity_metrics": metrics,
            })

        self.logger.info(
            f"Found {len(results)} similar movies for {original_movie.title} "
            f"(scores: {[r['similarity_score'] for r in results]})"
        )

        return results

    def get_similar_movies_for_multiple(
        self,
        movies: List[Movie],
        limit: int = 3,
        min_vote_count: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get similar movies for multiple movies.

        Args:
            movies: List of Movie models
            limit: Number of similar movies per movie
            min_vote_count: Minimum vote count for similar movies

        Returns:
            List of dictionaries containing:
                - "original_movie": Movie model
                - "similar_movies": List of similar movie dictionaries
        """
        results: List[Dict[str, Any]] = []

        for movie in movies:
            try:
                similar_movies = self.find_similar_movies(
                    original_movie=movie,
                    limit=limit,
                    min_vote_count=min_vote_count,
                )

                if similar_movies:
                    results.append({
                        "original_movie": movie,
                        "similar_movies": similar_movies,
                    })

                # Delay to avoid rate limiting
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Failed to find similar movies for {movie.title}: {e}")
                continue

        return results

    def prepare_similar_movies_for_export(
        self, similar_movies_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prepare similar movies data for CSV export.

        Args:
            similar_movies_data: List of dictionaries from get_similar_movies_for_multiple

        Returns:
            List of dictionaries formatted for export service
        """
        export_data: List[Dict[str, Any]] = []

        for item in similar_movies_data:
            original_movie = item.get("original_movie")
            similar_movies = item.get("similar_movies", [])

            if not original_movie or not similar_movies:
                continue

            for similar_item in similar_movies:
                similar_movie = similar_item.get("similar_movie")
                similarity_score = similar_item.get("similarity_score")
                similarity_reason = similar_item.get("similarity_reason", "")
                similarity_metrics = similar_item.get("similarity_metrics", {})

                export_data.append({
                    "original_movie": original_movie,
                    "similar_movie": similar_movie,
                    "similarity_score": similarity_score,
                    "similarity_reason": similarity_reason,
                    "similarity_metrics": similarity_metrics,
                })

        return export_data

