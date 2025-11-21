# InfraGPT-MCP Documentation

> Comprehensive documentation for the Infrastructure MCP Server

Welcome! This is your central hub for all documentation about the Infrastructure MCP Server for Claude Desktop.

## 📖 Documentation Structure

### 🚀 [Getting Started](getting-started/)
Quick setup and onboarding guide.

**[Quick Start Guide](getting-started/QUICK_START.md)**  
Get up and running in 5 minutes with step-by-step instructions.

### ⚙️ [Setup & Configuration](setup/)
Detailed configuration for Claude Desktop integration.

**[Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)**  
Complete guide for configuring and troubleshooting Claude Desktop integration.

### 📚 [Reference](reference/)
Technical documentation and architecture details.

**[Architecture](reference/ARCHITECTURE.md)**  
Deep dive into system architecture, components, data flow, and technical implementation.

### 📊 [Diagrams](diagrams/)
Visual architecture diagrams using Mermaid.

**[Architecture Diagrams](diagrams/architecture.md)**  
Interactive Mermaid diagrams showing system architecture, data flow, and component relationships.

---

## 🎯 Quick Navigation

### For New Users
1. Start → [Quick Start Guide](getting-started/QUICK_START.md)
2. Configure → [Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)
3. Understand → [Architecture Diagrams](diagrams/architecture.md)

### For Developers
1. Architecture → [Technical Details](reference/ARCHITECTURE.md)
2. Visual → [System Diagrams](diagrams/architecture.md)
3. Setup → [Development Setup](getting-started/QUICK_START.md)

### For Troubleshooting
1. Setup Issues → [Claude Desktop Setup - Troubleshooting](setup/CLAUDE_DESKTOP_SETUP.md#troubleshooting)
2. System Overview → [Architecture](reference/ARCHITECTURE.md)
3. Visual Flow → [Data Flow Diagrams](diagrams/architecture.md)

---

## 📊 What is This Project?

The **Infrastructure MCP Server** provides real-time infrastructure monitoring for Claude Desktop through the Model Context Protocol (MCP).

### Key Capabilities

| Category | Features |
|----------|----------|
| **System Monitoring** | CPU, memory, disk usage, processes, services |
| **Log Management** | System logs (syslog, auth, kernel, dmesg) with AI analysis |
| **Network** | Interface info, active connections, I/O statistics |
| **User Management** | Active sessions, authentication monitoring |
| **AI Analysis** | Smart log analysis with pattern detection or Gemini API |
| **Health Checks** | Automated scoring and actionable recommendations |

### 7 Available Tools

| Tool | Purpose |
|------|---------|
| `get_system_info` | Real-time system metrics |
| `get_service_status` | Process and service monitoring |
| `get_user_info` | User session information |
| `get_logs` | System log retrieval |
| `get_network_info` | Network interface details |
| `analyze_logs` | AI-powered log analysis |
| `health_check` | Comprehensive health assessment |

---

## 🎓 Common Tasks

### How do I...?

**...get started quickly?**  
→ [Quick Start Guide](getting-started/QUICK_START.md) (5 minutes)

**...configure Claude Desktop?**  
→ [Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)

**...understand the architecture?**  
→ [Architecture Diagrams](diagrams/architecture.md) then [Architecture Details](reference/ARCHITECTURE.md)

**...troubleshoot issues?**  
→ [Troubleshooting Section](setup/CLAUDE_DESKTOP_SETUP.md#troubleshooting)

**...see visual diagrams?**  
→ [Mermaid Diagrams](diagrams/architecture.md)

---

## 🔗 External Resources

- **[Claude Desktop](https://claude.ai/download)** - Download Claude Desktop
- **[Google Gemini API](https://makersuite.google.com/app/apikey)** - Get API key (optional)
- **[MCP Protocol](https://modelcontextprotocol.io/)** - Learn about MCP
- **[Main Project README](../README.md)** - Project overview

---

## 💡 Quick Examples

### Example Commands

Once configured, ask Claude:

```
"Check system health"
"What processes are using the most CPU?"
"Analyze recent logs for security issues"
"Show me network connections"
"How much free disk space do I have?"
```

### Expected Interactions

**User:** "Check the system health"  
**Claude:** Uses `health_check` tool → Returns health score, metrics, recommendations

**User:** "Analyze logs for errors"  
**Claude:** Uses `get_logs` + `analyze_logs` → Returns error analysis and insights

---

## 🛠️ Project Details

**Version:** 1.0.0  
**Status:** Production Ready ✅  
**MCP Protocol:** 2025-06-18  
**Python:** 3.8+ required  
**Platform:** macOS 11+ / Linux

---

## 🆘 Getting Help

### Documentation Issues?
- Check if you're reading the latest version
- Verify your Python environment matches requirements
- Review [troubleshooting guide](setup/CLAUDE_DESKTOP_SETUP.md#troubleshooting)

### Server Issues?
```bash
# Test the server directly
python test_client.py

# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp.log

# Verify configuration
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Still Stuck?
1. Review [Architecture](reference/ARCHITECTURE.md) for technical details
2. Check [Setup Guide](setup/CLAUDE_DESKTOP_SETUP.md) for configuration
3. See [Visual Diagrams](diagrams/architecture.md) for data flow

---

## 📈 Documentation Statistics

- **Total Pages:** 4
- **Getting Started:** 1 guide
- **Setup:** 1 comprehensive guide  
- **Reference:** 1 technical document
- **Diagrams:** 8 Mermaid diagrams

**Last Updated:** November 21, 2025

---

**Ready to start?** → [Quick Start Guide](getting-started/QUICK_START.md)

**Need detailed setup?** → [Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)

**Want visual overview?** → [Architecture Diagrams](diagrams/architecture.md)
