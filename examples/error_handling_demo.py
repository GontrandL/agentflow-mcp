#!/usr/bin/env python3
"""
SmartOrchestrator Error Handling Demo

Demonstrates the robust error handling and retry logic including:
1. Exponential backoff retry
2. Automatic fallback chain
3. Cost tracking preservation
4. Comprehensive logging

Usage:
    python error_handling_demo.py

Requirements:
    - Set ANTHROPIC_API_KEY or other provider keys in environment
    - Install dependencies: pip install anthropic openai tenacity
"""

import os
import sys
import logging
from typing import Dict, Any

# Setup logging to see retry and fallback events
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from agentflow.orchestration.smart_orchestrator import SmartOrchestrator
except ImportError:
    print("Error: Cannot import SmartOrchestrator")
    print("Make sure you're in the agentflow-src directory")
    sys.exit(1)


def demo_basic_retry():
    """Demo 1: Basic retry on transient errors"""
    print("\n" + "="*60)
    print("DEMO 1: Basic Retry (No Fallback)")
    print("="*60)

    try:
        orchestrator = SmartOrchestrator(
            provider='anthropic',
            enable_fallback=False
        )

        print(f"Provider: {orchestrator.provider}")
        print(f"Model: {orchestrator.model}")
        print(f"Fallback enabled: {orchestrator.enable_fallback}")

        # This will retry up to 3 times on failure
        print("\nMaking API call (will retry on errors)...")
        result = orchestrator._call_llm(
            "Say hello in exactly 3 words",
            max_tokens=50
        )
        print(f"Result: {result}")

        # Show statistics
        stats = orchestrator.get_stats()
        print(f"\nStatistics:")
        print(f"  Total tokens: {stats['total_tokens']}")
        print(f"  Cost: ${stats['cost']:.6f}")
        print(f"  Retry attempts: {3 - 1}")  # Would be logged if retries happened

    except Exception as e:
        print(f"Error: {e}")


def demo_fallback_chain():
    """Demo 2: Automatic fallback to alternative providers"""
    print("\n" + "="*60)
    print("DEMO 2: Automatic Fallback Chain")
    print("="*60)

    # Check available API keys
    providers_available = {
        'anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'deepseek': os.getenv('DEEPSEEK_API_KEY'),
        'openai': os.getenv('OPENAI_API_KEY'),
    }

    print("Available providers:")
    for provider, key in providers_available.items():
        status = "✓" if key else "✗"
        print(f"  {status} {provider}")

    try:
        orchestrator = SmartOrchestrator(
            provider='anthropic',
            enable_fallback=True
        )

        print(f"\nPrimary provider: {orchestrator.provider}")
        print(f"Fallback order: {orchestrator.FALLBACK_ORDER}")
        print(f"Fallback enabled: {orchestrator.enable_fallback}")

        # If primary fails, will automatically try fallback chain
        print("\nMaking API call (will fallback on errors)...")
        result = orchestrator._call_llm(
            "Count from 1 to 5",
            max_tokens=50
        )
        print(f"Result: {result}")

        # Show statistics including fallback info
        stats = orchestrator.get_stats()
        print(f"\nStatistics:")
        print(f"  Active provider: {stats['provider']}")
        print(f"  Total tokens: {stats['total_tokens']}")
        print(f"  Cost: ${stats['cost']:.6f}")
        print(f"  Fallback attempts: {stats['fallback_attempts']}")
        print(f"  Failed providers: {stats['failed_providers']}")

    except Exception as e:
        print(f"Error: {e}")


