# Infrastructure MCP Server

> AI-powered infrastructure monitoring for Claude Desktop using the Model Context Protocol (MCP).

Monitor your system in real-time with Claude's help - CPU, memory, logs, network, and intelligent AI-powered analysis.

[![MCP Protocol](https://img.shields.io/badge/MCP-1.0-blue)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test the server
python test_client.py

# 3. Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "infra-monitor": {
      "command": "python3",
      "args": ["-m", "infra_mcp.server"],
      "cwd": "/path/to/InfraGPT-NerdMeetup"
    }
  }
}

# 4. Restart Claude Desktop and ask:
# "Check system health"
```

**📖 [Complete Setup Guide →](docs/getting-started/QUICK_START.md)**

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **System Monitoring** | Real-time CPU, memory, disk, and process monitoring |
| 📊 **Log Analysis** | AI-powered analysis of system logs (syslog, auth, kernel) |
| 🌐 **Network Monitoring** | Network interfaces, connections, and I/O statistics |
| 👥 **User Management** | Active sessions and authentication monitoring |
| 🤖 **AI Insights** | Intelligent analysis with Google Gemini (optional) |
| 🏥 **Health Checks** | Automated system health scoring and recommendations |
| 🔒 **Mock Mode** | Full functionality without external API dependencies |

## 🛠️ Available Tools

7 powerful tools accessible through Claude Desktop:

- `get_system_info` - CPU, memory, disk metrics
- `get_service_status` - Process and service monitoring  
- `get_user_info` - User sessions and activity
- `get_logs` - System log retrieval
- `get_network_info` - Network interfaces and connections
- `analyze_logs` - AI-powered log analysis
- `health_check` - Comprehensive system health assessment

## 💡 Usage Examples

**System Health Check:**
```
You: Check the overall system health
Claude: ✅ System Health Score: 8/10
        CPU: 15%, Memory: 46%, Disk: 10%...
```

**Log Analysis:**
```
You: Analyze recent logs for security issues
Claude: 🔒 Security Analysis: No threats detected
        Found 3 authentication events...
```

**Service Monitoring:**
```
You: What services are using the most CPU?
Claude: Top processes: WindowServer (3.2%), Docker (1.8%)...
```

## 📚 Documentation

- **[Quick Start Guide](docs/getting-started/QUICK_START.md)** - Get up and running in 5 minutes
- **[Setup & Configuration](docs/setup/CLAUDE_DESKTOP_SETUP.md)** - Detailed Claude Desktop setup
- **[Architecture](docs/reference/ARCHITECTURE.md)** - Technical architecture and design
- **[Architecture Diagrams](docs/diagrams/architecture.md)** - Visual system diagrams (Mermaid)

## 🔧 Requirements

- **OS:** macOS 11+ or Linux
- **Python:** 3.8 or higher
- **Claude Desktop:** Latest version
- **Optional:** Google Gemini API key for real AI analysis

## 🎯 Architecture

```
Claude Desktop (MCP Client)
        ↓ JSON-RPC over stdio
Infrastructure MCP Server
        ↓ Uses
System Resources (psutil)
        ↓ Optional
Google Gemini API
```

**[View Detailed Architecture Diagrams →](docs/diagrams/architecture.md)**

## 🔐 Security & Privacy

- ✅ Runs as user process (no root required)
- ✅ Local processing first
- ✅ No data storage (ephemeral analysis)
- ✅ Optional external API (Gemini)
- ✅ Graceful permission handling

## 🧪 Testing

```bash
# Run comprehensive tests
python test_client.py

# Expected output:
# ✅ 7 tools available
# ✅ All tests passed
```

## 🐛 Troubleshooting

**Server not loading?**
- Check Claude Desktop config syntax
- Verify Python is accessible
- Review logs: `tail -f ~/Library/Logs/Claude/mcp.log`

**Permission errors?**
- Normal - server handles gracefully
- Some logs require elevated permissions

**Need help?** See [troubleshooting guide](docs/setup/CLAUDE_DESKTOP_SETUP.md#troubleshooting)

## 🤝 Contributing

Contributions welcome! This project follows standard open-source practices.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🌟 Project Status

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**MCP Protocol:** 2025-06-18  
**Last Updated:** November 21, 2025

---

**Ready to get started?** → [Quick Start Guide](docs/getting-started/QUICK_START.md)

**Questions?** → [Documentation](docs/)
