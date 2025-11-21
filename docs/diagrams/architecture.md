# Infrastructure MCP Server - Architecture Diagrams

This document contains architecture diagrams for the Infrastructure MCP Server using Mermaid syntax.

## System Architecture Overview

```mermaid
graph TB
    subgraph "Claude Desktop"
        CD[Claude AI Assistant]
    end
    
    subgraph "MCP Protocol Layer"
        STDIO[JSON-RPC over stdio]
    end
    
    subgraph "Infrastructure MCP Server"
        SERVER[InfraMcpServer<br/>server.py]
        MONITOR[InfraMonitor<br/>infra_monitor.py]
        ANALYZER[LogAnalyzer<br/>log_analyzer.py]
        TYPES[MCP Types<br/>mcp_types.py]
        
        SERVER --> MONITOR
        SERVER --> ANALYZER
        SERVER --> TYPES
    end
    
    subgraph "System Resources"
        SYS[System Metrics<br/>CPU, Memory, Disk]
        LOGS[System Logs<br/>syslog, auth, kernel]
        NET[Network Info<br/>Interfaces, Connections]
        PROC[Processes<br/>Services, Users]
    end
    
    subgraph "External Services"
        GEMINI[Google Gemini API<br/>Optional AI Analysis]
    end
    
    CD <-->|MCP Protocol| STDIO
    STDIO <-->|JSON-RPC| SERVER
    MONITOR -->|psutil| SYS
    MONITOR -->|Read| LOGS
    MONITOR -->|Query| NET
    MONITOR -->|List| PROC
    ANALYZER -.->|Optional| GEMINI
    
    style CD fill:#e1f5ff
    style SERVER fill:#fff4e6
    style MONITOR fill:#f3e5f5
    style ANALYZER fill:#e8f5e9
    style GEMINI fill:#fce4ec
```

## Component Architecture

```mermaid
graph LR
    subgraph "MCP Server Core"
        INIT[Initialize]
        TOOLS[Tools Registry]
        HANDLER[Request Handler]
        
        INIT --> TOOLS
        TOOLS --> HANDLER
    end
    
    subgraph "7 Available Tools"
        T1[get_system_info]
        T2[get_service_status]
        T3[get_user_info]
        T4[get_logs]
        T5[get_network_info]
        T6[analyze_logs]
        T7[health_check]
    end
    
    TOOLS --> T1
    TOOLS --> T2
    TOOLS --> T3
    TOOLS --> T4
    TOOLS --> T5
    TOOLS --> T6
    TOOLS --> T7
    
    style HANDLER fill:#bbdefb
    style T6 fill:#c8e6c9
    style T7 fill:#ffccbc
```

## Data Flow - Tool Execution

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant MCP Server
    participant InfraMonitor
    participant System
    
    User->>Claude: "Check system health"
    Claude->>MCP Server: tools/call: health_check
    MCP Server->>InfraMonitor: get_system_info()
    InfraMonitor->>System: Query metrics
    System-->>InfraMonitor: CPU, Memory, Disk data
    InfraMonitor-->>MCP Server: System metrics
    MCP Server->>MCP Server: Calculate health score
    MCP Server-->>Claude: Health report + recommendations
    Claude-->>User: "System health: 8/10..."
```

## Log Analysis Flow

```mermaid
flowchart TD
    START([User Query]) --> CLAUDE[Claude Desktop]
    CLAUDE --> DECIDE{Need Logs?}
    DECIDE -->|Yes| GETLOGS[Call: get_logs]
    GETLOGS --> READLOGS[InfraMonitor reads logs]
    READLOGS --> ANALYZE[Call: analyze_logs]
    
    ANALYZE --> CHECKAPI{Gemini API?}
    CHECKAPI -->|Yes| REALAI[Real AI Analysis]
    CHECKAPI -->|No| MOCKAI[Mock AI Analysis]
    
    REALAI --> GEMINI[Gemini API]
    GEMINI --> RESULT1[AI Insights]
    MOCKAI --> PATTERN[Pattern Detection]
    PATTERN --> RESULT2[Smart Analysis]
    
    RESULT1 --> RETURN[Return to Claude]
    RESULT2 --> RETURN
    RETURN --> PRESENT[Present to User]
    PRESENT --> END([User Response])
    
    style CLAUDE fill:#e1f5ff
    style REALAI fill:#c8e6c9
    style MOCKAI fill:#fff9c4
    style GEMINI fill:#fce4ec
