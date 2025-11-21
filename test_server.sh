#!/bin/bash

# Quick test script for the Infrastructure MCP Server

echo "========================================="
echo "Testing Infrastructure MCP Server"
echo "========================================="
echo ""

cd "$(dirname "$0")"

# Run the test client
echo "Running test client..."
echo ""

python3 test_client.py

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE

