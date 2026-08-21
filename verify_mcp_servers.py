#!/usr/bin/env python3
"""
Verification harness for the MCP protocol conversion (Silver #5, Gold #3/#6).

Acts as a REAL MCP CLIENT. For each of the three servers it:
  1. spawns `python <server>.py --mcp` as a subprocess,
  2. connects over stdio using the official mcp SDK client,
  3. performs the JSON-RPC `initialize` handshake (proves protocol, not CLI),
  4. calls `list_tools` (proves tools are registered/advertised),
  5. calls one dry-run tool (proves round-trip request/response works).

This is end-to-end proof the mcp_*.py files are genuine MCP servers speaking
JSON-RPC over stdio — not argparse scripts.

SAFETY:
  - Forces DRY_RUN=true + PAYMENT_APPROVAL_THRESHOLD=100 in the CHILD env, so no
    real email/payment/post occurs. The odoo probe deliberately calls
    record_payment($5000, new payee) and asserts the security gate REFUSES it
    (requires_approval) — proving the gate is enforced across the MCP boundary.

Run:  python verify_mcp_servers.py
Exit: 0 = PASS (all three servers speak MCP + behave correctly), 1 = FAIL, 2 = could not run.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

VAULT = Path(__file__).parent.resolve()
sys.path.insert(0, str(VAULT))

# Child servers inherit this env; dry-run ON, deterministic threshold.
CHILD_ENV = {**os.environ, 'DRY_RUN': 'true', 'PAYMENT_APPROVAL_THRESHOLD': '100'}

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

PER_SERVER_TIMEOUT = 180  # generous: `import mcp` alone is ~15s in the child


def _texts(call_result):
    out = []
    for c in getattr(call_result, 'content', []) or []:
        if getattr(c, 'type', None) == 'text':
            out.append(c.text)
    return out


async def probe(server_file, expected_name, expected_tools, call_name, call_args):
    """Spawn one server, handshake, list tools, call one tool. Return a report dict."""
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(VAULT / server_file), '--mcp'],
        env=CHILD_ENV,
        cwd=str(VAULT),
    )
    report = {'server': server_file, 'ok': False, 'steps': []}
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            got_name = init.serverInfo.name
            report['server_name'] = got_name
            report['protocol_version'] = getattr(init, 'protocolVersion', None)
            report['steps'].append(('initialize handshake', got_name == expected_name,
                                     f'serverInfo.name={got_name!r} (expected {expected_name!r})'))

            tools_resp = await session.list_tools()
            got_tools = sorted(t.name for t in tools_resp.tools)
            report['tools'] = got_tools
            report['steps'].append(('list_tools', got_tools == sorted(expected_tools),
                                    f'{got_tools} (expected {sorted(expected_tools)})'))

            call_result = await session.call_tool(call_name, call_args)
            texts = _texts(call_result)
            report['call_name'] = call_name
            report['call_texts'] = texts
            report['call_isError'] = bool(getattr(call_result, 'isError', False))
            # A well-formed call returns at least one text content block that parses.
            parsed = None
            if texts:
                try:
                    parsed = json.loads(texts[0])
                except json.JSONDecodeError:
                    parsed = None
            report['call_parsed'] = parsed
            report['steps'].append((f'call_tool({call_name})', bool(texts),
                                    f'isError={report["call_isError"]}, content_blocks={len(texts)}'))
            report['ok'] = all(ok for _, ok, _ in report['steps'])
            return report


async def run():
    plan = [
        dict(
            server_file='mcp_email.py',
            expected_name='ai-employee-email',
            expected_tools=['send_email', 'list_emails', 'draft_email'],
            call_name='draft_email',
            call_args={'to': 'mcp-test@example.com', 'subject': 'MCP proof',
                       'body': 'Written by verify_mcp_servers.py over the MCP protocol.'},
            extra_check=lambda p: (p['call_parsed'] or {}).get('success') is True,
            extra_desc='draft_email returned success=True',
        ),
        dict(
            server_file='mcp_odoo.py',
            expected_name='ai-employee-odoo',
            expected_tools=['create_invoice', 'get_leads', 'update_lead', 'record_payment'],
            call_name='record_payment',
            call_args={'invoice_id': 999, 'amount': 5000.0, 'partner_id': 2, 'payee_known': False},
            # Proof the security gate is enforced ACROSS the MCP boundary:
            extra_check=lambda p: (p['call_parsed'] or {}).get('requires_approval') is True
                                  and (p['call_parsed'] or {}).get('success') is False,
            extra_desc='record_payment($5000,new payee) BLOCKED by gate (requires_approval, success=False)',
        ),
        dict(
            server_file='mcp_social.py',
            expected_name='ai-employee-social',
            expected_tools=['post_social', 'draft_social', 'get_platform_status'],
            call_name='get_platform_status',
            call_args={},
            extra_check=lambda p: p['call_parsed'] is not None,
            extra_desc='get_platform_status returned a JSON object',
        ),
    ]

    print('=' * 74)
    print('MCP PROTOCOL SERVER VERIFICATION (real MCP client over stdio)')
    print(f'vault    : {VAULT}')
    print(f'python   : {sys.executable}')
    print(f'DRY_RUN  : {CHILD_ENV["DRY_RUN"]}  (child env)  timeout={PER_SERVER_TIMEOUT}s/server')
    print('=' * 74)

    all_ok = True
    for spec in plan:
        sf = spec['server_file']
        print(f'\n----- {sf}  ->  {spec["expected_name"]} -----')
        try:
            report = await asyncio.wait_for(
                probe(sf, spec['expected_name'], spec['expected_tools'],
                      spec['call_name'], spec['call_args']),
                timeout=PER_SERVER_TIMEOUT,
            )
        except asyncio.TimeoutError:
            print(f'  FAIL  timed out after {PER_SERVER_TIMEOUT}s')
            all_ok = False
            continue
        except Exception as e:
            print(f'  FAIL  {type(e).__name__}: {e}')
            all_ok = False
            continue

        for label, ok, detail in report['steps']:
            print(f'  {"PASS" if ok else "FAIL":4}  {label:28} {detail}')
        # extra semantic check
        extra_ok = bool(spec['extra_check'](report))
        print(f'  {"PASS" if extra_ok else "FAIL":4}  {"semantic":28} {spec["extra_desc"]}')
        if report.get('call_parsed') is not None:
            print(f'        call result: {json.dumps(report["call_parsed"], ensure_ascii=False)[:200]}')
        server_ok = report['ok'] and extra_ok
        all_ok = all_ok and server_ok
        print(f'  => {sf}: {"PASS" if server_ok else "FAIL"}')

    print('\n' + '=' * 74)
    print('RESULT:', 'PASS - all three servers speak real MCP protocol over stdio'
          if all_ok else 'FAIL - see per-server output above')
    print('=' * 74)
    return 0 if all_ok else 1


if __name__ == '__main__':
    try:
        sys.exit(asyncio.run(run()))
    except Exception as e:
        print(f'[ABORT] harness could not run: {type(e).__name__}: {e}')
        sys.exit(2)
