# Infrastructure MCP Server - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Desktop                            │
│                    (MCP Client / AI Assistant)                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ JSON-RPC over stdio
                           │ (MCP Protocol 2025-06-18)
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
│         │            └─────────────┘  └────────┬───────┘       │
│         │                     │                │                │
│         │                     │        ┌───────┴────────┐       │
│         │                     │        │  LLM Priority: │       │
│         │                     │        │  1. Ollama ✅  │       │
│         │                     │        │  2. Gemini     │       │
│         │                     │        │  3. Mock       │       │
│         │                     │        └───────┬────────┘       │
│         └─────────────────────┼────────────────┘                │
│                               │                                 │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                ┌───────────────┼────────────────┐
                ▼               ▼                ▼
        ┌───────────┐  ┌────────────┐  ┌──────────────┐
        │  Ollama   │  │ Gemini API │  │  Mock Mode   │
        │  (Local)  │  │ (Cloud)    │  │  (Patterns)  │
        │ PRIMARY ✅│  │  Fallback  │  │   Fallback   │
        └─────┬─────┘  └─────┬──────┘  └──────────────┘
              │              │
              ▼              ▼
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

**Purpose:** AI-powered log analysis with intelligent LLM fallback

**Key Class:** `LogAnalyzer`

**LLM Integration Strategy:**
1. **Ollama (Primary)** - Local LLM for privacy-first analysis
   - Runs on http://localhost:11434
   - No data leaves your machine
   - No API costs
   - Offline capability
   - Auto-detects available models

2. **Gemini (Fallback)** - Cloud AI when Ollama unavailable
   - Google Generative AI
   - Requires API key
   - Fallback if Ollama fails

3. **Mock Mode (Last Resort)** - Pattern-based analysis
   - No external dependencies
   - Regex pattern matching
   - Always available

**Features:**
- **Multiple Analysis Types:**
  - Summary - Overall assessment
  - Errors - Error detection
  - Security - Security events
  - Performance - Performance insights
- **Automatic LLM Detection:**
  - Checks Ollama availability on startup
  - Discovers installed models
  - Falls back gracefully if unavailable

**Methods:**
- `analyze_logs(logs, analysis_type)` - Log analysis with LLM priority
- `analyze_system_health(system_info, logs)` - Health assessment
- `_call_ollama_api(prompt)` - Ollama API integration
- `_initialize_ollama()` - Ollama detection and configuration

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

### Log Analysis Flow (with Ollama Priority)

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
    │       ├─► PRIORITY 1: Try Ollama (Local LLM) ✅
    │       │   │
    │       │   ├─► Check: http://localhost:11434/api/tags
    │       │   │
    │       │   ├─► If Available:
    │       │   │   ├─► Prepare prompt
    │       │   │   ├─► POST to /api/generate
    │       │   │   ├─► Stream response
    │       │   │   └─► Return AI analysis ✅
    │       │   │
    │       │   └─► If Failed: Continue to Priority 2
    │       │
    │       ├─► PRIORITY 2: Try Gemini (Cloud API)
    │       │   │
    │       │   ├─► Check: GEMINI_API_KEY exists
    │       │   │
    │       │   ├─► If Available:
    │       │   │   ├─► Initialize Gemini client
    │       │   │   ├─► Call Gemini API
    │       │   │   └─► Return AI analysis
    │       │   │
    │       │   └─► If Failed: Continue to Priority 3
    │       │
    │       └─► PRIORITY 3: Mock Mode (Pattern-Based)
    │           │
    │           ├─► Pattern detection (ERROR, WARNING, CRITICAL)
    │           ├─► Count occurrences
    │           ├─► Extract key information
    │           ├─► Generate template insights
    │           └─► Return mock analysis
    │
    └─► Return analysis to Claude
        │
        └─► Claude presents to user
