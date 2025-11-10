"""
Movie data models and validation using Pydantic.
Provides structured data models for TMDB API responses.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, TypedDict, Union

from pydantic import BaseModel, Field, field_validator


# TypedDict definitions for nested structures
class ProductionCompanyDict(TypedDict, total=False):
    """Type definition for production company data."""

    id: int
    name: str
    logo_path: Optional[str]
    origin_country: Optional[str]


class ProductionCountryDict(TypedDict, total=False):
    """Type definition for production country data."""

    iso_3166_1: str
    name: str


class SpokenLanguageDict(TypedDict, total=False):
    """Type definition for spoken language data."""

    iso_639_1: str
    name: str
    english_name: Optional[str]


class GenreKeywordDict(TypedDict):
    """Type definition for genre/keyword data from API."""

    id: int
    name: str


class TMDBMovieResponseDict(TypedDict, total=False):
    """
    Type definition for TMDB movie API response.
    
    Note: All fields are marked as optional (total=False) to match TMDB API response
    variations. The Pydantic Movie model enforces required fields (id, title).
    Required fields in actual API responses: id, title.
    """

    id: int  # Required in API response
    title: str  # Required in API response
    overview: Optional[str]
    release_date: Optional[str]
    vote_count: int
    vote_average: float
    popularity: float
    poster_path: Optional[str]
    backdrop_path: Optional[str]
    adult: bool
    original_language: Optional[str]
    original_title: Optional[str]
    video: bool
    genre_ids: Optional[List[int]]
    genres: Optional[List[GenreKeywordDict]]
    keywords: Optional[Union[List[GenreKeywordDict], Dict[str, Any]]]
    runtime: Optional[int]
    status: Optional[str]
    tagline: Optional[str]
    budget: Optional[int]
    revenue: Optional[int]
    homepage: Optional[str]
    imdb_id: Optional[str]
    production_companies: Optional[List[ProductionCompanyDict]]
    production_countries: Optional[List[ProductionCountryDict]]
    spoken_languages: Optional[List[SpokenLanguageDict]]


class Genre(BaseModel):
    """Genre model for movie genres."""

    id: int
    name: str

    class Config:
        """Pydantic configuration."""

        frozen = True


class Keyword(BaseModel):
    """Keyword model for movie keywords."""

    id: int
    name: str

    class Config:
        """Pydantic configuration."""

        frozen = True


class Movie(BaseModel):
    """
    Movie model representing a movie from TMDB API.
    Includes validation and helper methods.
    """

    id: int = Field(..., description="TMDB movie ID", gt=0)
    title: str = Field(..., min_length=1, description="Movie title")
    overview: Optional[str] = Field(None, description="Movie overview/description")
    release_date: Optional[str] = Field(None, description="Release date in YYYY-MM-DD format")
    vote_count: int = Field(0, ge=0, description="Number of votes")
    vote_average: float = Field(0.0, ge=0.0, le=10.0, description="Average vote rating")
    popularity: float = Field(0.0, ge=0.0, description="Popularity score")
    poster_path: Optional[str] = Field(None, description="Poster image path")
    backdrop_path: Optional[str] = Field(None, description="Backdrop image path")
    adult: bool = Field(False, description="Adult content flag")
    original_language: Optional[str] = Field(None, description="Original language code")
    original_title: Optional[str] = Field(None, description="Original title")
    video: bool = Field(False, description="Video flag")
    genre_ids: Optional[List[int]] = Field(None, description="List of genre IDs")

    # Extended fields (from detailed movie endpoint)
    genres: Optional[List[Genre]] = Field(None, description="List of genre objects")
    keywords: Optional[List[Keyword]] = Field(None, description="List of keyword objects")
    runtime: Optional[int] = Field(None, ge=0, description="Runtime in minutes")
    status: Optional[str] = Field(None, description="Movie status")
    tagline: Optional[str] = Field(None, description="Movie tagline")
    budget: Optional[int] = Field(None, ge=0, description="Budget in USD")
    revenue: Optional[int] = Field(None, ge=0, description="Revenue in USD")
    homepage: Optional[str] = Field(None, description="Homepage URL")
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    production_companies: Optional[List[Dict[str, Any]]] = Field(
        None, description="Production companies"
    )
    production_countries: Optional[List[Dict[str, Any]]] = Field(
        None, description="Production countries"
    )
    spoken_languages: Optional[List[Dict[str, Any]]] = Field(
        None, description="Spoken languages"
    )

    @field_validator("release_date")
    @classmethod
    def validate_release_date(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate release date format.

        Args:
            v: Release date string

        Returns:
            Validated release date string

        Raises:
            ValueError: If date format is invalid
        """
        if v is None or v == "":
            return None

        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            # Try to parse partial dates (YYYY-MM or YYYY)
            if len(v) == 7:  # YYYY-MM
                datetime.strptime(v, "%Y-%m")
                return v
            elif len(v) == 4:  # YYYY
                datetime.strptime(v, "%Y")
                return v
            else:
                raise ValueError(f"Invalid date format: {v}. Expected YYYY-MM-DD, YYYY-MM, or YYYY")

    @field_validator("poster_path", "backdrop_path")
    @classmethod
    def validate_image_path(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate image path format.

        Args:
            v: Image path string

        Returns:
            Validated image path or None
        """
        if v is None or v == "":
            return None
        # TMDB paths can be None or start with /
        if v.startswith("/"):
            return v
        return f"/{v}" if v else None

    @property
    def release_year(self) -> Optional[int]:
        """
        Extract release year from release_date.

        Returns:
            Release year or None
        """
        if not self.release_date:
            return None
        try:
            return int(self.release_date.split("-")[0])
        except (ValueError, IndexError):
            return None

    @property
    def full_poster_url(self) -> Optional[str]:
        """
        Get full poster URL.

        Returns:
            Full poster URL or None
        """
        if not self.poster_path:
            return None
        base_url = "https://image.tmdb.org/t/p/w500"
        return f"{base_url}{self.poster_path}"

    @property
    def full_backdrop_url(self) -> Optional[str]:
        """
        Get full backdrop URL.

        Returns:
            Full backdrop URL or None
        """
        if not self.backdrop_path:
            return None
        base_url = "https://image.tmdb.org/t/p/original"
        return f"{base_url}{self.backdrop_path}"

    @property
    def genre_names(self) -> List[str]:
        """
        Get list of genre names.

        Returns:
            List of genre names
        """
        if self.genres:
            return [genre.name for genre in self.genres]
        return []

    @property
    def keyword_names(self) -> List[str]:
        """
        Get list of keyword names.

        Returns:
            List of keyword names
        """
        if self.keywords:
            return [keyword.name for keyword in self.keywords]
        return []

    def normalize_title_for_sorting(self, ignore_articles: bool = False) -> str:
        """
        Normalize title for sorting purposes.

        Args:
            ignore_articles: If True, ignore articles (A, An, The) at the beginning

        Returns:
            Normalized title
        """
        title = self.title.strip()
        if ignore_articles:
            pattern = r"^(The|A|An)\s+(.+)$"
            match = re.match(pattern, title, re.IGNORECASE)
            if match:
                return match.group(2).strip()
        return title

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class MovieSearchResult(BaseModel):
    """
    Movie search result model for paginated search results.
    """

    page: int = Field(..., ge=1, description="Current page number")
    results: List[Movie] = Field(..., description="List of movies")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    total_results: int = Field(..., ge=0, description="Total number of results")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class SimilarMovie(BaseModel):
    """
    Similar movie model with similarity metadata.
    Extends Movie with similarity information.
    """

    movie: Movie = Field(..., description="Movie object")
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Similarity score")
    similarity_reason: Optional[str] = Field(None, description="Reason for similarity")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


def movie_from_tmdb_response(data: Union[Dict[str, Any], Mapping[str, Any]]) -> Movie:
    """
    Create a Movie model from TMDB API response.

    Args:
        data: Dictionary from TMDB API response

    Returns:
        Movie model instance

    Raises:
        ValueError: If required fields are missing or invalid
        TypeError: If data is not a valid mapping type
    """
    if not isinstance(data, dict):
        # Convert Mapping to dict for processing
        if isinstance(data, Mapping):
            data = dict(data)
        else:
            raise TypeError(f"Expected dict or Mapping, got {type(data)}")

    # Create a copy to avoid modifying the original
    movie_data: Dict[str, Any] = dict(data)

    # Handle keywords - TMDB returns keywords in different formats
    # From /movie/{id}/keywords endpoint: {"id": int, "keywords": [...]}
    # Keywords are typically not in the main movie response, so we handle them separately
    keywords: Optional[List[Keyword]] = None
    if "keywords" in movie_data:
        keywords_data: Any = movie_data.get("keywords")
        if keywords_data is not None:
            if isinstance(keywords_data, dict) and "keywords" in keywords_data:
                # Format from /movie/{id}/keywords endpoint
                keywords_list: Any = keywords_data.get("keywords")
                if isinstance(keywords_list, list):
                    keywords = [
                        Keyword(**kw)
                        for kw in keywords_list
                        if isinstance(kw, dict) and "id" in kw and "name" in kw
                    ]
            elif isinstance(keywords_data, list):
                # Direct list format
                keywords = [
                    Keyword(**kw)
                    for kw in keywords_data
                    if isinstance(kw, dict) and "id" in kw and "name" in kw
                ]
        # Remove from movie_data as it's handled separately
        movie_data.pop("keywords", None)

    # Handle genres
    genres: Optional[List[Genre]] = None
    genres_data: Any = movie_data.get("genres")
    if genres_data is not None and isinstance(genres_data, list):
        genres = [
            Genre(**genre)
            for genre in genres_data
            if isinstance(genre, dict) and "id" in genre and "name" in genre
        ]
        movie_data.pop("genres", None)

    # Add processed genres and keywords back
    if genres:
        movie_data["genres"] = genres
    if keywords:
        movie_data["keywords"] = keywords

    return Movie(**movie_data)


def validate_movie_list(movies: List[Mapping[str, Any]]) -> List[Movie]:
    """
    Validate and convert a list of movie dictionaries to Movie models.

    Args:
        movies: List of movie dictionaries or mappings

    Returns:
        List of validated Movie models

    Raises:
        TypeError: If movies is not a list
    """
    from src.utils.logger import get_logger

    if not isinstance(movies, list):
        raise TypeError(f"Expected list, got {type(movies)}")

    logger = get_logger("movie_models")
    validated_movies: List[Movie] = []

    for movie_data in movies:
        try:
            if not isinstance(movie_data, (dict, Mapping)):
                logger.warning(
                    f"Skipping invalid movie data type: {type(movie_data)}. Expected dict or Mapping."
                )
                continue

            movie: Movie = movie_from_tmdb_response(movie_data)
            validated_movies.append(movie)
        except (ValueError, TypeError) as e:
            # Log error but continue processing other movies
            movie_id: Union[int, str] = "unknown"
            if isinstance(movie_data, (dict, Mapping)):
                movie_id_raw: Any = movie_data.get("id", "unknown")
                movie_id = movie_id_raw if isinstance(movie_id_raw, (int, str)) else "unknown"
            logger.warning(f"Failed to validate movie {movie_id}: {e}")
            continue
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error validating movie: {e}", exc_info=True)
            continue

    return validated_movies

