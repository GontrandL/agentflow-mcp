"""
Secret Manager - Secure Secret Handling

Provides secure access to secrets from environment variables,
with caching and validation.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SecretManager:
    """
    Secure secret management

    Features:
    - Environment variable access
    - Validation and error handling
    - Secret caching (in-memory only)
    - Clear logging (without exposing secrets)
    """

    def __init__(self, prefix: Optional[str] = None):
        """
        Initialize secret manager

        Args:
            prefix: Optional prefix for environment variables (e.g., 'APP_')
        """
        self.prefix = prefix or ''
        self._cache: Dict[str, str] = {}

    def get(
        self,
        key: str,
        required: bool = True,
        default: Optional[str] = None
    ) -> Optional[str]:
        """
        Get secret value

        Args:
            key: Secret key (without prefix)
            required: Whether secret is required
            default: Default value if not found

        Returns:
            Secret value or None

        Raises:
            ValueError: If secret required but not found
        """
        # Check cache first
        full_key = self._get_full_key(key)
        if full_key in self._cache:
            return self._cache[full_key]

        # Get from environment
        value = os.getenv(full_key, default)

        if value is None and required:
            raise ValueError(
                f"Required secret '{full_key}' not found in environment. "
                f"Please set environment variable."
            )

        # Cache if found
        if value is not None:
            self._cache[full_key] = value
            logger.debug(f"Secret '{full_key}' loaded successfully")

        return value

    def set(self, key: str, value: str):
        """
        Set secret value (in cache only, does not modify environment)

        Args:
            key: Secret key
            value: Secret value
        """
        full_key = self._get_full_key(key)
        self._cache[full_key] = value
        logger.debug(f"Secret '{full_key}' set in cache")

    def clear_cache(self):
        """Clear secret cache"""
        self._cache.clear()
        logger.debug("Secret cache cleared")

    def validate(self, keys: list) -> Dict[str, bool]:
        """
        Validate that required secrets are available

        Args:
            keys: List of required secret keys

        Returns:
            Dict mapping key -> is_available
        """
        results = {}
        for key in keys:
            full_key = self._get_full_key(key)
            results[full_key] = os.getenv(full_key) is not None
        return results

    def _get_full_key(self, key: str) -> str:
        """Get full key with prefix"""
        if self.prefix and not key.startswith(self.prefix):
            return f"{self.prefix}{key}"
        return key

    def get_config(self, **keys) -> Dict[str, Any]:
        """
        Get multiple secrets as config dict

        Usage:
            config = secrets.get_config(
                api_key='API_KEY',
                db_url='DATABASE_URL'
            )

        Args:
            **keys: Mapping of config_name -> env_var_name

        Returns:
            Configuration dictionary
        """
        config = {}
        for config_name, env_var in keys.items():
            value = self.get(env_var, required=False)
            if value is not None:
                config[config_name] = value
        return config