```

**LLM Selection Logic:**
```
┌─────────────────────────────────────────┐
│  Is Ollama running on localhost:11434?  │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
       YES           NO
        │             │
        ▼             ▼
  ┌──────────┐  ┌────────────────┐
  │  Ollama  │  │ Try Gemini API │
  │   Mode   │  └────────┬───────┘
  │ ✅ LOCAL │           │
  └──────────┘    ┌──────┴──────┐
                  │             │
                 YES           NO
                  │             │
                  ▼             ▼
            ┌──────────┐  ┌──────────┐
            │  Gemini  │  │   Mock   │
            │   Mode   │  │   Mode   │
            │  CLOUD   │  │ PATTERN  │
            └──────────┘  └──────────┘
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
┌─────────────────────────────────────────────┐
│         Python 3.8+ Runtime                 │
├─────────────────────────────────────────────┤
│                                             │
│  Core Libraries:                            │
│  • psutil ────────────► System metrics      │
│  • requests ──────────► Ollama API calls    │
│  • json ──────────────► Serialization       │
│  • asyncio ───────────► Async handling      │
│  • subprocess ────────► System commands     │
│  • logging ───────────► Debug/info          │
│                                             │
│  Optional (LLM Fallback):                   │
│  • google-generativeai ─► Gemini API       │
│                                             │
│  External Services:                         │
│  • Ollama (localhost:11434) - Primary LLM   │
│    └─► Local, private, no API costs ✅      │
│  • Google Gemini API - Fallback LLM        │
│    └─► Cloud-based, requires API key       │
│                                             │
└─────────────────────────────────────────────┘
```

### LLM Dependencies

| Component | Required | Purpose | Status |
|-----------|----------|---------|--------|
| **Ollama** | Recommended | Local AI analysis | ✅ Primary |
| `requests>=2.32.0` | Yes | Ollama API | ✅ Required |
| **Gemini API** | Optional | Cloud AI fallback | 🔄 Fallback |
| `google-generativeai>=0.8.3` | Optional | Gemini client | 🔄 Optional |
| **Mock Mode** | Always | Pattern analysis | ✅ Built-in |

## Configuration

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "infra-monitor": {
      "command": "/path/to/python3",
      "args": ["-u", "-m", "infra_mcp.server"],
      "cwd": "/path/to/InfraGPT-NerdMeetup",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "OLLAMA_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2",
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

**Key Configuration Notes:**
- `-u` flag ensures unbuffered Python output (critical for stdio)
- `PYTHONUNBUFFERED=1` enforces unbuffered mode
- Full path to Python interpreter recommended (e.g., from `pyenv`)

### Environment Variables

**Ollama Configuration (Primary LLM):**
- `OLLAMA_URL` - Ollama API endpoint (default: http://localhost:11434)
- `OLLAMA_MODEL` - Preferred model name (default: llama3.2)
  - Options: llama3.2, llama3.1, mistral, codellama, etc.
  - Falls back to any available model if not found

**Gemini Configuration (Fallback LLM):**
- `GEMINI_API_KEY` - Google Gemini API key (optional)
  - Only used if Ollama is unavailable
  - Get key from: https://makersuite.google.com/app/apikey

**General Settings:**
- `PYTHONUNBUFFERED` - Unbuffered output (required: "1")
- `LOG_LEVEL` - Logging level (default: INFO)
- `PYTHONPATH` - Python module path (optional)

**LLM Priority:**
```
Ollama (local) → Gemini (cloud) → Mock (patterns)
     ↓               ↓                 ↓
  Primary         Fallback         Always Available
  No cost         API cost          Free
  Private         Cloud             Local
```

## Security Architecture

### Access Control

```
┌─────────────────────────────────────────────┐
│           Security Layers                   │
├─────────────────────────────────────────────┤
│                                             │
│  1. Process Isolation                       │
│     └─► Runs as user process                │
│                                             │
│  2. Permission Handling                     │
│     └─► Graceful fallback                   │
│                                             │
│  3. Data Privacy (Enhanced with Ollama) ✅  │
│     ├─► Ollama: 100% local processing       │
│     │   └─► No data leaves your machine     │
│     ├─► Gemini: Optional cloud fallback     │
│     │   └─► Only if user provides API key   │
│     └─► Mock: Local pattern matching        │
│                                             │
│  4. No Data Storage                         │
│     └─► Ephemeral processing                │
│     └─► Logs analyzed in memory only        │
│                                             │
│  5. Network Security                        │
│     ├─► Ollama: localhost only              │
│     ├─► Gemini: HTTPS to Google             │
│     └─► Mock: No network required           │
│                                             │
└─────────────────────────────────────────────┘
```

### Privacy Model with Ollama

```
Data Flow Analysis:

With Ollama (Primary):
  User System → MCP Server → Ollama (localhost:11434)
                                    ↓
                              Local LLM Processing
                                    ↓
                            ← AI Analysis Returns
  ✅ Data never leaves machine
  ✅ Complete privacy
  ✅ No API logging
  ✅ Works offline

