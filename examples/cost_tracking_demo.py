"""
Cost Tracking Demonstration

This example demonstrates the comprehensive cost tracking features
implemented in Phase 2 of the SmartOrchestrator.

Features demonstrated:
1. Real-time token parsing and cost calculation
2. Per-task cost tracking
3. Cost accumulation across operations
4. Comprehensive cost summary export
5. Cost-based decision making
"""

import os
import json
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator


def demo_basic_tracking():
    """Demonstrate basic cost tracking"""
    print("=" * 60)
    print("DEMO 1: Basic Cost Tracking")
    print("=" * 60)

    # Initialize orchestrator
    orch = SmartOrchestrator(provider='anthropic', enable_fallback=False)

    # Example task
    task = "Create a REST API with authentication"
    capabilities = ["coding", "security", "testing"]
    context = {"complexity": "medium"}

    # Run planning (this will make an LLM call)
    print(f"\nAnalyzing task: {task}")
    plan = orch.analyze_and_plan(task, capabilities, context)

    # Get immediate cost feedback
    current_cost = orch.get_cost()
    print(f"Cost for planning: ${current_cost:.6f}")
    print(f"Tokens used: {orch.input_tokens + orch.output_tokens}")

    print("\n")


def demo_cost_summary():
    """Demonstrate comprehensive cost summary"""
    print("=" * 60)
    print("DEMO 2: Comprehensive Cost Summary")
    print("=" * 60)

    orch = SmartOrchestrator(provider='deepseek', enable_fallback=False)

    # Perform multiple operations
    operations = [
        ("analyze_and_plan", "Build web application"),
        ("analyze_and_plan", "Add user authentication"),
        ("validate_outputs", "Check code quality")
    ]

    for op_type, task_desc in operations:
        print(f"Executing: {op_type} - {task_desc}")
        try:
            if op_type == "analyze_and_plan":
                orch.analyze_and_plan(task_desc, ["coding"], {})
            # Add other operations as needed
        except Exception as e:
            print(f"  Error: {e}")

    # Get comprehensive summary
    summary = orch.get_cost_summary()

    print(f"\n{'─' * 60}")
    print("COST SUMMARY")
    print(f"{'─' * 60}")
    print(f"Total Cost: ${summary['total_cost']:.6f}")
    print(f"Tasks Executed: {summary['task_count']}")
    print(f"Average Cost per Task: ${summary['average_cost']:.6f}")

    print(f"\n{'─' * 60}")
    print("COSTS BY OPERATION")
    print(f"{'─' * 60}")
    for operation, data in summary['by_operation'].items():
        print(f"{operation}:")
        print(f"  Count: {data['count']}")
        print(f"  Total: ${data['total_cost']:.6f}")
        print(f"  Average: ${data['avg_cost']:.6f}")
        print(f"  Avg Latency: {data['avg_latency_ms']:.2f}ms")

    print(f"\n{'─' * 60}")
    print("EFFICIENCY METRICS")
    print(f"{'─' * 60}")
    metrics = summary['efficiency_metrics']
    print(f"Cost per 1K tokens: ${metrics['cost_per_1k_tokens']:.6f}")
    print(f"Avg tokens per task: {metrics['avg_tokens_per_task']:.2f}")
    print(f"Input/Output ratio: {metrics['input_output_ratio']:.2f}")
    print(f"Total tokens: {metrics['total_tokens']}")

    print("\n")


def demo_provider_comparison():
    """Compare costs across different providers"""
    print("=" * 60)
    print("DEMO 3: Provider Cost Comparison")
    print("=" * 60)

    providers = ['deepseek', 'gpt-mini', 'anthropic']
    task = "Write a Python function to implement binary search"
    results = {}

    for provider in providers:
        print(f"\nTesting {provider}...")
        try:
            orch = SmartOrchestrator(provider=provider, enable_fallback=False)
            orch.analyze_and_plan(task, ["coding"], {})

            results[provider] = {
                'cost': orch.get_cost(),
                'tokens': orch.input_tokens + orch.output_tokens,
                'input_tokens': orch.input_tokens,
                'output_tokens': orch.output_tokens
            }
            print(f"  Cost: ${results[provider]['cost']:.6f}")
            print(f"  Tokens: {results[provider]['tokens']}")
        except Exception as e:
            print(f"  Error: {e}")
            results[provider] = {'cost': float('inf'), 'tokens': 0}

    # Find best option
    valid_results = {k: v for k, v in results.items() if v['cost'] != float('inf')}
    if valid_results:
        cheapest = min(valid_results.items(), key=lambda x: x[1]['cost'])
        fastest = min(valid_results.items(), key=lambda x: x[1]['tokens'])

        print(f"\n{'─' * 60}")
        print("RESULTS")
        print(f"{'─' * 60}")
        print(f"Cheapest: {cheapest[0]} at ${cheapest[1]['cost']:.6f}")
        print(f"Most efficient: {fastest[0]} with {fastest[1]['tokens']} tokens")

    print("\n")


def demo_budget_constraint():
    """Demonstrate budget-constrained execution"""
    print("=" * 60)
    print("DEMO 4: Budget-Constrained Execution")
    print("=" * 60)

    max_budget = 0.01  # $0.01 budget
    orch = SmartOrchestrator(provider='deepseek', enable_fallback=False)

    print(f"Budget limit: ${max_budget:.6f}\n")

    tasks = [
        "Design database schema",
        "Implement API endpoints",
        "Add error handling",
        "Write unit tests"
    ]

    for i, task in enumerate(tasks, 1):
        initial_cost = orch.get_cost()
        remaining = max_budget - initial_cost

        if remaining <= 0:
            print(f"\nBudget exhausted after {i-1} tasks!")
            break

        print(f"\nTask {i}: {task}")
        print(f"  Remaining budget: ${remaining:.6f}")

        try:
            orch.analyze_and_plan(task, ["coding"], {})
            task_cost = orch.get_cost() - initial_cost
            print(f"  Task cost: ${task_cost:.6f}")
            print(f"  Total spent: ${orch.get_cost():.6f}")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n{'─' * 60}")
    print(f"Final cost: ${orch.get_cost():.6f} / ${max_budget:.6f}")
    print(f"Budget usage: {(orch.get_cost() / max_budget * 100):.1f}%")

    print("\n")


def demo_export_cost_data():
    """Demonstrate exporting cost data"""
    print("=" * 60)
    print("DEMO 5: Export Cost Data")
    print("=" * 60)

    orch = SmartOrchestrator(provider='anthropic', enable_fallback=False)

    # Generate some activity
    tasks = [
        "Implement user registration",
        "Add password hashing",
        "Create login endpoint"
    ]

    for task in tasks:
        try:
            orch.analyze_and_plan(task, ["coding", "security"], {})
        except Exception as e:
            print(f"Error: {e}")

    # Export to JSON
    summary = orch.get_cost_summary()
    output_file = "/tmp/cost_report.json"

    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nCost report exported to: {output_file}")
    print(f"Total cost: ${summary['total_cost']:.6f}")
    print(f"Tasks tracked: {summary['task_count']}")

    # Display sample task data
    print(f"\n{'─' * 60}")
    print("SAMPLE TASK DATA")
    print(f"{'─' * 60}")
    if summary['tasks']:
        task = summary['tasks'][0]
        print(f"Provider: {task['provider']}")
        print(f"Model: {task['model']}")
        print(f"Operation: {task['operation']}")
        print(f"Input tokens: {task['input_tokens']}")
        print(f"Output tokens: {task['output_tokens']}")
        print(f"Cost: ${task['total_cost']:.6f}")
        print(f"Latency: {task['latency_ms']:.2f}ms")

    print("\n")


def demo_operation_analysis():
    """Analyze which operations are most expensive"""
    print("=" * 60)
    print("DEMO 6: Operation Performance Analysis")
    print("=" * 60)

    orch = SmartOrchestrator(provider='anthropic', enable_fallback=False)

    # Simulate various operations
    operations = {
        'analyze_and_plan': 3,
        'assign_workers': 2,
        'validate_outputs': 4,
        'generate_specs': 2
    }

    print("Simulating operations...\n")
    for op_type, count in operations.items():
        for i in range(count):
            print(f"  {op_type} #{i+1}")
            # In real usage, call appropriate methods
            # For demo, we just track
            orch._set_operation(op_type)
            # Simulate with mock usage
            orch._track_usage(1000 + i * 100, 500 + i * 50)

    # Analyze results
    summary = orch.get_cost_summary()
    by_op = summary['by_operation']

    # Sort by total cost
    sorted_ops = sorted(by_op.items(), key=lambda x: x[1]['total_cost'], reverse=True)

    print(f"\n{'─' * 60}")
    print("OPERATIONS RANKED BY COST")
    print(f"{'─' * 60}")
    for rank, (op_name, op_data) in enumerate(sorted_ops, 1):
        print(f"{rank}. {op_name}")
        print(f"   Total: ${op_data['total_cost']:.6f}")
        print(f"   Count: {op_data['count']}")
        print(f"   Avg: ${op_data['avg_cost']:.6f}")
        print(f"   Tokens: {op_data['total_tokens']}")
        print(f"   Latency: {op_data['avg_latency_ms']:.2f}ms")
        print()

    print(f"Total cost: ${summary['total_cost']:.6f}")
    print(f"Most expensive: {sorted_ops[0][0]} (${sorted_ops[0][1]['total_cost']:.6f})")

    print("\n")


def main():
    """Run all demonstrations"""
    print("\n")
    print("=" * 60)
    print("COST TRACKING DEMONSTRATION")
    print("Phase 2: Token Usage Tracking")
    print("=" * 60)
    print("\n")

    # Check for API keys
    required_keys = {
        'ANTHROPIC_API_KEY': 'Anthropic',
        'OPENROUTER_API_KEY': 'OpenRouter (DeepSeek)',
        'OPENAI_API_KEY': 'OpenAI (GPT-Mini)'
    }

    missing_keys = []
    for key, name in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"  - {key} ({name})")

    if missing_keys:
        print("WARNING: Missing API keys:")
        print("\n".join(missing_keys))
        print("\nSome demos may fail. Set these in your .env file.")
        print("=" * 60)
        print("\n")

    # Run demos
    try:
        demo_basic_tracking()
    except Exception as e:
        print(f"Demo 1 failed: {e}\n")

    try:
        demo_cost_summary()
    except Exception as e:
        print(f"Demo 2 failed: {e}\n")

    try:
        demo_provider_comparison()
    except Exception as e:
        print(f"Demo 3 failed: {e}\n")

    try:
        demo_budget_constraint()
    except Exception as e:
        print(f"Demo 4 failed: {e}\n")

    try:
        demo_export_cost_data()
    except Exception as e:
        print(f"Demo 5 failed: {e}\n")

    try:
        demo_operation_analysis()
    except Exception as e:
        print(f"Demo 6 failed: {e}\n")

    print("=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - docs/COST_TRACKING.md")
    print("  - tests/test_token_tracking.py")
    print("\n")


if __name__ == "__main__":
    main()
