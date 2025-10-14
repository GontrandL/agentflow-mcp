"""
Test script for SmartOrchestrator Dashboard Integration

This script demonstrates how to use SmartOrchestrator with metrics tracking
and validates that the dashboard receives data correctly.
"""

import os
import sys
import time
from pathlib import Path

# Add agentflow to path
sys.path.insert(0, str(Path(__file__).parent / 'agentflow'))

from agentflow.orchestration import SmartOrchestratorWithLogging


def test_basic_orchestration():
    """Test basic orchestration with metrics tracking"""
    print("=" * 60)
    print("SmartOrchestrator Dashboard Integration Test")
    print("=" * 60)
    print()

    # Check for API keys
    api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("ERROR: No API key found!")
        print("Please set ANTHROPIC_API_KEY or OPENROUTER_API_KEY")
        return False

    print("Step 1: Initializing SmartOrchestrator with metrics...")
    try:
        orchestrator = SmartOrchestratorWithLogging(
            provider='anthropic',
            enable_metrics=True,
            enable_fallback=True,
            log_level='INFO'
        )
        print("✓ Orchestrator initialized successfully")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        return False

    # Test task
    task = """
    Create a simple Python function that calculates the factorial of a number.
    The function should:
    - Accept an integer parameter
    - Return the factorial
    - Handle edge cases (0, 1, negative numbers)
    """

    capabilities = [
        "Python code generation",
        "Error handling",
        "Mathematical operations"
    ]

    context = {
        "language": "Python",
        "complexity": "low",
        "style": "clean and well-documented"
    }

    print("Step 2: Analyzing task and creating plan...")
    try:
        start_time = time.time()
        plan = orchestrator.analyze_and_plan(task, capabilities, context)
        duration = time.time() - start_time

        print(f"✓ Plan created in {duration:.2f}s")
        print(f"  - Complexity: {plan.complexity}")
        print(f"  - Decompose: {plan.decompose}")
        print(f"  - Subtasks: {len(plan.subtasks)}")
        print()
    except Exception as e:
        print(f"✗ Failed to create plan: {e}")
        return False

    # Get and display metrics
    print("Step 3: Collecting metrics...")
    try:
        metrics = orchestrator.get_orchestrator_metrics()

        print("✓ Metrics collected:")
        print(f"  - Total tasks: {metrics.get('total_tasks', 0)}")
        print(f"  - Total cost: ${metrics.get('total_cost', 0):.6f}")
        print(f"  - Success rate: {metrics.get('success_rate', 0):.1f}%")
        print()

        # Display orchestrator-specific stats
        if 'orchestrator' in metrics:
            orch_stats = metrics['orchestrator']
            print("  Orchestrator Stats:")
            print(f"    - Provider: {orch_stats.get('provider', 'unknown')}")
            print(f"    - Model: {orch_stats.get('model', 'unknown')}")
            print(f"    - Input tokens: {orch_stats.get('input_tokens', 0):,}")
            print(f"    - Output tokens: {orch_stats.get('output_tokens', 0):,}")
            print(f"    - Cost: ${orch_stats.get('cost', 0):.6f}")
            print()
    except Exception as e:
        print(f"✗ Failed to collect metrics: {e}")
        return False

    # Save metrics to disk
    print("Step 4: Saving metrics to disk...")
    try:
        metrics_file = 'logs/orchestrator_metrics.json'
        orchestrator.save_metrics(metrics_file)
        print(f"✓ Metrics saved to {metrics_file}")
        print()
    except Exception as e:
        print(f"✗ Failed to save metrics: {e}")
        return False

    # Verify metrics file
    print("Step 5: Verifying metrics file...")
    try:
        metrics_path = Path(metrics_file)
        if metrics_path.exists():
            file_size = metrics_path.stat().st_size
            print(f"✓ Metrics file created ({file_size} bytes)")
            print()
        else:
            print("✗ Metrics file not found")
            return False
    except Exception as e:
        print(f"✗ Failed to verify metrics file: {e}")
        return False

    return True


def simulate_multiple_tasks():
    """Simulate multiple tasks to generate more metrics data"""
    print("=" * 60)
    print("Simulating Multiple Tasks (for richer dashboard data)")
    print("=" * 60)
    print()

    # Check for API keys
    api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("ERROR: No API key found!")
        return False

    print("Initializing orchestrator...")
    orchestrator = SmartOrchestratorWithLogging(
        provider='anthropic',
        enable_metrics=True,
        enable_fallback=True
    )
    print()

    # Simple tasks to execute
    tasks = [
        "Write a function to reverse a string",
        "Create a function to check if a number is prime",
        "Generate a function to calculate Fibonacci sequence"
    ]

    for i, task_description in enumerate(tasks, 1):
        print(f"Task {i}/{len(tasks)}: {task_description}")
        try:
            plan = orchestrator.analyze_and_plan(
                task_description,
                ["Python code generation"],
                {"complexity": "low"}
            )
            print(f"  ✓ Completed (complexity: {plan.complexity})")

            # Save metrics after each task
            orchestrator.save_metrics()
        except Exception as e:
            print(f"  ✗ Failed: {e}")

        print()

    # Final metrics summary
    print("=" * 60)
    print("Final Metrics Summary")
    print("=" * 60)

    metrics = orchestrator.get_orchestrator_metrics()
    print(f"Total tasks: {metrics.get('total_tasks', 0)}")
    print(f"Total cost: ${metrics.get('total_cost', 0):.6f}")
    print(f"Success rate: {metrics.get('success_rate', 0):.1f}%")
    print()

    if 'orchestrator' in metrics:
        orch_stats = metrics['orchestrator']
        print(f"Provider: {orch_stats.get('provider', 'unknown')}")
        print(f"Total tokens: {orch_stats.get('total_tokens', 0):,}")
        print(f"Average cost per task: ${metrics.get('total_cost', 0) / max(metrics.get('total_tasks', 1), 1):.6f}")
        print()

    print("✓ Metrics saved. Start dashboard to view:")
    print("  python dashboard_server.py")
    print()

    return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Test SmartOrchestrator Dashboard Integration'
    )
    parser.add_argument(
        '--mode',
        choices=['basic', 'multiple'],
        default='basic',
        help='Test mode: basic (1 task) or multiple (3 tasks)'
    )

    args = parser.parse_args()

    try:
        if args.mode == 'basic':
            success = test_basic_orchestration()
        else:
            success = simulate_multiple_tasks()

        if success:
            print("=" * 60)
            print("SUCCESS: Dashboard integration test passed!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Start the dashboard server:")
            print("   python dashboard_server.py")
            print()
            print("2. Open your browser:")
            print("   http://localhost:5000")
            print()
            print("3. You should see:")
            print("   - Total cost and task count")
            print("   - Cost charts")
            print("   - Recent tasks table")
            print()
            sys.exit(0)
        else:
            print("=" * 60)
            print("FAILED: Dashboard integration test failed")
            print("=" * 60)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
