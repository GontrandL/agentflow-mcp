# Quick Install - APC & AgentFlow MCP Servers

## Method 1: Automated Script (Recommended)

```bash
cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src
./INSTALL_MCP_SERVERS.sh
```

Then verify:
```bash
claude mcp list
```

---

## Method 2: Manual Commands

Copy-paste these commands into your terminal (outside Claude Code):

```bash
# Navigate to agentflow-src
cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src

# Add APC MCP server
claude mcp add apc /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/apc_mcp_wrapper.sh

# Add AgentFlow MCP server
claude mcp add agentflow /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src/agentflow_mcp_wrapper.sh

# Verify installation
claude mcp list
```

---

## Expected Output

```
Checking MCP server health...

apc: ✓ Connected
agentflow: ✓ Connected
claude-flow: ✓ Connected
ruv-swarm: ✓ Connected
taskmaster-ai: ✓ Connected (if installed)
```

---

## If Servers Show as Failed

Check the logs:
```bash
# View MCP logs
ls ~/.cache/claude-cli-nodejs/*/mcp-logs-*/

# Test server manually
cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src
./apc_mcp_wrapper.sh
# (Press Ctrl+C to exit)
```

---

## Troubleshooting

### Error: "Server not found"
- Ensure wrapper scripts are executable: `chmod +x *.sh`
- Verify paths are absolute (not relative)

### Error: "Connection timeout"
- Test 3-step handshake: `python3 test_mcp_handshake.py`
- Check Python venv exists: `ls .venv/bin/python3`

### Error: "Module not found"
- Activate venv: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

---

## Quick Test After Installation

Once installed, ask Claude Code in the new session:

**"List all available MCP tools"**

You should see tools from:
- ✅ apc (6 tools)
- ✅ agentflow (4 tools)
- ✅ claude-flow (84 tools)
- ✅ ruv-swarm (18 tools)

Total: 112+ tools available!
