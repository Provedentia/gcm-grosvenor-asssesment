# Movie Recommendation Engine

## Overview

The `MovieRecommendationEngine` implements a **two-stage approach** to finding similar movies:

### Stage 1: Smart Candidate Selection
Reduces the search space from millions of movies to hundreds by using intelligent filtering strategies.

### Stage 2: Multi-Factor Similarity Calculation
Uses weighted scoring (genres, keywords, ratings, year, popularity) to rank candidates and return the most similar movies.

## Why Two Stages?

**Problem**: Comparing a movie against millions of movies in the TMDB database would be:
- Extremely slow (millions of API calls)
- Expensive (API rate limits and costs)
- Inefficient (most movies are completely unrelated)

**Solution**: Two-stage approach
1. **Candidate Selection**: Quickly filter to ~100-200 relevant candidates using heuristics
2. **Similarity Calculation**: Calculate detailed similarity scores only for candidates

This reduces API calls from millions to hundreds while maintaining high quality recommendations.

## Strategies

### 1. TMDB API Strategy (`tmdb_api`)
- **How**: Uses TMDB's `/movie/{id}/similar` and `/movie/{id}/recommendations` endpoints
- **Candidates**: ~20-40 movies
- **API Calls**: 2 per movie
- **Pros**: Fast, simple, leverages TMDB's algorithms
- **Cons**: Less control, black box algorithm

### 2. Same Year Strategy (`same_year`)
- **How**: Gets movies from the target movie's release year
- **Candidates**: ~20-50 movies
- **API Calls**: 1 per movie
- **Pros**: Temporal relevance, movies from same era
- **Cons**: Limited pool, may miss cross-era similarities

### 3. Same Genre Strategy (`same_genre`)
- **How**: Gets top movies for each of the target movie's genres (top 2 genres)
- **Candidates**: ~50-100 movies
- **API Calls**: 2 per movie (one per genre)
- **Pros**: Thematically similar, genre-based matching
- **Cons**: More API calls, may be too narrow

### 4. Hybrid Strategy (`hybrid`) - **RECOMMENDED**
- **How**: Combines multiple approaches:
  - TMDB suggestions (~40 movies)
  - Same year movies (~50 movies)
  - Nearby years ±2 years (~40 movies total)
- **Candidates**: ~100-200 movies
- **API Calls**: 5-8 per movie
- **Pros**: Best quality, large diverse pool, combines multiple signals
- **Cons**: More API calls, slower

## Usage

### Basic Usage

```python
from src.api.TMDB import TMDBClient
from src.services.movie_recommendation_engine import MovieRecommendationEngine
from src.services.movie_service import MovieService

# Initialize
api_client = TMDBClient()
recommendation_engine = MovieRecommendationEngine(tmdb_client=api_client)
movie_service = MovieService(tmdb_client=api_client)

# Get top 10 movies from 2023
top_movies = movie_service.get_top_movies_by_year(year=2023, top_n=10)

# Find 3 similar movies for each using hybrid strategy
similarity_results = recommendation_engine.find_similar_movies_for_each(
    top_movies=top_movies,
    similar_per_movie=3,
    strategy="hybrid"  # RECOMMENDED
)

# Process results
for result in similarity_results:
    original_movie = result["original_movie"]
    similar_movies = result["similar_movies"]
    
    print(f"{original_movie.title}:")
    for similar in similar_movies:
        print(f"  - {similar['similar_movie'].title} (score: {similar['similarity_score']:.3f})")
```

### Strategy Selection

```python
# Fast and simple (good for quick results)
results = recommendation_engine.find_similar_movies_for_each(
    top_movies=movies,
    similar_per_movie=3,
    strategy="tmdb_api"
)

# Best quality (recommended for production)
results = recommendation_engine.find_similar_movies_for_each(
    top_movies=movies,
    similar_per_movie=3,
    strategy="hybrid"
)
```

## Architecture

### Components

1. **MovieRecommendationEngine** (`src/services/movie_recommendation_engine.py`)
   - Orchestrates the complete workflow
   - Manages candidate selection strategies
   - Delegates similarity calculation to RecommendationService

2. **RecommendationService** (`src/services/recommendation_service.py`)
   - Calculates similarity scores using weighted metrics
   - Handles genre, keyword, rating, year, and popularity similarity

3. **TMDBClient** (`src/api/TMDB.py`)
   - Updated with `get_movie_recommendations()` method
   - Updated with genre filtering in `get_movies_by_year()` and `discover_movies()`

4. **Helper Functions** (`src/models/Movies.py`)
   - `remove_duplicate_movies()`: Removes duplicates while preserving order

## Performance

### API Call Tracking
The engine tracks API calls for monitoring:
```python
print(f"API calls made: {recommendation_engine.api_calls_made}")
```

### Typical Performance
- **TMDB API Strategy**: ~2 API calls per movie, ~5-10 seconds for 10 movies
- **Hybrid Strategy**: ~5-8 API calls per movie, ~20-40 seconds for 10 movies

## Configuration

Configuration is managed through `config/config.yaml`:
```yaml
recommendation:
  min_vote_count: 100
  min_vote_average: 6.0
  weights:
    genre_similarity: 0.4
    rating: 0.3
    popularity: 0.2
    release_year: 0.1
```

## Example Output

```
Finding similar movies using HYBRID strategy...
============================================================
Found similar movies for 10 movies:

The Matrix (1999):
  - The Matrix Reloaded (score: 0.856) - Similar genres (Action, Science Fiction); Similar themes (3 shared keywords)
  - Inception (score: 0.782) - Similar genres (Action, Science Fiction); Similar ratings
  - Blade Runner (score: 0.745) - Similar genres (Science Fiction); Similar release period

Inception (2010):
  - The Matrix (score: 0.782) - Similar genres (Action, Science Fiction); Similar ratings
  - Interstellar (score: 0.765) - Similar genres (Science Fiction); Similar themes (2 shared keywords)
  - Shutter Island (score: 0.712) - Similar ratings; Similar themes (1 shared keywords)

Performance: 67 API calls made
```

## Integration with Existing Code

The engine integrates seamlessly with existing services:

- **MovieService**: Gets top movies by year
- **RecommendationService**: Calculates similarity scores
- **ExportService**: Exports results to CSV (via RecommendationService.prepare_similar_movies_for_export)

See `example_recommendation_engine.py` for a complete working example.

## Future Enhancements

The two-stage approach is designed to be extensible:

1. **More Candidate Strategies**: Add new strategies (e.g., director-based, actor-based)
2. **Better Similarity Algorithms**: Enhance RecommendationService with ML models
3. **Caching**: Cache candidate pools to reduce API calls
4. **Parallel Processing**: Process multiple movies in parallel
5. **User Preferences**: Incorporate user preferences into similarity calculation

