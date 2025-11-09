"""
Configuration management module for loading environment variables and YAML config.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""

    def __init__(
        self,
        env_file: Optional[str] = None,
        config_file: Optional[str] = None,
    ):
        """
        Initialize configuration manager.

        Args:
            env_file: Path to .env file (defaults to .env in project root)
            config_file: Path to YAML config file (defaults to config/config.yaml)
        """
        # Determine project root (assuming this file is in src/utils/)
        self.project_root = Path(__file__).parent.parent.parent

        # Load environment variables
        if env_file is None:
            env_file = self.project_root / ".env"
        load_dotenv(env_file)

        # Load YAML configuration
        if config_file is None:
            config_file = self.project_root / "config" / "config.yaml"

        self.config_data = self._load_yaml(config_file)

    def _load_yaml(self, config_file: Path) -> Dict[str, Any]:
        """
        Load YAML configuration file.

        Args:
            config_file: Path to YAML config file

        Returns:
            Configuration dictionary
        """
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r") as f:
            return yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value from YAML config.

        Args:
            key: Dot-separated key path (e.g., 'api.timeout')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config_data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value
        """
        return os.getenv(key, default)

    def get_env_bool(self, key: str, default: bool = False) -> bool:
        """
        Get boolean environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Boolean value
        """
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def get_env_int(self, key: str, default: int = 0) -> int:
        """
        Get integer environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Integer value
        """
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default

    # TMDB API Configuration
    @property
    def tmdb_api_key(self) -> str:
        """Get TMDB API key from environment."""
        api_key = self.get_env("TMDB_API_KEY")
        if not api_key:
            raise ValueError("TMDB_API_KEY not found in environment variables")
        return api_key

    @property
    def tmdb_api_base_url(self) -> str:
        """Get TMDB API base URL."""
        return self.get_env("TMDB_API_BASE_URL", "https://api.themoviedb.org/3")

    # Application Configuration
    @property
    def environment(self) -> str:
        """Get application environment."""
        return self.get_env("ENVIRONMENT", "development")

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get_env("LOG_LEVEL", "INFO")

    # Caching Configuration
    @property
    def cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.get_env_bool("CACHE_ENABLED", True)

    @property
    def cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        return self.get_env_int("CACHE_TTL", 3600)

    @property
    def redis_host(self) -> str:
        """Get Redis host."""
        return self.get_env("REDIS_HOST", "localhost")

    @property
    def redis_port(self) -> int:
        """Get Redis port."""
        return self.get_env_int("REDIS_PORT", 6379)

    @property
    def redis_db(self) -> int:
        """Get Redis database number."""
        return self.get_env_int("REDIS_DB", 0)

    # Rate Limiting
    @property
    def rate_limit_requests(self) -> int:
        """Get rate limit requests per period."""
        return self.get_env_int("RATE_LIMIT_REQUESTS", 40)

    @property
    def rate_limit_period(self) -> int:
        """Get rate limit period in seconds."""
        return self.get_env_int("RATE_LIMIT_PERIOD", 10)


# Singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get singleton configuration instance.

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
