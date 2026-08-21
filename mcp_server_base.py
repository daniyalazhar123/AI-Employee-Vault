#!/usr/bin/env python3
"""
Shared MCP protocol scaffolding for the AI Employee vault servers.

Turns a plain Python "logic" object (MCPEmailServer / MCPOdooServer /
MCPSocialServer) into a REAL Model Context Protocol server that speaks JSON-RPC
over stdio using the official `mcp` SDK:

    mcp.server.Server          -> the protocol server + tool registry
    @server.list_tools()       -> advertises tools (name, description, schema)
    @server.call_tool()        -> dispatches a tool call to the logic method
    mcp.server.stdio.stdio_server() -> the stdio transport (JSON-RPC framing)

This is the real MCP protocol layer the hackathon spec asks for (Silver #5,
Gold #3 / #6) — NOT an argparse CLI. The existing logic classes are reused
unchanged; this module only wraps them.

IMPORTANT: MCP-over-stdio uses **stdout** for the JSON-RPC stream. Any print or
log line written to stdout corrupts the protocol. Callers must set
AI_EMPLOYEE_LOG_STREAM=stderr *before* importing modules that call
setup_logging(); as a belt-and-suspenders measure, run_mcp_server() also
repoints any already-attached stdout logging handlers to stderr just before the
transport starts.
"""

import asyncio
import json
import logging
import sys
from typing import Callable, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types


class ToolSpec:
    """One MCP tool: its advertised schema + the sync handler that runs it."""

    def __init__(self, name: str, description: str, input_schema: Dict,
                 handler: Callable[[Dict], object]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


def _redirect_stdout_logging_to_stderr() -> None:
    """Repoint any logging StreamHandler bound to stdout onto stderr.

    Import-time logs are already handled by AI_EMPLOYEE_LOG_STREAM, but this
    catches anything else (root logger, third-party libraries) so the stdout
    JSON-RPC channel stays clean.
    """
    seen_loggers = [logging.getLogger()]
    seen_loggers += [logging.getLogger(n) for n in list(logging.root.manager.loggerDict)]
    for lg in seen_loggers:
        for h in list(getattr(lg, 'handlers', []) or []):
            if isinstance(h, logging.StreamHandler) and getattr(h, 'stream', None) is sys.stdout:
                try:
                    h.setStream(sys.stderr)
                except Exception:
                    h.stream = sys.stderr


def build_mcp_server(server_name: str, tools: List[ToolSpec]) -> Server:
    """Build a low-level MCP Server with list_tools + call_tool registered."""
    server = Server(server_name)
    by_name = {t.name: t for t in tools}
    advertised = [
        types.Tool(name=t.name, description=t.description, inputSchema=t.input_schema)
        for t in tools
    ]

    @server.list_tools()
    async def _list_tools() -> List[types.Tool]:
        return advertised

    @server.call_tool()
    async def _call_tool(name: str, arguments: Optional[Dict]) -> List[types.TextContent]:
        spec = by_name.get(name)
        if spec is None:
            payload = {'success': False, 'message': f'Unknown tool: {name}'}
            return [types.TextContent(type='text', text=json.dumps(payload))]
        try:
            # Logic methods are synchronous and may do blocking IO (SMTP, XML-RPC,
            # Playwright). Run them in a worker thread so the stdio event loop
            # stays responsive.
            result = await asyncio.to_thread(spec.handler, arguments or {})
        except Exception as e:
            result = {'success': False, 'message': f'{type(e).__name__}: {e}'}
        if not isinstance(result, (dict, list, str)):
            result = {'result': str(result)}
        text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, default=str)
        return [types.TextContent(type='text', text=text)]

    return server


async def _serve(server: Server) -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run_mcp_server(server_name: str, tools: List[ToolSpec]) -> None:
    """Blocking entry point: serve MCP over stdio until the client disconnects."""
    _redirect_stdout_logging_to_stderr()
    asyncio.run(_serve(build_mcp_server(server_name, tools)))
