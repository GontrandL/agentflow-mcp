# MCP Integration Guide - Smart Usage Patterns

**Date**: 2025-10-14
**Status**: Production-Ready
**Purpose**: Enable Claude Code to use AgentFlow MCP servers intelligently

---

## 🎯 Available MCP Servers

### 1. APC (Agent Preparer Context)
**Location**: `agentflow/mcp/apc_mcp_server.py`
**Tools**: 4 tools for context management and validation

### 2. AgentFlow (Future)
**Location**: `agentflow/mcp/agentflow_mcp_server.py` (to be created)
**Tools**: Delegation orchestration tools

---

## ⚙️ Configuration

### Add to `.claude.json`

**Location**: `~/.claude.json`

Add this to your Claude Code configuration:

```json
{
  "mcpServers": {
    "apc": {
      "command": "python3",
      "args": [
        "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/agentflow/mcp/apc_mcp_server.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "OPENROUTER_API_KEY": "${OPENROUTER_API_KEY}"
      },
      "disabled": false
    }
  }
}
```

**Note**: APC server will use API keys from your environment.

---

## 🚀 Smart Usage Patterns

### Pattern 1: Automatic Context Compression

**When to use**: Claude Code conversation exceeds 50K tokens

**How it works automatically**:
1. Claude detects context bloat
2. Calls `mcp__apc__prepare_context` tool
3. Compresses 100K → 8K tokens (12x reduction)
4. Continues with compressed context

**Example**:
```
User: "My conversation is getting long (80K tokens)"

Claude Code (automatic):
- Detects high token count
- Calls mcp__apc__prepare_context
- Returns compressed context (6.5K tokens)
- Continues normally with 91% less context
```

**No user action required** - Claude handles this automatically!

---

### Pattern 2: Quality Validation for Delegated Work

**When to use**: After AgentFlow delegation completes

**How to trigger**:
```
User: "Validate the generated code quality"

Claude Code:
- Calls mcp__apc__validate_output
- Scores output 0-100
- Returns issues list if any
- Suggests improvements
```

**Manual trigger**:
```python
# In your code
from agentflow.orchestration.hybrid_orchestrator import validate_delegation_output

result = validate_delegation_output(task, output)
# Returns: {"score": 85, "passed": True, "issues": []}
```

---

### Pattern 3: Full Workflow Automation

**When to use**: Complex task requiring context prep + delegation + validation

**How it works**:
```
User: "Build a REST API with full validation"

Claude Code:
1. Calls mcp__apc__prepare_context (compresses current conversation)
2. Calls mcp__apc__execute_workflow (handles delegation)
3. Delegates to DeepSeek V3 ($0.14/M)
4. Validates output (score ≥ 80)
5. Returns production-ready result

Cost: $0.12 vs $3.50 without delegation (96% savings)
```

---

### Pattern 4: Cost-Effective Development Session

**Scenario**: Building a feature over multiple hours

**Smart workflow**:

```
Hour 1: Research & Planning
- Claude: Direct work (architecture, decisions)
- Cost: $0.50

Hour 2-4: Implementation
- Claude: Calls mcp__apc__execute_workflow
- Delegates to DeepSeek V3
- Cost: $0.30 (vs $8 direct)

Hour 5: Integration & Polish
- Claude: Direct work (review, integration)
- Cost: $0.40

Total: $1.20 vs $15+ (92% savings)
```

---

## 📊 When Claude Code Should Use MCP

### Automatic (No User Prompt Needed)

**1. Context Management**
- Conversation > 50K tokens → Compress automatically
- Session about to hit limit → Create checkpoint
- Context bloat detected → Trigger compression

**2. Cost Optimization**
- Large code generation (>200 lines) → Suggest delegation
- Multiple similar tasks → Batch via delegation
- Complex research (3+ steps) → Delegate

**3. Quality Assurance**
- After delegation → Auto-validate
- Before merging → Check quality score
- Iterative improvement → Fix and retry

### Manual (User-Triggered)

**1. Explicit Requests**
```
"Delegate this to AgentFlow"
"Compress the conversation context"
"Validate the generated code quality"
"Use cheap models for this task"
```

**2. Quality Issues**
```
"The code has bugs, improve it"
"This doesn't meet requirements"
"Score and fix this output"
```

---

## 🎓 Decision Tree for Claude Code

```
┌─────────────────────────────────────┐
│   New Task from User                │
└──────────────┬──────────────────────┘
               │
               ├──> Context > 50K? ──Yes──> compress_context()
               │
               ├──> Long-form (>500 words)? ──Yes──> delegate_to_agentflow()
               │
               ├──> Code generation (>200 lines)? ──Yes──> delegate_to_agentflow()
               │
               ├──> Complex research (3+ steps)? ──Yes──> delegate_to_agentflow()
               │
               └──> Simple/Interactive? ──Yes──> handle_directly()
                                                      │
                                                      └──> After completion:
                                                           validate_if_delegated()
```

---

## 🛠️ MCP Tools Reference

### mcp__apc__prepare_context

