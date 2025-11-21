#!/bin/bash

# Diagnostic script for Infrastructure MCP Server

echo "════════════════════════════════════════════════════════════════"
echo "      Infrastructure MCP Server - Diagnostic Tool"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd "$(dirname "$0")"

# Check 1: Python version
echo "1️⃣  Checking Python version..."
python3 --version
if [ $? -eq 0 ]; then
    echo "   ✅ Python 3 is available"
else
    echo "   ❌ Python 3 not found!"
    exit 1
fi
echo ""

# Check 2: Server files
echo "2️⃣  Checking server files..."
if [ -f "infra_mcp/server.py" ]; then
    echo "   ✅ server.py exists"
else
    echo "   ❌ server.py not found!"
    exit 1
fi

if [ -f "infra_mcp/__init__.py" ]; then
    echo "   ✅ __init__.py exists"
else
    echo "   ❌ __init__.py not found!"
    exit 1
fi
echo ""

# Check 3: Dependencies
echo "3️⃣  Checking Python dependencies..."
python3 -c "import psutil; print('   ✅ psutil installed')" 2>/dev/null || echo "   ⚠️  psutil not installed (run: pip3 install -r requirements.txt)"
python3 -c "import google.generativeai; print('   ✅ google-generativeai installed (optional)')" 2>/dev/null || echo "   ℹ️  google-generativeai not installed (optional - mock mode works)"
echo ""

# Check 4: Server import test
echo "4️⃣  Testing server import..."
PYTHONPATH=. python3 -c "from infra_mcp import InfraMcpServer; server = InfraMcpServer(); print(f'   ✅ Server imports successfully'); print(f'   ✅ {len(server.tools)} tools loaded')" 2>&1 | grep -v "WARNING"
if [ $? -eq 0 ]; then
    echo "   ✅ Server imports successfully"
else
    echo "   ❌ Server import failed!"
fi
echo ""

# Check 5: Claude Desktop config
echo "5️⃣  Checking Claude Desktop configuration..."
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    echo "   ✅ Config file exists"
    
    # Validate JSON
    if python3 -m json.tool "$CLAUDE_CONFIG" > /dev/null 2>&1; then
        echo "   ✅ JSON syntax is valid"
    else
        echo "   ❌ Invalid JSON syntax!"
    fi
    
    # Check for infra-monitor
    if grep -q "infra-monitor" "$CLAUDE_CONFIG"; then
        echo "   ✅ infra-monitor server configured"
    else
        echo "   ⚠️  infra-monitor not found in config"
    fi
else
    echo "   ❌ Claude Desktop config not found!"
    echo "   Run: cp claude_desktop_config.json \"$CLAUDE_CONFIG\""
fi
echo ""

# Check 6: Claude Desktop process
echo "6️⃣  Checking if Claude Desktop is running..."
if pgrep -x "Claude" > /dev/null; then
    echo "   ✅ Claude Desktop is running"
    
    # Check if MCP server process is running
    if pgrep -f "infra_mcp.server" > /dev/null; then
        echo "   ✅ MCP server process is running"
    else
        echo "   ⚠️  MCP server process not found (may take 15-20 seconds after Claude starts)"
    fi
else
    echo "   ℹ️  Claude Desktop is not running"
fi
echo ""

# Check 7: Run test client
echo "7️⃣  Running test client..."
python3 test_client.py 2>&1 | grep -E "(✅|❌|🎉)" | head -5
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "                    DIAGNOSTIC COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "If all checks passed:"
echo "  1. Restart Claude Desktop (Cmd+Q, then reopen)"
echo "  2. Wait 15-20 seconds"
echo "  3. Ask Claude: 'What infrastructure monitoring tools do you have?'"
echo ""
echo "If checks failed, see TROUBLESHOOTING.md or run:"
echo "  ./setup.sh"
echo ""


