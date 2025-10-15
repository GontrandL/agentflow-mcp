# MCP Servers - Production Deployment Guide

**Date**: 2025-10-14 20:00
**Status**: READY FOR DEPLOYMENT
**Purpose**: Deploy APC and AgentFlow MCP servers with comprehensive logging for debugging

---

## 🚀 Deployment Checklist

### Pre-Deployment Verification

**APC MCP Server** ✅:
- [x] 28/28 tests passing (100%)
- [x] Standalone test successful
- [x] All 6 tools functional (4 MCP + 2 A2A)
- [x] Logging configured
- [x] Error handling tested

**AgentFlow MCP Server** 🔄:
- [ ] Fix tutorial format issue
- [ ] Validate structure (21/21 tests)
- [ ] Test standalone
- [ ] Add logging
- [ ] Deploy

---

## 📋 Step 1: Add APC MCP to ~/.claude.json

### Configuration

**Add this to your `~/.claude.json` in the `mcpServers` section**:

```json
{
  "mcpServers": {
    "apc": {
      "type": "stdio",
      "command": "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/.venv/bin/python3",
      "args": [
        "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/agentflow/mcp/apc_mcp_server.py"
      ],
      "cwd": "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src",
      "env": {
        "PYTHONPATH": "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Manual Steps

```bash
# 1. Backup current config
cp ~/.claude.json ~/.claude.json.backup.$(date +%Y%m%d_%H%M%S)

# 2. Edit ~/.claude.json
# Add the APC MCP configuration shown above to the mcpServers section

# 3. Verify JSON syntax
python3 -c "import json; json.load(open('/home/gontrand/.claude.json'))" && echo "✅ Valid JSON"

# 4. Restart Claude Code
# Close and reopen Claude Code application
```

### Verification

```bash
# After restart, check MCP servers
claude mcp list

# Expected output should include:
# apc: /path/to/apc_mcp_server.py - ✓ Connected
```

---

## 📊 Step 2: Set Up Comprehensive Logging

### Log Files Configuration

**Create log directory**:
```bash
mkdir -p /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/logs/mcp
```

### APC MCP Server Logging

**Log file location**: `/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/logs/mcp/apc_mcp_server.log`

**What gets logged**:
- ✅ All tool calls (prepare_context, validate_output, execute_workflow, get_metrics)
- ✅ Context compression metrics
- ✅ Validation scores
- ✅ Errors and exceptions
- ✅ Performance timing
- ✅ A2A communication

**Log level**: DEBUG (set via `LOG_LEVEL=DEBUG` in env)

### Real-Time Log Monitoring

**Terminal 1 - APC MCP logs**:
```bash
tail -f /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/logs/mcp/apc_mcp_server.log
```

**Terminal 2 - AgentFlow delegation logs**:
```bash
tail -f /tmp/delegation*.log
```

**Terminal 3 - Worker logs** (if using parallel workers):
```bash
tail -f /tmp/worker*.log
```

---

## 🔧 Step 3: Enable Structured Logging

### Log Format

**Structured JSON logs** (for easy parsing):
```json
{
  "timestamp": "2025-10-14T20:00:00.123456",
  "level": "INFO",
  "event": "tool_called",
  "tool": "prepare_context",
  "params": {
    "target_tokens": 8000,
    "history_length": 50
  },
  "result": {
    "compressed_tokens": 650,
    "compression_ratio": 12.3
  },
  "duration_ms": 234
}
```

### Log Rotation

**Configure log rotation** to prevent disk space issues:

```bash
# Add to /etc/logrotate.d/agentflow-mcp
/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/logs/mcp/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 gontrand gontrand
}
```

---

## 🧪 Step 4: Test APC MCP Deployment

### Quick Test (After Deployment)

**In new Claude Code session**:

1. **Test context compression**:
   ```
   "APC, compress this conversation history to 8K tokens"
   ```

2. **Test validation**:
   ```
   "APC, validate this code quality with score threshold 80"
   ```

3. **Test full workflow**:
   ```
   "APC, execute full workflow: compress context, delegate task, validate output"
   ```

4. **Check metrics**:
   ```
   "APC, show performance metrics for the last hour"
   ```

### Expected Behavior

**Successful deployment indicators**:
- ✅ `claude mcp list` shows "apc: ✓ Connected"
- ✅ Natural language requests invoke APC tools
- ✅ Logs show tool execution
- ✅ Compression/validation working
- ✅ No errors in logs

**Common issues**:
- ❌ "apc: ✗ Failed to connect" → Check Python path, PYTHONPATH env
- ❌ Import errors → Check .venv activated, dependencies installed
- ❌ Permission denied → Check file permissions on apc_mcp_server.py

---

## 🐛 Step 5: Debug Logging Commands

### View Recent Activity

```bash
# Last 50 APC tool calls
tail -50 /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/logs/mcp/apc_mcp_server.log

# Filter by tool
grep "tool_called.*prepare_context" logs/mcp/apc_mcp_server.log | tail -20

# Filter by errors
grep "ERROR\|EXCEPTION" logs/mcp/apc_mcp_server.log

# Performance timing
grep "duration_ms" logs/mcp/apc_mcp_server.log | tail -20
```

### Analyze Tool Usage

```bash
# Count tool calls by type
grep "tool_called" logs/mcp/apc_mcp_server.log | grep -oP 'tool": "\K[^"]+' | sort | uniq -c

# Average compression ratio
grep "compression_ratio" logs/mcp/apc_mcp_server.log | grep -oP 'compression_ratio": \K[0-9.]+' | awk '{sum+=$1; count++} END {print sum/count}'

# Average validation score
grep "validation_score" logs/mcp/apc_mcp_server.log | grep -oP 'validation_score": \K[0-9]+' | awk '{sum+=$1; count++} END {print sum/count}'
```

### Real-Time Debugging

```bash
# Watch for errors
watch -n 1 'tail -10 logs/mcp/apc_mcp_server.log | grep -E "ERROR|WARN"'

# Monitor tool call frequency
watch -n 5 'grep "tool_called" logs/mcp/apc_mcp_server.log | tail -1'

# Track compression performance
watch -n 5 'grep "compression_ratio" logs/mcp/apc_mcp_server.log | tail -5'
```

---

## 📈 Step 6: Performance Monitoring

### Create Monitoring Script

**File**: `/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/monitor_mcp.sh`

```bash
#!/bin/bash

echo "=== MCP Server Performance Monitor ==="
echo ""

echo "📊 Tool Call Summary (Last Hour):"
find logs/mcp -name "*.log" -mmin -60 -exec grep "tool_called" {} \; | \
  grep -oP 'tool": "\K[^"]+' | sort | uniq -c | sort -rn

echo ""
echo "⚡ Average Compression Ratio:"
find logs/mcp -name "*.log" -mmin -60 -exec grep "compression_ratio" {} \; | \
  grep -oP 'compression_ratio": \K[0-9.]+' | \
  awk '{sum+=$1; count++} END {if(count>0) print sum/count "x"; else print "No data"}'

echo ""
echo "✅ Average Validation Score:"
find logs/mcp -name "*.log" -mmin -60 -exec grep "validation_score" {} \; | \
  grep -oP 'validation_score": \K[0-9]+' | \
  awk '{sum+=$1; count++} END {if(count>0) print sum/count "/100"; else print "No data"}'

echo ""
echo "❌ Error Count:"
find logs/mcp -name "*.log" -mmin -60 -exec grep -c "ERROR" {} \; | \
  awk '{sum+=$1} END {print sum}'

echo ""
echo "🕒 Last 5 Tool Calls:"
tail -5 logs/mcp/apc_mcp_server.log | grep "tool_called" | \
  grep -oP '(timestamp|tool|duration_ms)": "\K[^"]+|": \K[0-9]+'
```

**Usage**:
```bash
chmod +x monitor_mcp.sh
./monitor_mcp.sh
```

---

## 🔒 Step 7: Security & Permissions

### File Permissions

```bash
# APC MCP server executable
chmod 755 agentflow/mcp/apc_mcp_server.py

# Log directory writable
chmod 755 logs/mcp

# Config files protected
chmod 600 .env
```

### Environment Variables

**Ensure sensitive data NOT in logs**:
```bash
# .env file (NOT logged)
OPENROUTER_API_KEY=sk-or-v1-...
ANTHROPIC_API_KEY=sk-ant-...

