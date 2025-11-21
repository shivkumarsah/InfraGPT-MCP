#!/usr/bin/env python3
"""
Command-line interface for testing the Infrastructure MCP Server.
"""

import json
import asyncio
import sys
from typing import Dict, Any
from infra_mcp.server import InfraMcpServer


async def test_tool(server: InfraMcpServer, tool_name: str, arguments: Dict[str, Any] = None):
    """Test a specific tool."""
    if arguments is None:
        arguments = {}
    
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print('='*60)
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    response = await server.handle_request(request)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        result = response.get("result", {})
        content = result.get("content", [])
        if content and len(content) > 0:
            text = content[0].get("text", "")
            try:
                data = json.loads(text)
                print(json.dumps(data, indent=2, default=str))
            except json.JSONDecodeError:
                print(text)
        else:
            print("No content returned")


async def main():
    """Main CLI function."""
    print("\n" + "="*60)
    print("🚀 Infrastructure MCP Server - Test Client")
    print("="*60)
    
    server = InfraMcpServer()
    
    # Test initialization
    print("\n" + "="*60)
    print("Testing: Server Initialization")
    print("="*60)
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    
    response = await server.handle_request(init_request)
    print("✅ Initialization successful")
    print(json.dumps(response, indent=2))
    
    # Test tools list
    print("\n" + "="*60)
    print("Testing: Available Tools List")
    print("="*60)
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response = await server.handle_request(tools_request)
    tools = response.get("result", {}).get("tools", [])
    print(f"✅ Found {len(tools)} available tools:\n")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool['name']}")
        print(f"     {tool['description']}\n")
    
    # Test individual tools
    print("\n" + "="*60)
    print("🔧 TESTING ALL TOOLS")
    print("="*60)
    
    await test_tool(server, "get_system_info")
    await test_tool(server, "get_service_status")
    await test_tool(server, "get_user_info")
    await test_tool(server, "get_logs", {"log_type": "syslog", "lines": 10})
    await test_tool(server, "get_network_info")
    await test_tool(server, "analyze_logs", {"log_type": "syslog", "analysis_type": "summary", "lines": 20})
    await test_tool(server, "health_check", {"include_logs": True})
    
    print("\n" + "="*60)
    print("🎉 All tests completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

