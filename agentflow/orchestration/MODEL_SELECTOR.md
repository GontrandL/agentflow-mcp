# Dynamic Model Selection System

Intelligent task routing based on complexity analysis with cost/quality/speed optimization.

## Overview

The ModelSelector provides automatic model selection based on task complexity, with performance tracking and machine learning capabilities to optimize selection over time.

## Features

### 1. Complexity Analysis (`_analyze_complexity`)

Analyzes tasks on a 0-10 scale considering:

- **Context Size** (0-4 points)
  - <1KB: 1 point (simple)
  - 1-5KB: 2 points (small)
  - 5-15KB: 3 points (medium)
  - >15KB: 4 points (large)

- **Requirements Count** (0-3 points)
  - ≤3 requirements: 1 point
  - 4-8 requirements: 2 points
  - >8 requirements: 3 points

- **Task Type** (0-3 points)
  - Low complexity: 1 point
  - Medium complexity: 2 points
  - High complexity: 3 points

**Total Score:** 0-10 (sum of all factors)

### 2. Decision Matrix

Routes tasks to optimal providers based on complexity:

```python
DECISION_MATRIX = {
    'simple': {
        'provider': 'gpt-mini',
        'reason': 'Low complexity task - fast, cheap model optimal',
        'thresholds': {
            'max_context_size': 5000,
            'max_requirements': 3,
            'complexity_score': 3
        }
    },
    'medium': {
        'provider': 'deepseek',
        'reason': 'Medium complexity - balanced cost/quality',
        'thresholds': {
            'max_context_size': 15000,
            'max_requirements': 8,
            'complexity_score': 6
        }
    },
    'complex': {
        'provider': 'anthropic',
        'reason': 'High complexity - premium reasoning required',
        'thresholds': {
            'max_context_size': 50000,
            'max_requirements': float('inf'),
            'complexity_score': 10
        }
    },
    'speed_critical': {
        'provider': 'gpt-mini',
        'reason': 'Speed priority - fast model with minimal overhead',
        'thresholds': {
            'max_latency': 2.0
        }
    }
}
```

### 3. Performance Tracking

Tracks metrics per model:

- **Cost:** Total cost and cost per token (millicents)
- **Quality:** Average quality scores from validation
- **Speed:** Average latency in seconds
- **Errors:** Error rate and retry count
- **Usage:** Total requests and tokens

### 4. Machine Learning

Optimizes selection over time:

- **Learning from History:** Uses past performance to select models
- **Weighted Scoring:** Balances cost/quality/speed based on priorities
- **Adaptive Selection:** Improves recommendations as more data is collected

## Usage

### Basic Usage

```python
from agentflow.orchestration import ModelSelector

# Initialize selector
selector = ModelSelector(
    available_models=['gpt-mini', 'deepseek', 'anthropic'],
    enable_learning=True
)

# Analyze and select model for task
task = {
    'description': 'Complex code generation task',
    'context': {'codebase': '...large context...'},
    'complexity': 'high',
    'requirements': {
        'edge_cases': ['case1', 'case2', 'case3'],
        'validation_criteria': ['criterion1', 'criterion2']
    }
}

provider, reason = selector.select_model_by_complexity(task)
print(f"Selected: {provider} - {reason}")
# Output: Selected: anthropic - High complexity - premium reasoning required
```

### Integration with SmartOrchestrator

```python
from agentflow.orchestration import SmartOrchestrator

# Enable dynamic model selection
orchestrator = SmartOrchestrator(
    provider='anthropic',
    enable_model_selection=True,  # Enable automatic routing
    enable_fallback=True
)

# The orchestrator will automatically select the optimal model
# based on task complexity
plan = orchestrator.analyze_and_plan(
    task="Generate comprehensive API documentation",
    capabilities=['code_gen', 'docs'],
    context={'complexity': 'high'}
)
```

### Performance Tracking

