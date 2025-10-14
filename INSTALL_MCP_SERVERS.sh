#!/bin/bash
# Install APC and AgentFlow MCP servers using claude mcp add command
# Run these commands in your terminal (not in Claude Code)

echo "🚀 Installing APC and AgentFlow MCP Servers..."
echo ""

# Get absolute paths
AGENTFLOW_SRC="/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src"
APC_WRAPPER="$AGENTFLOW_SRC/apc_mcp_wrapper.sh"
AGENTFLOW_WRAPPER="$AGENTFLOW_SRC/agentflow_mcp_wrapper.sh"

# Verify wrappers exist
if [ ! -f "$APC_WRAPPER" ]; then
    echo "❌ APC wrapper not found: $APC_WRAPPER"
    exit 1
fi

if [ ! -f "$AGENTFLOW_WRAPPER" ]; then
    echo "❌ AgentFlow wrapper not found: $AGENTFLOW_WRAPPER"
    exit 1
fi

echo "✅ Found APC wrapper: $APC_WRAPPER"
echo "✅ Found AgentFlow wrapper: $AGENTFLOW_WRAPPER"
echo ""

# Add APC MCP server
echo "📦 Adding APC MCP server..."
claude mcp add apc "$APC_WRAPPER"

# Add AgentFlow MCP server
echo "📦 Adding AgentFlow MCP server..."
claude mcp add agentflow "$AGENTFLOW_WRAPPER"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Run 'claude mcp list' to verify both servers are connected."
