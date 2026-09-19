"""Unit tests for MCP server protocol and tool registry (Phase 7)."""

from __future__ import annotations

import json

import pytest

from app.mcp.server import handle_jsonrpc_request


@pytest.mark.asyncio
async def test_mcp_initialize() -> None:
    """Test MCP initialize handshake."""
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"clientInfo": {"name": "hermes", "version": "0.21.3"}},
    }
    resp = await handle_jsonrpc_request(req)
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    assert "result" in resp
    assert resp["result"]["serverInfo"]["name"] == "ielts-learning-service"


@pytest.mark.asyncio
async def test_mcp_tools_list() -> None:
    """Test discovery of registered MCP tools."""
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }
    resp = await handle_jsonrpc_request(req)
    assert resp["jsonrpc"] == "2.0"
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "get_learner_profile" in tool_names
    assert "preflight_writing" in tool_names
    assert "create_attempt" in tool_names
    assert "save_assessment" in tool_names


@pytest.mark.asyncio
async def test_mcp_tool_call_preflight() -> None:
    """Test calling preflight_writing via MCP."""
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "preflight_writing",
            "arguments": {
                "task_type": "task_2",
                "text": "In my opinion, technology has transformed global communication.\n\nFirst, instant messaging enables real-time collaboration...\n\nSecond, digital platforms lower educational costs...\n\nIn conclusion, technological progress benefits society.",
            },
        },
    }
    resp = await handle_jsonrpc_request(req)
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 3
    content_text = resp["result"]["content"][0]["text"]
    result_data = json.loads(content_text)
    assert result_data["status"] == "success"
    assert result_data["data"]["task_type"] == "task_2"
    assert result_data["data"]["has_clear_position_markers"] is True
