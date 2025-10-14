# SmartOrchestrator Error Handling & Retry Logic

## Overview

The SmartOrchestrator implements robust error handling with automatic retry and fallback mechanisms to ensure high availability and resilience when interacting with LLM providers.

## Features

### 1. Exponential Backoff Retry

Every LLM API call uses exponential backoff retry with the following parameters:

- **Max Attempts**: 3 retries
- **Backoff Schedule**: 2s, 4s, 8s, 16s (exponential)
- **Target Exceptions**: All API exceptions
- **Logging**: Automatic warning logs before each retry

```python
orchestrator = SmartOrchestrator(
    provider='anthropic',
    api_key='your-key',
    enable_fallback=False  # Use retry only
)

# Automatically retries up to 3 times on failure
result = orchestrator._call_llm("Your prompt here")
```

### 2. Automatic Fallback Chain

When the primary provider fails after exhausting retries, the orchestrator automatically switches to alternative providers in a predefined order:

**Fallback Order**: `deepseek → grok-fast → gpt-mini → anthropic`

This order prioritizes:
1. **Cost**: Start with cheapest providers
2. **Speed**: Move to faster providers
3. **Reliability**: End with most reliable provider

```python
orchestrator = SmartOrchestrator(
    provider='anthropic',
    api_key='your-key',
    enable_fallback=True  # Enable automatic fallback
)

# If anthropic fails, automatically tries deepseek, then grok-fast, etc.
result = orchestrator._call_llm("Your prompt here")
```

### 3. Cost Tracking Preservation

Token usage and costs are tracked across **all** retry and fallback attempts:

```python
orchestrator._call_llm("Prompt 1")  # Uses anthropic
orchestrator._call_llm("Prompt 2")  # Falls back to deepseek

stats = orchestrator.get_stats()
print(f"Total cost: ${stats['cost']:.4f}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Fallback attempts: {stats['fallback_attempts']}")
print(f"Failed providers: {stats['failed_providers']}")
```

## Configuration

### Environment Variables

Configure API keys for all providers you want to use:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export DEEPSEEK_API_KEY="sk-..."
export GROK_API_KEY="xai-..."
export OPENAI_API_KEY="sk-..."
```

### Initialization Options

```python
orchestrator = SmartOrchestrator(
    provider='anthropic',           # Primary provider
    model='claude-sonnet-4.5',     # Optional: specific model
    api_key='your-key',            # Optional: provide directly
    enable_fallback=True           # Enable/disable fallback chain
)
```

## Provider Information

### Supported Providers

| Provider | Model | Cost ($/1M tokens) | Max Tokens | Use Case |
|----------|-------|-------------------|------------|----------|
| `deepseek` | deepseek-chat | $0.14 / $0.28 | 8192 | Cost-effective |
| `grok-fast` | grok-beta | $5.00 / $15.00 | 4096 | Fast inference |
| `gpt-mini` | gpt-4o-mini | $0.15 / $0.60 | 4096 | Balanced |
| `anthropic` | claude-sonnet-4.5 | $3.00 / $15.00 | 8192 | High quality |
| `openai` | gpt-4-turbo | $10.00 / $30.00 | 4096 | Premium |
| `openai-4o` | gpt-4o | $2.50 / $10.00 | 4096 | Multimodal |

### Fallback Chain Logic

1. **Primary Provider**: Initial attempt with retry
2. **DeepSeek**: Cheapest fallback option
3. **Grok Fast**: Fast alternative
4. **GPT Mini**: Balanced option
5. **Anthropic**: Most reliable (if not primary)

## Error Scenarios

### Scenario 1: Transient API Error

```
Attempt 1: ❌ Rate limit error
Wait 2s...
Attempt 2: ✅ Success
```

Result: Request succeeds after retry, no fallback needed.

### Scenario 2: Provider Down

```
Primary (anthropic):
  Attempt 1: ❌ Connection timeout
  Wait 2s...
  Attempt 2: ❌ Connection timeout
  Wait 4s...
  Attempt 3: ❌ Connection timeout

Fallback to deepseek:
  Attempt 1: ✅ Success
```

Result: Request succeeds with fallback provider, cost tracking preserved.

### Scenario 3: All Providers Fail

```
Primary (anthropic): ❌ Failed (3 attempts)
Fallback (deepseek): ❌ Failed (3 attempts)
Fallback (grok-fast): ❌ Failed (3 attempts)
Fallback (gpt-mini): ❌ Failed (3 attempts)

