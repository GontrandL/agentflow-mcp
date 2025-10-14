# Cost Tracking Flow Diagram

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ analyze_and_plan()
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              SmartOrchestrator Methods                      │
│  - analyze_and_plan()                                       │
│  - assign_workers()                                         │
│  - validate_outputs()                                       │
│  - generate_specs()                                         │
│  - generate_feedback()                                      │
│  - assemble_and_polish()                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ _set_operation("analyze_and_plan")
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Operation Context Setup                        │
│  - Sets: self.current_operation                             │
│  - Records: self.operation_start_time                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ _call_llm(prompt)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 LLM Provider Call                           │
│  Anthropic:  messages.create()                              │
│  OpenAI:     chat.completions.create()                      │
│  OpenRouter: chat.completions.create()                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ response with usage data
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Token Usage Parsing                            │
│  Anthropic:  response.usage.input_tokens                    │
│              response.usage.output_tokens                   │
│  OpenAI:     response.usage.prompt_tokens                   │
│              response.usage.completion_tokens               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ _track_usage(input_tokens, output_tokens)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Cost Calculation                            │
│  input_cost = input_tokens × config['input_price']          │
│  output_cost = output_tokens × config['output_price']       │
│  total_cost = input_cost + output_cost                      │
│  latency = time.time() - operation_start_time               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Create TaskCost record
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              TaskCost Record Creation                       │
│  TaskCost(                                                  │
│    timestamp,                                               │
│    provider,                                                │
│    model,                                                   │
│    operation,                                               │
│    input_tokens,                                            │
│    output_tokens,                                           │
│    input_cost,                                              │
│    output_cost,                                             │
│    total_cost,                                              │
│    latency_ms                                               │
│  )                                                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Accumulate
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Cost Accumulation                              │
│  self.input_tokens += input_tokens                          │
│  self.output_tokens += output_tokens                        │
│  self.total_cost += total_cost                              │
│  self.task_costs.append(task_cost)                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Return response text
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 User Application                            │
│  - Receives result                                          │
│  - Can call get_cost() or get_cost_summary()                │
└─────────────────────────────────────────────────────────────┘
```

## Data Structures

### TaskCost Record

```
┌─────────────────────────────────────────────────────────────┐
│                       TaskCost                              │
├─────────────────────────────────────────────────────────────┤
│ timestamp: float        │ Unix timestamp                    │
│ provider: str           │ "anthropic", "deepseek", etc.     │
│ model: str              │ Specific model name               │
│ operation: str          │ "analyze_and_plan", etc.          │
│ input_tokens: int       │ Number of prompt tokens           │
│ output_tokens: int      │ Number of completion tokens       │
│ input_cost: float       │ Cost for input tokens             │
│ output_cost: float      │ Cost for output tokens            │
│ total_cost: float       │ input_cost + output_cost          │
│ latency_ms: float       │ API call duration in ms           │
└─────────────────────────────────────────────────────────────┘
```

### Orchestrator State

```
┌─────────────────────────────────────────────────────────────┐
│              SmartOrchestrator State                        │
├─────────────────────────────────────────────────────────────┤
│ Cumulative Totals:                                          │
│   - input_tokens: int          (sum of all input tokens)    │
│   - output_tokens: int         (sum of all output tokens)   │
│   - total_cost: float          (sum of all costs)           │
│                                                             │
│ Tracking Collections:                                       │
│   - task_costs: List[TaskCost] (all individual records)     │
│                                                             │
│ Current Context:                                            │
│   - current_operation: str     (current operation name)     │
│   - operation_start_time: float (for latency tracking)      │
└─────────────────────────────────────────────────────────────┘
```

## Cost Summary Generation Flow

```
                       get_cost_summary()
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│          Aggregate task_costs by provider                   │
│  - Group by provider name                                   │
│  - Sum costs per provider                                   │
│  - Count tasks per provider                                 │
│  - Calculate averages                                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Aggregate task_costs by operation                  │
│  - Group by operation type                                  │
│  - Sum costs per operation                                  │
│  - Count calls per operation                                │
│  - Calculate averages and latencies                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Calculate efficiency metrics                       │
│  - cost_per_1k_tokens                                       │
│  - avg_tokens_per_task                                      │
│  - input_output_ratio                                       │
│  - total_tokens                                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Assemble complete summary                          │
│  {                                                          │
│    'total_cost': ...,                                       │
│    'task_count': ...,                                       │
│    'average_cost': ...,                                     │
│    'by_provider': {...},                                    │
│    'by_operation': {...},                                   │
│    'efficiency_metrics': {...},                             │
│    'tasks': [...]                                           │
│  }                                                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Return summary dict
                            ▼
                      User Application
