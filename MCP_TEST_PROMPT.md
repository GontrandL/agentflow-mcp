# MCP Tools Comprehensive Test Suite

**Instructions:** Copy this entire prompt and send it to your other Claude Code session.

---

## 🧪 MCP Tools Test Request

I need you to run a comprehensive test of all newly installed MCP tools to verify they're working correctly. Please test each tool systematically and report results.

### Test Environment
- Location: `/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src`
- MCP Servers: `apc`, `agentflow`, `taskmaster-ai`
- Expected: 10+ tools available

---

## Test 1: List All Available MCP Tools

**Action:** List all MCP tools currently available in this session.

**Expected Output:**
- Should see tools from `apc` (6 tools)
- Should see tools from `agentflow` (4 tools)
- Should see tools from `taskmaster-ai` (tools vary)

**Please display:**
- Total count of MCP tools
- Group by server (apc, agentflow, taskmaster-ai)
- Tool names and brief descriptions

---

## Test 2: APC Context Compression Test

**Action:** Use `mcp__apc__prepare_context` to compress the following conversation:

**Test Input:**
```
Conversation History:
- User: "I need to build a REST API with authentication"
- Assistant: "I'll help you build a REST API. We'll use Express.js for the server, JWT for authentication, bcrypt for password hashing, and PostgreSQL for the database. First, let's set up the project structure..."
- User: "How do I implement password reset?"
- Assistant: "For password reset, we'll implement a secure token-based system. First, generate a unique reset token, store it in the database with expiration time, send email with reset link..."
- User: "What about rate limiting?"
- Assistant: "Rate limiting is crucial for API security. We'll use express-rate-limit middleware to prevent abuse. Configure it to allow 100 requests per 15 minutes per IP address..."
```

**Current Task:** "Add OAuth2 social login (Google, GitHub)"

**Expected Results:**
- Compressed summary (should be significantly shorter)
- Key decisions extracted (JWT, PostgreSQL, rate limiting)
- Code snippets preserved (if any)
- Compression ratio reported (should be >3x)
- Total tokens reduced

**Validation Criteria:**
✅ Tool executes without errors
✅ Returns compressed summary
✅ Preserves essential context
✅ Reports compression metrics

---

## Test 3: APC Output Validation Test

**Action:** Use `mcp__apc__validate_output` to score this code:

**Test Input - Task:**
```
"Implement a user authentication function with password hashing"
```

**Test Input - Output (Code to Validate):**
```python
import bcrypt
from typing import Optional

def authenticate_user(username: str, password: str, stored_hash: str) -> bool:
    """
    Authenticate user with bcrypt password verification.

    Args:
        username: Username for logging
        password: Plain text password to verify
        stored_hash: Bcrypt hash from database

    Returns:
        True if authentication successful, False otherwise
    """
    try:
        # Verify password against stored hash
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    except Exception as e:
        print(f"Authentication error for {username}: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Demo hash for password "testpass123"
    demo_hash = bcrypt.hashpw("testpass123".encode('utf-8'), bcrypt.gensalt())
    result = authenticate_user("testuser", "testpass123", demo_hash.decode('utf-8'))
    print(f"Authentication: {'Success' if result else 'Failed'}")
```

**Expected Results:**
- Score: 70-95/100
- Completeness check (30 points max)
- Correctness check (40 points max)
- Production-ready check (30 points max)
- Passed: True/False (threshold 80)
- Issues list (if any)

**Validation Criteria:**
✅ Tool executes without errors
✅ Returns numerical score (0-100)
✅ Provides breakdown (completeness/correctness/production)
✅ Lists any issues found
✅ Gives clear pass/fail indication

---

## Test 4: APC Project Query Test

**Action:** Use `mcp__apc__query_project` to query this project's structure.

**Test Queries (try each):**

**Query 1:** Find Python files
```
query_type: "find_files"
query: "*.py"
file_type: "code"
limit: 10
```

**Query 2:** Find test files
```
query_type: "find_pattern"
query: "test"
file_type: "test"
limit: 5
```

**Query 3:** Natural language
```
query_type: "ask"
query: "Where is the MCP server implementation?"
limit: 10
```

**Expected Results:**
- Returns list of matching files
- File paths are correct
- Descriptions are relevant (for "ask" queries)
- Respects limit parameter

**Validation Criteria:**
✅ Tool executes for all 3 query types
✅ Returns file lists
✅ Paths are valid
✅ Results match query intent

---

## Test 5: APC Get Metrics Test

**Action:** Use `mcp__apc__get_metrics` to retrieve performance stats.

**No parameters needed.**

**Expected Results:**
- total_requests: Number (may be 0 if no prior usage)
- success_rate: Percentage (0-100)
- avg_validation_score: Number (0-100)
- avg_compression_ratio: Number (e.g., 8.5x)
- avg_cost_per_request: Dollar amount

**Validation Criteria:**
✅ Tool executes without errors
✅ Returns JSON with metrics
✅ All fields present
✅ Values are reasonable

---

## Test 6: AgentFlow Task Delegation Test

**Action:** Use `mcp__agentflow__delegate_task` to delegate a simple task.

**Test Input:**
```
task_description: "Write a Python function that calculates the factorial of a number using recursion. Include docstring and example usage."

context: [
  {"type": "requirement", "content": "Must handle n >= 0"},
  {"type": "requirement", "content": "Must include type hints"},
  {"type": "requirement", "content": "Must have docstring with Args and Returns"}
]

target_model: "cost-effective"
```

