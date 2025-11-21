"""
MCP Server for Infrastructure Monitoring

This server provides tools for monitoring system infrastructure including:
- Machine/VM log retrieval
- Service status monitoring  
- User details and session information
- AI-powered log analysis using Gemini LLM
"""

import json
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .mcp_types import (
    Tool, ToolListResult, ToolResult, InitializeResult, 
    ServerCapabilities, ToolCapability, McpRequest, McpResponse, McpError,
    dataclass_to_dict
)
from .infra_monitor import InfraMonitor
from .log_analyzer import LogAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfraMcpServer:
    """MCP Server for Infrastructure Monitoring."""
    
    def __init__(self):
        self.infra_monitor = InfraMonitor()
        self.log_analyzer = LogAnalyzer()
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize available MCP tools."""
        return [
            Tool(
                name="get_system_info",
                description="Get comprehensive system information including CPU, memory, disk usage, and uptime",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_service_status", 
                description="Get status of system services and running processes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Specific service name to check (optional)"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_user_info",
                description="Get user information including active sessions and system users",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_logs",
                description="Retrieve system logs with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_type": {
                            "type": "string",
                            "description": "Type of logs to retrieve",
                            "enum": ["syslog", "auth", "kernel", "dmesg"],
                            "default": "syslog"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of lines to retrieve",
                            "default": 100,
                            "minimum": 1,
                            "maximum": 1000
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_network_info",
                description="Get network interface information and active connections",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="analyze_logs",
                description="AI-powered log analysis using Gemini LLM",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_type": {
                            "type": "string",
                            "description": "Type of logs to analyze",
                            "enum": ["syslog", "auth", "kernel", "dmesg"],
                            "default": "syslog"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform",
                            "enum": ["summary", "errors", "security", "performance"],
                            "default": "summary"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of log lines to analyze",
                            "default": 100,
                            "minimum": 10,
                            "maximum": 500
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="health_check",
                description="Comprehensive system health analysis combining metrics and AI insights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_logs": {
                            "type": "boolean",
                            "description": "Include log analysis in health check",
                            "default": True
                        }
                    },
                    "required": []
                }
            )
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return await self._handle_tool_call(request_id, params)
            elif method == "prompts/list":
                return self._handle_prompts_list(request_id)
            elif method == "resources/list":
                return self._handle_resources_list(request_id)
            else:
                return self._create_error_response(
                    request_id, -32601, f"Method not found: {method}"
                )
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._create_error_response(
                request.get("id"), -32603, f"Internal error: {str(e)}"
            )
    
    def _handle_initialize(self, request_id: Union[str, int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        capabilities = ServerCapabilities(
            tools=ToolCapability(tools=True)
        )
        
        # Use the client's protocol version if provided, otherwise default to 2024-11-05
        # Claude Desktop uses 2025-06-18, we should match or use a compatible version
        client_version = params.get("protocolVersion", "2024-11-05")
        
        result = InitializeResult(
            protocolVersion=client_version,
            capabilities=capabilities,
            serverInfo={
                "name": "Infrastructure MCP Server",
                "version": "1.0.0",
                "description": "Infrastructure monitoring with AI-powered log analysis"
            }
        )
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": dataclass_to_dict(result)
        }
    
    def _handle_tools_list(self, request_id: Union[str, int]) -> Dict[str, Any]:
        """Handle tools/list request."""
        result = ToolListResult(tools=self.tools)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": dataclass_to_dict(result)
        }
    
    def _handle_prompts_list(self, request_id: Union[str, int]) -> Dict[str, Any]:
        """Handle prompts/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": []
            }
        }
    
    def _handle_resources_list(self, request_id: Union[str, int]) -> Dict[str, Any]:
        """Handle resources/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": []
            }
        }
    
    async def _handle_tool_call(self, request_id: Union[str, int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "get_system_info":
                result = self.infra_monitor.get_system_info()
            elif tool_name == "get_service_status":
                service_name = arguments.get("service_name")
                result = self.infra_monitor.get_service_status(service_name)
            elif tool_name == "get_user_info":
                result = self.infra_monitor.get_user_info()
            elif tool_name == "get_logs":
                log_type = arguments.get("log_type", "syslog")
                lines = arguments.get("lines", 100)
                result = self.infra_monitor.get_logs(log_type, lines)
            elif tool_name == "get_network_info":
                result = self.infra_monitor.get_network_info()
            elif tool_name == "analyze_logs":
                log_type = arguments.get("log_type", "syslog")
                analysis_type = arguments.get("analysis_type", "summary")
                lines = arguments.get("lines", 100)
                
                # Get logs first
                log_data = self.infra_monitor.get_logs(log_type, lines)
                logs = log_data.get("logs", [])
                
                # Analyze logs
                analysis = self.log_analyzer.analyze_logs(logs, analysis_type)
                result = {
                    "log_data": log_data,
                    "analysis": analysis
                }
            elif tool_name == "health_check":
                include_logs = arguments.get("include_logs", True)
                
                # Get system info
                system_info = self.infra_monitor.get_system_info()
                
                # Get logs if requested
                logs = []
                if include_logs:
                    log_data = self.infra_monitor.get_logs("syslog", 50)
                    logs = log_data.get("logs", [])
                
                # Perform health analysis
                health_analysis = self.log_analyzer.analyze_system_health(system_info, logs)
                
                result = {
                    "system_info": system_info,
                    "health_analysis": health_analysis,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return self._create_error_response(
                    request_id, -32601, f"Unknown tool: {tool_name}"
                )
            
            # Format result for MCP
            tool_result = ToolResult(
                content=[{
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str)
                }]
            )
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": dataclass_to_dict(tool_result)
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return self._create_error_response(
                request_id, -32603, f"Tool execution error: {str(e)}"
            )
    
    def _create_error_response(self, request_id: Union[str, int], code: int, message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


class StdioMcpServer:
    """MCP Server that communicates via stdio."""
    
    def __init__(self):
        self.server = InfraMcpServer()
    
    def run(self):
        """Run the MCP server with stdio transport."""
        # Write to stderr so Claude Desktop can see it in logs
        print("Starting Infrastructure MCP Server...", file=sys.stderr, flush=True)
        logger.info("Starting Infrastructure MCP Server...")
        
        try:
            while True:
                # Read line from stdin
                try:
                    line = sys.stdin.readline()
                except Exception as e:
                    print(f"Error reading stdin: {e}", file=sys.stderr, flush=True)
                    logger.error(f"Error reading stdin: {e}")
                    break
                
                if not line:
                    print("EOF received on stdin, server stopping", file=sys.stderr, flush=True)
                    logger.info("EOF received, server stopping")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse JSON request
                    request = json.loads(line)
                    method = request.get('method', 'unknown')
                    request_id = request.get('id', 'none')
                    
                    print(f"Received request: {method} (id: {request_id})", file=sys.stderr, flush=True)
                    logger.info(f"Received: {method} (id: {request_id})")
                    
                    # Handle notifications (no response needed)
                    if 'id' not in request:
                        # For notifications, we don't send a response
                        if method == 'notifications/initialized':
                            print("Client sent initialized notification", file=sys.stderr, flush=True)
                            logger.info("Client initialized successfully")
                        else:
                            print(f"Received notification: {method}", file=sys.stderr, flush=True)
                            logger.info(f"Received notification: {method}")
                        continue
                    
                    # Handle request (make it synchronous)
                    response = asyncio.run(self.server.handle_request(request))
                    
                    # Send response
                    response_str = json.dumps(response)
                    print(response_str)
                    sys.stdout.flush()
                    
                    print(f"Sent response for: {method} ({len(response_str)} bytes)", file=sys.stderr, flush=True)
                    logger.info(f"Sent response for: {method}")
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}", file=sys.stderr, flush=True)
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                except Exception as e:
                    print(f"Error processing request: {e}", file=sys.stderr, flush=True)
                    logger.error(f"Error processing request: {e}")
                    
        except KeyboardInterrupt:
            print("Server stopped by user (KeyboardInterrupt)", file=sys.stderr, flush=True)
            logger.info("Server stopped by user")
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr, flush=True)
            logger.error(f"Server error: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
        finally:
            print("Infrastructure MCP Server stopped", file=sys.stderr, flush=True)
            logger.info("Infrastructure MCP Server stopped")


def main():
    """Main entry point for the MCP server."""
    server = StdioMcpServer()
    server.run()


if __name__ == "__main__":
    main()

