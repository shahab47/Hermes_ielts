"""JSON-RPC 2.0 stdio MCP server for integration with Hermes Agent."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from app.mcp.tools import MCPToolRegistry


async def handle_jsonrpc_request(request: dict[str, Any]) -> dict[str, Any]:
    """Process incoming JSON-RPC 2.0 request."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "ielts-learning-service",
                    "version": "0.1.0",
                },
            },
        }

    elif method == "tools/list":
        tools = MCPToolRegistry.get_tool_definitions()
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": tools},
        }

    elif method == "tools/call":
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = await MCPToolRegistry.execute_tool(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result),
                    }
                ]
            },
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}",
            },
        }


async def run_stdio_server() -> None:
    """Run interactive stdio JSON-RPC loop compatible with Windows, Linux, and macOS."""
    while True:
        line_bytes = await asyncio.to_thread(sys.stdin.buffer.readline)
        if not line_bytes:
            break
        raw_text = line_bytes.decode("utf-8", errors="replace").strip()
        if not raw_text:
            continue

        try:
            req_data = json.loads(raw_text)
            resp = await handle_jsonrpc_request(req_data)
            out_bytes = (json.dumps(resp) + "\n").encode("utf-8")
            sys.stdout.buffer.write(out_bytes)
            sys.stdout.buffer.flush()
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc!s}"},
            }
            sys.stdout.buffer.write((json.dumps(err_resp) + "\n").encode("utf-8"))
            sys.stdout.buffer.flush()


def main() -> None:
    """Entrypoint for the MCP server CLI."""
    asyncio.run(run_stdio_server())


if __name__ == "__main__":
    main()
