# Testing Guide - InfraGPT MCP Server

## 🧪 Regression Test Suite

A comprehensive test suite that validates all MCP server functionality.

### Quick Start

```bash
# Run all tests
python3 regression_test.py

# View detailed report
cat regression_test_report.json | python3 -m json.tool
```

## 📊 Test Coverage

### What Gets Tested

#### 1. Server Initialization (3 tests)
- Server instantiation
- Tool loading (7 tools)
- Tool registration

#### 2. MCP Protocol Compliance (5 tests)
- JSON-RPC 2.0 format
- Request/response ID matching
- Protocol version handling
- Server info response
- Tools listing

#### 3. System Info Tool (7 tests)
- Hostname and platform detection
- CPU metrics (count, percentage)
- Memory usage
- Disk usage
- System uptime

#### 4. Service Status Tool (2 tests)
- Process count retrieval
- Top processes listing

#### 5. User Info Tool (2 tests)
- Current user detection
- User session information

#### 6. Logs Tool (2 tests)
- Syslog retrieval
- Dmesg log access

#### 7. Network Info Tool (2 tests)
- Network interface enumeration
- I/O counter statistics

#### 8. Analyze Logs Tool (4 tests)
- Summary analysis
- Error detection
- Security analysis
- Performance analysis

#### 9. Health Check Tool (2 tests)
- System health metrics
- AI-powered health analysis

#### 10. LLM Mode Detection (2 tests)
- Ollama detection
- Fallback mechanism (Gemini/Mock)

#### 11. Error Handling (2 tests)
- Invalid method handling
- Invalid tool handling

## 📈 Test Results

### Last Run Results
- **Total Tests**: 33
- **Passed**: 33
- **Failed**: 0
- **Pass Rate**: 100%

### Test Artifacts

Files created by test runs:
- `regression_test.py` - Test suite script
- `regression_test_report.json` - Detailed JSON report

## 🔍 Understanding Test Output

### Success Example
```
✅ PASS: System info: Has hostname
✅ PASS: System info: Has platform
```

### Failure Example (if occurs)
```
❌ FAIL: System info: Has hostname
      Error: Field 'hostname' not found in response
```

## 🛠️ Running Specific Tests

The test suite runs all tests sequentially. To run specific tests, modify `regression_test.py`:

```python
# In main() function, comment out tests you don't want:
async def run_all_tests(self):
    await self.test_server_initialization()
    # await self.test_mcp_protocol()  # Skip this
    await self.test_system_info_tool()
    # ... etc
```

## 📋 Test Checklist

Run regression tests:

- ✅ Before committing code changes
- ✅ Before deploying to production
- ✅ After updating dependencies
- ✅ After system configuration changes
- ✅ Weekly as part of maintenance
- ✅ After Ollama model changes

## 🐛 Debugging Failed Tests

### If Tests Fail

1. **Check test output** - Look at the error message
   ```bash
   python3 regression_test.py 2>&1 | grep "FAIL"
   ```

2. **Check detailed report**
   ```bash
   cat regression_test_report.json | grep -A 5 '"passed": false'
   ```

3. **Run individual components**
   ```bash
   # Test server standalone
   python3 test_client.py
   
   # Check system access
   python3 -c "import psutil; print(psutil.cpu_percent())"
   ```

4. **Check dependencies**
   ```bash
   pip3 list | grep -E "(psutil|requests|google)"
   ```

5. **Check Ollama status**
   ```bash
   curl http://localhost:11434/api/tags
   ```

## 📊 Interpreting Results

### LLM Mode Detection

The tests will show which LLM mode is active:

- **Ollama Mode**: Local LLM detected and working
  ```
  INFO:infra_mcp.log_analyzer:Using Ollama at http://localhost:11434
  ```

- **Gemini Fallback**: Ollama unavailable, using Gemini
  ```
  WARNING:infra_mcp.log_analyzer:Ollama failed, trying Gemini fallback
  ```

- **Mock Mode**: No LLM available, using pattern-based analysis
  ```
  WARNING:infra_mcp.log_analyzer:No LLM available, using mock mode
  ```

### Test Performance

Typical test execution time:
- **Full suite**: 5-10 seconds
- **With Ollama active**: 8-15 seconds (includes LLM calls)
- **Mock mode**: 3-5 seconds (fastest)

## 🔄 Continuous Integration

### Add to CI/CD Pipeline

```yaml
# Example GitHub Actions
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Install dependencies
      run: pip3 install -r requirements.txt
    - name: Run regression tests
      run: python3 regression_test.py
```

### Pre-commit Hook

```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
echo "Running regression tests..."
python3 regression_test.py
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Commit aborted."
    exit 1
fi
echo "✅ All tests passed!"
```

## 📖 Additional Testing

### Manual Testing with Claude Desktop

1. Start Claude Desktop
2. Wait 15-20 seconds for server initialization
3. Try commands:
   - "Check system info"
   - "Analyze system logs"
   - "Show network status"
   - "Run health check"

### Testing with Test Client

```bash
# Interactive test client
python3 test_client.py

# Options in test client:
# 1. Get system info
# 2. Get service status
# 3. Get user info
# 4. Get logs
# 5. Get network info
# 6. Analyze logs
# 7. Health check
# 8. List available tools
# 9. Exit
```

## 📚 Test Documentation

### Adding New Tests

When adding new features, update the regression test:

1. Add test method to `RegressionTest` class:
   ```python
   async def test_new_feature(self):
       """Test new feature."""
       print("\n" + "="*70)
       print("TEST SUITE X: NEW FEATURE")
       print("="*70)
       
       try:
           # Your test code here
           self.log_test("New feature works", True)
       except Exception as e:
           self.log_test("New feature works", False, str(e))
   ```

2. Call it from `run_all_tests()`:
   ```python
   await self.test_new_feature()
   ```

3. Run tests to verify:
   ```bash
   python3 regression_test.py
   ```

## 🎯 Best Practices

1. **Run tests regularly** - Don't wait for issues
2. **Check test reports** - Review `regression_test_report.json`
3. **Monitor LLM mode** - Ensure Ollama is working as expected
4. **Keep dependencies updated** - Test after updates
5. **Document failures** - Note any issues for team review

## 📞 Support

If tests fail consistently:

1. Check system requirements (Python 3.8+, psutil, requests)
2. Verify Ollama installation (`ollama list`)
3. Check file permissions
4. Review server logs
5. Run diagnostic script: `./diagnose.sh`

## ✅ Success Criteria

All tests should pass (33/33) before:
- Deploying to production
- Releasing new versions
- Merging code changes
- Updating documentation

---

**Last Updated**: 2025-11-22  
**Test Suite Version**: 1.0  
**Coverage**: 100% of MCP tools and protocol features

