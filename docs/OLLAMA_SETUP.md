# 🦙 Ollama Integration Guide

The Infrastructure MCP Server now supports **Ollama** as the primary LLM provider with **Gemini as fallback**.

## 🎯 LLM Priority Order

1. **Ollama (Local)** - Primary/Default ✅
2. **Gemini (Cloud)** - Fallback
3. **Mock Mode** - Pattern-based analysis (no LLM)

## 🚀 Quick Setup

### Step 1: Install Ollama

**macOS:**
```bash
brew install ollama
```

Or download from: https://ollama.ai/download

### Step 2: Start Ollama Service

```bash
# Start Ollama service
ollama serve
```

This runs on `http://localhost:11434` by default.

### Step 3: Pull a Model

```bash
# Recommended models (choose one):

# Fast and efficient (default)
ollama pull llama3.2

# Most capable
ollama pull llama3.1

# Good for coding
ollama pull codellama

# Lightweight
ollama pull mistral
```

### Step 4: Configure Environment (Optional)

Create `.env` file in project root:

```bash
# Ollama configuration (optional - uses defaults if not set)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Gemini fallback (optional)
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 5: Restart Claude Desktop

1. Quit Claude Desktop (Cmd+Q)
2. Reopen Claude Desktop
3. Wait 15-20 seconds

## ✅ Verify Ollama is Working

### Check if Ollama is Running:
```bash
curl http://localhost:11434/api/tags
```

Expected: JSON with list of available models

### Test the MCP Server:
```bash
cd /Users/shivkumars/ProjectsLocal/InfraGPT-NerdMeetup
python3 test_client.py 2>&1 | grep -i ollama
```

Expected output:
```
INFO:infra_mcp.log_analyzer:Using Ollama at http://localhost:11434 with model llama3.2
```

## 🎯 How It Works

### Priority System

```
1. Try Ollama (local)
   ├─ Check if http://localhost:11434 is accessible
   ├─ Check if model exists
   └─ If successful → Use Ollama ✅

2. Fallback to Gemini (cloud)
   ├─ Check if GEMINI_API_KEY is set
   └─ If successful → Use Gemini ✅

3. Use Mock Mode
   └─ Pattern-based analysis (no external LLM) ✅
```

### Benefits of Ollama

✅ **100% Local** - No data sent to cloud  
✅ **No API Costs** - Free to use  
✅ **Fast** - Low latency responses  
✅ **Privacy** - Your logs stay on your machine  
✅ **Offline** - Works without internet  
✅ **Customizable** - Choose your preferred model  

## 📊 Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| llama3.2 | 2GB | ⚡⚡⚡ | ⭐⭐⭐ | Default - Fast & Good |
| llama3.1 | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Best Quality |
| mistral | 4.1GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Good Balance |
| codellama | 3.8GB | ⚡⚡ | ⭐⭐⭐⭐ | Code-focused |
| llama2 | 3.8GB | ⚡⚡ | ⭐⭐⭐ | Lightweight |

## 🔧 Configuration Options

### Environment Variables

```bash
# Ollama URL (default: http://localhost:11434)
export OLLAMA_URL=http://localhost:11434

# Ollama model (default: llama3.2)
export OLLAMA_MODEL=llama3.2

# Gemini fallback (optional)
export GEMINI_API_KEY=your_key_here
```

### In Claude Desktop Config

Update `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "infra-monitor": {
      "command": "/Users/shivkumars/.pyenv/shims/python3",
      "args": ["-u", "-m", "infra_mcp.server"],
      "cwd": "/Users/shivkumars/ProjectsLocal/InfraGPT-NerdMeetup",
      "env": {
        "PYTHONPATH": "/Users/shivkumars/ProjectsLocal/InfraGPT-NerdMeetup",
        "PYTHONUNBUFFERED": "1",
        "OLLAMA_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2",
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

## 🐛 Troubleshooting

### Ollama Not Connecting

**Problem:** "Ollama not available" in logs

**Solutions:**
1. Check if Ollama is running:
   ```bash
   ps aux | grep ollama
   ```

2. Start Ollama service:
   ```bash
   ollama serve
   ```

3. Test connection:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Model Not Found

**Problem:** "Preferred model not found"

**Solutions:**
1. List available models:
   ```bash
   ollama list
   ```

2. Pull the model:
   ```bash
   ollama pull llama3.2
   ```

3. Or let the server auto-select first available model

### Slow Responses

**Problem:** Ollama responses are slow

**Solutions:**
1. Use a smaller model (llama3.2 instead of llama3.1)
2. Adjust temperature and num_predict in code
3. Check system resources (RAM, CPU)

### Falls Back to Gemini

**Problem:** Server uses Gemini instead of Ollama

**Causes:**
- Ollama service not running
- Model not pulled
- Ollama URL incorrect
- Firewall blocking connection

**Fix:** Follow setup steps above

## 📈 Performance Comparison

| LLM | Latency | Cost | Privacy | Quality |
|-----|---------|------|---------|---------|
| Ollama | ~2-5s | Free | 100% | ⭐⭐⭐⭐ |
| Gemini | ~1-3s | Paid | Cloud | ⭐⭐⭐⭐⭐ |
| Mock | <1s | Free | 100% | ⭐⭐⭐ |

## 🎓 Advanced Usage

### Change Model on the Fly

```bash
# Set environment variable
export OLLAMA_MODEL=mistral

# Restart Claude Desktop
```

### Use Remote Ollama

```bash
# Point to remote Ollama server
export OLLAMA_URL=http://remote-server:11434
```

### Monitor Ollama Performance

```bash
# Watch Ollama logs
tail -f ~/.ollama/logs/server.log
```

## 🎉 Success!

Once Ollama is set up, your log analysis will be:
- ✅ 100% local and private
- ✅ Fast and responsive
- ✅ Free (no API costs)
- ✅ Offline capable

Try asking Claude:
```
Analyze recent system logs for errors using the local LLM
```

---

**Status:** Ollama integration complete ✅  
**Default LLM:** Ollama (local)  
**Fallback:** Gemini (cloud)  
**Last Resort:** Mock mode (pattern-based)

