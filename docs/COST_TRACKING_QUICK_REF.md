# Cost Tracking Quick Reference

## Quick Start

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# Initialize with any provider
orch = SmartOrchestrator(provider='anthropic')

# Use normally - tracking is automatic
plan = orch.analyze_and_plan("Task", ["capability"], {})

# Get cost
cost = orch.get_cost()  # Returns: 0.012345

# Get detailed summary
summary = orch.get_cost_summary()
```

## Key Methods

### Get Current Cost
```python
total_cost = orch.get_cost()
# Returns: float (dollars)
```

### Get Cost Summary
```python
summary = orch.get_cost_summary()
# Returns: dict with structure below
```

### Reset Tracking
```python
orch.reset_stats()
# Clears all tracking data
```

## Cost Summary Structure

```python
{
    # Top-level metrics
    'total_cost': 0.012345,
    'task_count': 5,
    'average_cost': 0.002469,

    # By provider
    'by_provider': {
        'anthropic': {
            'total_cost': 0.012345,
            'input_tokens': 10000,
            'output_tokens': 5000,
            'task_count': 5,
            'operations': {
                'analyze_and_plan': {
                    'count': 2,
                    'total_cost': 0.005,
                    'avg_latency_ms': 1234.56
                }
            }
        }
    },

    # By operation
    'by_operation': {
        'analyze_and_plan': {
            'count': 2,
            'total_cost': 0.005,
            'avg_cost': 0.0025,
            'total_tokens': 6000,
            'avg_latency_ms': 1234.56
        }
    },

    # Efficiency
    'efficiency_metrics': {
        'cost_per_1k_tokens': 0.000823,
        'avg_tokens_per_task': 3000.0,
        'input_output_ratio': 2.0,
        'total_input_tokens': 10000,
        'total_output_tokens': 5000,
        'total_tokens': 15000
    },

    # Individual tasks
    'tasks': [
        {
            'timestamp': 1234567890.123,
            'provider': 'anthropic',
            'model': 'claude-sonnet-4-5',
            'operation': 'analyze_and_plan',
            'input_tokens': 2000,
            'output_tokens': 1000,
            'input_cost': 0.006,
            'output_cost': 0.015,
            'total_cost': 0.021,
            'latency_ms': 1234.56
        }
    ]
}
```

## Provider Pricing (per 1M tokens)

| Provider | Input | Output |
|----------|-------|--------|
| DeepSeek | $0.14 | $0.28 |
| GPT-Mini | $0.15 | $0.60 |
| Anthropic | $3.00 | $15.00 |
| Grok-Fast | $5.00 | $15.00 |

## Common Patterns

### Check Cost After Operation
```python
initial = orch.get_cost()
orch.analyze_and_plan(task, caps, ctx)
operation_cost = orch.get_cost() - initial
```

### Budget Constraint
```python
MAX_BUDGET = 0.10
if orch.get_cost() < MAX_BUDGET:
    orch.analyze_and_plan(task, caps, ctx)
else:
    print("Budget exceeded!")
```

### Export to JSON
```python
import json
with open('costs.json', 'w') as f:
    json.dump(orch.get_cost_summary(), f, indent=2)
```

### Compare Providers
```python
results = {}
for provider in ['deepseek', 'anthropic']:
    orch = SmartOrchestrator(provider=provider)
    orch.analyze_and_plan(task, caps, ctx)
    results[provider] = orch.get_cost()

cheapest = min(results, key=results.get)
```

### Find Most Expensive Operation
```python
summary = orch.get_cost_summary()
ops = summary['by_operation']
most_expensive = max(ops.items(), key=lambda x: x[1]['total_cost'])
print(f"Most expensive: {most_expensive[0]} at ${most_expensive[1]['total_cost']}")
```

## Tracked Operations

All operations automatically tracked:
- `analyze_and_plan`
- `assign_workers`
- `generate_specs`
- `validate_outputs`
- `generate_feedback`
- `assemble_and_polish`

## Key Features

✅ Automatic tracking (no code changes needed)
✅ Real-time cost calculation
✅ Per-task details with latency
✅ Provider and operation grouping
✅ Efficiency metrics
✅ Export to JSON
✅ Cost accuracy <5% error
✅ Works with fallback chain
✅ Preserved across provider switches

## Troubleshooting

**Cost is zero?**
```python
# Check if tasks were executed
print(f"Tasks: {len(orch.task_costs)}")
print(f"Tokens: {orch.input_tokens + orch.output_tokens}")
```

**Need to start fresh?**
```python
orch.reset_stats()
```

**Want per-task breakdown?**
```python
for task in orch.get_cost_summary()['tasks']:
    print(f"{task['operation']}: ${task['total_cost']:.6f}")
```

## Files

- **Implementation**: `agentflow/orchestration/smart_orchestrator.py`
- **Tests**: `tests/test_token_tracking.py`
- **Full Docs**: `docs/COST_TRACKING.md`
- **Demo**: `examples/cost_tracking_demo.py`
- **Completion Report**: `docs/PHASE2_COMPLETION.md`

## Running Tests

```bash
cd agentflow-src
pytest tests/test_token_tracking.py -v
```

## Demo

```bash
cd agentflow-src
python examples/cost_tracking_demo.py
```