```

## Provider Fallback with Cost Tracking

```
┌─────────────────────────────────────────────────────────────┐
│              Primary Provider Call                          │
│  Provider: anthropic                                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ API Error!
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Fallback Attempt #1                            │
│  Provider: deepseek                                         │
│  Note: Cost tracking continues                              │
│  - self.total_cost preserved                                │
│  - self.task_costs preserved                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Success!
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Track with New Provider                        │
│  TaskCost record created with:                              │
│  - provider: "deepseek"                                     │
│  - All costs accumulated                                    │
│  - Previous costs preserved                                 │
└─────────────────────────────────────────────────────────────┘

Final State:
  self.total_cost = (primary_cost + fallback_cost)
  self.task_costs = [primary_record, fallback_record]
```

## Operation Tracking Timeline

```
Time (ms)
    0 │  orch.analyze_and_plan() called
      │
   10 │  _set_operation("analyze_and_plan")
      │    └─ self.operation_start_time = time.time()
      │
   50 │  _call_llm(prompt) invoked
      │
  800 │  API call in flight...
      │
 1500 │  Response received
      │    └─ Parse tokens from response.usage
      │
 1520 │  _track_usage() called
      │    ├─ Calculate costs
      │    ├─ latency = time.time() - start_time  (1510ms)
      │    ├─ Create TaskCost record
      │    ├─ Accumulate totals
      │    └─ Append to task_costs
      │
 1550 │  Return to user
      │    └─ Cost data available via get_cost()
```

## Multi-Operation Scenario

```
Session Timeline:

Operation 1: analyze_and_plan
├─ Duration: 1500ms
├─ Tokens: 2000 input, 1000 output
├─ Cost: $0.021
└─ State: total_cost = $0.021, task_costs = [task1]

Operation 2: assign_workers
├─ Duration: 800ms
├─ Tokens: 1500 input, 800 output
├─ Cost: $0.016
└─ State: total_cost = $0.037, task_costs = [task1, task2]

Operation 3: validate_outputs
├─ Duration: 2000ms
├─ Tokens: 3000 input, 1500 output
├─ Cost: $0.032
└─ State: total_cost = $0.069, task_costs = [task1, task2, task3]

get_cost_summary() called:
└─ Returns:
   ├─ total_cost: $0.069
   ├─ task_count: 3
   ├─ average_cost: $0.023
   ├─ by_operation: {
   │    "analyze_and_plan": {...},
   │    "assign_workers": {...},
   │    "validate_outputs": {...}
   │  }
   └─ efficiency_metrics: {...}
```

## Key Design Decisions

### 1. Automatic Tracking
- No user code changes required
- Operations automatically call `_set_operation()`
- Tracking happens in `_track_usage()`

### 2. Preserved Across Fallbacks
- Cost accumulation continues during fallback
- Provider switches recorded in TaskCost records
- Total cost maintained across all attempts

### 3. Per-Task Granularity
- Each LLM call gets its own TaskCost record
- Enables detailed analysis and debugging
- Supports export for external analysis

### 4. Real-Time Availability
- Costs calculated immediately after each call
- `get_cost()` always returns current total
- No batch processing or delays

### 5. Comprehensive Metrics
- Token counts (input/output)
- Costs (input/output/total)
- Latency (API call duration)
- Operation context (name, provider, model)

## Performance Characteristics

```
Per-Call Overhead:
├─ _set_operation():     ~0.01ms
├─ Token parsing:        ~0.05ms
├─ Cost calculation:     ~0.05ms
├─ TaskCost creation:    ~0.02ms
└─ List append:          ~0.01ms
                         ────────
Total overhead:          ~0.14ms  (<1% of typical API latency)

Memory Usage:
├─ TaskCost record:      ~200 bytes
├─ 1,000 tasks:          ~200 KB
└─ 10,000 tasks:         ~2 MB  (still negligible)
```

## Error Handling

```
┌─────────────────────────────────────────────────────────────┐
│              Normal Flow with Error                         │
├─────────────────────────────────────────────────────────────┤
│ 1. _set_operation() succeeds                                │
│ 2. _call_llm() fails (network error)                        │
│ 3. Exception raised                                         │
│ 4. Cost tracking: No TaskCost created (no response)         │
│ 5. User receives exception                                  │
│ 6. State: Unchanged from before the call                    │
└─────────────────────────────────────────────────────────────┘

With Fallback:
1. Primary fails → no TaskCost
2. Fallback succeeds → TaskCost created
3. Result: Only successful calls tracked
4. Accurate cost representation
```

## Thread Safety Note

Current implementation is **not thread-safe**. For concurrent usage:

```python
# Option 1: One orchestrator per thread
thread_orch = SmartOrchestrator(provider='anthropic')

# Option 2: Lock-based access
import threading
lock = threading.Lock()
with lock:
    plan = orch.analyze_and_plan(task, caps, ctx)
```

Future enhancement: Add thread-safe tracking with locks.
