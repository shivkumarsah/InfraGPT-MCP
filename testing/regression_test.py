#!/usr/bin/env python3
"""
Comprehensive Regression Test Suite for Infrastructure MCP Server

Tests all functionality including:
- Server initialization
- All 7 MCP tools
- LLM modes (Ollama, Gemini, Mock)
- Error handling
- Edge cases
"""

import json
import asyncio
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from infra_mcp.server import InfraMcpServer
from infra_mcp.log_analyzer import LogAnalyzer


class RegressionTest:
    """Comprehensive regression test suite."""
    
    def __init__(self):
        self.server = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if passed:
            self.tests_passed += 1
            print(f"{status}: {test_name}")
        else:
            self.tests_failed += 1
            print(f"{status}: {test_name}")
            if message:
                print(f"      Error: {message}")
    
    async def test_server_initialization(self):
        """Test 1: Server initialization."""
        print("\n" + "="*70)
        print("TEST SUITE 1: SERVER INITIALIZATION")
        print("="*70)
        
        try:
            self.server = InfraMcpServer()
            self.log_test("Server instantiation", True)
        except Exception as e:
            self.log_test("Server instantiation", False, str(e))
            return False
        
        # Check tools loaded
        try:
            tools_count = len(self.server.tools)
            expected = 7
            if tools_count == expected:
                self.log_test(f"Tools loaded ({tools_count}/7)", True)
            else:
                self.log_test(f"Tools loaded", False, f"Expected {expected}, got {tools_count}")
        except Exception as e:
            self.log_test("Tools loaded", False, str(e))
        
        # Check tool names
        expected_tools = [
            "get_system_info", "get_service_status", "get_user_info",
            "get_logs", "get_network_info", "analyze_logs", "health_check"
        ]
        try:
            tool_names = [tool.name for tool in self.server.tools]
            all_present = all(name in tool_names for name in expected_tools)
            if all_present:
                self.log_test("All expected tools present", True)
            else:
                missing = set(expected_tools) - set(tool_names)
                self.log_test("All expected tools present", False, f"Missing: {missing}")
        except Exception as e:
            self.log_test("All expected tools present", False, str(e))
        
        return True
    
    async def test_mcp_protocol(self):
        """Test 2: MCP protocol compliance."""
        print("\n" + "="*70)
        print("TEST SUITE 2: MCP PROTOCOL")
        print("="*70)
        
        # Test initialize request
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            }
            response = await self.server.handle_request(request)
            
            # Validate response structure
            if "jsonrpc" in response and response["jsonrpc"] == "2.0":
                self.log_test("Initialize: JSON-RPC version", True)
            else:
                self.log_test("Initialize: JSON-RPC version", False, "Missing or wrong version")
            
            if "id" in response and response["id"] == 1:
                self.log_test("Initialize: Response ID matches", True)
            else:
                self.log_test("Initialize: Response ID matches", False)
            
            if "result" in response:
                result = response["result"]
                if "protocolVersion" in result:
                    self.log_test("Initialize: Protocol version in response", True)
                else:
                    self.log_test("Initialize: Protocol version in response", False)
                
                if "serverInfo" in result:
                    self.log_test("Initialize: Server info in response", True)
                else:
                    self.log_test("Initialize: Server info in response", False)
            else:
                self.log_test("Initialize: Has result", False, "No result field")
                
        except Exception as e:
            self.log_test("Initialize request", False, str(e))
        
        # Test tools/list request
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            response = await self.server.handle_request(request)
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                self.log_test(f"Tools list: Returns {len(tools)} tools", len(tools) == 7)
            else:
                self.log_test("Tools list", False, "No tools in response")
                
        except Exception as e:
            self.log_test("Tools list request", False, str(e))
    
    async def test_system_info_tool(self):
        """Test 3: get_system_info tool."""
        print("\n" + "="*70)
        print("TEST SUITE 3: SYSTEM INFO TOOL")
        print("="*70)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_system_info",
                    "arguments": {}
                }
            }
            response = await self.server.handle_request(request)
            
            if "result" in response:
                result = response["result"]
                content = result.get("content", [])
                if content:
                    data = json.loads(content[0]["text"])
                    
                    # Check expected fields
                    expected_fields = ["hostname", "platform", "cpu_count", "cpu_percent", 
                                     "memory", "disk", "uptime"]
                    for field in expected_fields:
                        if field in data:
                            self.log_test(f"System info: Has {field}", True)
                        else:
                            self.log_test(f"System info: Has {field}", False)
                else:
                    self.log_test("System info: Has content", False)
            else:
                self.log_test("System info: Tool execution", False, "No result")
                
        except Exception as e:
            self.log_test("System info tool", False, str(e))
    
    async def test_service_status_tool(self):
        """Test 4: get_service_status tool."""
        print("\n" + "="*70)
        print("TEST SUITE 4: SERVICE STATUS TOOL")
        print("="*70)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_service_status",
                    "arguments": {}
                }
            }
            response = await self.server.handle_request(request)
            
            if "result" in response:
                result = response["result"]
                content = result.get("content", [])
                if content:
                    data = json.loads(content[0]["text"])
                    
                    if "total_processes" in data:
                        self.log_test("Service status: Has process count", True)
                    else:
                        self.log_test("Service status: Has process count", False)
                    
                    if "top_processes" in data:
                        self.log_test("Service status: Has top processes", True)
                    else:
                        self.log_test("Service status: Has top processes", False)
                else:
                    self.log_test("Service status: Has content", False)
            else:
                self.log_test("Service status: Tool execution", False)
                
        except Exception as e:
            self.log_test("Service status tool", False, str(e))
    
    async def test_user_info_tool(self):
        """Test 5: get_user_info tool."""
        print("\n" + "="*70)
        print("TEST SUITE 5: USER INFO TOOL")
        print("="*70)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "get_user_info",
                    "arguments": {}
                }
            }
            response = await self.server.handle_request(request)
            
            if "result" in response:
                result = response["result"]
                content = result.get("content", [])
                if content:
                    data = json.loads(content[0]["text"])
                    
                    if "current_user" in data:
                        self.log_test("User info: Has current user", True)
                    else:
                        self.log_test("User info: Has current user", False)
                    
                    self.log_test("User info: Tool execution", True)
                else:
                    self.log_test("User info: Has content", False)
            else:
                self.log_test("User info: Tool execution", False)
                
        except Exception as e:
            self.log_test("User info tool", False, str(e))
    
    async def test_logs_tool(self):
        """Test 6: get_logs tool."""
        print("\n" + "="*70)
        print("TEST SUITE 6: LOGS TOOL")
        print("="*70)
        
        # Test with different log types
        log_types = ["syslog", "dmesg"]
        for log_type in log_types:
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "get_logs",
                        "arguments": {
                            "log_type": log_type,
                            "lines": 10
                        }
                    }
                }
                response = await self.server.handle_request(request)
                
                if "result" in response:
                    result = response["result"]
                    content = result.get("content", [])
                    if content:
                        data = json.loads(content[0]["text"])
                        if "log_type" in data and data["log_type"] == log_type:
                            self.log_test(f"Logs: {log_type} execution", True)
                        else:
                            self.log_test(f"Logs: {log_type} execution", False)
                    else:
                        self.log_test(f"Logs: {log_type} has content", False)
                else:
                    self.log_test(f"Logs: {log_type} tool", False)
                    
            except Exception as e:
                self.log_test(f"Logs: {log_type} tool", False, str(e))
    
    async def test_network_info_tool(self):
        """Test 7: get_network_info tool."""
        print("\n" + "="*70)
        print("TEST SUITE 7: NETWORK INFO TOOL")
        print("="*70)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "get_network_info",
                    "arguments": {}
                }
            }
            response = await self.server.handle_request(request)
            
            if "result" in response:
                result = response["result"]
                content = result.get("content", [])
                if content:
                    data = json.loads(content[0]["text"])
                    
                    if "interfaces" in data:
                        self.log_test("Network info: Has interfaces", True)
                    else:
                        self.log_test("Network info: Has interfaces", False)
                    
                    if "io_counters" in data:
                        self.log_test("Network info: Has I/O counters", True)
                    else:
                        self.log_test("Network info: Has I/O counters", False)
                else:
                    self.log_test("Network info: Has content", False)
            else:
                self.log_test("Network info: Tool execution", False)
                
        except Exception as e:
            self.log_test("Network info tool", False, str(e))
    
    async def test_analyze_logs_tool(self):
        """Test 8: analyze_logs tool."""
        print("\n" + "="*70)
        print("TEST SUITE 8: ANALYZE LOGS TOOL")
        print("="*70)
        
        analysis_types = ["summary", "errors", "security", "performance"]
        for analysis_type in analysis_types:
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": 8,
                    "method": "tools/call",
                    "params": {
                        "name": "analyze_logs",
                        "arguments": {
                            "log_type": "syslog",
                            "analysis_type": analysis_type,
                            "lines": 20
                        }
                    }
                }
                response = await self.server.handle_request(request)
                
                if "result" in response:
                    result = response["result"]
                    content = result.get("content", [])
                    if content:
                        data = json.loads(content[0]["text"])
                        if "analysis" in data:
                            analysis = data["analysis"]
                            if "analysis_type" in analysis and analysis["analysis_type"] == analysis_type:
                                self.log_test(f"Analyze logs: {analysis_type}", True)
                            else:
                                self.log_test(f"Analyze logs: {analysis_type}", False)
                        else:
                            self.log_test(f"Analyze logs: {analysis_type} has analysis", False)
                    else:
                        self.log_test(f"Analyze logs: {analysis_type} has content", False)
                else:
                    self.log_test(f"Analyze logs: {analysis_type}", False)
                    
            except Exception as e:
                self.log_test(f"Analyze logs: {analysis_type}", False, str(e))
    
    async def test_health_check_tool(self):
        """Test 9: health_check tool."""
        print("\n" + "="*70)
        print("TEST SUITE 9: HEALTH CHECK TOOL")
        print("="*70)
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "health_check",
                    "arguments": {
                        "include_logs": True
                    }
                }
            }
            response = await self.server.handle_request(request)
            
            if "result" in response:
                result = response["result"]
                content = result.get("content", [])
                if content:
                    data = json.loads(content[0]["text"])
                    
                    if "system_info" in data:
                        self.log_test("Health check: Has system info", True)
                    else:
                        self.log_test("Health check: Has system info", False)
                    
                    if "health_analysis" in data:
                        self.log_test("Health check: Has health analysis", True)
                    else:
                        self.log_test("Health check: Has health analysis", False)
                else:
                    self.log_test("Health check: Has content", False)
            else:
                self.log_test("Health check: Tool execution", False)
                
        except Exception as e:
            self.log_test("Health check tool", False, str(e))
    
    async def test_llm_modes(self):
        """Test 10: LLM mode detection."""
        print("\n" + "="*70)
        print("TEST SUITE 10: LLM MODE DETECTION")
        print("="*70)
        
        try:
            analyzer = LogAnalyzer()
            
            # Check which mode is active
            if hasattr(analyzer, 'llm_mode'):
                mode = analyzer.llm_mode
                self.log_test(f"LLM mode detected: {mode}", True, f"Using {mode}")
                
                # Verify mode is one of expected values
                valid_modes = ["ollama", "gemini", "mock"]
                if mode in valid_modes:
                    self.log_test("LLM mode is valid", True)
                else:
                    self.log_test("LLM mode is valid", False, f"Unknown mode: {mode}")
            else:
                self.log_test("LLM mode attribute exists", False)
                
        except Exception as e:
            self.log_test("LLM mode detection", False, str(e))
    
    async def test_error_handling(self):
        """Test 11: Error handling."""
        print("\n" + "="*70)
        print("TEST SUITE 11: ERROR HANDLING")
        print("="*70)
        
        # Test invalid method
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "invalid_method",
                "params": {}
            }
            response = await self.server.handle_request(request)
            
            if "error" in response:
                self.log_test("Error handling: Invalid method returns error", True)
            else:
                self.log_test("Error handling: Invalid method returns error", False)
                
        except Exception as e:
            self.log_test("Error handling: Invalid method", False, str(e))
        
        # Test invalid tool
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {
                    "name": "invalid_tool",
                    "arguments": {}
                }
            }
            response = await self.server.handle_request(request)
            
            if "error" in response:
                self.log_test("Error handling: Invalid tool returns error", True)
            else:
                self.log_test("Error handling: Invalid tool returns error", False)
                
        except Exception as e:
            self.log_test("Error handling: Invalid tool", False, str(e))
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("REGRESSION TEST SUMMARY")
        print("="*70)
        
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        if self.tests_failed > 0:
            print("\n⚠️  Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  ❌ {result['test']}")
                    if result["message"]:
                        print(f"     {result['message']}")
        
        print("\n" + "="*70)
        
        # Save results to file
        report_file = "regression_test_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": self.tests_passed,
                    "failed": self.tests_failed,
                    "pass_rate": pass_rate
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.tests_failed == 0
    
    async def run_all_tests(self):
        """Run all regression tests."""
        print("\n" + "="*70)
        print("INFRASTRUCTURE MCP SERVER - REGRESSION TEST SUITE")
        print("="*70)
        print(f"Started: {datetime.now().isoformat()}")
        print("="*70)
        
        # Run test suites
        await self.test_server_initialization()
        await self.test_mcp_protocol()
        await self.test_system_info_tool()
        await self.test_service_status_tool()
        await self.test_user_info_tool()
        await self.test_logs_tool()
        await self.test_network_info_tool()
        await self.test_analyze_logs_tool()
        await self.test_health_check_tool()
        await self.test_llm_modes()
        await self.test_error_handling()
        
        # Print summary
        success = self.print_summary()
        
        return success


async def main():
    """Main entry point."""
    test = RegressionTest()
    success = await test.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

