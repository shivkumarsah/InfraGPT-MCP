#!/usr/bin/env python3
"""
Quick test to verify MCP server works via stdio
"""
import subprocess
import json
import sys

def test_mcp_server():
    """Test the MCP server via stdio"""
    print("Testing MCP server via stdio...")
    
    # Start the server
    process = subprocess.Popen(
        ["python3", "-m", "infra_mcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/Users/shivkumars/ProjectsLocal/InfraGPT-NerdMeetup",
        env={"PYTHONPATH": "/Users/shivkumars/ProjectsLocal/InfraGPT-NerdMeetup"},
        text=True
    )
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    try:
        # Send request
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "result" in response:
                print("✅ Server responded successfully!")
                print(f"✅ Server: {response['result'].get('serverInfo', {}).get('name')}")
                print(f"✅ Version: {response['result'].get('serverInfo', {}).get('version')}")
                return True
            else:
                print(f"❌ Error in response: {response}")
                return False
        else:
            print("❌ No response from server")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        process.terminate()
        process.wait(timeout=2)

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)


