#!/bin/bash
# Wrapper for AgentFlow MCP Server - stderr logging is properly configured
cd "$(dirname "$0")"
exec ./.venv/bin/python3 agentflow/mcp/agentflow_mcp_server.py