```python
# Track execution performance
@selector.track_execution('gpt-mini')
def call_model():
    # Your model call
    return {
        'cost': 0.001,
        'tokens': 1000,
        'quality_score': 0.85
    }

# Record quality scores
selector.record_quality_score('gpt-mini', 0.92)

# Get performance report
report = selector.get_performance_report()
print(report['recommendations'])
# Output: {
#   'best_for_cost': 'gpt-mini',
#   'best_for_quality': 'anthropic',
#   'best_for_speed': 'gpt-mini'
# }
```

### Optimization with Constraints

```python
# Find models meeting specific constraints
valid_models = selector.optimize_selection(
    target_cost=0.01,     # Max cost per token (millicents)
    min_quality=0.85,     # Min quality score (0-1)
    max_latency=3.0       # Max latency (seconds)
)

for model_name, summary in valid_models:
    print(f"{model_name}:")
    print(f"  Quality: {summary['avg_quality']:.2f}")
    print(f"  Cost: ${summary['cost_per_token']:.4f}/token")
    print(f"  Latency: {summary['avg_latency']:.2f}s")
```

### Priority-Based Selection

```python
# Select model based on priority
cost_optimized = selector.select_model({'priority': 'cost'})
quality_optimized = selector.select_model({'priority': 'quality'})
speed_optimized = selector.select_model({'priority': 'speed'})
balanced = selector.select_model({'priority': 'balanced'})

print(f"Cost priority: {cost_optimized}")
print(f"Quality priority: {quality_optimized}")
print(f"Speed priority: {speed_optimized}")
print(f"Balanced: {balanced}")
```

## Complexity Score Mapping

| Score Range | Model Type | Provider | Use Case |
|-------------|------------|----------|----------|
| 0-3 | Simple | gpt-mini | Quick tasks, simple queries |
| 4-6 | Medium | deepseek | Standard code generation |
| 7-10 | Complex | anthropic | Complex reasoning, large context |
| N/A | Speed Critical | gpt-mini | Real-time applications |

## Performance Metrics

### Tracked Metrics

```python
class ModelPerformanceMetrics:
    model_name: str
    total_cost: float           # Total cost in dollars
    total_tokens: int           # Total tokens processed
    total_errors: int           # Error count
    total_requests: int         # Total API calls
    total_latency: float        # Total latency in seconds
    quality_scores: List[float] # Quality scores (0-1)
    last_used: datetime         # Last usage timestamp
```

### Calculated Metrics

- **Cost per Token:** `(total_cost * 1000) / total_tokens` (millicents)
- **Average Quality:** `mean(quality_scores)`
- **Average Latency:** `total_latency / total_requests` (seconds)
- **Error Rate:** `total_errors / total_requests` (percentage)

## Weighted Scoring

The selector uses a weighted scoring system to balance priorities:

```python
# Default weights
weights = {
    'cost': 0.4,    # 40% weight on cost
    'quality': 0.4, # 40% weight on quality
    'speed': 0.2    # 20% weight on speed
}

# Priority adjustments
if priority == 'cost':
    weights = {'cost': 0.6, 'quality': 0.3, 'speed': 0.1}
elif priority == 'quality':
    weights = {'cost': 0.2, 'quality': 0.7, 'speed': 0.1}
elif priority == 'speed':
    weights = {'cost': 0.3, 'quality': 0.2, 'speed': 0.5}
```

Score normalization:
- **Cost:** Lower is better (inverted: `1 - normalized_cost`)
- **Quality:** Higher is better (direct: `normalized_quality`)
- **Speed:** Lower is better (inverted: `1 - normalized_speed`)

## Persistence

Save and load metrics for long-term learning:

```python
# Save metrics to file
selector.save_metrics('model_performance.json')

# Load metrics from file
selector.load_metrics('model_performance.json')

# Reset metrics
selector.reset_metrics()
```

## Advanced Features

### Custom Available Models

