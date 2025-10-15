#!/usr/bin/env python3
"""
Test MCP server stdin/stdout protocol.
This minimal test checks if we can properly read JSON-RPC from stdin and respond.
"""
import sys
import json
import asyncio

async def test_stdin_async():
    """Test async stdin reading."""
    print("ASYNC TEST: Waiting for input...", file=sys.stderr)

    # Try reading one line
    loop = asyncio.get_event_loop()
    line = await loop.run_in_executor(None, sys.stdin.readline)

    print(f"ASYNC TEST: Received: {line.strip()}", file=sys.stderr)

    try:
        request = json.loads(line.strip())
        print(f"ASYNC TEST: Parsed request: {request.get('method')}", file=sys.stderr)

        # Send response
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"status": "ok", "method_received": request.get("method")}
        }
        print(json.dumps(response), flush=True)
        print("ASYNC TEST: Response sent", file=sys.stderr)

    except json.JSONDecodeError as e:
        print(f"ASYNC TEST: JSON error: {e}", file=sys.stderr)

def test_stdin_sync():
    """Test synchronous stdin reading."""
    print("SYNC TEST: Waiting for input...", file=sys.stderr)

    line = sys.stdin.readline()
    print(f"SYNC TEST: Received: {line.strip()}", file=sys.stderr)

    try:
        request = json.loads(line.strip())
        print(f"SYNC TEST: Parsed request: {request.get('method')}", file=sys.stderr)

        # Send response
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"status": "ok", "method_received": request.get("method")}
        }
        print(json.dumps(response), flush=True)
        print("SYNC TEST: Response sent", file=sys.stderr)

    except json.JSONDecodeError as e:
        print(f"SYNC TEST: JSON error: {e}", file=sys.stderr)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'sync'

    if mode == 'async':
        asyncio.run(test_stdin_async())
    else:
        test_stdin_sync()