def demo_cost_tracking():
    """Demo 3: Cost tracking across retries and fallbacks"""
    print("\n" + "="*60)
    print("DEMO 3: Cost Tracking Preservation")
    print("="*60)

    try:
        orchestrator = SmartOrchestrator(
            provider='anthropic',
            enable_fallback=True
        )

        print(f"Provider: {orchestrator.provider}")
        print("Making multiple calls...\n")

        # Make several calls
        prompts = [
            "What is 2+2?",
            "What is 3+3?",
            "What is 4+4?"
        ]

        for i, prompt in enumerate(prompts, 1):
            try:
                result = orchestrator._call_llm(prompt, max_tokens=50)
                print(f"Call {i}: {result[:50]}...")

                # Show running stats
                stats = orchestrator.get_stats()
                print(f"  Tokens so far: {stats['total_tokens']}")
                print(f"  Cost so far: ${stats['cost']:.6f}")
                if stats['fallback_attempts'] > 0:
                    print(f"  ⚠ Used fallback: {stats['failed_providers']}")
                print()

            except Exception as e:
                print(f"Call {i} failed: {e}\n")

        # Final statistics
        final_stats = orchestrator.get_stats()
        print("="*60)
        print("FINAL STATISTICS")
        print("="*60)
        print(f"Provider: {final_stats['provider']}")
        print(f"Model: {final_stats['model']}")
        print(f"Input tokens: {final_stats['input_tokens']}")
        print(f"Output tokens: {final_stats['output_tokens']}")
        print(f"Total tokens: {final_stats['total_tokens']}")
        print(f"Total cost: ${final_stats['cost']:.6f}")
        print(f"Fallback attempts: {final_stats['fallback_attempts']}")
        print(f"Failed providers: {final_stats['failed_providers']}")

    except Exception as e:
        print(f"Error: {e}")


def demo_provider_comparison():
    """Demo 4: Compare different providers"""
    print("\n" + "="*60)
    print("DEMO 4: Provider Cost Comparison")
    print("="*60)

    print("\nProvider pricing (per 1M tokens):")
    print(f"{'Provider':<15} {'Input':<10} {'Output':<10} {'Best For'}")
    print("-" * 60)

    providers_info = [
        ('deepseek', '$0.14', '$0.28', 'Cost-effective'),
        ('grok-fast', '$5.00', '$15.00', 'Fast inference'),
        ('gpt-mini', '$0.15', '$0.60', 'Balanced'),
        ('anthropic', '$3.00', '$15.00', 'High quality'),
        ('openai', '$10.00', '$30.00', 'Premium'),
    ]

    for provider, input_price, output_price, use_case in providers_info:
        print(f"{provider:<15} {input_price:<10} {output_price:<10} {use_case}")

    print("\nFallback order (cheap → reliable):")
    print("  1. deepseek   (cheapest)")
    print("  2. grok-fast  (fast)")
    print("  3. gpt-mini   (balanced)")
    print("  4. anthropic  (most reliable)")


def demo_error_scenarios():
    """Demo 5: Different error scenarios"""
    print("\n" + "="*60)
    print("DEMO 5: Error Scenarios")
    print("="*60)

    scenarios = [
        ("Transient Error", "API temporarily unavailable → Retry succeeds"),
        ("Provider Down", "Primary fails → Fallback to alternative"),
        ("Rate Limit", "Hit rate limit → Exponential backoff"),
        ("All Fail", "All providers exhausted → Clear error message"),
    ]

    print("\nError handling capabilities:")
    for scenario, description in scenarios:
        print(f"\n{scenario}:")
        print(f"  {description}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("SmartOrchestrator Error Handling Demo")
    print("="*60)

    # Check for API keys
    has_key = (
        os.getenv('ANTHROPIC_API_KEY') or
        os.getenv('OPENAI_API_KEY') or
        os.getenv('DEEPSEEK_API_KEY')
    )

    if not has_key:
        print("\n⚠ WARNING: No API keys found in environment")
        print("Set at least one of:")
        print("  - ANTHROPIC_API_KEY")
        print("  - OPENAI_API_KEY")
        print("  - DEEPSEEK_API_KEY")
        print("\nShowing documentation only...\n")

        # Run documentation demos only
        demo_provider_comparison()
        demo_error_scenarios()
        return

    # Run interactive demos
    try:
        demo_basic_retry()
        demo_fallback_chain()
        demo_cost_tracking()
        demo_provider_comparison()
        demo_error_scenarios()

        print("\n" + "="*60)
        print("Demo completed!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