**Expected Results:**
- task_id: String (unique identifier)
- model: String (e.g., "deepseek/deepseek-chat")
- status: "completed" or "in_progress"
- result: Generated code (if completed)
- estimated_cost: Dollar amount (should be very low)

**Validation Criteria:**
✅ Tool executes without errors
✅ Returns task_id
✅ Provides status
✅ If completed, includes generated code
✅ Code meets requirements
✅ Cost is significantly lower than direct Claude usage

---

## Test 7: AgentFlow List Models Test

**Action:** Use `mcp__agentflow__list_models` to see available models.

**No parameters needed.**

**Expected Results:**
- List of available models
- Each model includes:
  - name: Model identifier
  - provider: Provider name (e.g., "deepseek", "openai")
  - cost_per_1k_input: Price
  - cost_per_1k_output: Price
  - capabilities: List of features

**Validation Criteria:**
✅ Tool executes without errors
✅ Returns list of models
✅ Includes pricing information
✅ Shows cost comparison (DeepSeek vs Claude)

---

## Test 8: Taskmaster AI Integration Test

**Action:** Use Taskmaster AI tools to break down a simple PRD.

**Test Input (PRD):**
```
Product Requirement: User Profile Management

Features:
1. Users can view their profile with avatar, name, email, bio
2. Users can edit their profile information
3. Users can upload a new avatar image
4. Profile changes are validated before saving
5. Users see confirmation message after successful update

Technical Requirements:
- React frontend with TypeScript
- REST API for profile operations (GET, PUT)
- Image upload with size/type validation
- Form validation on client and server
- Responsive design for mobile and desktop
```

**Expected Results:**
- Task breakdown into 5-10 actionable tasks
- Each task has:
  - Title
  - Description
  - Priority
  - Dependencies (if any)
  - Estimated effort

**Validation Criteria:**
✅ Tool executes without errors
✅ Returns structured task list
✅ Tasks are logical and actionable
✅ Covers all PRD features
✅ Includes technical requirements

---

## Test 9: Error Handling Test

**Action:** Test how tools handle invalid inputs.

**Test 9a:** APC Validate with empty output
```
task: "Write a function"
output: ""
```

**Expected:** Should return error or very low score with clear message

**Test 9b:** AgentFlow Delegate with missing task_description
```
context: [{"content": "test"}]
(no task_description)
```

**Expected:** Should return validation error about required field

**Validation Criteria:**
✅ Tools handle errors gracefully
✅ Error messages are clear
✅ No crashes or hangs
✅ Returns proper JSON-RPC error responses

---

## Test 10: Performance Test

**Action:** Measure tool response times.

**Test each tool and report:**
- Time to first response
- Time to completion
- Any timeouts or delays
- Resource usage (if observable)

**Expected:**
- APC tools: <5 seconds response
- AgentFlow delegation: <10 seconds for simple tasks
- Taskmaster: <5 seconds for PRD breakdown
- No timeouts
- Smooth execution

**Validation Criteria:**
✅ All tools respond within expected time
✅ No timeouts
✅ No performance degradation over multiple calls

---

## Test Report Format

Please provide a comprehensive report in this format:

```markdown
# MCP Tools Test Results

## Summary
- Total Tests: 10
- Passed: X/10
- Failed: X/10
- Warnings: X

## Test Results

### ✅ Test 1: List All Available MCP Tools
**Status:** PASS/FAIL
**Details:**
- Total tools found: X
- APC tools: X
- AgentFlow tools: X
- Taskmaster tools: X
**Notes:** [Any observations]

### ✅ Test 2: APC Context Compression
**Status:** PASS/FAIL
**Input tokens:** ~X
**Output tokens:** ~X
**Compression ratio:** Xx
**Details:** [Compressed summary]
**Notes:** [Any observations]

[Continue for all 10 tests...]

## Issues Found
1. [Issue description and severity]
2. [Issue description and severity]

## Performance Observations
- Average response time: X seconds
- Slowest tool: [name] (X seconds)
- Fastest tool: [name] (X seconds)

## Recommendations
1. [Recommendation based on test results]
2. [Recommendation based on test results]

## Overall Assessment
[Summary of MCP tools functionality, readiness for production use, and any concerns]
```

---

## Success Criteria

**All tests PASS if:**
✅ All 10 tests execute without crashes
✅ Tools return expected data structures
✅ Response times are reasonable (<10 seconds)
✅ Error handling works gracefully
✅ Results match expected outputs
✅ Cost savings are demonstrated (AgentFlow)
✅ Quality validation works (APC)

**READY FOR PRODUCTION if:**
- 9+ tests pass
- No critical failures
- Performance is acceptable
- Error handling is robust

---

## Additional Context

**Server Locations:**
- APC: `/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/agentflow/mcp/apc_mcp_server.py`
- AgentFlow: `/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/agentflow/mcp/agentflow_mcp_server.py`

**Documentation:**
- `MCP_SUCCESS_FINAL.md` - Deployment summary
- `MCP_DEPLOYMENT_SUCCESS.md` - Technical details
- `QUICK_INSTALL.md` - Quick reference

**If any test fails:**
1. Note the exact error message
2. Check MCP logs: `~/.cache/claude-cli-nodejs/*/mcp-logs-*/`
3. Report back for debugging

---

**Please run all 10 tests systematically and provide the complete test report.** 🧪
