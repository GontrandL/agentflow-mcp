"""
Example: Generate GitHub API Integration

Demonstrates how to use the Integration Framework to generate
a production-ready GitHub API integration.

Expected results:
- Cost: <$0.02
- Time: ~12 seconds generation + 4 minutes review
- Quality: 95%+ validation score
- Output: Complete integration package with adapter, tests, docs
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentflow.orchestration import SmartOrchestrator
from agentflow.orchestration.integration_builder import IntegrationBuilder


def main():
    """Generate GitHub API integration"""

    print("=" * 60)
    print("GitHub API Integration Generation")
    print("=" * 60)
    print()

    # 1. Initialize SmartOrchestrator
    print("[1/5] Initializing SmartOrchestrator...")
    print("      Provider: deepseek (cheapest)")
    print("      Fallback: enabled")
    print("      Model selection: enabled")
    print()

    try:
        orchestrator = SmartOrchestrator(
            provider='deepseek',
            enable_fallback=True,
            enable_model_selection=True
        )
        print("      Status: Ready")
    except Exception as e:
        print(f"      Error: {e}")
        print("      Note: Set DEEPSEEK_API_KEY or OPENROUTER_API_KEY environment variable")
        return

    print()

    # 2. Create IntegrationBuilder
    print("[2/5] Creating IntegrationBuilder...")
    builder = IntegrationBuilder(orchestrator)
    print("      Status: Ready")
    print()

    # 3. Define requirements
    print("[3/5] Defining integration requirements...")
    requirements = {
        'base_url': 'https://api.github.com',
        'auth_type': 'bearer',
        'rate_limit': 5000,  # GitHub rate limit
        'endpoints': [
            {'method': 'GET', 'path': '/user'},
            {'method': 'GET', 'path': '/repos/{owner}/{repo}'},
            {'method': 'GET', 'path': '/repos/{owner}/{repo}/issues'},
            {'method': 'POST', 'path': '/repos/{owner}/{repo}/issues'},
            {'method': 'GET', 'path': '/search/repositories'}
        ],
        'features': ['retry', 'rate_limiting', 'metrics', 'caching']
    }

    print("      Base URL:", requirements['base_url'])
    print("      Auth Type:", requirements['auth_type'])
    print("      Rate Limit:", requirements['rate_limit'], "requests/hour")
    print("      Endpoints:", len(requirements['endpoints']))
    print()

    # 4. Generate integration
    print("[4/5] Generating integration...")
    print("      This will take ~12 seconds...")
    print()

    try:
        package = builder.build_integration(
            service_name='GitHub',
            integration_type='api',
            requirements=requirements
        )

        print("      Status: Complete!")
        print()

        # Display metrics
        metrics = package.metadata['build_metrics']
        print("      Build Metrics:")
        print(f"        Duration: {metrics['duration_seconds']:.2f} seconds")
        print(f"        Cost: ${metrics['total_cost']:.6f}")
        print(f"        Validation Score: {metrics['validation_score']:.1f}/100")
        print(f"        Subtasks: {metrics['subtask_count']}")
        print()

        # Display cost breakdown
        orchestrator_stats = package.metadata['orchestrator_stats']
        print("      Cost Breakdown:")
        print(f"        Provider: {orchestrator_stats['provider']}")
        print(f"        Model: {orchestrator_stats['model']}")
        print(f"        Input tokens: {orchestrator_stats['input_tokens']:,}")
        print(f"        Output tokens: {orchestrator_stats['output_tokens']:,}")
        print(f"        Total cost: ${orchestrator_stats['cost']:.6f}")
        print()

    except Exception as e:
        print(f"      Error: {e}")
        return

    # 5. Save integration package
    print("[5/5] Saving integration package...")
    output_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        'integrations',
        'github'
    )

    try:
        package.save_to_directory(output_dir)
        print(f"      Saved to: {output_dir}")
        print()
        print("      Generated files:")
        print(f"        - github_adapter.py")
        print(f"        - test_github_adapter.py")
        print(f"        - GITHUB_INTEGRATION.md")
        print(f"        - config.yaml")
        print(f"        - examples.py")
        print(f"        - metadata.json")
        print()

    except Exception as e:
        print(f"      Error saving: {e}")

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print(f"Service: GitHub")
    print(f"Pattern: {package.pattern_type}")
    print(f"Cost: ${metrics['total_cost']:.6f} (Target: <$0.02)")
    print(f"Quality: {metrics['validation_score']:.0f}% (Target: >95%)")
    print(f"Time: {metrics['duration_seconds']:.1f}s generation + ~4 min review")
    print()
    print("ROI vs Manual Development:")
    print(f"  Manual: 23 hours @ $80/hour = $1,840")
    print(f"  Framework: ${metrics['total_cost']:.6f}")
    print(f"  ROI: {1840 / metrics['total_cost']:.0f}x")
    print()
    print("Next steps:")
    print("  1. Review generated code")
    print("  2. Set GITHUB_API_KEY environment variable")
    print("  3. Run tests: pytest integrations/github/test_github_adapter.py")
    print("  4. Deploy to production")
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
