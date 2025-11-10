"""
Example usage of the MovieRecommendationEngine.

This script demonstrates how to use the two-stage recommendation engine:
1. Stage 1: Smart candidate selection (reduces search space)
2. Stage 2: Multi-factor similarity calculation (ranks candidates)
"""

from src.api.TMDB import TMDBClient
from src.services.movie_recommendation_engine import MovieRecommendationEngine
from src.services.movie_service import MovieService
from src.services.recommendation_service import RecommendationService


def main():
    """Example usage of MovieRecommendationEngine."""
    # Initialize services
    api_client = TMDBClient()
    recommendation_service = RecommendationService(tmdb_client=api_client)
    recommendation_engine = MovieRecommendationEngine(
        tmdb_client=api_client,
        recommendation_service=recommendation_service,
    )

    # Initialize movie service to get top movies
    movie_service = MovieService(tmdb_client=api_client)

    # Get top 10 movies from 2023
    print("Fetching top 10 movies from 2023...")
    top_movies, _ = movie_service.get_top_movies_by_year(year=2023, top_n=10)

    print(f"Found {len(top_movies)} top movies:")
    for movie in top_movies:
        print(f"  - {movie.title} ({movie.release_year})")

    # Find 3 similar movies for each using hybrid strategy (RECOMMENDED)
    print("\n" + "=" * 60)
    print("Finding similar movies using HYBRID strategy...")
    print("=" * 60)

    all_similarity_results = recommendation_engine.find_similar_movies_for_each(
        top_movies=top_movies,
        similar_per_movie=3,
        strategy="hybrid",  # RECOMMENDED: Best quality, combines multiple signals
    )

    # Display results
    print(f"\nFound similar movies for {len(all_similarity_results)} movies:")
    for result in all_similarity_results:
        original_movie = result["original_movie"]
        similar_movies = result["similar_movies"]

        print(f"\n{original_movie.title} ({original_movie.release_year}):")
        for similar in similar_movies:
            similar_movie = similar["similar_movie"]
            score = similar["similarity_score"]
            reason = similar["similarity_reason"]
            print(f"  - {similar_movie.title} (score: {score:.3f}) - {reason}")

    # Example: Using different strategies
    print("\n" + "=" * 60)
    print("Example: Using TMDB API strategy (faster, less control)...")
    print("=" * 60)

    # Use TMDB API strategy for a single movie (faster)
    single_movie_results = recommendation_engine.find_similar_movies_for_each(
        top_movies=top_movies[:1],  # Just the first movie
        similar_per_movie=3,
        strategy="tmdb_api",  # Fast, uses TMDB's algorithms
    )

    if single_movie_results:
        result = single_movie_results[0]
        original_movie = result["original_movie"]
        similar_movies = result["similar_movies"]

        print(f"\n{original_movie.title} - Similar movies (TMDB API strategy):")
        for similar in similar_movies:
            similar_movie = similar["similar_movie"]
            score = similar["similarity_score"]
            print(f"  - {similar_movie.title} (score: {score:.3f})")

    # Display performance metrics
    print(f"\n{'=' * 60}")
    print(f"Performance: {recommendation_engine.api_calls_made} API calls made")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

