"""
Movie Recommendation Engine with two-stage approach:
Stage 1: Smart candidate selection (to avoid comparing against millions of movies)
Stage 2: Multi-factor similarity calculation using ML techniques

This module orchestrates the complete recommendation workflow by:
1. Selecting candidate movies using various strategies (TMDB API, same year, same genre, hybrid)
2. Calculating similarity scores for candidates using multi-factor weighted scoring
3. Returning top N similar movies for each target movie
"""

import time
from typing import Any, Dict, List, Optional, Tuple

from src.api.TMDB import TMDBClient
from src.models.Movies import Movie, movie_from_tmdb_response, remove_duplicate_movies, validate_movie_list
from src.utils.config import get_config
from src.utils.logger import get_logger


class MovieRecommendationEngine:
    """
    Movie recommendation engine that finds similar movies using a two-stage approach.

    Stage 1: Smart candidate selection - Reduces the search space from millions to hundreds
    Stage 2: Multi-factor similarity calculation - Uses weighted scoring to rank candidates

    This class orchestrates candidate selection strategies and calculates similarity
    scores using multi-factor weighted scoring.
    """

    def __init__(
        self,
        tmdb_client: Optional[TMDBClient] = None,
    ):
        """
        Initialize the movie recommendation engine.

        Args:
            tmdb_client: TMDB API client instance (creates new one if not provided)
        """
        self.config = get_config()
        self.logger = get_logger("movie_recommendation_engine")
        self.tmdb_client = tmdb_client or TMDBClient()

        # Configuration
        self.min_vote_count = self.config.get("recommendation.min_vote_count", 100)
        self.min_vote_average = self.config.get("recommendation.min_vote_average", 6.0)
        self.api_delay = self.config.get("recommendation.api_delay", 0.1)

        # Similarity calculation weights from config (focus on actual similarity factors)
        weights = self.config.get("recommendation.weights", {})
        self.genre_weight = weights.get("genre_similarity", 0.3)
        self.keyword_weight = weights.get("keyword_similarity", 0.1)
        self.director_weight = weights.get("director_similarity", 0.1)
        self.collection_weight = weights.get("collection_similarity", 0.3)
        self.production_company_weight = weights.get("production_company_similarity", 0.2)

        # Track API calls for performance monitoring
        self.api_calls_made = 0

        self.logger.info("Movie recommendation engine initialized")

    def find_similar_movies_for_each(
        self,
        top_movies: List[Movie],
        similar_per_movie: int = 3,
        strategy: str = "hybrid",
    ) -> List[Dict[str, Any]]:
        """
        Find similar movies for each movie in the list.

        This is the main method that orchestrates the complete workflow:
        1. For each target movie, get candidate pool using selected strategy
        2. Calculate similarity scores for all candidates
        3. Return top N similar movies for each target

        Args:
            top_movies: List of target movies to find similar movies for
            similar_per_movie: Number of similar movies to return per target movie
            strategy: Candidate selection strategy. Options:
                - "tmdb_api": Use TMDB's similar/recommendations endpoints
                - "same_year": Get movies from same release year
                - "same_genre": Get movies with overlapping genres
                - "hybrid": Combine multiple approaches (RECOMMENDED)

        Returns:
            List of dictionaries containing:
                - "original_movie": Movie model
                - "similar_movies": List of similar movie dictionaries with:
                    - "similar_movie": Movie model
                    - "similarity_score": float
                    - "similarity_reason": str
                    - "similarity_metrics": dict

        Raises:
            ValueError: If strategy is invalid
        """
        if strategy not in ["tmdb_api", "same_year", "same_genre", "hybrid"]:
            raise ValueError(
                f"Invalid strategy: {strategy}. "
                "Must be one of: tmdb_api, same_year, same_genre, hybrid"
            )

        self.logger.info(
            f"Finding {similar_per_movie} similar movies for {len(top_movies)} movies "
            f"using strategy: {strategy}"
        )

        self.api_calls_made = 0
        results: List[Dict[str, Any]] = []

        for i, target_movie in enumerate(top_movies, 1):
            try:
                self.logger.info(
                    f"Processing movie {i}/{len(top_movies)}: {target_movie.title} (ID: {target_movie.id})"
                )

                # Stage 1: Get candidate pool
                candidates = self._get_candidate_pool(target_movie, strategy)
                self.logger.debug(
                    f"Found {len(candidates)} candidates for {target_movie.title}"
                )

                if not candidates:
                    self.logger.warning(
                        f"No candidates found for {target_movie.title}, skipping"
                    )
                    continue

                # Stage 2: Calculate similarity scores and get top N
                similar_movies = self._calculate_similarity_and_rank(
                    target_movie=target_movie,
                    candidates=candidates,
                    top_n=similar_per_movie,
                )

                if similar_movies:
                    results.append({
                        "original_movie": target_movie,
                        "similar_movies": similar_movies,
                    })
                    self.logger.info(
                        f"Found {len(similar_movies)} similar movies for {target_movie.title}"
                    )
                else:
                    self.logger.warning(
                        f"No similar movies found for {target_movie.title} after ranking"
                    )

                # Delay to avoid rate limiting
                if i < len(top_movies):
                    time.sleep(self.api_delay)

            except Exception as e:
                self.logger.error(
                    f"Error processing {target_movie.title}: {e}", exc_info=True
                )
                continue

        self.logger.info(
            f"Completed processing. Total API calls made: {self.api_calls_made}. "
            f"Found similar movies for {len(results)}/{len(top_movies)} movies"
        )

        return results

    def _get_candidate_pool(
        self, target_movie: Movie, strategy: str
    ) -> List[Movie]:
        """
        Get candidate pool based on selected strategy.

        Args:
            target_movie: Target movie to find candidates for
            strategy: Candidate selection strategy

        Returns:
            List of candidate Movie models
        """
        if strategy == "tmdb_api":
            return self._get_candidates_from_tmdb_api(target_movie)
        elif strategy == "same_year":
            return self._get_candidates_same_year(target_movie)
        elif strategy == "same_genre":
            return self._get_candidates_same_genre(target_movie)
        elif strategy == "hybrid":
            return self._get_candidates_hybrid(target_movie)
        else:
            raise ValueError(f"Invalid strategy: {strategy}")

    def _get_candidates_from_tmdb_api(self, target_movie: Movie) -> List[Movie]:
        """
        Get candidates using TMDB's similar and recommendations endpoints.

        Strategy:
        - Use TMDB's /movie/{id}/similar endpoint
        - Use TMDB's /movie/{id}/recommendations endpoint
        - Combine both, remove duplicates
        - Returns ~20-40 candidates

        Pros: Fast, simple, leverages TMDB's algorithms
        Cons: Less control, black box algorithm

        Args:
            target_movie: Target movie to find candidates for

        Returns:
            List of candidate Movie models
        """
        self.logger.debug(
            f"Getting candidates from TMDB API for {target_movie.title}"
        )
        candidates: List[Movie] = []

        # Get similar movies
        try:
            similar_data = self.tmdb_client.get_similar_movies(target_movie.id, page=1)
            self.api_calls_made += 1

            if similar_data and "results" in similar_data:
                similar_movies_data = similar_data.get("results", [])
                # Filter by minimum vote count
                filtered = [
                    m
                    for m in similar_movies_data
                    if m.get("vote_count", 0) >= self.min_vote_count
                ]
                candidates.extend(filtered)
                self.logger.debug(
                    f"Found {len(filtered)} similar movies from TMDB API"
                )
        except Exception as e:
            self.logger.warning(f"Error getting similar movies: {e}")

        time.sleep(self.api_delay)

        # Get recommendations
        try:
            recommendations_data = self.tmdb_client.get_movie_recommendations(
                target_movie.id, page=1
            )
            self.api_calls_made += 1

            if recommendations_data and "results" in recommendations_data:
                rec_movies_data = recommendations_data.get("results", [])
                # Filter by minimum vote count
                filtered = [
                    m
                    for m in rec_movies_data
                    if m.get("vote_count", 0) >= self.min_vote_count
                ]
                candidates.extend(filtered)
                self.logger.debug(
                    f"Found {len(filtered)} recommended movies from TMDB API"
                )
        except Exception as e:
            self.logger.warning(f"Error getting recommendations: {e}")

        # Convert to Movie models and remove duplicates
        movies = validate_movie_list(candidates)
        unique_movies = remove_duplicate_movies(movies)

        # Exclude target movie
        unique_movies = [m for m in unique_movies if m.id != target_movie.id]

        self.logger.debug(
            f"TMDB API strategy: {len(candidates)} raw candidates -> "
            f"{len(unique_movies)} unique candidates (excluding target)"
        )

        return unique_movies

    def _get_candidates_same_year(self, target_movie: Movie) -> List[Movie]:
        """
        Get candidates from the same release year as target movie.

        Strategy:
        - Get movies from target movie's release year
        - Sort by popularity or vote count
        - Filter by minimum votes
        - Returns ~20-50 candidates

        Pros: Temporal relevance, movies from same era
        Cons: Limited pool, may miss cross-era similarities

        Args:
            target_movie: Target movie to find candidates for

        Returns:
            List of candidate Movie models
        """
        if not target_movie.release_year:
            self.logger.warning(
                f"No release year for {target_movie.title}, cannot use same_year strategy"
            )
            return []

        self.logger.debug(
            f"Getting candidates from year {target_movie.release_year} "
            f"for {target_movie.title}"
        )

        candidates: List[Movie] = []

        try:
            # Get movies from same year, sorted by popularity
            year_data = self.tmdb_client.get_movies_by_year(
                year=target_movie.release_year,
                min_vote_count=self.min_vote_count,
                min_vote_average=self.min_vote_average,
                sort_by="popularity.desc",
                page=1,
            )
            self.api_calls_made += 1

            if year_data and "results" in year_data:
                movies_data = year_data.get("results", [])
                # Get top 50 movies from the year
                candidates.extend(movies_data[:50])
                self.logger.debug(
                    f"Found {len(movies_data)} movies from year {target_movie.release_year}"
                )
        except Exception as e:
            self.logger.warning(f"Error getting movies from same year: {e}")

        # Convert to Movie models
        movies = validate_movie_list(candidates)

        # Exclude target movie
        movies = [m for m in movies if m.id != target_movie.id]

        self.logger.debug(
            f"Same year strategy: {len(candidates)} raw candidates -> "
            f"{len(movies)} candidates (excluding target)"
        )

        return movies

    def _get_candidates_same_genre(self, target_movie: Movie) -> List[Movie]:
        """
        Get candidates with overlapping genres.

        Strategy:
        - For each of target movie's genres (limit to top 2)
        - Get top 25 movies per genre
        - Remove duplicates
        - Returns ~50-100 candidates

        Pros: Thematically similar, genre-based matching
        Cons: More API calls, may be too narrow

        Args:
            target_movie: Target movie to find candidates for

        Returns:
            List of candidate Movie models
        """
        if not target_movie.genres or len(target_movie.genres) == 0:
            self.logger.warning(
                f"No genres for {target_movie.title}, cannot use same_genre strategy"
            )
            return []

        self.logger.debug(
            f"Getting candidates by genre for {target_movie.title} "
            f"(genres: {target_movie.genre_names})"
        )

        candidates: List[Movie] = []

        # Limit to top 2 genres to avoid too many API calls
        genres_to_use = target_movie.genres[:2]

        for genre in genres_to_use:
            try:
                # Get movies for this genre using discover endpoint
                # Optionally filter by year if available
                genre_data = self.tmdb_client.discover_movies(
                    year=target_movie.release_year,  # None if no year, which is fine
                    min_vote_count=self.min_vote_count,
                    min_vote_average=self.min_vote_average,
                    sort_by="popularity.desc",
                    page=1,
                    with_genres=genre.id,
                )
                self.api_calls_made += 1

                if genre_data and "results" in genre_data:
                    movies_data = genre_data.get("results", [])
                    # Get top 25 movies per genre
                    candidates.extend(movies_data[:25])
                    self.logger.debug(
                        f"Found {len(movies_data)} movies for genre {genre.name}"
                    )

                time.sleep(self.api_delay)

            except Exception as e:
                self.logger.warning(
                    f"Error getting movies for genre {genre.name}: {e}"
                )
                continue

        # Convert to Movie models and remove duplicates
        movies = validate_movie_list(candidates)
        unique_movies = remove_duplicate_movies(movies)

        # Exclude target movie
        unique_movies = [m for m in unique_movies if m.id != target_movie.id]

        self.logger.debug(
            f"Same genre strategy: {len(candidates)} raw candidates -> "
            f"{len(unique_movies)} unique candidates (excluding target)"
        )

        return unique_movies

    def _get_candidates_hybrid(self, target_movie: Movie) -> List[Movie]:
        """
        Get candidates using hybrid strategy (RECOMMENDED).

        Strategy:
        - Combine TMDB suggestions (~40 movies from similar + recommendations)
        - Add same year movies (~50 movies)
        - Add nearby years ±2 years (~10 movies each = 40 total)
        - Remove duplicates based on movie ID
        - Returns ~100-200 candidates

        Pros: Best quality, large diverse pool, combines multiple signals
        Cons: More API calls (5-8 per movie), slower

        Args:
            target_movie: Target movie to find candidates for

        Returns:
            List of candidate Movie models
        """
        self.logger.debug(
            f"Getting candidates using hybrid strategy for {target_movie.title}"
        )
        all_candidates: List[Movie] = []

        # 1. Get TMDB API suggestions (similar + recommendations)
        tmdb_candidates = self._get_candidates_from_tmdb_api(target_movie)
        all_candidates.extend(tmdb_candidates)
        self.logger.debug(f"TMDB API: {len(tmdb_candidates)} candidates")

        # 2. Get same year movies
        if target_movie.release_year:
            same_year_candidates = self._get_candidates_same_year(target_movie)
            all_candidates.extend(same_year_candidates)
            self.logger.debug(
                f"Same year ({target_movie.release_year}): {len(same_year_candidates)} candidates"
            )

            # 3. Get nearby years (±2 years)
            for year_offset in [-2, -1, 1, 2]:
                nearby_year = target_movie.release_year + year_offset
                if nearby_year > 1900 and nearby_year <= 2025:  # Reasonable year range
                    try:
                        year_data = self.tmdb_client.get_movies_by_year(
                            year=nearby_year,
                            min_vote_count=self.min_vote_count,
                            min_vote_average=self.min_vote_average,
                            sort_by="popularity.desc",
                            page=1,
                        )
                        self.api_calls_made += 1

                        if year_data and "results" in year_data:
                            movies_data = year_data.get("results", [])
                            # Get top 10 movies from nearby year
                            nearby_movies = validate_movie_list(movies_data[:10])
                            all_candidates.extend(nearby_movies)
                            self.logger.debug(
                                f"Nearby year {nearby_year}: {len(nearby_movies)} candidates"
                            )

                        time.sleep(self.api_delay)

                    except Exception as e:
                        self.logger.warning(
                            f"Error getting movies from year {nearby_year}: {e}"
                        )
                        continue

        # Remove duplicates and exclude target movie
        unique_candidates = remove_duplicate_movies(all_candidates)
        unique_candidates = [m for m in unique_candidates if m.id != target_movie.id]

        self.logger.debug(
            f"Hybrid strategy: {len(all_candidates)} raw candidates -> "
            f"{len(unique_candidates)} unique candidates (excluding target)"
        )

        return unique_candidates

    def _calculate_similarity_and_rank(
        self, target_movie: Movie, candidates: List[Movie], top_n: int
    ) -> List[Dict[str, Any]]:
        """
        Calculate similarity scores for candidates and return top N.

        This is Stage 2 of the recommendation process:
        - Calculates weighted similarity scores using multi-factor scoring
        - Ranks candidates by similarity score
        - Returns top N most similar movies

        Args:
            target_movie: Target movie to compare against
            candidates: List of candidate movies
            top_n: Number of top similar movies to return

        Returns:
            List of dictionaries containing similar movie information:
                - "similar_movie": Movie model
                - "similarity_score": float
                - "similarity_reason": str
                - "similarity_metrics": dict
        """
        if not candidates:
            return []

        self.logger.debug(
            f"Calculating similarity scores for {len(candidates)} candidates "
            f"for {target_movie.title}"
        )

        # Enrich candidates with details (genres, keywords) if not already enriched
        # This is needed for accurate similarity calculation
        enriched_candidates = self._enrich_candidates_if_needed(candidates)

        # Calculate similarity scores
        scored_movies: List[Tuple[Movie, float, Dict[str, Any]]] = []

        for candidate in enriched_candidates:
            # Skip if it's the same movie
            if candidate.id == target_movie.id:
                continue

            try:
                score, metrics = self.calculate_similarity_score(
                    target_movie, candidate
                )
                scored_movies.append((candidate, score, metrics))
            except Exception as e:
                self.logger.warning(
                    f"Error calculating similarity for candidate {candidate.id}: {e}"
                )
                continue

        # Sort by similarity score (highest first)
        scored_movies.sort(key=lambda x: x[1], reverse=True)

        # Get top N
        top_similar = scored_movies[:top_n]

        # Format results
        results: List[Dict[str, Any]] = []
        for movie, score, metrics in top_similar:
            results.append({
                "similar_movie": movie,
                "similarity_score": score,
                "similarity_reason": metrics.get("similarity_reason", "General similarity"),
                "similarity_metrics": metrics,
            })

        self.logger.debug(
            f"Ranked {len(scored_movies)} candidates, returning top {len(results)} "
            f"for {target_movie.title}"
        )

        return results

    def _calculate_genre_similarity(
        self, genres1: List[str], genres2: List[str]
    ) -> float:
        """
        Calculate genre similarity using Jaccard similarity.

        Args:
            genres1: List of genre names from first movie
            genres2: List of genre names from second movie

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not genres1 or not genres2:
            return 0.0

        set1 = set(genres1)
        set2 = set(genres2)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        return intersection / union

    def _calculate_keyword_similarity(
        self, keywords1: List[str], keywords2: List[str]
    ) -> float:
        """
        Calculate keyword similarity using Jaccard similarity.

        Args:
            keywords1: List of keyword names from first movie
            keywords2: List of keyword names from second movie

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not keywords1 or not keywords2:
            return 0.0

        set1 = set(keywords1)
        set2 = set(keywords2)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        return intersection / union

    def _calculate_director_similarity(
        self, director1: Optional[str], director2: Optional[str]
    ) -> float:
        """
        Calculate director similarity (binary: same director = 1.0, different = 0.0).

        Args:
            director1: Director name from first movie
            director2: Director name from second movie

        Returns:
            Similarity score: 1.0 if same director, 0.0 otherwise
        """
        if not director1 or not director2:
            return 0.0

        # Case-insensitive comparison
        if director1.lower().strip() == director2.lower().strip():
            return 1.0

        return 0.0

    def _calculate_collection_similarity(
        self, collection_id1: Optional[int], collection_id2: Optional[int]
    ) -> float:
        """
        Calculate collection/franchise similarity (binary: same collection = 1.0, different = 0.0).

        Args:
            collection_id1: Collection ID from first movie
            collection_id2: Collection ID from second movie

        Returns:
            Similarity score: 1.0 if same collection, 0.0 otherwise
        """
        if collection_id1 is None or collection_id2 is None:
            return 0.0

        if collection_id1 == collection_id2:
            return 1.0

        return 0.0

    def _calculate_production_company_similarity(
        self, companies1: List[int], companies2: List[int]
    ) -> float:
        """
        Calculate production company similarity using Jaccard similarity.
        If movies share at least one production company (e.g., both are Pixar movies),
        they get a similarity score based on overlap.

        Args:
            companies1: List of production company IDs from first movie
            companies2: List of production company IDs from second movie

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not companies1 or not companies2:
            return 0.0

        set1 = set(companies1)
        set2 = set(companies2)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        # Jaccard similarity: intersection / union
        # If they share at least one company, score > 0
        return intersection / union

    def calculate_similarity_score(
        self, target_movie: Movie, candidate_movie: Movie
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate overall similarity score between two movies.

        Focuses on actual similarity factors:
        - Genre similarity: configurable (default 0.3)
        - Keyword similarity: configurable (default 0.1)
        - Director similarity: configurable (default 0.1) (same director = 1.0, different = 0.0)
        - Collection/franchise similarity: configurable (default 0.3) (same collection = 1.0, different = 0.0)
        - Production company similarity: configurable (default 0.2) (Jaccard similarity of production companies)

        Args:
            target_movie: Target movie to compare against
            candidate_movie: Candidate movie to compare

        Returns:
            Tuple of (similarity_score, metrics_dict)
            - similarity_score: Overall similarity score (0.0 to 1.0)
            - metrics_dict: Dictionary containing detailed metrics
        """
        # Get genre and keyword names
        genres1 = target_movie.genre_names if target_movie.genres else []
        genres2 = candidate_movie.genre_names if candidate_movie.genres else []
        keywords1 = target_movie.keyword_names if target_movie.keywords else []
        keywords2 = candidate_movie.keyword_names if candidate_movie.keywords else []
        
        # Get production company IDs
        companies1 = target_movie.production_company_ids
        companies2 = candidate_movie.production_company_ids

        # Calculate individual similarities
        genre_sim = self._calculate_genre_similarity(genres1, genres2)
        keyword_sim = self._calculate_keyword_similarity(keywords1, keywords2)
        director_sim = self._calculate_director_similarity(
            target_movie.director, candidate_movie.director
        )
        collection_sim = self._calculate_collection_similarity(
            target_movie.collection_id, candidate_movie.collection_id
        )
        production_company_sim = self._calculate_production_company_similarity(
            companies1, companies2
        )

        # Calculate weighted overall similarity score
        similarity_score = (
            (genre_sim * self.genre_weight) +
            (keyword_sim * self.keyword_weight) +
            (director_sim * self.director_weight) +
            (collection_sim * self.collection_weight) +
            (production_company_sim * self.production_company_weight)
        )

        # Ensure score is between 0.0 and 1.0
        similarity_score = max(0.0, min(1.0, similarity_score))

        # Find shared genres, keywords, and production companies
        shared_genres = list(set(genres1).intersection(set(genres2)))
        shared_keywords = list(set(keywords1).intersection(set(keywords2)))
        shared_companies = list(set(companies1).intersection(set(companies2)))
        shared_company_names = []
        if shared_companies and target_movie.production_companies:
            # Get names of shared production companies
            company_name_map = {
                company.get("id"): company.get("name", "")
                for company in target_movie.production_companies
                if isinstance(company, dict) and company.get("id")
            }
            shared_company_names = [
                company_name_map.get(company_id, "")
                for company_id in shared_companies
                if company_name_map.get(company_id)
            ]

        # Generate similarity reason
        similarity_reason = self._generate_similarity_reason(
            genre_sim, keyword_sim, director_sim, collection_sim, production_company_sim,
            shared_genres, target_movie.director, candidate_movie.director,
            target_movie.collection_name, candidate_movie.collection_name,
            shared_company_names
        )

        # Build metrics dictionary
        metrics = {
            "genre_similarity": genre_sim,
            "keyword_similarity": keyword_sim,
            "director_similarity": director_sim,
            "collection_similarity": collection_sim,
            "production_company_similarity": production_company_sim,
            "shared_genres": shared_genres,
            "shared_keywords": shared_keywords,
            "shared_production_companies": shared_company_names,
            "similarity_reason": similarity_reason,
        }

        return similarity_score, metrics

    def _generate_similarity_reason(
        self,
        genre_sim: float,
        keyword_sim: float,
        director_sim: float,
        collection_sim: float,
        production_company_sim: float,
        shared_genres: List[str],
        director1: Optional[str],
        director2: Optional[str],
        collection1: Optional[str],
        collection2: Optional[str],
        shared_company_names: List[str],
    ) -> str:
        """
        Generate human-readable similarity reason.

        Args:
            genre_sim: Genre similarity score
            keyword_sim: Keyword similarity score
            director_sim: Director similarity score
            collection_sim: Collection similarity score
            production_company_sim: Production company similarity score
            shared_genres: List of shared genres
            director1: Director name from first movie
            director2: Director name from second movie
            collection1: Collection name from first movie
            collection2: Collection name from second movie
            shared_company_names: List of shared production company names

        Returns:
            Human-readable similarity reason
        """
        reasons = []

        # Collection/franchise (highest priority)
        if collection_sim > 0.0 and collection1:
            reasons.append(f"Same franchise: {collection1}")

        # Production company (high priority - e.g., Pixar, Disney, Marvel)
        if production_company_sim > 0.0 and shared_company_names:
            # Show up to 2 production companies
            company_str = ", ".join(shared_company_names[:2])
            if len(shared_company_names) > 2:
                company_str += f" (+{len(shared_company_names) - 2} more)"
            reasons.append(f"Same studio: {company_str}")

        # Director (high priority)
        if director_sim > 0.0 and director1:
            reasons.append(f"Same director: {director1}")

        # Genre similarity
        if genre_sim > 0.5:
            if shared_genres:
                reasons.append(f"Similar genres: {', '.join(shared_genres[:3])}")
            else:
                reasons.append("Similar genres")
        elif genre_sim > 0.0:
            reasons.append("Some genre overlap")

        # Keyword similarity
        if keyword_sim > 0.3:
            reasons.append("Similar themes/keywords")

        if not reasons:
            return "General similarity"
        elif len(reasons) == 1:
            return reasons[0]
        else:
            return "; ".join(reasons[:3])  # Limit to 3 reasons

    def _enrich_candidates_if_needed(self, candidates: List[Movie]) -> List[Movie]:
        """
        Enrich candidates with detailed information (genres, keywords, director, collection) if needed.

        Args:
            candidates: List of candidate movies

        Returns:
            List of enriched Movie models
        """
        enriched: List[Movie] = []

        for candidate in candidates:
            # Check if movie already has all similarity-related fields
            # Note: collection_id can be None (not all movies have collections)
            # We check if director exists to determine if we need to fetch credits
            needs_enrichment = (
                not candidate.genres or
                not candidate.keywords or
                candidate.director is None  # Director might be None if not fetched yet
            )

            if not needs_enrichment:
                enriched.append(candidate)
                continue

            # Enrich with details
            try:
                # Get movie details (includes collection)
                details_data = self.tmdb_client.get_movie_details(candidate.id)
                self.api_calls_made += 1

                if not details_data:
                    enriched.append(candidate)
                    continue

                # Get keywords
                keywords_data = self.tmdb_client.get_movie_keywords(candidate.id)
                self.api_calls_made += 1

                if keywords_data and "keywords" in keywords_data:
                    details_data["keywords"] = keywords_data

                # Get credits to extract director
                credits_data = self.tmdb_client.get_movie_credits(candidate.id)
                self.api_calls_made += 1

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

                # Create enriched movie
                enriched_movie = movie_from_tmdb_response(details_data)
                enriched.append(enriched_movie)

                time.sleep(self.api_delay)

            except Exception as e:
                self.logger.warning(
                    f"Failed to enrich candidate {candidate.id}: {e}"
                )
                enriched.append(candidate)

        return enriched


# Alias for backwards compatibility with tests
RecommendationService = MovieRecommendationEngine

