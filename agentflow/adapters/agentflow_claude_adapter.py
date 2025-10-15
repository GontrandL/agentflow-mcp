#!/usr/bin/env python3
"""
AgentFlow Claude API Adapter
Permet d'utiliser Claude (Anthropic) comme backend pour AgentFlow
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClaudeLLMEngine:
    """
    Adapter pour utiliser Claude avec AgentFlow
    Compatible avec l'interface AgentFlow LLM engine
    """

    def __init__(self, model="claude-3-5-sonnet-20241022", api_key=None):
        """
        Initialize Claude LLM Engine

        Args:
            model: Claude model name (default: claude-3-5-sonnet)
            api_key: Anthropic API key (if not in env)
        """
        self.model = model
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Please set it in .env file or pass as parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        print(f"✅ Claude LLM Engine initialized with model: {self.model}")

    def generate(self, prompt, max_tokens=4096, temperature=0.7, **kwargs):
        """
        Generate completion using Claude

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            print(f"❌ Error calling Claude API: {e}")
            raise

    def chat(self, messages, max_tokens=4096, temperature=0.7, **kwargs):
        """
        Chat completion using Claude

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            print(f"❌ Error in chat: {e}")
            raise


def test_claude_engine():
    """
    Test simple du Claude engine
    """
    print("\n🧪 Testing Claude LLM Engine...")
    print("━" * 50)

    # Initialize engine
    engine = ClaudeLLMEngine()

    # Test 1: Simple generation
    print("\n📝 Test 1: Simple Generation")
    response = engine.generate("What is 2+2? Answer in one word.", max_tokens=100)
    print(f"Response: {response}")

    # Test 2: Chat format
    print("\n💬 Test 2: Chat Format")
    messages = [
        {"role": "user", "content": "What is the capital of France? Answer in one word."}
    ]
    response = engine.chat(messages, max_tokens=100)
    print(f"Response: {response}")

    print("\n✅ All tests passed!")
    print("━" * 50)


if __name__ == "__main__":
    test_claude_engine()
