#!/usr/bin/env python3
"""
Test MCP 3-step handshake.
"""
import subprocess
import json
import time

server_path = "./agentflow/mcp/apc_mcp_server.py"

# Start server
proc = subprocess.Popen(
    ["./.venv/bin/python3", server_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

try:
    # Step 1: Initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }

    print("Step 1: Sending initialize request...")
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()

    # Read response
    response = proc.stdout.readline()
    print(f"Response: {response[:200]}...")
    init_response = json.loads(response)
    print(f"✅ Initialize successful: {init_response['result']['name']}")

    # Step 2: Send initialized notification
    init_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }

    print("\nStep 2: Sending initialized notification...")
    proc.stdin.write(json.dumps(init_notification) + "\n")
    proc.stdin.flush()

    # No response expected for notifications
    time.sleep(0.2)
    print("✅ Notification sent (no response expected)")

    # Step 3: Test list_tools (should work now)
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "list_tools",
        "params": {}
    }

    print("\nStep 3: Testing list_tools after initialization...")
    proc.stdin.write(json.dumps(list_request) + "\n")
    proc.stdin.flush()

    response = proc.stdout.readline()
    list_response = json.loads(response)
    print(f"✅ Tools available: {len(list_response['result']['tools'])} tools")

    print("\n🎉 3-step handshake SUCCESS!")

finally:
    proc.terminate()
    proc.wait(timeout=1)