```python
selector = ModelSelector(
    available_models=['custom-model-1', 'custom-model-2'],
    default_weights={'cost': 0.5, 'quality': 0.5, 'speed': 0.0}
)
```

### Disable Learning

```python
# Use static decision matrix only
selector = ModelSelector(enable_learning=False)
```

### Access Decision Matrix

```python
from agentflow.orchestration.model_selector import DECISION_MATRIX

# View routing rules
for task_type, config in DECISION_MATRIX.items():
    print(f"{task_type}: {config['provider']}")
    print(f"  Reason: {config['reason']}")
    print(f"  Thresholds: {config.get('thresholds', {})}")
```

## Testing

Run the test suite:

```bash
python test_model_selector.py
```

Tests cover:
1. Initialization and configuration
2. Complexity analysis accuracy
3. Model selection routing
4. Decision matrix structure
5. Performance metrics tracking
6. Optimization with constraints
7. Quality score recording

## Cost Analysis

Example cost comparison for 10K tokens:

| Model | Provider | Cost (10K tokens) | Speed | Quality |
|-------|----------|-------------------|-------|---------|
| gpt-4o-mini | gpt-mini | $0.0075 | Fast | Good |
| deepseek-chat | deepseek | $0.0021 | Medium | Good |
| claude-sonnet-4-5 | anthropic | $0.18 | Slow | Excellent |

**Savings Example:**
- 100 simple tasks (10K tokens each) with gpt-mini: $0.75
- Same 100 tasks with anthropic: $18.00
- **Savings: $17.25 (96% reduction)**

## Best Practices

1. **Enable Learning:** Set `enable_learning=True` for continuous improvement
2. **Record Quality:** Always record quality scores for completed tasks
3. **Save Metrics:** Persist metrics regularly for long-term optimization
4. **Monitor Performance:** Review performance reports periodically
5. **Adjust Priorities:** Use priority parameter based on task requirements
6. **Set Constraints:** Use `optimize_selection()` for budget-constrained scenarios

## Dependencies

- **Optional:** `structlog` (for structured logging)
- **Optional:** `tenacity` (for retry logic)

Falls back gracefully if dependencies not available.

## Integration Points

### SmartOrchestrator

Automatically integrated when `enable_model_selection=True`:

```python
orchestrator = SmartOrchestrator(
    provider='anthropic',
    enable_model_selection=True
)
```

The orchestrator will:
1. Analyze task complexity before execution
2. Select optimal model automatically
3. Switch providers if needed
4. Track performance metrics
5. Learn from historical data

### Manual Integration

```python
# Create selector
selector = ModelSelector()

# Select model for task
task_dict = {
    'description': task_description,
    'context': task_context,
    'complexity': estimated_complexity,
    'requirements': task_requirements
}

provider, reason = selector.select_model_by_complexity(task_dict)

# Use selected provider
# ... model call ...

# Record quality
selector.record_quality_score(provider, quality_score)
```

## Troubleshooting

### No models meet constraints

```python
valid_models = selector.optimize_selection(
    target_cost=0.001,  # Very low cost
    min_quality=0.99,   # Very high quality
    max_latency=0.5     # Very low latency
)
# Returns: []
```

**Solution:** Relax constraints or add more models.

### Incorrect routing

```python
# Check complexity score
score = selector._analyze_complexity(task)
print(f"Complexity score: {score}/10")

# Verify thresholds
print(DECISION_MATRIX)
```

### Missing metrics

```python
# Check if model has been used
if selector.metrics['model-name'].total_requests == 0:
    print("Model not yet used - no metrics available")
```

## Roadmap

Future enhancements:
- [ ] Multi-objective optimization
- [ ] A/B testing support
- [ ] Real-time cost tracking
- [ ] Provider health monitoring
- [ ] Automatic model discovery
- [ ] Custom complexity analyzers
- [ ] Neural network-based selection

## License

Part of AutoCoder-Next project.