```

## Tool Categories

```mermaid
mindmap
  root((MCP Tools))
    Monitoring
      get_system_info
      get_service_status
      get_network_info
    User Management
      get_user_info
    Log Management
      get_logs
    AI Analysis
      analyze_logs
      health_check
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "macOS/Linux System"
        HOME[User Home Directory]
        
        subgraph "Project Directory"
            CODE[infra_mcp/<br/>Source Code]
            CONFIG[pyproject.toml<br/>requirements.txt]
            TEST[test_client.py<br/>Test Suite]
        end
        
        subgraph "Claude Desktop"
            CLAUDE_APP[Claude Application]
            CLAUDE_CONFIG[claude_desktop_config.json]
        end
    end
    
    subgraph "Runtime"
        PYTHON[Python 3.8+<br/>Interpreter]
        PSUTIL[psutil Library]
        GEMINI_LIB[google-generativeai<br/>Optional]
    end
    
    HOME --> CODE
    HOME --> CONFIG
    HOME --> TEST
    
    CLAUDE_CONFIG -->|Launch| PYTHON
    PYTHON -->|Import| CODE
    CODE -->|Uses| PSUTIL
    CODE -.->|Optional| GEMINI_LIB
    
    CLAUDE_APP -->|stdio| CODE
    
    style CLAUDE_APP fill:#e1f5ff
    style CODE fill:#fff4e6
    style PYTHON fill:#f3e5f5
```

## Security Model

```mermaid
graph TD
    subgraph "Security Layers"
        L1[Process Isolation]
        L2[Permission Handling]
        L3[Data Privacy]
        L4[No Data Storage]
    end
    
    subgraph "Access Control"
        READ[Read System Metrics]
        LOGS[Read Log Files]
        NET[Query Network]
        NOWRITE[No Write Operations]
    end
    
    L1 --> READ
    L2 --> LOGS
    L2 --> NET
    L3 --> PROCESS[Local Processing First]
    L4 --> EPHEMERAL[Ephemeral Analysis]
    
    PROCESS -.->|Optional| EXTERNAL[External API]
    
    style L2 fill:#fff9c4
    style L3 fill:#c8e6c9
    style L4 fill:#bbdefb
    style NOWRITE fill:#ffccbc
```

## Error Handling Flow

```mermaid
flowchart LR
    REQUEST[Tool Request] --> VALIDATE{Valid?}
    
    VALIDATE -->|Yes| EXECUTE[Execute Tool]
    VALIDATE -->|No| ERROR1[Return Error]
    
    EXECUTE --> SYSCALL{System Call}
    
    SYSCALL -->|Success| RETURN[Return Data]
    SYSCALL -->|Permission Denied| FALLBACK[Try Alternative]
    SYSCALL -->|Not Found| EMPTY[Return Empty]
    SYSCALL -->|Other Error| ERROR2[Log & Report]
    
    FALLBACK --> ALT{Alternative?}
    ALT -->|Yes| PARTIAL[Partial Data]
    ALT -->|No| EMPTY
    
    RETURN --> SUCCESS([Success])
    ERROR1 --> FAIL([Fail Gracefully])
    ERROR2 --> FAIL
    EMPTY --> SUCCESS
    PARTIAL --> SUCCESS
    
    style SUCCESS fill:#c8e6c9
    style FAIL fill:#ffccbc
    style FALLBACK fill:#fff9c4
```

---

## Legend

- **Blue boxes**: Client/User interfaces
- **Yellow boxes**: Core server components
- **Purple boxes**: Infrastructure components
- **Green boxes**: AI/Analysis components
- **Pink boxes**: External services
- **Orange boxes**: Health monitoring

## Viewing These Diagrams

These diagrams use Mermaid syntax and can be viewed in:
- GitHub (native support)
- VS Code (with Mermaid extension)
- Any Markdown viewer with Mermaid support
- [Mermaid Live Editor](https://mermaid.live/)

## Related Documentation

- [Architecture Details](../reference/ARCHITECTURE.md) - Detailed technical architecture
- [Quick Start](../getting-started/QUICK_START.md) - Getting started guide
- [Setup Guide](../setup/CLAUDE_DESKTOP_SETUP.md) - Configuration instructions

