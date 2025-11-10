"""
TMDB API Client for retrieving movie data from The Movie Database API.
This module only handles API communication and data retrieval.
"""

import time
from typing import Any, Dict, Optional

import requests

from src.utils.config import get_config
from src.utils.logger import get_logger


class TMDBClient:
    """
    TMDB API client for making requests to The Movie Database API.
    This class only handles API calls and returns raw or minimally processed data.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TMDB API client.

        Args:
            api_key: TMDB API key. If not provided, will be loaded from config.
        """
        self.config = get_config()
        self.logger = get_logger("tmdb_client")
        self.api_key = api_key or self.config.tmdb_api_key
        self.base_url = self.config.tmdb_api_base_url or "https://api.themoviedb.org/3"
        
        # Get configuration from config.yaml
        self.timeout = self.config.get("api.timeout", 30)
        self.max_retries = self.config.get("api.max_retries", 3)
        self.retry_delay = self.config.get("api.retry_delay", 1)
        self.language = self.config.get("data.language", "en-US")
        self.region = self.config.get("data.region", "US")
        
        # Setup session with authentication
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json;charset=utf-8"
        })
        
        self.logger.info("TMDB client initialized")

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to the TMDB API with retry logic and error handling.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            method: HTTP method (default: GET)

        Returns:
            JSON response data or None if request failed
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        params = params or {}
        
        # Add default parameters
        default_params = {
            "language": self.language,
            "region": self.region
        }
        params.update({k: v for k, v in default_params.items() if k not in params})
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Making {method} request to {url} with params: {params}")
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                self.logger.debug(f"Successfully received response from {endpoint}")
                return data
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    self.logger.error(f"Failed to retrieve data from {endpoint}: {str(e)}")
                    return None
        
        return None

    def get_movies_by_year(
        self,
        year: int,
        min_vote_count: Optional[int] = None,
        min_vote_average: Optional[float] = None,
        sort_by: str = "vote_count.desc",
        page: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve movies from a specific year using TMDB discover endpoint.

        Args:
            year: Release year
            min_vote_count: Minimum number of votes (from config if not provided)
            min_vote_average: Minimum vote average (from config if not provided)
            sort_by: Sort order (default: vote_count.desc)
            page: Page number to retrieve

        Returns:
            API response dictionary with results and pagination info, or None if failed
        """
        if min_vote_count is None:
            min_vote_count = self.config.get("recommendation.min_vote_count", 100)
        if min_vote_average is None:
            min_vote_average = self.config.get("recommendation.min_vote_average", 6.0)
        
        self.logger.info(
            f"Retrieving movies from year {year} "
            f"(min_votes: {min_vote_count}, min_rating: {min_vote_average}, page: {page})"
        )
        
        params = {
            "primary_release_year": year,
            "vote_count.gte": min_vote_count,
            "vote_average.gte": min_vote_average,
            "sort_by": sort_by,
            "page": page,
            "include_adult": False
        }
        
        data = self._make_request("discover/movie", params)
        return data


    def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a movie.

        Args:
            movie_id: TMDB movie ID

        Returns:
            Movie details dictionary or None if not found
        """
        self.logger.debug(f"Retrieving details for movie ID {movie_id}")
        data = self._make_request(f"movie/{movie_id}")
        return data

    def get_movie_keywords(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        Get keywords for a movie.

        Args:
            movie_id: TMDB movie ID

        Returns:
            Keywords response dictionary or None if not found
        """
        self.logger.debug(f"Retrieving keywords for movie ID {movie_id}")
        data = self._make_request(f"movie/{movie_id}/keywords")
        return data

    def get_similar_movies(
        self,
        movie_id: int,
        page: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Get similar movies based on TMDB's similarity algorithm.

        Args:
            movie_id: TMDB movie ID
            page: Page number to retrieve

        Returns:
            API response dictionary with similar movies, or None if failed
        """
        self.logger.debug(f"Getting similar movies for movie ID {movie_id}, page {page}")
        data = self._make_request(f"movie/{movie_id}/similar", params={"page": page})
        return data

    def get_movie_credits(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cast and crew information for a movie.

        Args:
            movie_id: TMDB movie ID

        Returns:
            Credits response dictionary or None if not found
        """
        self.logger.debug(f"Retrieving credits for movie ID {movie_id}")
        data = self._make_request(f"movie/{movie_id}/credits")
        return data

    def get_movie_reviews(self, movie_id: int, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get reviews for a movie.

        Args:
            movie_id: TMDB movie ID
            page: Page number to retrieve

        Returns:
            Reviews response dictionary or None if not found
        """
        self.logger.debug(f"Retrieving reviews for movie ID {movie_id}, page {page}")
        data = self._make_request(f"movie/{movie_id}/reviews", params={"page": page})
        return data

    def search_movies(
        self,
        query: str,
        page: int = 1,
        include_adult: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Search for movies by query string.

        Args:
            query: Search query string
            page: Page number to retrieve
            include_adult: Include adult content in results

        Returns:
            Search results dictionary or None if failed
        """
        self.logger.debug(f"Searching for movies with query: {query}")
        params = {
            "query": query,
            "page": page,
            "include_adult": include_adult
        }
        data = self._make_request("search/movie", params)
        return data
