#!/bin/bash

# Infrastructure MCP Server Setup Script

set -e

echo "========================================="
echo "Infrastructure MCP Server Setup"
echo "========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

# Check if Python >= 3.8
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Error: Python 3.8 or higher is required"
    exit 1
fi

echo "✅ Python version is compatible"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check for Gemini API key
echo "Checking for Gemini API key..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY environment variable not set"
    echo "   The server will run in mock mode (simulated AI analysis)"
    echo "   To enable real AI analysis:"
    echo "   1. Get API key from: https://makersuite.google.com/app/apikey"
    echo "   2. Add to ~/.zshrc or ~/.bashrc:"
    echo "      export GEMINI_API_KEY=\"your_api_key_here\""
    echo ""
else
    echo "✅ Gemini API key found"
    echo ""
fi

# Test the server
echo "Testing the MCP server..."
python3 -c "from infra_mcp import InfraMcpServer; print('✅ Server imports successfully')"
echo ""

# Create Claude Desktop config directory
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
echo "Checking Claude Desktop configuration..."

if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "Creating Claude Desktop config directory..."
    mkdir -p "$CLAUDE_CONFIG_DIR"
    echo "✅ Created directory: $CLAUDE_CONFIG_DIR"
else
    echo "✅ Claude Desktop config directory exists"
fi

# Generate Claude Desktop configuration
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
echo ""
echo "Claude Desktop configuration file location:"
echo "  $CLAUDE_CONFIG_FILE"
echo ""

# Create example configuration
cat > claude_config_example.json <<EOF
{
  "mcpServers": {
    "infra-monitor": {
      "command": "python3",
      "args": ["-m", "infra_mcp.server"],
      "cwd": "$SCRIPT_DIR",
      "env": {
        "GEMINI_API_KEY": "\${GEMINI_API_KEY}"
      }
    }
  }
}
EOF

echo "✅ Created example configuration: claude_config_example.json"
echo ""

# Check if Claude Desktop config exists
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "⚠️  Claude Desktop configuration already exists"
    echo "   To add the MCP server, merge the contents of:"
    echo "   $SCRIPT_DIR/claude_config_example.json"
    echo "   into: $CLAUDE_CONFIG_FILE"
else
    echo "Would you like to create the Claude Desktop configuration? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cp claude_config_example.json "$CLAUDE_CONFIG_FILE"
        echo "✅ Created Claude Desktop configuration"
        echo "   Configuration file: $CLAUDE_CONFIG_FILE"
    else
        echo "Skipped creating configuration file"
        echo "You can manually copy claude_config_example.json later"
    fi
fi

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop if it's running"
echo "2. Wait 10-30 seconds for MCP server initialization"
echo "3. Try asking Claude: 'Check the system health'"
echo ""
echo "To test the server manually:"
echo "  cd $SCRIPT_DIR"
echo "  python3 test_client.py"
echo ""
echo "For troubleshooting, see: docs/setup/CLAUDE_DESKTOP_SETUP.md"
echo ""

