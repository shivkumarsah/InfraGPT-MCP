# Infrastructure MCP Server - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Desktop                            │
│                    (MCP Client / AI Assistant)                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ JSON-RPC over stdio
                           │ (MCP Protocol v1.0)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure MCP Server                     │
│                         (infra_mcp)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐         ┌──────────────────┐              │
│  │  StdioMcpServer │◄────────┤  InfraMcpServer  │              │
│  │  (Transport)    │         │  (Core Logic)    │              │
│  └─────────────────┘         └──────────────────┘              │
│         │                             │                         │
│         │                     ┌───────┴────────┐               │
│         │                     ▼                ▼                │
│         │            ┌─────────────┐  ┌────────────────┐       │
│         │            │InfraMonitor │  │ LogAnalyzer    │       │
│         │            │(System Data)│  │(AI Analysis)   │       │
│         │            └─────────────┘  └────────────────┘       │
│         │                     │                ▼                │
│         └─────────────────────┼─────────  Gemini API           │
│                               │         (Optional)              │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      macOS/Linux System                          │
├─────────────────────────────────────────────────────────────────┤
│  • CPU, Memory, Disk (psutil)                                   │
│  • System Logs (/var/log/*)                                     │
│  • Services (systemctl)                                         │
│  • Network Interfaces (psutil)                                  │
│  • User Sessions (psutil)                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. MCP Server Layer (`server.py`)

**Responsibilities:**
- JSON-RPC request handling
- MCP protocol implementation
- Request routing
- Response formatting
- Error handling

**Key Classes:**
- `InfraMcpServer` - Core MCP logic
- `StdioMcpServer` - stdio transport

**MCP Methods Supported:**
- `initialize` - Server initialization
- `tools/list` - List available tools
- `tools/call` - Execute tools
- `prompts/list` - Empty (not used)
- `resources/list` - Empty (not used)

### 2. Infrastructure Monitor (`infra_monitor.py`)

**Purpose:** Collect system information and metrics

**Key Class:** `InfraMonitor`

**Methods:**
- `get_system_info()` - CPU, memory, disk, uptime
- `get_service_status(service_name)` - Services & processes
- `get_user_info()` - Active sessions & system users
- `get_logs(log_type, lines)` - System log retrieval
- `get_network_info()` - Network interfaces & connections

**Data Sources:**
- `psutil` - System metrics
- `/var/log/*` - Log files
- `systemctl` - Service status
- `/etc/passwd` - User information
- `dmesg` - Kernel messages

### 3. Log Analyzer (`log_analyzer.py`)

**Purpose:** AI-powered log analysis

**Key Class:** `LogAnalyzer`

**Features:**
- **Mock Mode** - Pattern-based analysis (no API required)
- **AI Mode** - Google Gemini LLM integration
- **Multiple Analysis Types:**
  - Summary - Overall assessment
  - Errors - Error detection
  - Security - Security events
  - Performance - Performance insights

**Methods:**
- `analyze_logs(logs, analysis_type)` - Log analysis
- `analyze_system_health(system_info, logs)` - Health assessment

### 4. MCP Types (`mcp_types.py`)

**Purpose:** MCP protocol data structures

**Key Components:**
- Protocol types (Tool, ToolResult, etc.)
- Request/Response structures
- Serialization helpers
- Type definitions

## Data Flow

### Tool Execution Flow

```
1. Claude Desktop Request
   │
   ├─► JSON-RPC over stdin
   │
2. StdioMcpServer receives
   │
   ├─► Parse JSON
   ├─► Extract method & params
   │
3. InfraMcpServer handles
   │
   ├─► Route to handler
   ├─► Validate parameters
   │
4. Execute Tool
   │
   ├─► InfraMonitor (system data)
   │   OR
   └─► LogAnalyzer (AI analysis)
       │
       ├─► Mock Mode (local patterns)
       │   OR
       └─► Gemini API (real AI)
   │
5. Format Response
   │
   ├─► Create ToolResult
   ├─► Serialize to JSON
   │
6. Return via stdout
   │
   └─► JSON-RPC response
       │
7. Claude Desktop receives
   │
   └─► Display to user
```

### Log Analysis Flow

```
User Question
    │
    ▼
Claude decides to analyze logs
    │
    ├─► Call: get_logs(log_type, lines)
    │   └─► Returns: raw log data
    │
    ├─► Call: analyze_logs(log_type, analysis_type)
    │   │
    │   ├─► Get logs from InfraMonitor
    │   │
    │   └─► LogAnalyzer.analyze_logs()
    │       │
    │       ├─► Check for API key
    │       │
    │       ├─► Mock Mode (no API key)
    │       │   ├─► Pattern detection
    │       │   ├─► Count errors/warnings
    │       │   └─► Generate insights
    │       │
    │       └─► AI Mode (with API key)
    │           ├─► Prepare prompt
    │           ├─► Call Gemini API
    │           └─► Format response
    │
    └─► Return analysis to Claude
        │
        └─► Claude presents to user
```

## Tool Implementation

### Tool Registration

```python
tools = [
    Tool(
        name="get_system_info",
        description="Get system information...",
        inputSchema={...}
    ),
    ...
]
```

### Tool Execution

```python
if tool_name == "get_system_info":
    result = self.infra_monitor.get_system_info()
elif tool_name == "analyze_logs":
    logs = self.infra_monitor.get_logs(...)
    analysis = self.log_analyzer.analyze_logs(logs, ...)
    result = {"log_data": logs, "analysis": analysis}
```

## Dependencies & Libraries

```
┌─────────────────────────────────────┐
│      Python 3.8+ Runtime            │
├─────────────────────────────────────┤
│                                     │
│  Core Libraries:                    │
│  • psutil ────────► System metrics  │
│  • json ──────────► Serialization   │
│  • asyncio ───────► Async handling  │
│  • subprocess ────► System commands │
│  • logging ───────► Debug/info      │
│                                     │
│  Optional:                          │
│  • google-generativeai → Gemini API│
│                                     │
└─────────────────────────────────────┘
```

## Configuration

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "infra-monitor": {
      "command": "python3",
      "args": ["-m", "infra_mcp.server"],
      "cwd": "/path/to/project",
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

### Environment Variables

- `GEMINI_API_KEY` - Google Gemini API key (optional)
- `LOG_LEVEL` - Logging level (default: INFO)
- `PYTHONPATH` - Python module path

## Security Architecture

### Access Control

```
┌─────────────────────────────────────┐
│         Security Layers             │
├─────────────────────────────────────┤
│                                     │
│  1. Process Isolation               │
│     └─► Runs as user process        │
│                                     │
│  2. Permission Handling             │
│     └─► Graceful fallback           │
│                                     │
│  3. Data Privacy                    │
│     ├─► Local processing first      │
│     └─► Optional external API       │
│                                     │
│  4. No Data Storage                 │
│     └─► Ephemeral processing        │
│                                     │
└─────────────────────────────────────┘
```

### Permission Model

```
System Resource          Permission    Fallback
────────────────────────────────────────────────
CPU/Memory/Disk          User          None
Running Processes        User          Limited list
System Logs              Read          tail command
Service Status           User/sudo     Partial
Network Info             User          Limited
User Sessions            User          Current only
```

## Performance Characteristics

### Resource Usage

- **Memory**: ~50-100 MB (idle)
- **CPU**: <1% (idle), 5-15% (during analysis)
- **Startup**: ~1-2 seconds
- **Response Time**: 
  - System info: <1 second
  - Log retrieval: 1-2 seconds
  - AI analysis: 2-5 seconds (Gemini) / <1 second (mock)

### Scalability

- **Concurrent Requests**: Handles one at a time (stdio)
- **Log Size**: Configured limits (1-1000 lines)
- **Process List**: Limited to top 10 by CPU

## Error Handling

```
Error Type              Handler             User Impact
────────────────────────────────────────────────────────
Permission Denied       Try alternatives    Partial data
File Not Found          Return empty        No data
API Timeout             Mock fallback       Mock analysis
Invalid JSON            Parse error         Error message
Missing Tool            Error response      Tool not found
System Error            Log & return        Error message
```

## Extension Points

### Adding New Tools

1. Define tool in `_initialize_tools()`
2. Add handler in `_handle_tool_call()`
3. Implement logic in `InfraMonitor` or `LogAnalyzer`
4. Update documentation

### Adding Analysis Types

1. Add to `analyze_logs()` prompts
2. Create mock analysis template
3. Update tool schema enum
4. Test with `test_client.py`

## Testing Architecture

```
Test Client (test_client.py)
    │
    ├─► Initialize Server
    ├─► List Tools
    ├─► Test Each Tool
    │   ├─► get_system_info
    │   ├─► get_service_status
    │   ├─► get_user_info
    │   ├─► get_logs
    │   ├─► get_network_info
    │   ├─► analyze_logs
    │   └─► health_check
    │
    └─► Verify Responses
```

## Deployment Model

```
Development:
  Local Python ─► Direct execution ─► Test client

Production:
  Claude Desktop ─► stdio MCP ─► InfraGPT-MCP

Alternative:
  Any MCP Client ─► stdio MCP ─► InfraGPT-MCP
```

## Version Compatibility

| Component | Version | Status |
|-----------|---------|--------|
| MCP Protocol | 1.0 | ✅ Supported |
| Python | 3.8+ | ✅ Required |
| Claude Desktop | Latest | ✅ Tested |
| macOS | 11+ | ✅ Tested |
| Linux | Most distros | ✅ Expected |

---

**Architecture Version**: 1.0  
**Last Updated**: November 21, 2025  
**Status**: Stable ✅