With Gemini (Fallback):
  User System → MCP Server → Internet → Google Gemini API
                                              ↓
                                        Cloud Processing
                                              ↓
                            ← AI Analysis Returns
  ⚠️ Data sent to cloud
  ⚠️ Subject to Google's privacy policy
  ✅ Encrypted in transit (HTTPS)

With Mock (Last Resort):
  User System → MCP Server → Pattern Matching (local)
                                    ↓
                            ← Analysis Returns
  ✅ Completely local
  ✅ Zero network access
  ⚠️ Basic analysis only
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

- **Memory**: ~50-100 MB (MCP server idle)
- **CPU**: <1% (idle), 5-15% (during analysis)
- **Startup**: ~1-2 seconds
- **Response Time**: 
  - System info: <1 second
  - Log retrieval: 1-2 seconds
  - AI analysis: 
    - **Ollama**: 3-8 seconds (local inference) ✅
    - **Gemini**: 2-5 seconds (API latency)
    - **Mock**: <1 second (pattern matching)

### LLM Performance Comparison

| Metric | Ollama (Local) | Gemini (Cloud) | Mock Mode |
|--------|----------------|----------------|-----------|
| **Latency** | 3-8 seconds | 2-5 seconds | <1 second |
| **Privacy** | 100% local ✅ | Data sent to cloud | 100% local ✅ |
| **Cost** | Free ✅ | API costs | Free ✅ |
| **Offline** | Yes ✅ | No | Yes ✅ |
| **Quality** | High ✅ | Very High | Basic |
| **Setup** | Install Ollama | API key only | None ✅ |

**Ollama Resource Impact:**
- Runs separately as a service
- Memory: ~2-4 GB (depends on model)
- CPU: 20-60% during inference (brief)
- GPU: Optional (significantly faster with GPU)

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

Production (with Ollama - Recommended):
  Ollama Service (localhost:11434)
        ↓
  Claude Desktop ─► stdio MCP ─► InfraGPT-MCP ─► Ollama
                                     │
                                     └─► System Monitoring
  ✅ 100% Local
  ✅ Private
  ✅ No API costs

Production (Cloud Fallback):
  Claude Desktop ─► stdio MCP ─► InfraGPT-MCP ─► Gemini API
                                     │
                                     └─► System Monitoring
  ⚠️ Data sent to cloud
  ⚠️ Requires API key
  ⚠️ API costs

Alternative:
  Any MCP Client ─► stdio MCP ─► InfraGPT-MCP
```

## Ollama Setup Architecture

### Installation Flow

```
1. Install Ollama
   brew install ollama
   (or download from ollama.ai)
        ↓
2. Start Ollama Service
   ollama serve
   (runs on localhost:11434)
        ↓
3. Pull LLM Model
   ollama pull llama3.2
   (or llama3.1, mistral, etc.)
        ↓
4. Configure MCP Server
   Set OLLAMA_URL=http://localhost:11434
   Set OLLAMA_MODEL=llama3.2 (optional)
        ↓
5. Start Claude Desktop
   MCP server auto-detects Ollama
        ↓
6. Ready! 
   AI analysis now 100% local ✅
```

### Ollama Service Architecture

```
┌─────────────────────────────────────────┐
│         Ollama Service                  │
│    (Background Process)                 │
├─────────────────────────────────────────┤
│                                         │
│  HTTP Server: localhost:11434           │
│  │                                      │
│  ├─► /api/tags      (list models)      │
│  ├─► /api/generate  (inference)        │
│  └─► /api/chat      (chat interface)   │
│                                         │
│  Model Storage: ~/.ollama/models       │
│  │                                      │
│  ├─► llama3.2  (2GB)                   │
│  ├─► llama3.1  (4.7GB)                 │
│  └─► mistral   (4.1GB)                 │
│                                         │
└─────────────────────────────────────────┘
```

## LLM Selection & Fallback Architecture

### Decision Flow

```python
# Pseudocode for LLM selection
class LogAnalyzer:
    def __init__(self):
        # Priority 1: Try Ollama
        if self._initialize_ollama():
            self.llm_mode = "ollama"
            self.ollama_url = "http://localhost:11434"
            self.ollama_model = self._detect_model()
        
        # Priority 2: Try Gemini
        elif os.getenv("GEMINI_API_KEY"):
            self.llm_mode = "gemini"
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Priority 3: Mock Mode
        else:
            self.llm_mode = "mock"
    
    def analyze_logs(self, logs, analysis_type):
        # Try Ollama first
        if self.llm_mode == "ollama":
            try:
                return self._call_ollama_api(prompt)
            except Exception:
                # Fall back to Gemini
                if os.getenv("GEMINI_API_KEY"):
                    return self._call_gemini_api(prompt)
                # Fall back to Mock
                return self._mock_analysis(logs, analysis_type)
        
        # Try Gemini second
        elif self.llm_mode == "gemini":
            try:
                return self._call_gemini_api(prompt)
            except Exception:
                # Fall back to Mock
                return self._mock_analysis(logs, analysis_type)
        
        # Mock mode (always works)
        else:
            return self._mock_analysis(logs, analysis_type)
