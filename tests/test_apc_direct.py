#!/usr/bin/env python3
"""
Test APC MCP server directly without imports that might hang.
"""
import sys
import json

# Minimal MCP server test
def main():
    print("Starting minimal MCP server test...", file=sys.stderr)

    # Read one request
    try:
        line = sys.stdin.readline()
        print(f"Received: {line.strip()}", file=sys.stderr)

        request = json.loads(line.strip())
        method = request.get('method')

        print(f"Method: {method}", file=sys.stderr)

        # Respond
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "test", "version": "1.0"},
                "capabilities": {"tools": {}}
            }
        }

        print(json.dumps(response), flush=True)
        print("Response sent", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
