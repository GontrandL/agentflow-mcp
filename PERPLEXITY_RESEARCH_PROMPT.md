# Perplexity Research Request: MCP Protocol Implementation in Python

## Context
We are building two Python-based MCP (Model Context Protocol) servers:
1. **APC MCP Server** - Agent Preparer Context (context compression & validation)
2. **AgentFlow MCP Server** - Task delegation and parallel execution

Both servers also integrate **A2A Protocol** (Agent-to-Agent communication) for 50-100x faster inter-agent messaging.

## Current Problem
The servers are configured but not connecting to Claude Code. NPM-based MCP servers (claude-flow, ruv-swarm) work fine, but our Python servers timeout on initialization.

**Symptoms:**
- `claude mcp list` doesn't show the Python servers
- Server waits on stdin but doesn't respond to initialize request
- No MCP logs created for these servers
- Manual test with JSON-RPC initialize message times out after 5 seconds

## Research Questions

### 1. MCP Protocol Specification (Priority: CRITICAL)
**Question:** What is the exact MCP (Model Context Protocol) initialization handshake specification as of 2024-2025?

**Details needed:**
- Complete JSON-RPC message format for `initialize` method
- Required fields in initialize request/response
- Protocol version string format (we saw "2024-11-05" in tests)
- Capabilities negotiation format
- Expected server info structure
- Tool definition schema

**Sources to check:**
- Official MCP specification (Anthropic/ModelContextProtocol)
- Claude Code MCP integration documentation
- Working MCP server implementations (especially Python ones)

### 2. Python MCP SDK/Library (Priority: HIGH)
**Question:** Is there an official Python SDK or library for implementing MCP servers?

**Details needed:**
- Package name (PyPI)
- Installation method
- Basic usage example
- Async/stdio handling
- How it compares to implementing from scratch

**Check:**
- `mcp` package on PyPI
- `anthropic-mcp` or similar
- Official Anthropic GitHub repositories
- Community implementations

### 3. Stdio Protocol Best Practices (Priority: HIGH)
**Question:** What are the best practices for implementing stdin/stdout JSON-RPC servers in Python with async?

**Details needed:**
- How to properly read from stdin in asyncio
- How to ensure clean stdout (no logging/print interference)
- Buffering considerations
- Line-by-line vs stream reading
- Error handling for broken pipes

**Common pitfalls to avoid:**
- Logging to stdout
- Not flushing output
- Blocking I/O in async context
- Unicode/encoding issues

### 4. A2A Protocol Integration (Priority: MEDIUM)
**Question:** How should A2A (Agent-to-Agent) protocol integrate with MCP servers?

**Details needed:**
- Is A2A a separate communication channel or does it use MCP?
- Message queue architecture for agent coordination
- Performance benchmarks (claimed 50-100x speedup)
- Example implementations

### 5. Working Python MCP Examples (Priority: CRITICAL)
**Question:** Can you find working examples of Python-based MCP servers?

**Search for:**
- GitHub repositories with "mcp server python"
- Working stdio-based MCP implementations
- Python servers that successfully connect to Claude Code
- Sample code showing full request/response cycle

**Key files to look for:**
- Server initialization code
- Request handling loop
- Tool registration
- Error handling

### 6. Debugging MCP Connections (Priority: HIGH)
**Question:** How to debug MCP server connection issues with Claude Code?

**Details needed:**
- Log file locations for MCP servers
- Environment variables for debug mode
- Common connection failure reasons
- How to test MCP server manually
- Tools for MCP protocol testing

## Our Current Implementation

**Key implementation details:**
```python
# Server reads from stdin in async loop
async def run(self):
    while True:
        line = await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline
        )
        if not line:
            break
        request = json.loads(line.strip())
        response = await self.handle_request(request)
        print(json.dumps(response), flush=True)

# Handles initialize, list_tools, and 4-6 tool methods
async def handle_request(self, request):
    method = request.get('method')
    if method == 'initialize':
        return {"jsonrpc": "2.0", "id": request['id'], "result": self.server_info}
    # ... other methods
```

**Logging configuration:**
- structlog redirected to stderr
- logging.basicConfig(level=ERROR, stream=stderr)
- Wrapper script: `exec python3 server.py 2>/dev/null`

## Success Criteria

The research should help us:
1. ✅ Get both Python MCP servers to show in `claude mcp list`
2. ✅ Successfully handle initialize handshake
3. ✅ Expose 10+ tools via MCP protocol
4. ✅ Maintain A2A protocol integration for fast inter-agent communication
5. ✅ Match reliability of NPM-based MCP servers (claude-flow, ruv-swarm)

## Output Format

Please provide:
1. **Protocol Specification** - Exact MCP handshake format
2. **Python SDK Recommendation** - Official library or best implementation approach
3. **Working Example** - Complete minimal Python MCP server that works
4. **Our Bug Diagnosis** - What's likely wrong with our implementation
5. **Fix Recommendations** - Step-by-step to get servers working
6. **A2A Integration Pattern** - How to combine MCP + A2A protocols

## Timeline
This is blocking advanced AI coding workflow development. Priority research request.

---

**Thank you! This research will enable cutting-edge AI agent coordination systems.**
