# Claude Desktop Setup Guide

This guide will help you integrate the Infrastructure MCP Server with Claude Desktop for AI-powered infrastructure monitoring.

## 📋 Prerequisites

- Claude Desktop installed on your system
- Python 3.8 or higher
- macOS (this guide is tailored for macOS)

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd /Users/shivkumars/ProjectsLocal/InfraGPT-MCP
pip install -r requirements.txt
```

### Step 2: Test the Server

```bash
python test_client.py
```

You should see output showing all 7 tools being tested successfully.

### Step 3: Configure Claude Desktop

#### Find/Create Claude Desktop Configuration

The configuration file is located at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Create the directory if it doesn't exist:
```bash
mkdir -p ~/Library/Application\ Support/Claude
```

#### Add MCP Server Configuration

Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "infra-monitor": {
      "command": "python",
      "args": ["-m", "infra_mcp.server"],
      "cwd": "/Users/shivkumars/ProjectsLocal/InfraGPT-MCP",
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

**Important**: The `cwd` path must be absolute. Update it if your project is in a different location.

### Step 4: Set Environment Variables (Optional)

For AI-powered log analysis, set up your Gemini API key:

```bash
# Add to ~/.zshrc or ~/.bashrc
export GEMINI_API_KEY="your_gemini_api_key_here"
```

Get a Gemini API key from: https://makersuite.google.com/app/apikey

**Note**: The server works in mock mode without the API key, providing simulated AI analysis.

### Step 5: Restart Claude Desktop

1. **Quit Claude Desktop completely** (Cmd+Q)
2. **Reopen Claude Desktop**
3. **Wait 10-30 seconds** for the MCP server to initialize

### Step 6: Verify Integration

In Claude Desktop, start a new conversation and try:

1. **Check available tools:**
   ```
   What infrastructure monitoring tools do you have access to?
   ```

2. **Test system monitoring:**
   ```
   Can you check the system health?
   ```

3. **Test log analysis:**
   ```
   Analyze recent system logs for any issues
   ```

## 🎯 Usage Examples

### Example 1: System Health Check
```
You: Can you check the overall system health and provide recommendations?

Claude will use:
- get_system_info tool
- health_check tool

Expected output:
- System Health Score: X/10
- CPU, Memory, Disk usage metrics
- Recommendations for improvements
```

### Example 2: Service Monitoring
```
You: What services are currently running on the system?

Claude will use:
- get_service_status tool

Expected output:
- List of active services
- Top processes by CPU usage
- Process count statistics
```

### Example 3: Log Analysis
```
You: Analyze recent system logs for security issues

Claude will use:
- get_logs tool
- analyze_logs tool (with security analysis type)

Expected output:
- Security events found
- Authentication attempts
- Recommendations for security improvements
```

### Example 4: Network Information
```
You: Show me the current network configuration and active connections

Claude will use:
- get_network_info tool

Expected output:
- Network interfaces and their addresses
- Active connections
- Network I/O statistics
```

## 🔧 Available Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `get_system_info` | CPU, memory, disk usage | "Show me system resources" |
| `get_service_status` | Service and process status | "Is Docker running?" |
| `get_user_info` | Active user sessions | "Who is logged in?" |
| `get_logs` | System log retrieval | "Show me recent errors" |
| `get_network_info` | Network interfaces | "What network connections are active?" |
| `analyze_logs` | AI-powered log analysis | "Analyze logs for security issues" |
| `health_check` | Comprehensive health check | "Check overall system health" |

## 🐛 Troubleshooting

### Problem: MCP Server Not Loading

**Symptoms**: Claude doesn't recognize the infrastructure monitoring tools

**Solutions**:
1. Check configuration file syntax:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
   ```

2. Verify the `cwd` path is correct:
   ```bash
   ls -la /Users/shivkumars/ProjectsLocal/InfraGPT-MCP/infra_mcp
   ```

3. Test the server manually:
   ```bash
   cd /Users/shivkumars/ProjectsLocal/InfraGPT-MCP
   python -m infra_mcp.server
   ```
   Type: `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}`
   Press Enter. You should see a JSON response.
   Press Ctrl+D to exit.

4. Check Claude Desktop logs:
   ```bash
   tail -f ~/Library/Logs/Claude/*.log
   ```

### Problem: Permission Denied Errors

**Symptoms**: Can't access system logs or certain resources

**Solutions**:
1. Some logs require elevated privileges
2. Try running test_client.py to see which operations fail
3. Consider using `sudo` for log access (not recommended for Claude Desktop integration)

### Problem: Environment Variables Not Working

**Symptoms**: Gemini API key not being recognized

**Solutions**:
1. Restart your terminal after setting environment variables
2. Verify the variable is set:
   ```bash
   echo $GEMINI_API_KEY
   ```
3. Restart Claude Desktop completely after setting environment variables
4. Alternatively, set the API key directly in the Claude config (not recommended for security)

### Problem: Tools Not Appearing in Claude

**Symptoms**: Claude doesn't mention infrastructure monitoring capabilities

**Solutions**:
1. Wait 30-60 seconds after starting Claude Desktop
2. Start a completely new conversation
3. Ask explicitly: "What MCP servers are available?"
4. Check if the server process is running:
   ```bash
   ps aux | grep infra_mcp
   ```

## 📊 Testing the Server

Run the comprehensive test suite:

```bash
cd /Users/shivkumars/ProjectsLocal/InfraGPT-MCP
python test_client.py
```

This will test all 7 tools and show you sample output.

## 🔒 Security Notes

- The server accesses system logs and may require appropriate permissions
- Log data is processed locally before being sent to Gemini API (if configured)
- Mock mode (without API key) keeps all analysis completely local
- Consider running with restricted permissions in production environments

## 📚 Additional Resources

- [Main README](README.md) - Complete project documentation
- [Google Gemini API](https://makersuite.google.com/app/apikey) - Get your API key
- [Claude Desktop](https://claude.ai/download) - Download Claude Desktop

## 🎉 Success!

Once configured, you can:
- ✅ Ask Claude to monitor your infrastructure in real-time
- ✅ Get AI-powered analysis of system logs
- ✅ Request system health checks with intelligent recommendations
- ✅ Monitor service status and performance
- ✅ Analyze network activity and connections
- ✅ Track user sessions and system activity

Claude will automatically use the appropriate MCP tools to answer your infrastructure-related questions!

