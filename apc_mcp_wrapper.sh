#!/bin/bash
# Wrapper for APC MCP Server - stderr logging is properly configured
cd "$(dirname "$0")"
exec ./.venv/bin/python3 agentflow/mcp/apc_mcp_server.py