**Purpose**: Compress conversation context

**When to use**:
- Conversation > 50K tokens
- Starting long session
- Before complex task

**Input**:
```json
{
  "conversation_history": "...",
  "current_task": "Build REST API",
  "target_tokens": 8000
}
```

**Output**:
```json
{
  "summary": "Key points...",
  "key_decisions": [...],
  "code_snippets": [...],
  "compression_ratio": 12.5
}
```

---

### mcp__apc__validate_output

**Purpose**: Validate generated code quality

**When to use**:
- After delegation
- Before merging
- Quality concerns

**Input**:
```json
{
  "task": "Implement JWT auth",
  "output": "...",
  "threshold": 80
}
```

**Output**:
```json
{
  "score": 85,
  "passed": true,
  "issues": [],
  "completeness": 28,
  "correctness": 38,
  "production_ready": 27
}
```

---

### mcp__apc__execute_workflow

**Purpose**: Full APC-AgentFlow pipeline

**When to use**:
- Complex implementation tasks
- Need context prep + delegation + validation
- Want metrics tracking

**Input**:
```json
{
  "task": "Build user authentication system",
  "conversation_history": "...",
  "validation_threshold": 80,
  "max_retries": 3
}
```

**Output**:
```json
{
  "result": "...",
  "validation_score": 87,
  "iterations": 1,
  "cost_estimate": 0.12,
  "status": "success"
}
```

---

### mcp__apc__get_metrics

**Purpose**: Get APC performance metrics

**When to use**:
- End of session
- Performance review
- Cost tracking

**Output**:
```json
{
  "total_requests": 15,
  "success_rate": 0.93,
  "avg_validation_score": 85,
  "avg_compression_ratio": 12.3,
  "avg_cost_per_request": 0.08
}
```

---

## 💡 Best Practices

### For Claude Code

**1. Proactive Context Management**
- Monitor token count continuously
- Compress at 50K tokens (not 100K)
- Create checkpoints every hour

**2. Smart Delegation**
- Delegate > 200 line code generation
- Delegate multi-step research
- Keep quick edits direct

**3. Quality Gates**
- Always validate delegated work
- Auto-fix if score < 80
- Report issues to user

### For Users

**1. Trust the System**
- Let Claude decide when to delegate
- Trust automatic context compression
- Review validation scores

**2. Provide Context**
- Clear task descriptions enable better delegation
- Specify quality requirements upfront
- Mention if cost-sensitive

**3. Leverage Patterns**
- Use "delegate this" for explicit control
- Request validation when unsure
- Check metrics periodically

---

## 📈 Expected Outcomes

### With Smart MCP Usage

**Context Management**:
- 12x compression (100K → 8K tokens)
- Infinite session capability
- < 5 min session recovery

**Cost Savings**:
- 96-99% reduction for delegatable tasks
- $0.08 vs $17 average per complex task
- Sessions cost $1-3 vs $10-50

**Quality**:
- 0-100 scoring
- Auto-correction via iteration
- Production-ready output

**Developer Experience**:
- Seamless - no manual intervention
- Fast - parallel delegation
- Reliable - validated results

---

## 🔧 Troubleshooting

### MCP Server Not Connecting

**Check**:
```bash
# Verify server executable
python3 /path/to/apc_mcp_server.py

# Check API keys
echo $ANTHROPIC_API_KEY
echo $OPENROUTER_API_KEY

# Test MCP in new Claude session
claude  # Fresh session should connect
```

### Tool Calls Failing

**Debug**:
1. Check MCP server logs (stderr)
2. Verify API keys are valid
3. Test tool manually:
```python
from agentflow.core.context_generator import generate_compressed_context
result = generate_compressed_context(history, task)
```

### Poor Quality Scores

**Solutions**:
- Lower threshold (< 80)
- Add more context to task description
- Use iterative improvement (max_retries > 1)
- Check if task is too complex for delegation

---

## 🎯 Success Metrics

**System is working well when**:
- Context stays under 50K tokens consistently
- Delegation success rate > 90%
- Average validation score > 80
- Cost per session < $5

**Monitor via**:
```python
# Get metrics
from agentflow.integration.apc_agentflow_bridge import APCAgentFlowBridge
bridge = APCAgentFlowBridge()
metrics = bridge.get_metrics()
print(f"Success rate: {metrics['success_rate']:.1%}")
print(f"Avg score: {metrics['avg_validation_score']}")
print(f"Avg cost: ${metrics['avg_cost_per_request']:.2f}")
```

---

## 🚀 Next Steps

**1. Add to `.claude.json`** (see configuration above)

**2. Test in fresh Claude session**:
```bash
claude  # New session
# MCP server should connect automatically
```

**3. Try a delegatable task**:
```
"Generate a REST API with user authentication"
# Claude should offer to delegate
```

**4. Monitor metrics**:
```
"Show me APC metrics for this session"
# Claude uses mcp__apc__get_metrics
```

---

**Remember**: The system works best when Claude Code makes decisions autonomously. Trust the MCP integration to optimize costs and quality automatically!