RuntimeError: All providers failed
```

Result: Exception raised with detailed error information.

## Logging

All error handling events are logged with appropriate levels:

```python
# INFO: Successful calls and fallback switches
orchestrator.logger.info("Calling primary provider: anthropic")
orchestrator.logger.info("Fallback successful: deepseek")

# WARNING: Retry attempts
orchestrator.logger.warning("Retrying after error...")

# ERROR: Failures
orchestrator.logger.error("API call failed: Connection timeout")
orchestrator.logger.error("Fallback to deepseek failed: Rate limit")
```

## Monitoring & Statistics

### Get Detailed Statistics

```python
stats = orchestrator.get_stats()

{
    'provider': 'deepseek',           # Current active provider
    'model': 'deepseek-chat',         # Current model
    'input_tokens': 15000,            # Total input tokens
    'output_tokens': 5000,            # Total output tokens
    'total_tokens': 20000,            # Combined total
    'cost': 0.0042,                   # Total cost in USD
    'fallback_attempts': 2,           # Number of fallbacks
    'failed_providers': ['anthropic'], # Providers that failed
    'enable_fallback': True           # Fallback status
}
```

### Reset Statistics

```python
# Reset all counters
orchestrator.reset_stats()

# Clears:
# - Token counts
# - Cost tracking
# - Fallback attempts
# - Failed provider list
```

## Best Practices

### 1. Always Use Fallback in Production

```python
# ✅ Recommended
orchestrator = SmartOrchestrator(
    provider='anthropic',
    enable_fallback=True
)
```

### 2. Configure Multiple Providers

Set up API keys for at least 3 providers to ensure high availability:

```bash
export ANTHROPIC_API_KEY="..."
export DEEPSEEK_API_KEY="..."
export OPENAI_API_KEY="..."
```

### 3. Monitor Fallback Rates

Track fallback statistics to identify provider reliability issues:

```python
stats = orchestrator.get_stats()
if stats['fallback_attempts'] > 0:
    logger.warning(f"Primary provider failing: {stats['failed_providers']}")
```

### 4. Handle Total Failures Gracefully

```python
try:
    result = orchestrator._call_llm(prompt)
except RuntimeError as e:
    if "All providers failed" in str(e):
        # Implement your fallback logic
        # - Queue for later retry
        # - Use cached response
        # - Return error to user
        pass
```

### 5. Cost Optimization

Review provider costs and adjust primary provider based on usage:

```python
stats = orchestrator.get_stats()
cost_per_token = stats['cost'] / stats['total_tokens']

if cost_per_token > threshold:
    # Consider switching to cheaper primary provider
    orchestrator = SmartOrchestrator(provider='deepseek')
```

## Testing

Run error handling tests:

```bash
cd agentflow-src
pytest tests/test_smart_orchestrator_error_handling.py -v
```

Test coverage includes:
- Retry mechanism validation
- Fallback chain execution
- Cost tracking preservation
- Error logging verification
- Provider configuration checks

## Troubleshooting

### Issue: Fallback not working

**Solution**: Verify API keys are set for fallback providers:

```python
import os
print(os.getenv('DEEPSEEK_API_KEY'))  # Should not be None
print(os.getenv('OPENAI_API_KEY'))    # Should not be None
```

### Issue: High latency

**Cause**: Multiple retries and fallbacks add latency.

**Solution**:
- Check primary provider health
- Consider faster primary provider
- Adjust retry configuration

### Issue: Unexpected costs

**Cause**: Fallback providers may have different pricing.

**Solution**:
- Monitor `get_stats()` regularly
- Set up cost alerts
- Review fallback frequency

## Implementation Details

### Retry Decorator

Uses `tenacity` library with exponential backoff:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=16),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def _call_llm_with_retry(self, prompt, max_tokens):
    # API call implementation
    pass
```

### Fallback Logic

```python
def _call_llm(self, prompt, max_tokens):
    try:
        return self._call_llm_with_retry(prompt, max_tokens)
    except Exception as primary_error:
        for fallback_provider in FALLBACK_ORDER:
            # Skip failed/unavailable providers
            # Switch to fallback provider
            # Attempt call
            # Return on success
            # Continue on failure
        raise RuntimeError("All providers failed")
```

## Version History

- **v0.1.2**: Initial error handling implementation
  - Exponential backoff retry (3 attempts)
  - Automatic fallback chain
  - Cost tracking preservation
  - Comprehensive logging

## Future Enhancements

Planned improvements:
- [ ] Configurable retry parameters per provider
- [ ] Circuit breaker pattern
- [ ] Provider health checks
- [ ] Automatic provider selection based on historical performance
- [ ] Cost budgets and limits
- [ ] Metrics dashboard integration
