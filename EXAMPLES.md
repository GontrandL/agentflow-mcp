# Examples

Real-world usage examples for APC + AgentFlow MCP Servers.

---

## Table of Contents

- [Quick Examples](#quick-examples)
- [AgentFlow Delegation](#agentflow-delegation)
- [APC Context Compression](#apc-context-compression)
- [APC Quality Validation](#apc-quality-validation)
- [Combined Workflows](#combined-workflows)
- [Advanced Usage](#advanced-usage)

---

## Quick Examples

### Hello World (FREE Model)

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# Simple task delegation
result = SmartOrchestrator().orchestrate("Write hello world in Python")
print(result)

# Output: Production-ready code in ~10 seconds, $0.00 cost!
```

### Context Compression

```python
from agentflow.core.context_generator import generate_compressed_context

conversation = [
    {'role': 'user', 'content': 'How do I build a REST API?'},
    {'role': 'assistant', 'content': 'Use Flask or FastAPI...'},
]

compressed = generate_compressed_context(conversation, "Add authentication", 8000)
print(f"Compressed to {compressed.total_tokens} tokens ({compressed.compression_ratio:.1f}x)")
```

---

## AgentFlow Delegation

### Example 1: Generate API Endpoint

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = """
Create a FastAPI endpoint for user registration:
- POST /api/register
- Input: email, password, name
- Validate email format
- Hash password with bcrypt
- Return JWT token
- Include error handling
- Add type hints and docstrings
"""

orchestrator = SmartOrchestrator()
code = orchestrator.orchestrate(task)
print(code)

# Uses FREE Llama 3.3 70B automatically!
# Cost: $0.00
# Time: ~15 seconds
# Quality: 85+/100
```

### Example 2: Generate Test Suite

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = """
Create pytest test suite for a Calculator class with methods:
- add(a, b)
- subtract(a, b)
- multiply(a, b)
- divide(a, b)

Include:
- Happy path tests
- Edge cases (division by zero, negative numbers)
- Type hints
- Fixtures if needed
"""

tests = SmartOrchestrator().orchestrate(task)
print(tests)

# Cost: $0.00 with FREE models
```

### Example 3: Refactor Code

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

legacy_code = """
def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

task = f"""
Refactor this code for better readability and performance:
{legacy_code}

Requirements:
- Use list comprehension
- Add type hints
- Add docstring
- Handle edge cases
"""

refactored = SmartOrchestrator().orchestrate(task)
print(refactored)
```

---

## APC Context Compression

### Example 4: Compress Long Session

```python
from agentflow.core.context_generator import generate_compressed_context

# Simulate long conversation (50+ messages)
long_conversation = [
    {'role': 'user', 'content': 'How do I optimize database queries?'},
    {'role': 'assistant', 'content': 'Use indexes, optimize JOIN operations...'},
    # ... 48 more messages
]

# Compress to 8K tokens
compressed = generate_compressed_context(
    conversation_history=long_conversation,
    current_task="Add connection pooling",
    target_tokens=8000
)

print(f"Original: {len(long_conversation)} messages")
print(f"Compressed tokens: {compressed.total_tokens}")
print(f"Compression ratio: {compressed.compression_ratio:.1f}x")
print(f"\nKey decisions: {compressed.key_decisions}")
print(f"Code snippets: {len(compressed.code_snippets)}")
print(f"\nSummary:\n{compressed.summary}")
```

### Example 5: Extract Decisions from Conversation

```python
from agentflow.core.context_generator import generate_compressed_context

conversation = [
    {'role': 'user', 'content': 'Which database should I use?'},
    {'role': 'assistant', 'content': 'Use PostgreSQL for ACID compliance'},
    {'role': 'user', 'content': 'What about caching?'},
    {'role': 'assistant', 'content': 'Use Redis for session caching'},
]

result = generate_compressed_context(conversation, "Implement caching", 8000)

# Extract key architectural decisions
for decision in result.key_decisions:
    print(f"- {decision}")

# Output:
# - Use PostgreSQL for ACID compliance
# - Use Redis for session caching
```

---

## APC Quality Validation

### Example 6: Validate Generated Code

```python
from agentflow.orchestration.hybrid_orchestrator import HybridOrchestrator
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# Generate code
task = "Create async function to fetch URL with retry logic"
code = SmartOrchestrator().orchestrate(task)

# Validate quality
validator = HybridOrchestrator(validation_threshold=80)
result = validator.validate_worker_output('worker_1', task, code)

print(f"Score: {result['score']}/100")
print(f"Passed (≥80): {result['score'] >= 80}")
print(f"\nBreakdown:")
print(f"  Completeness: {result['completeness']:.0f}/30")
print(f"  Correctness: {result['correctness']:.0f}/40")
print(f"  Production-ready: {result['production_ready']:.0f}/30")

if result['issues']:
    print(f"\nIssues found:")
    for issue in result['issues']:
        print(f"  - {issue}")
        
if result['fix_instructions']:
    print(f"\nFix instructions:")
    for instruction in result['fix_instructions']:
        print(f"  - {instruction}")
```

### Example 7: Quality Gate for Deployment

```python
from agentflow.orchestration.hybrid_orchestrator import HybridOrchestrator

MIN_SCORE = 85  # Production quality threshold

orchestrator = HybridOrchestrator(validation_threshold=MIN_SCORE)

task = "Create user authentication middleware"
code = "..."  # Generated code

result = orchestrator.validate_worker_output('auth_gen', task, code)

if result['score'] >= MIN_SCORE:
    print(f"✅ Quality check passed ({result['score']}/100) - Ready for production!")
    # Deploy code
else:
    print(f"⚠️ Quality check failed ({result['score']}/100)")
    print("Issues to fix:", result['issues'])
    # Send back for improvements
```

---

## Combined Workflows

### Example 8: Full APC-AgentFlow Pipeline

```python
from agentflow.integration.apc_agentflow_bridge import APCAgentFlowBridge

# Long conversation + complex task
conversation = [
    # ... 30+ messages about building a REST API
]

bridge = APCAgentFlowBridge(validation_threshold=85)

result = bridge.execute_with_context(
    conversation_history=conversation,
    current_task="Add OAuth2 authentication to existing API",
    max_retries=2
)

print(f"✅ Task completed!")
print(f"Validation score: {result['validation_score']}/100")
print(f"Iterations needed: {result['iterations']}")
print(f"Estimated cost: ${result['cost_estimate']}")
print(f"\nGenerated code:\n{result['result']}")
```

### Example 9: Iterative Improvement Loop

```python
from agentflow.orchestration.hybrid_orchestrator import HybridOrchestrator
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = "Create comprehensive user authentication system"
max_iterations = 3

orchestrator = HybridOrchestrator(validation_threshold=90)
smart_orch = SmartOrchestrator()

for i in range(max_iterations):
    print(f"\nIteration {i+1}:")
    
    # Generate code
    code = smart_orch.orchestrate(task)
    
    # Validate
    result = orchestrator.validate_worker_output(f'worker_{i}', task, code)
    
    print(f"Score: {result['score']}/100")
    
    if result['score'] >= 90:
        print("✅ High quality achieved!")
        break
    
    # Improve task description with fix instructions
    task += f"\n\nPrevious attempt had issues: {', '.join(result['issues'])}"
    task += f"\nFix: {', '.join(result['fix_instructions'])}"
```

---

## Advanced Usage

### Example 10: Parallel Worker Execution

```python
import asyncio
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

async def parallel_workers():
    tasks = [
        "Create user model with SQLAlchemy",
        "Create post model with relationships",
        "Create comment model with foreign keys",
        "Create migration scripts",
        "Create API routes for CRUD operations"
    ]
    
    orchestrator = SmartOrchestrator()
    
    # Execute all tasks in parallel
    results = await asyncio.gather(*[
        asyncio.to_thread(orchestrator.orchestrate, task)
        for task in tasks
    ])
    
    return results

# Run parallel workers
results = asyncio.run(parallel_workers())
for i, result in enumerate(results):
    print(f"\n=== Worker {i+1} Result ===")
    print(result[:200] + "...")  # First 200 chars

# 5 workers complete in parallel (~time of 1 worker)
# Total cost: $0.00 with FREE models!
```

### Example 11: Model Comparison

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = "Create binary search algorithm with type hints"

# Try different models
models = [
    'meta-llama/llama-3.3-70b-instruct:free',  # FREE
    'deepseek/deepseek-chat',  # $0.14/M
    'anthropic/claude-sonnet-4',  # $3/M
]

for model in models:
    orchestrator = SmartOrchestrator()
    # Note: Model selection is automatic, this is for demonstration
    result = orchestrator.orchestrate(task)
    print(f"\nModel: {model}")
    print(f"Cost: {'$0.00' if ':free' in model else 'Variable'}")
    print(f"Result: {result[:150]}...")
```

### Example 12: Custom Validation Criteria

```python
from agentflow.orchestration.hybrid_orchestrator import HybridOrchestrator

# Custom validation for specific requirements
class CustomValidator(HybridOrchestrator):
    def validate_worker_output(self, worker_name, task, output):
        result = super().validate_worker_output(worker_name, task, output)
        
        # Custom checks
        if 'async' not in output:
            result['issues'].append("Missing async/await pattern")
            result['score'] -= 10
        
        if 'type hint' not in output.lower() and ':' not in output:
            result['issues'].append("Missing type hints")
            result['score'] -= 10
        
        return result

validator = CustomValidator(validation_threshold=85)
result = validator.validate_worker_output('custom', task, code)
```

---

## Real-World Scenarios

### Example 13: Daily Development Workflow

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# Morning: Generate boilerplate
SmartOrchestrator().orchestrate("Create FastAPI project structure")

# Mid-day: Write tests
SmartOrchestrator().orchestrate("Create test suite for user service")

# Afternoon: Refactor
SmartOrchestrator().orchestrate("Refactor database queries for performance")

# All tasks: $0.00 with FREE models! 🎉
```

### Example 14: Long Project Session

```python
from agentflow.core.context_generator import generate_compressed_context
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# After 4 hours of conversation (80K tokens)
conversation = [...]  # Long conversation history

# Compress before continuing
compressed = generate_compressed_context(
    conversation,
    "Add WebSocket support to API",
    target_tokens=8000
)

# Use compressed context for next task
task = f"""
Based on our discussion: {compressed.summary}

Key decisions: {compressed.key_decisions}

Now add WebSocket support...
"""

result = SmartOrchestrator().orchestrate(task)
```

---

## Tips & Best Practices

### Tip 1: Let FREE Models Handle Routine Work

```python
# ✅ Good: Use FREE models for:
- Code generation
- Documentation writing
- Test creation
- Refactoring
- Boilerplate generation

# ⚠️ Only use paid models for:
- Complex architectural decisions
- Security-critical code
- Novel algorithm design
```

### Tip 2: Use Quality Validation Before Merging

```python
# Always validate before merging to main
result = validate(task, code)
if result['score'] >= 85:
    merge_to_main(code)
else:
    request_changes(result['fix_instructions'])
```

### Tip 3: Compress Context Regularly

```python
# When conversation exceeds 50K tokens
if len(conversation_history) > 50:
    compressed = generate_compressed_context(
        conversation_history,
        current_task,
        target_tokens=8000
    )
    # Start new conversation with compressed context
```

---

## Performance Benchmarks

From real-world testing (2025-10-14):

| Task | Model | Time | Cost | Quality |
|------|-------|------|------|---------|
| Factorial function | FREE Llama 3.3 70B | 13s | $0.00 | 87/100 |
| REST API endpoint | FREE Llama 3.3 70B | 15s | $0.00 | 85/100 |
| Test suite | FREE Qwen 2.5 | 12s | $0.00 | 83/100 |
| Context compression | N/A | <1s | $0.00 | N/A |
| Quality validation | N/A | <1s | $0.00 | N/A |

---

## More Examples

Check the `/examples` directory for:
- Complete project templates
- Integration patterns
- Performance optimizations
- Error handling strategies

---

**Want to contribute examples? See [CONTRIBUTING.md](CONTRIBUTING.md)**
