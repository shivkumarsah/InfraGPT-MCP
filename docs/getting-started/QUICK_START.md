# Quick Start Guide - Infrastructure MCP Server

Get started with the Infrastructure MCP Server in 5 minutes!

## 🚀 Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
cd /Users/shivkumars/ProjectsLocal/InfraGPT-MCP
./setup.sh
```

This script will:
- ✅ Check Python version (3.8+ required)
- ✅ Install all dependencies
- ✅ Create Claude Desktop configuration
- ✅ Test the MCP server
- ✅ Set up example configuration files

## 🚀 Option 2: Manual Setup

### Step 1: Install Dependencies

```bash
cd /Users/shivkumars/ProjectsLocal/InfraGPT-MCP
pip3 install -r requirements.txt
```

### Step 2: Test the Server

```bash
python3 test_client.py
```

You should see:
```
🚀 Infrastructure MCP Server - Test Client
============================================================
✅ Initialization successful
✅ Found 7 available tools
...
🎉 All tests completed successfully!
```

### Step 3: Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "infra-monitor": {
      "command": "python3",
      "args": ["-m", "infra_mcp.server"],
      "cwd": "/Users/shivkumars/ProjectsLocal/InfraGPT-MCP",
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop (Cmd+Q)
2. Reopen Claude Desktop
3. Wait 10-30 seconds

### Step 5: Test with Claude

Ask Claude:
```
Can you check the system health?
```

## 🎯 First Commands to Try

### 1. System Health Check
```
Check the overall system health and provide recommendations
```

### 2. View System Resources
```
Show me the current system information including CPU, memory, and disk usage
```

### 3. Check Running Services
```
What services are currently running on this system?
```

### 4. Analyze Logs
```
Analyze recent system logs for any errors or issues
```

### 5. Network Information
```
Show me the network configuration and active connections
```

## 🛠️ Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup.sh` | Initial setup | `./setup.sh` |
| `test_server.sh` | Run tests | `./test_server.sh` |
| `check_claude_config.sh` | Verify config | `./check_claude_config.sh` |
| `test_client.py` | Direct testing | `python3 test_client.py` |

## 📊 What You Get

### 7 Powerful Tools

1. **get_system_info** - Real-time CPU, memory, disk metrics
2. **get_service_status** - Service and process monitoring
3. **get_user_info** - Active user sessions and system users
4. **get_logs** - System log retrieval (syslog, auth, kernel, dmesg)
5. **get_network_info** - Network interfaces and connections
6. **analyze_logs** - AI-powered log analysis (4 analysis types)
7. **health_check** - Comprehensive system health assessment

### AI Analysis Modes

- **Summary** - Overall log analysis and insights
- **Errors** - Error detection and troubleshooting
- **Security** - Security event analysis and recommendations
- **Performance** - Performance bottleneck identification

## 🔧 Optional: Gemini API Setup

For real AI-powered analysis (optional - works in mock mode without it):

1. Get API key: https://makersuite.google.com/app/apikey
2. Add to `~/.zshrc` or `~/.bashrc`:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
3. Restart terminal and Claude Desktop

## ✅ Verify Installation

Check everything is working:

```bash
# 1. Test the server
python3 test_client.py

# 2. Verify Claude config
./check_claude_config.sh

# 3. Check if it's running
ps aux | grep infra_mcp
```

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip3 install -r requirements.txt

# Test manually
python3 -m infra_mcp.server
```

### Claude doesn't see the tools?
```bash
# Verify config syntax
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check the config
./check_claude_config.sh

# Restart Claude Desktop completely
```

### Permission errors?
Some logs require elevated permissions. The server handles this gracefully and will show what it can access.

## 📚 More Information

- **[README.md](README.md)** - Complete project documentation
- **[CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)** - Detailed setup guide
- **Example conversations** - See README.md for usage examples

## 🎉 You're Ready!

Once configured, Claude can:
- 🖥️ Monitor your system in real-time
- 📊 Analyze system logs intelligently
- 🔍 Identify performance issues
- 🔒 Detect security events
- 💡 Provide actionable recommendations

Start asking Claude about your infrastructure - it now has eyes into your system!

