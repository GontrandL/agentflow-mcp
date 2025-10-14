# Cost Tracking Documentation

## Overview

Phase 2 of the SmartOrchestrator implements comprehensive real-time cost tracking that monitors token usage and calculates actual costs per task across all operations.

## Features

### 1. Real-Time Token Parsing
- Automatically extracts token usage from OpenRouter/OpenAI/Anthropic API responses
- Tracks both input (prompt) and output (completion) tokens
- Works across all supported providers

### 2. Accurate Cost Calculation
- Uses provider-specific pricing (per 1M tokens)
- Calculates costs for each individual operation
- Maintains cumulative cost totals
- Accuracy validated to within 5% tolerance

### 3. Per-Task Tracking
- Records detailed metrics for each LLM call:
  - Timestamp
  - Provider and model used
  - Operation type (analyze_and_plan, validate_outputs, etc.)
  - Input/output token counts
  - Individual and total costs
  - API call latency

### 4. Comprehensive Cost Analytics
- Costs grouped by provider
- Costs grouped by operation type
- Efficiency metrics (cost per 1K tokens, etc.)
- Average latency tracking
- Detailed task-level breakdowns

## Provider Pricing

Current pricing per 1M tokens (as configured):

| Provider | Input Cost | Output Cost |
|----------|-----------|-------------|
| DeepSeek | $0.14 | $0.28 |
| GPT-Mini | $0.15 | $0.60 |
| Anthropic | $3.00 | $15.00 |
| Grok-Fast | $5.00 | $15.00 |

## Usage

### Basic Usage

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# Initialize orchestrator
orch = SmartOrchestrator(provider='anthropic')

# Perform operations (cost tracking is automatic)
plan = orch.analyze_and_plan(
    task="Build REST API",
    capabilities=["coding"],
    context={}
)

# Get current total cost
total_cost = orch.get_cost()
print(f"Total cost so far: ${total_cost:.6f}")
```

### Getting Cost Summary

```python
# Get comprehensive cost breakdown
summary = orch.get_cost_summary()

print(f"Total cost: ${summary['total_cost']}")
print(f"Tasks executed: {summary['task_count']}")
print(f"Average cost per task: ${summary['average_cost']}")

# View costs by provider
for provider, data in summary['by_provider'].items():
    print(f"{provider}: ${data['total_cost']} ({data['task_count']} tasks)")

# View costs by operation
for operation, data in summary['by_operation'].items():
    print(f"{operation}: ${data['total_cost']} (avg: ${data['avg_cost']})")
```

### Cost Summary Structure

The `get_cost_summary()` method returns a dictionary with the following structure:

```python
{
    'total_cost': 0.012345,           # Total cost across all operations
    'task_count': 5,                  # Number of tasks executed
    'average_cost': 0.002469,         # Average cost per task

    'by_provider': {                  # Costs grouped by provider
        'anthropic': {
            'total_cost': 0.012345,
            'input_tokens': 10000,
            'output_tokens': 5000,
            'task_count': 5,
            'operations': {            # Operations breakdown
                'analyze_and_plan': {
                    'count': 2,
                    'total_cost': 0.005000,
                    'avg_latency_ms': 1234.56
                }
            }
        }
    },

    'by_operation': {                 # Costs grouped by operation type
        'analyze_and_plan': {
            'count': 2,
            'total_cost': 0.005000,
            'avg_cost': 0.002500,
            'total_tokens': 6000,
            'avg_latency_ms': 1234.56
        }
    },

    'efficiency_metrics': {           # Efficiency indicators
        'cost_per_1k_tokens': 0.000823,
        'avg_tokens_per_task': 3000.0,
        'input_output_ratio': 2.0,
        'total_input_tokens': 10000,
        'total_output_tokens': 5000,
        'total_tokens': 15000
    },

    'tasks': [                        # Individual task details
        {
            'timestamp': 1234567890.123,
            'provider': 'anthropic',
            'model': 'claude-sonnet-4-5-20250929',
            'operation': 'analyze_and_plan',
            'input_tokens': 2000,
            'output_tokens': 1000,
            'input_cost': 0.006000,
            'output_cost': 0.015000,
            'total_cost': 0.021000,
            'latency_ms': 1234.56
        }
    ]
}
```

### Exporting Cost Data

```python
import json

# Export to JSON file
summary = orch.get_cost_summary()
with open('cost_report.json', 'w') as f:
    json.dump(summary, f, indent=2)

# Export to CSV (tasks only)
import csv

