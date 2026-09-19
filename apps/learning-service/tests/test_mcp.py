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


@pytest.mark.asyncio
async def test_mcp_tool_call_analyze_audio() -> None:
    """Test calling analyze_audio via MCP."""
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "analyze_audio",
            "arguments": {
                "attempt_id": "att_123",
                "segments": [
                    {"text": "Well, my hometown is very peaceful", "start": 0.0, "end": 2.5},
                    {"text": "and there are many scenic parks.", "start": 3.0, "end": 5.5},
                ],
                "total_duration_sec": 5.5,
            },
        },
    }
    resp = await handle_jsonrpc_request(req)
    assert resp["jsonrpc"] == "2.0"
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert content["data"]["word_count"] > 0
    assert "speech_rate_wpm" in content["data"]


@pytest.mark.asyncio
async def test_mcp_tools_full_coverage() -> None:
    """Verify that all core categories are represented in the MCP tools registry."""
    req = {"jsonrpc": "2.0", "id": 5, "method": "tools/list", "params": {}}
    resp = await handle_jsonrpc_request(req)
    tools = {t["name"] for t in resp["result"]["tools"]}

    # Ensure at least 25 tools are exposed
    assert len(tools) >= 25

    # Check key tools from every section
    assert "get_learner_profile" in tools
    assert "get_active_weaknesses" in tools
    assert "generate_daily_plan" in tools
    assert "get_due_reviews" in tools
    assert "search_learning_content" in tools
    assert "get_progress_summary" in tools
    assert "analyze_audio" in tools
