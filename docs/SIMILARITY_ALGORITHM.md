# Similarity Matching System

## Overview

The recommendation service implements a basic similarity matching algorithm that finds similar movies based on multiple criteria. The system is designed to be extensible and can be enhanced with more complex algorithms in the future.

## Algorithm Components

### 1. Genre Similarity
- **Method**: Jaccard Similarity
- **Formula**: `intersection(genres1, genres2) / union(genres1, genres2)`
- **Weight**: 0.4 (configurable)
- **Range**: 0.0 to 1.0

### 2. Keyword Similarity
- **Method**: Jaccard Similarity
- **Formula**: `intersection(keywords1, keywords2) / union(keywords1, keywords2)`
- **Weight**: Combined with genre similarity (average)
- **Range**: 0.0 to 1.0

### 3. Content Similarity
- **Method**: Average of genre and keyword similarity
- **Formula**: `(genre_similarity + keyword_similarity) / 2`
- **Weight**: 0.4 (same as genre_weight)
- **Purpose**: Measures thematic/content similarity

### 4. Rating Similarity
- **Method**: Normalized difference
- **Formula**: `1.0 - (|rating1 - rating2| / max_rating)`
- **Weight**: 0.3 (configurable)
- **Range**: 0.0 to 1.0
- **Max Rating**: 10.0

### 5. Year Similarity
- **Method**: Inverse distance with threshold
- **Formula**: `1.0 - (|year1 - year2| / max_diff)` if diff < max_diff, else 0.0
- **Weight**: 0.1 (configurable)
- **Max Difference**: 20 years (configurable)
- **Range**: 0.0 to 1.0

### 6. Popularity Factor
- **Method**: Normalized popularity score
- **Formula**: `min(popularity / 100.0, 1.0)`
- **Weight**: 0.2 (configurable)
- **Purpose**: Slight boost for popular movies
- **Range**: 0.0 to 1.0

## Overall Similarity Score

The final similarity score is calculated as a weighted sum:

```
similarity_score = 
    (content_similarity * 0.4) +
    (rating_similarity * 0.3) +
    (popularity_factor * 0.2) +
    (year_similarity * 0.1)
```

## Similarity Metrics

Each similar movie includes detailed metrics:

- **similarity_score**: Overall similarity score (0.0 to 1.0)
- **genre_similarity**: Genre overlap score
- **keyword_similarity**: Keyword overlap score
- **content_similarity**: Combined content similarity
- **rating_similarity**: Rating proximity score
- **year_similarity**: Release year proximity score
- **shared_genres**: List of shared genres
- **shared_keywords**: List of shared keywords
- **similarity_reason**: Human-readable explanation

## Workflow

1. **Get Candidates**: Retrieve similar movies from TMDB API
2. **Enrich Data**: Fetch full details (genres, keywords, etc.)
3. **Calculate Scores**: Compute similarity scores for all candidates
4. **Sort & Filter**: Sort by similarity score, select top N
5. **Generate Reasons**: Create human-readable similarity explanations

## Configuration

Weights can be adjusted in `config/config.yaml`:

```yaml
recommendation:
  weights:
    genre_similarity: 0.4
    rating: 0.3
    popularity: 0.2
    release_year: 0.1
```

## Extensibility

The system is designed to be easily extended with:

1. **Machine Learning Models**: Replace scoring functions with ML models
2. **Collaborative Filtering**: Add user-based recommendations
3. **Content-Based Filtering**: Enhance content similarity with NLP
4. **Hybrid Approaches**: Combine multiple recommendation strategies
5. **Custom Metrics**: Add new similarity dimensions (director, cast, etc.)

## Usage Example

```python
from src.services.recommendation_service import RecommendationService
from src.models.Movies import Movie

service = RecommendationService()

# Find similar movies
similar_movies = service.find_similar_movies(
    original_movie=movie,
    limit=3,
    min_vote_count=100
)

# Each result contains:
# - similar_movie: Movie model
# - similarity_score: float
# - similarity_reason: str
# - similarity_metrics: dict
```

## Future Enhancements

Potential improvements:

1. **TF-IDF on Keywords**: Weight keywords by importance
2. **Embedding Models**: Use movie embeddings for semantic similarity
3. **User Ratings**: Incorporate user preferences
4. **Temporal Factors**: Consider viewing trends
5. **Diversity**: Ensure recommendation diversity
6. **Cold Start**: Handle movies with limited data
7. **A/B Testing**: Test different algorithms
8. **Performance**: Cache similarity scores
9. **Real-time Updates**: Update recommendations dynamically
10. **Explainability**: Enhanced similarity explanations

## Performance Considerations

- **Caching**: Similarity scores can be cached
- **Batch Processing**: Process multiple movies efficiently
- **Rate Limiting**: Respects TMDB API rate limits
- **Parallel Processing**: Can be parallelized for multiple movies

## Testing

Test the similarity system:

```bash
python main.py --year 2020 --similar-movies --similar-limit 3
```

This will:
1. Get top 10 movies from 2020
2. Find 3 similar movies for each
3. Export to `similar_movies.csv` with all metrics

