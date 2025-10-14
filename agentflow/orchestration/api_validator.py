"""
API Validator - Pre-flight validation of API keys and models

Prevents worker crashes by validating:
1. API key format and presence
2. API connectivity with minimal call
3. Model availability
4. Fallback chain validity

This is the DEFINITIVE solution to recurring worker configuration issues.
"""

import os
import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of API validation"""
    valid: bool
    provider: str
    model: Optional[str] = None
    error: Optional[str] = None
    tested: bool = False  # Whether connectivity was tested


class APIValidator:
    """
    Pre-flight validator for API keys and models

    Usage:
        validator = APIValidator()
        result = validator.validate_provider('deepseek')
        if result.valid:
            # Safe to use
        else:
            # Handle error: result.error
    """

    # Valid API key patterns
    KEY_PATTERNS = {
        'openrouter': r'^sk-or-v1-[a-f0-9]{64}$',
        'anthropic': r'^sk-ant-api\d+-[\w-]+$',
        'openai': r'^sk-[a-zA-Z0-9]{48}$',
        'deepseek': r'^sk-[a-f0-9]{32}$',  # DeepSeek direct API
    }

    # Invalid placeholder values
    INVALID_VALUES = [
        'CHANGE_ME',
        'your-key-here',
        'your-api-key-here',
        'YOUR_API_KEY',
        'xxx',
        'test',
        '',
        None
    ]

    def __init__(self, test_connectivity: bool = True):
        """
        Initialize validator

        Args:
            test_connectivity: Whether to test API connectivity (adds ~1 second per provider)
        """
        self.test_connectivity = test_connectivity

    def validate_provider(self, provider: str, api_key: Optional[str] = None) -> ValidationResult:
        """
        Validate provider configuration

        Args:
            provider: Provider name (deepseek, anthropic, gpt-mini, grok-fast)
            api_key: Optional API key (will read from env if not provided)

        Returns:
            ValidationResult with details
        """
        # Map provider to key source
        key_sources = {
            'deepseek': ['DEEPSEEK_API_KEY', 'OPENROUTER_API_KEY'],
            'anthropic': ['ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY'],
            'gpt-mini': ['OPENAI_API_KEY', 'OPENROUTER_API_KEY'],
            'grok-fast': ['GROK_API_KEY', 'OPENROUTER_API_KEY'],
        }

        if provider not in key_sources:
            return ValidationResult(
                valid=False,
                provider=provider,
                error=f"Unknown provider: {provider}"
            )

        # Get API key
        if api_key is None:
            for env_var in key_sources[provider]:
                api_key = os.getenv(env_var)
                if api_key:
                    logger.debug(f"Found API key in {env_var}")
                    break

        if not api_key:
            return ValidationResult(
                valid=False,
                provider=provider,
                error=f"No API key found for {provider}. Checked: {', '.join(key_sources[provider])}"
            )

        # Check for invalid placeholders
        if api_key in self.INVALID_VALUES:
            return ValidationResult(
                valid=False,
                provider=provider,
                error=f"API key is placeholder value: {api_key}"
            )

        # Validate key format
        format_valid = self._validate_key_format(provider, api_key)
        if not format_valid:
            return ValidationResult(
                valid=False,
                provider=provider,
                error=f"API key format invalid for {provider}"
            )

        # Test connectivity if enabled
        if self.test_connectivity:
            connectivity_valid, error = self._test_connectivity(provider, api_key)
            if not connectivity_valid:
                return ValidationResult(
                    valid=False,
                    provider=provider,
                    error=error,
                    tested=True
                )
            return ValidationResult(valid=True, provider=provider, tested=True)

        return ValidationResult(valid=True, provider=provider, tested=False)

    def validate_fallback_chain(self, providers: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate fallback chain and return valid providers

        Args:
            providers: List of provider names in order

        Returns:
            Tuple of (valid_providers, errors)
        """
        valid = []
        errors = []

        for provider in providers:
            result = self.validate_provider(provider)
            if result.valid:
                valid.append(provider)
                logger.info(f"✓ {provider}: Valid")
            else:
                errors.append(f"✗ {provider}: {result.error}")
                logger.warning(f"✗ {provider}: {result.error}")

        return valid, errors

    def _validate_key_format(self, provider: str, api_key: str) -> bool:
        """
        Validate API key format

        Args:
            provider: Provider name
            api_key: API key to validate

        Returns:
            True if format is valid
        """
        # OpenRouter keys work for multiple providers
        if api_key.startswith('sk-or-v1-'):
            pattern = self.KEY_PATTERNS['openrouter']
            return re.match(pattern, api_key) is not None

        # Provider-specific validation
        if provider == 'anthropic':
            pattern = self.KEY_PATTERNS['anthropic']
            return re.match(pattern, api_key) is not None
        elif provider in ['gpt-mini', 'openai']:
            pattern = self.KEY_PATTERNS['openai']
            return re.match(pattern, api_key) is not None
        elif provider == 'deepseek':
            # Could be OpenRouter or DeepSeek direct
            if api_key.startswith('sk-or-v1-'):
                return True  # Already validated above
            pattern = self.KEY_PATTERNS['deepseek']
            return re.match(pattern, api_key) is not None

        # Unknown provider - accept any non-empty key
        return len(api_key) > 10

    def _test_connectivity(self, provider: str, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Test API connectivity with minimal call

        Args:
            provider: Provider name
            api_key: API key

        Returns:
            Tuple of (success, error_message)
        """
        try:
            import openai

            # Use OpenRouter for most providers
            if provider in ['deepseek', 'anthropic']:
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                model = "deepseek/deepseek-chat" if provider == 'deepseek' else "anthropic/claude-sonnet-4-20250514"
            elif provider == 'grok-fast':
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.x.ai/v1"
                )
                model = "grok-2-1212"
            else:  # gpt-mini, openai
                client = openai.OpenAI(api_key=api_key)
                model = "gpt-4o-mini"

            # Minimal test call (1 token)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
                timeout=10
            )

            if response and response.choices:
                logger.info(f"✓ {provider}: Connectivity test passed")
                return True, None
            else:
                return False, f"Invalid response from {provider}"

        except Exception as e:
            error_msg = str(e)

            # Parse common errors
            if '401' in error_msg or 'Unauthorized' in error_msg:
                return False, f"Invalid API key (401 Unauthorized)"
            elif '403' in error_msg or 'Forbidden' in error_msg:
                return False, f"API key lacks permissions (403 Forbidden)"
            elif '429' in error_msg or 'rate limit' in error_msg.lower():
                # Rate limit is actually a sign the key works!
                logger.info(f"✓ {provider}: Key valid (rate limited)")
                return True, None
            elif 'timeout' in error_msg.lower():
                return False, f"Connection timeout"
            else:
                return False, f"API error: {error_msg[:100]}"

    def get_best_provider(self, preferred_order: Optional[List[str]] = None) -> Optional[str]:
        """
        Get best available provider from ordered list

        Args:
            preferred_order: Ordered list of preferred providers
                           (defaults to: deepseek, grok-fast, gpt-mini, anthropic)

        Returns:
            First valid provider or None
        """
        if preferred_order is None:
            preferred_order = ['deepseek', 'grok-fast', 'gpt-mini', 'anthropic']

        for provider in preferred_order:
            result = self.validate_provider(provider)
            if result.valid:
                logger.info(f"Selected provider: {provider}")
                return provider

        return None


def validate_before_delegation(provider: str, fallback_chain: Optional[List[str]] = None) -> Dict:
    """
    Convenience function for pre-flight validation before worker execution

    Args:
        provider: Primary provider to validate
        fallback_chain: Optional fallback providers to validate

    Returns:
        Dict with validation results

    Raises:
        RuntimeError: If no valid providers found
    """
    validator = APIValidator(test_connectivity=True)

    # Validate primary provider
    result = validator.validate_provider(provider)

    validation_data = {
        'primary_provider': provider,
        'primary_valid': result.valid,
        'primary_error': result.error,
        'fallback_chain': [],
        'valid_providers': []
    }

    if result.valid:
        validation_data['valid_providers'].append(provider)

    # Validate fallback chain
    if fallback_chain:
        valid_fallbacks, errors = validator.validate_fallback_chain(fallback_chain)
        validation_data['fallback_chain'] = fallback_chain
        validation_data['valid_providers'].extend(valid_fallbacks)
        validation_data['fallback_errors'] = errors

    # Fail if no valid providers
    if not validation_data['valid_providers']:
        error_msg = f"No valid API providers found!\n"
        error_msg += f"Primary ({provider}): {result.error}\n"
        if fallback_chain:
            error_msg += f"Fallbacks: {', '.join(errors)}"
        raise RuntimeError(error_msg)

    logger.info(f"✓ Validation complete: {len(validation_data['valid_providers'])} valid provider(s)")
    return validation_data
