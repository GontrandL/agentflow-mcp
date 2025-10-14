#!/usr/bin/env python3
"""
AgentFlow Universal LLM Adapter
Supporte: Claude, OpenRouter (gratuit!), LiteLLM (router universel)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UniversalLLMEngine:
    """
    Adapter universel pour AgentFlow
    Supporte:
    - OpenRouter (avec modèles gratuits!)
    - Claude API direct
    - LiteLLM (router pour tous les LLMs)
    - N'importe quel LLM compatible OpenAI API
    """

    def __init__(self, provider="openrouter", model=None, api_key=None):
        """
        Initialize Universal LLM Engine

        Args:
            provider: 'openrouter', 'claude', 'litellm', 'openai', etc.
            model: Model name (provider-specific)
            api_key: API key (if not in env)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()

        # Default models par provider
        self.default_models = {
            'openrouter': 'meta-llama/llama-3.2-3b-instruct:free',  # FREE!
            'claude': 'claude-3-5-sonnet-20241022',
            'openai': 'gpt-4o-mini',
            'litellm': 'gpt-4o-mini'
        }

        self.model = model or self.default_models.get(provider)

        self._initialize_client()

        print(f"✅ Universal LLM Engine initialized")
        print(f"   Provider: {self.provider}")
        print(f"   Model: {self.model}")
        print(f"   API Key: {'✓' if self.api_key else '✗'}")

    def _get_api_key(self):
        """Get API key based on provider"""
        key_mapping = {
            'openrouter': 'OPENROUTER_API_KEY',
            'claude': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'litellm': 'OPENAI_API_KEY'  # LiteLLM uses OpenAI format
        }

        env_var = key_mapping.get(self.provider)
        if env_var:
            return os.getenv(env_var)

        return None

    def _initialize_client(self):
        """Initialize the appropriate client"""
        if self.provider == 'openrouter':
            self._init_openrouter()
        elif self.provider == 'claude':
            self._init_claude()
        elif self.provider == 'litellm':
            self._init_litellm()
        else:
            # Default to OpenAI-compatible
            self._init_openai_compatible()

    def _init_openrouter(self):
        """Initialize OpenRouter client"""
        from openai import OpenAI

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

        # FREE models disponibles:
        # - meta-llama/llama-3.2-3b-instruct:free (3B, fast)
        # - meta-llama/llama-3.2-1b-instruct:free (1B, very fast)
        # - qwen/qwen-2-7b-instruct:free (7B, good quality)
        # - google/gemma-2-9b-it:free (9B, Google)

        print(f"\n💡 OpenRouter FREE models available:")
        print(f"   - meta-llama/llama-3.2-3b-instruct:free (3B, recommended)")
        print(f"   - meta-llama/llama-3.2-1b-instruct:free (1B, fastest)")
        print(f"   - qwen/qwen-2-7b-instruct:free (7B, best quality)")
        print(f"   - google/gemma-2-9b-it:free (9B, Google)")

    def _init_claude(self):
        """Initialize Claude client"""
        from anthropic import Anthropic
        self.client = Anthropic(api_key=self.api_key)

    def _init_litellm(self):
        """Initialize LiteLLM client"""
        import litellm
        litellm.set_verbose = False
        self.litellm = litellm

    def _init_openai_compatible(self):
        """Initialize OpenAI or compatible client"""
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt, max_tokens=4096, temperature=0.7, **kwargs):
        """
        Generate completion

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        try:
            if self.provider == 'claude':
                return self._generate_claude(prompt, max_tokens, temperature, **kwargs)
            elif self.provider == 'litellm':
                return self._generate_litellm(prompt, max_tokens, temperature, **kwargs)
            else:
                return self._generate_openai_compatible(prompt, max_tokens, temperature, **kwargs)

        except Exception as e:
            print(f"❌ Error generating: {e}")
            raise

    def _generate_openai_compatible(self, prompt, max_tokens, temperature, **kwargs):
        """Generate using OpenAI-compatible API (OpenRouter, OpenAI, etc.)"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content

    def _generate_claude(self, prompt, max_tokens, temperature, **kwargs):
        """Generate using Claude API"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _generate_litellm(self, prompt, max_tokens, temperature, **kwargs):
        """Generate using LiteLLM (router universel)"""
        response = self.litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content

    def chat(self, messages, max_tokens=4096, temperature=0.7, **kwargs):
        """
        Chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        try:
            if self.provider == 'claude':
                return self._chat_claude(messages, max_tokens, temperature, **kwargs)
            elif self.provider == 'litellm':
                return self._chat_litellm(messages, max_tokens, temperature, **kwargs)
            else:
                return self._chat_openai_compatible(messages, max_tokens, temperature, **kwargs)

        except Exception as e:
            print(f"❌ Error in chat: {e}")
            raise

    def _chat_openai_compatible(self, messages, max_tokens, temperature, **kwargs):
        """Chat using OpenAI-compatible API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content

    def _chat_claude(self, messages, max_tokens, temperature, **kwargs):
        """Chat using Claude API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages
        )
        return response.content[0].text

    def _chat_litellm(self, messages, max_tokens, temperature, **kwargs):
        """Chat using LiteLLM"""
        response = self.litellm.completion(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content


def test_engine(provider="openrouter", model=None):
    """
    Test du Universal Engine

    Usage:
        # OpenRouter (FREE!)
        python agentflow_universal_adapter.py openrouter

        # Claude
        python agentflow_universal_adapter.py claude

        # LiteLLM
        python agentflow_universal_adapter.py litellm
    """
    print("\n🧪 Testing Universal LLM Engine...")
    print("━" * 50)

    # Initialize engine
    engine = UniversalLLMEngine(provider=provider, model=model)

    # Test 1: Simple generation
    print("\n📝 Test 1: Simple Generation")
    print("Query: What is 2+2? Answer briefly.")
    response = engine.generate(
        "What is 2+2? Answer in one short sentence.",
        max_tokens=100
    )
    print(f"✅ Response: {response}")

    # Test 2: Chat format
    print("\n💬 Test 2: Chat Format")
    print("Query: Capital of France?")
    messages = [
        {"role": "user", "content": "What is the capital of France? Answer in one word."}
    ]
    response = engine.chat(messages, max_tokens=100)
    print(f"✅ Response: {response}")

    print("\n✅ All tests passed!")
    print("━" * 50)

    return engine


if __name__ == "__main__":
    import sys

    provider = sys.argv[1] if len(sys.argv) > 1 else "openrouter"
    model = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\n🚀 Testing with provider: {provider}")
    if model:
        print(f"   Model: {model}")

    test_engine(provider, model)
