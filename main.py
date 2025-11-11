"""
Main entry point for the TMDB Movie Recommendation application.
"""

import argparse
import sys
from pathlib import Path

from src.services.movie_service import MovieService
from src.services.recommendation_service import RecommendationService
from src.services.export_service import ExportService
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
        "--similar-movies",
        action="store_true",
        help="Also find and export similar movies for each top movie",
    )
    parser.add_argument(
        "--similar-limit",
        type=int,
        default=3,
        help="Number of similar movies to find per movie (default: 3)",
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
            print(f"\n🔍 Finding similar movies for each movie...")
            recommendation_service = RecommendationService()
            export_service = ExportService()

            # Get similar movies for all top movies
            similar_movies_data = recommendation_service.get_similar_movies_for_multiple(
                movies=movies,
                limit=args.similar_limit,
            )

            if similar_movies_data:
                # Prepare data for export
                export_data = recommendation_service.prepare_similar_movies_for_export(
                    similar_movies_data
                )

                # Export similar movies with year in filename
                similar_filename = f"similar_movies_{args.year}.csv"
                similar_csv_path = export_service.export_similar_movies_to_csv(
                    similar_movies_data=export_data,
                    filename=similar_filename,
                )

                total_similar = sum(
                    len(item.get("similar_movies", [])) for item in similar_movies_data
                )
                print(f"\n✅ Success! Exported {total_similar} similar movies to: {similar_csv_path}")
                logger.info(f"Exported {total_similar} similar movies to {similar_csv_path}")
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