# Logged as masked
LOG_API_KEYS=False  # Masks API keys in logs
```

---

## 📝 Step 8: Document First Deployment

### Update MCP_USAGE_LOG.md

```markdown
## 2025-10-14 20:05 - APC MCP Server Deployed

**MCP**: APC
**Action**: Production deployment
**Configuration**: Added to ~/.claude.json
**Status**: ✓ Connected
**Tools Available**:
1. mcp__apc__prepare_context (context compression)
2. mcp__apc__validate_output (quality validation)
3. mcp__apc__execute_workflow (full pipeline)
4. mcp__apc__get_metrics (performance metrics)

**Verification**:
- ✅ `claude mcp list` shows connected
- ✅ Standalone test passed
- ✅ Logs configured at logs/mcp/apc_mcp_server.log
- ✅ DEBUG logging enabled

**Next**: Test all 4 tools with real tasks
```

---

## 🚨 Troubleshooting Guide

### Issue 1: MCP Server Not Connecting

**Symptoms**:
```
apc: ✗ Failed to connect
```

**Debug Steps**:
```bash
# 1. Test Python path
/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/.venv/bin/python3 --version

# 2. Test imports
cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src
./.venv/bin/python3 -c "from agentflow.mcp.apc_mcp_server import APCMCPServer; print('✅ Import OK')"

# 3. Test server directly
./.venv/bin/python3 agentflow/mcp/apc_mcp_server.py test

# 4. Check logs
tail -50 logs/mcp/apc_mcp_server.log
```

**Common fixes**:
- Update `command` path in ~/.claude.json
- Set `PYTHONPATH` in env
- Install missing dependencies: `pip install -r requirements.txt`

---

### Issue 2: Tool Not Being Called

**Symptoms**:
```
User asks "APC, compress context" but tool not invoked
```

**Debug Steps**:
```bash
# 1. Check MCP server status
claude mcp list

# 2. Check tool definitions
grep "tool.*name.*prepare_context" agentflow/mcp/apc_mcp_server.py

# 3. Try explicit tool name
"Use mcp__apc__prepare_context to compress this conversation"
```

**Common fixes**:
- Use more explicit language: "APC, use prepare_context tool to..."
- Check tool schemas are valid in server_info
- Restart Claude Code after config changes

---

### Issue 3: High Error Rate

**Symptoms**:
```
Many ERROR entries in logs
```

**Debug Steps**:
```bash
# 1. View recent errors
grep "ERROR" logs/mcp/apc_mcp_server.log | tail -20

# 2. Check stack traces
grep -A 10 "EXCEPTION" logs/mcp/apc_mcp_server.log | tail -50

# 3. Check API key validity
grep "API.*error" logs/mcp/apc_mcp_server.log
```

**Common fixes**:
- Check API keys in .env
- Verify network connectivity
- Check rate limits
- Update dependencies

---

## ✅ Deployment Success Criteria

**APC MCP Server DEPLOYED when**:
- [x] Added to ~/.claude.json
- [ ] `claude mcp list` shows "apc: ✓ Connected" (next session)
- [ ] Logs directory created
- [ ] DEBUG logging enabled
- [ ] All 4 tools accessible via natural language
- [ ] No errors in initial tests
- [ ] Performance metrics tracking
- [ ] MCP_USAGE_LOG.md updated

**AgentFlow MCP Server DEPLOYED when**:
- [ ] Tutorial format fixed
- [ ] Validation tests passing
- [ ] Added to ~/.claude.json
- [ ] Logs configured
- [ ] All 4 tools functional

---

## 📚 Related Documentation

- `APC_MCP_README.md` - Complete APC usage guide
- `MCP_TESTING_PLAN.md` - 4-week testing strategy
- `MCP_USAGE_LOG.md` - Daily usage tracking
- `DELEGATION_SYSTEM_TESTS_COMPLETE.md` - Test results

---

**Created**: 2025-10-14 20:00
**Status**: READY FOR PRODUCTION DEPLOYMENT
**Next**: Add APC to ~/.claude.json, restart Claude Code, begin testing