with open('tasks.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=summary['tasks'][0].keys())
    writer.writeheader()
    writer.writerows(summary['tasks'])
```

### Resetting Statistics

```python
# Reset all tracking data
orch.reset_stats()

# Start fresh tracking
total_cost = orch.get_cost()  # Returns 0.0
```

## Advanced Usage

### Cost-Based Decision Making

```python
def run_with_budget(orch, task, max_budget=0.10):
    """Run orchestration with budget constraint"""

    # Track initial cost
    initial_cost = orch.get_cost()

    # Run planning
    plan = orch.analyze_and_plan(task, capabilities=[], context={})

    # Check if we're within budget
    current_cost = orch.get_cost()
    cost_so_far = current_cost - initial_cost

    if cost_so_far > max_budget:
        raise ValueError(f"Budget exceeded: ${cost_so_far} > ${max_budget}")

    print(f"Planning cost: ${cost_so_far:.6f}")
    print(f"Remaining budget: ${max_budget - cost_so_far:.6f}")

    return plan
```

### Provider Cost Comparison

```python
def compare_provider_costs():
    """Compare costs across different providers"""

    providers = ['deepseek', 'gpt-mini', 'anthropic']
    task = "Write a Python function to sort a list"

    results = {}

    for provider in providers:
        orch = SmartOrchestrator(provider=provider)

        # Run same task
        orch.analyze_and_plan(task, capabilities=['coding'], context={})

        # Record cost
        results[provider] = {
            'cost': orch.get_cost(),
            'tokens': orch.input_tokens + orch.output_tokens
        }

    # Find cheapest
    cheapest = min(results.items(), key=lambda x: x[1]['cost'])
    print(f"Cheapest provider: {cheapest[0]} at ${cheapest[1]['cost']:.6f}")

    return results
```

### Operation Performance Analysis

```python
def analyze_operation_performance(orch):
    """Analyze which operations are most expensive"""

    summary = orch.get_cost_summary()
    operations = summary['by_operation']

    # Sort by total cost
    sorted_ops = sorted(
        operations.items(),
        key=lambda x: x[1]['total_cost'],
        reverse=True
    )

    print("Most expensive operations:")
    for op_name, op_data in sorted_ops:
        print(f"  {op_name}:")
        print(f"    Total: ${op_data['total_cost']:.6f}")
        print(f"    Count: {op_data['count']}")
        print(f"    Avg: ${op_data['avg_cost']:.6f}")
        print(f"    Latency: {op_data['avg_latency_ms']:.2f}ms")
```

## Testing

Run the comprehensive test suite:

```bash
# Run all token tracking tests
pytest agentflow-src/tests/test_token_tracking.py -v

# Run specific test class
pytest agentflow-src/tests/test_token_tracking.py::TestCostCalculation -v

# Run with coverage
pytest agentflow-src/tests/test_token_tracking.py --cov=agentflow.orchestration.smart_orchestrator
```

## Validation

Cost calculations are validated to be accurate within 5% of expected costs based on provider pricing. This is tested across multiple scenarios:

- Different providers (Anthropic, DeepSeek, GPT-Mini)
- Various token counts (1K to 50K tokens)
- Multiple operation types
- Cumulative tracking across many calls

## Implementation Details

### Token Tracking Flow

1. **Operation Start**: `_set_operation()` is called to mark the beginning of an operation
2. **LLM Call**: `_call_llm()` executes the API request
3. **Response Parsing**: Token counts extracted from response.usage
4. **Cost Calculation**: `_track_usage()` calculates costs based on provider pricing
5. **Recording**: Creates TaskCost record with all details
6. **Accumulation**: Updates total_cost and appends to task_costs list

### Internal Methods

- `_set_operation(operation: str)`: Set current operation context
- `_track_usage(input_tokens: int, output_tokens: int)`: Track and calculate costs
- `_costs_by_provider()`: Aggregate costs by provider
- `get_cost_summary()`: Export comprehensive cost data

## Best Practices

1. **Budget Monitoring**: Check costs periodically during long-running operations
2. **Provider Selection**: Use cost data to inform provider choices
3. **Operation Optimization**: Identify and optimize expensive operations
4. **Regular Exports**: Export cost data regularly for analysis
5. **Reset Between Sessions**: Use `reset_stats()` to start fresh tracking

## Troubleshooting

### Cost Appears Zero

Ensure operations are actually being executed and API calls are successful:
```python
print(f"Task count: {len(orch.task_costs)}")
print(f"Total tokens: {orch.input_tokens + orch.output_tokens}")
```

### Costs Seem High

Check which operations are consuming the most:
```python
summary = orch.get_cost_summary()
for op, data in summary['by_operation'].items():
    print(f"{op}: ${data['total_cost']} ({data['count']} calls)")
```

### Missing Provider Data

Verify the provider is configured in PROVIDERS dict:
```python
print(SmartOrchestrator.PROVIDERS.keys())
```

## Future Enhancements

Planned improvements for cost tracking:

1. **Budget Alerts**: Automatic warnings when approaching budget limits
2. **Cost Prediction**: Estimate total cost before execution
3. **Historical Analysis**: Track costs over time with database storage
4. **Dashboard Integration**: Real-time cost monitoring UI
5. **Optimization Recommendations**: Suggest cheaper alternatives

## Support

For issues or questions:
- Review test suite: `agentflow-src/tests/test_token_tracking.py`
- Check implementation: `agentflow-src/agentflow/orchestration/smart_orchestrator.py`
- File issues on project repository
