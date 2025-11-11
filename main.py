"""
Main entry point for the TMDB Movie Recommendation application.
"""

import argparse
import sys
from pathlib import Path

from src.services.movie_service import MovieService
from src.services.movie_recommendation_engine import MovieRecommendationEngine
from src.utils.logger import get_logger


def main():
    """Main function to run the movie service."""
    parser = argparse.ArgumentParser(
        description="TMDB Movie Recommendation - Get top movies from a year and export to CSV"
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year to retrieve movies from (e.g., 2020)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top movies to retrieve (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output CSV filename (default: top_movies_{year}.csv, year is automatically added)",
    )
    parser.add_argument(
        "--min-votes",
        type=int,
        default=None,
        help="Minimum vote count (uses config default if not specified)",
    )
    parser.add_argument(
        "--min-rating",
        type=float,
        default=None,
        help="Minimum vote average (uses config default if not specified)",
    )
    parser.add_argument(
        "--no-similar-movies",
        action="store_false",
        dest="similar_movies",
        default=True,
        help="Disable finding and exporting similar movies (enabled by default)",
    )
    parser.add_argument(
        "--similar-limit",
        type=int,
        default=3,
        help="Number of similar movies to find per movie (default: 3)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="tmdb_api",
        choices=["tmdb_api", "same_year", "same_genre", "hybrid"],
        help=(
            "Candidate selection strategy for recommendations (default: tmdb_api). "
            "Options: tmdb_api (fast, uses TMDB's algorithm), "
            "same_year (movies from same year), same_genre (overlapping genres), "
            "hybrid (best quality, slowest)"
        ),
    )

    args = parser.parse_args()

    logger = get_logger("main")

    try:
        logger.info(f"Starting movie service for year {args.year}")
        
        # Generate output filename with year
        if args.output is None:
            # Default filename with year
            output_filename = f"top_movies_{args.year}.csv"
        else:
            # Insert year before file extension if user provided custom filename
            output_path = Path(args.output)
            if output_path.suffix:
                output_filename = f"{output_path.stem}_{args.year}{output_path.suffix}"
            else:
                output_filename = f"{args.output}_{args.year}.csv"
        
        # Initialize service
        movie_service = MovieService()

        # Get and export top movies
        movies, csv_path = movie_service.get_and_export_top_movies(
            year=args.year,
            top_n=args.top_n,
            filename=output_filename,
            min_vote_count=args.min_votes,
            min_vote_average=args.min_rating,
        )

        logger.info(f"Successfully processed {len(movies)} movies")
        print(f"\n✅ Success! Exported {len(movies)} movies to: {csv_path}")
        print(f"\nMovies retrieved:")
        for i, movie in enumerate(movies, 1):
            print(f"  {i}. {movie.title} ({movie.release_year}) - Votes: {movie.vote_count}")

        # Find similar movies if requested
        if args.similar_movies:
            print(f"\n🔍 Finding similar movies for each movie using '{args.strategy}' strategy...")
            logger.info(f"Using recommendation strategy: {args.strategy}")

            # Initialize recommendation engine
            recommendation_engine = MovieRecommendationEngine()

            # Find similar movies using the recommendation engine
            recommendations_data = recommendation_engine.find_similar_movies_for_each(
                top_movies=movies,
                similar_per_movie=args.similar_limit,
                strategy=args.strategy,
            )

            if recommendations_data:
                # Flatten for export
                flattened: list[dict] = []
                for entry in recommendations_data:
                    original = entry.get("original_movie")
                    for sim in entry.get("similar_movies", []):
                        flattened.append({
                            "original_movie": original,
                            "similar_movie": sim.get("similar_movie"),
                            "similarity_score": sim.get("similarity_score"),
                            "similarity_reason": sim.get("similarity_reason"),
                            "similarity_metrics": sim.get("similarity_metrics", {}),
                        })

                # Export similar movies with year in filename
                from src.services.export_service import ExportService
                export_service = ExportService()
                similar_filename = f"similar_movies_{args.year}.csv"
                similar_csv_path = export_service.export_similar_movies_to_csv(
                    similar_movies_data=flattened,
                    filename=similar_filename,
                )

                total_similar = sum(len(item.get("similar_movies", [])) for item in recommendations_data)
                print(f"\n✅ Success! Exported {total_similar} similar movies to: {similar_csv_path}")
                print(f"   Strategy used: {args.strategy}")
                print(f"   API calls made: {recommendation_engine.api_calls_made}")
                logger.info(
                    f"Exported {total_similar} similar movies to {similar_csv_path} "
                    f"using strategy {args.strategy} ({recommendation_engine.api_calls_made} API calls)"
                )
            else:
                print("\n⚠️  No similar movies found")
                logger.warning("No similar movies found")

        return 0

    except ValueError as e:
        logger.error(f"Value error: {e}")
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

