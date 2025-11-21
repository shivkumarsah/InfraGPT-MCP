#!/bin/bash

# Check Claude Desktop Configuration Script

echo "========================================="
echo "Claude Desktop Configuration Checker"
echo "========================================="
echo ""

CLAUDE_CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

echo "Checking Claude Desktop configuration..."
echo "Configuration file: $CLAUDE_CONFIG_FILE"
echo ""

# Check if config file exists
if [ ! -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "❌ Configuration file not found!"
    echo ""
    echo "To create it, run:"
    echo "  ./setup.sh"
    exit 1
fi

echo "✅ Configuration file exists"
echo ""

# Validate JSON
echo "Validating JSON syntax..."
if python3 -m json.tool "$CLAUDE_CONFIG_FILE" > /dev/null 2>&1; then
    echo "✅ JSON syntax is valid"
else
    echo "❌ Invalid JSON syntax!"
    echo ""
    echo "Please fix the JSON syntax in:"
    echo "  $CLAUDE_CONFIG_FILE"
    exit 1
fi
echo ""

# Display configuration
echo "Current configuration:"
echo "----------------------------------------"
python3 -m json.tool "$CLAUDE_CONFIG_FILE"
echo "----------------------------------------"
echo ""

# Check for MCP server entry
if grep -q "infra-monitor" "$CLAUDE_CONFIG_FILE"; then
    echo "✅ Infrastructure MCP Server is configured"
else
    echo "⚠️  Infrastructure MCP Server not found in configuration"
    echo ""
    echo "Add the following to mcpServers section:"
    cat claude_config_example.json
fi
echo ""

# Check if Claude Desktop is running
if pgrep -x "Claude" > /dev/null; then
    echo "✅ Claude Desktop is running"
    echo ""
    echo "⚠️  If you just updated the configuration:"
    echo "   1. Quit Claude Desktop (Cmd+Q)"
    echo "   2. Reopen Claude Desktop"
    echo "   3. Wait 10-30 seconds for initialization"
else
    echo "ℹ️  Claude Desktop is not running"
    echo ""
    echo "To start using the MCP server:"
    echo "  1. Open Claude Desktop"
    echo "  2. Wait 10-30 seconds for initialization"
    echo "  3. Try: 'Check the system health'"
fi
echo ""

# Check environment variables
echo "Checking environment variables..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set (server will run in mock mode)"
else
    echo "✅ GEMINI_API_KEY is set"
fi
echo ""

echo "========================================="
echo "Configuration check complete!"
echo "========================================="