```

### Runtime Detection

```
Server Startup:
    │
    ├─► Check Ollama availability
    │   └─► GET http://localhost:11434/api/tags
    │       │
    │       ├─► Success: Set llm_mode = "ollama" ✅
    │       │   └─► Detect models: ["llama3.2", "llama3.1", ...]
    │       │
    │       └─► Failure: Continue to next check
    │
    ├─► Check Gemini API key
    │   └─► Check GEMINI_API_KEY environment variable
    │       │
    │       ├─► Exists: Set llm_mode = "gemini"
    │       │
    │       └─► Missing: Continue to next check
    │
    └─► Default to Mock Mode
        └─► Set llm_mode = "mock" (always available)

Every Analysis Request:
    │
    ├─► Try current llm_mode
    │   │
    │   ├─► Success: Return analysis ✅
    │   │
    │   └─► Failure: Try next fallback
    │       │
    │       └─► Eventually reaches Mock Mode (never fails)
```

### LLM Feature Comparison

| Feature | Ollama | Gemini | Mock |
|---------|--------|--------|------|
| **Privacy** | 100% local | Cloud-based | 100% local |
| **Cost** | Free | Pay-per-use | Free |
| **Setup** | Install service | API key only | Built-in |
| **Offline** | Yes ✅ | No | Yes ✅ |
| **Speed** | 3-8s | 2-5s | <1s |
| **Quality** | High | Very High | Basic |
| **Models** | Many options | Fixed | N/A |
| **Customizable** | Yes ✅ | Limited | No |
| **Data retention** | None ✅ | Per Google policy | None ✅ |
| **Network required** | No ✅ | Yes | No ✅ |

### Recommended Configuration

**For Production (Privacy-First):**
```bash
# Best: Ollama only
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
# No GEMINI_API_KEY = stays local always ✅
```

**For Development (Maximum Reliability):**
```bash
# Ollama primary, Gemini fallback
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
GEMINI_API_KEY=your_api_key_here
```

**For Testing (No Dependencies):**
```bash
# Mock mode only
# No environment variables needed
# Always works, basic analysis
```

## Version Compatibility

| Component | Version | Status |
|-----------|---------|--------|
| MCP Protocol | 2025-06-18 | ✅ Supported |
| Python | 3.8+ | ✅ Required |
| Claude Desktop | Latest | ✅ Tested |
| Ollama | Latest | ✅ Recommended |
| macOS | 11+ | ✅ Tested |
| Linux | Most distros | ✅ Expected |

### LLM Compatibility

| LLM | Integration | Models Tested | Status |
|-----|-------------|---------------|--------|
| **Ollama** | HTTP API | llama3.2, llama3.1, mistral | ✅ Primary |
| **Gemini** | Python SDK | gemini-1.5-flash | ✅ Fallback |
| **Mock** | Built-in | Pattern matching | ✅ Always Available |

---

**Architecture Version**: 2.0 (Ollama Integration)  
**Last Updated**: November 22, 2025  
**Status**: Production Ready ✅

**Major Changes in v2.0:**
- ✅ Ollama as primary LLM (100% local, private)
- ✅ Intelligent LLM fallback system (Ollama → Gemini → Mock)
- ✅ Enhanced privacy with local-first approach
- ✅ Zero API costs with Ollama
- ✅ Offline capability with Ollama
- ✅ Protocol version updated to 2025-06-18
- ✅ Comprehensive regression testing (33 tests, 100% pass rate)

