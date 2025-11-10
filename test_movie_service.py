"""
Simple test script for the movie service.
Run this to test the movie service functionality.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.movie_service import MovieService
from src.utils.logger import get_logger


def test_movie_service():
    """Test the movie service."""
    logger = get_logger("test")

    # Check if API key is set
    if not os.getenv("TMDB_API_KEY"):
        print("❌ Error: TMDB_API_KEY environment variable not set!")
        print("Please set it in a .env file or export it:")
        print("  export TMDB_API_KEY=your_api_key_here")
        return 1

    try:
        print("🚀 Starting movie service test...")
        print("=" * 50)

        # Initialize service
        service = MovieService()

        # Test with year 2020
        year = 2020
        top_n = 10

        print(f"\n📽️  Fetching top {top_n} movies from year {year}...")
        movies, csv_path = service.get_and_export_top_movies(
            year=year,
            top_n=top_n,
            filename="test_top_movies.csv",
        )

        print(f"\n✅ Success! Retrieved {len(movies)} movies")
        print(f"📄 CSV file saved to: {csv_path}")
        print("\n" + "=" * 50)
        print("📋 Movies retrieved:")
        print("=" * 50)

        for i, movie in enumerate(movies, 1):
            print(f"\n{i}. {movie.title}")
            print(f"   Year: {movie.release_year}")
            print(f"   Votes: {movie.vote_count:,}")
            print(f"   Rating: {movie.vote_average}/10")
            print(f"   Genres: {', '.join(movie.genre_names) if movie.genre_names else 'N/A'}")

        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        print(f"📁 Check the CSV file at: {csv_path}")

        return 0

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(test_movie_service())

