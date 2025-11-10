"""
Quick test script to verify article removal functionality.
"""

from src.models.Movies import Movie, Genre, Keyword


def test_article_removal():
    """Test that articles are properly removed from movie titles."""
    
    # Test cases: (title, expected_with_articles, expected_without_articles)
    test_cases = [
        ("The Matrix", "The Matrix", "Matrix"),
        ("A Beautiful Mind", "A Beautiful Mind", "Beautiful Mind"),
        ("An American Tail", "An American Tail", "American Tail"),
        ("In Time", "In Time", "Time"),
        ("On the Waterfront", "On the Waterfront", "Waterfront"),  # Removes "On", then "the"
        ("For Whom the Bell Tolls", "For Whom the Bell Tolls", "Whom the Bell Tolls"),
        ("And Justice for All", "And Justice for All", "Justice for All"),
        ("The A-Team", "The A-Team", "A-Team"),  # "A-Team" doesn't match (no space after "A")
        ("The Lord of the Rings", "The Lord of the Rings", "Lord of the Rings"),
        ("Matrix", "Matrix", "Matrix"),  # No article
        ("Batman Begins", "Batman Begins", "Batman Begins"),  # No article
        ("The The Movie", "The The Movie", "Movie"),  # Multiple articles
        ("A The Movie", "A The Movie", "Movie"),  # Multiple articles
        ("Of Mice and Men", "Of Mice and Men", "Mice and Men"),  # Preposition
        ("With Honors", "With Honors", "Honors"),  # Preposition
        ("By the Sea", "By the Sea", "Sea"),  # Preposition + article
    ]
    
    print("Testing article removal functionality...")
    print("=" * 70)
    
    for title, expected_with, expected_without in test_cases:
        # Create a minimal movie object
        movie = Movie(
            id=1,
            title=title,
            vote_count=1000,
            vote_average=7.5,
            popularity=50.0
        )
        
        # Test with articles
        result_with = movie.normalize_title_for_sorting(ignore_articles=False)
        # Test without articles
        result_without = movie.normalize_title_for_sorting(ignore_articles=True)
        
        # Check results
        with_ok = result_with == expected_with
        without_ok = result_without == expected_without
        
        status = "✓" if (with_ok and without_ok) else "✗"
        
        print(f"{status} Title: '{title}'")
        print(f"   With articles:    '{result_with}' (expected: '{expected_with}') {'✓' if with_ok else '✗'}")
        print(f"   Without articles: '{result_without}' (expected: '{expected_without}') {'✓' if without_ok else '✗'}")
        print()
    
    print("=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    test_article_removal()

