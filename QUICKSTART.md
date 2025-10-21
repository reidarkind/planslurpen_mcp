# Planslurpen MCP Server - Quick Start Guide

Get up and running with the Planslurpen MCP server in 5 minutes!

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Claude Desktop app (or another MCP client)

## 🚀 Quick Setup

### Step 1: Install Dependencies

Open your terminal and navigate to the `planslurpen_mcp` directory:

```bash
cd /Users/thoretollevik/Desktop/planslurpen_mcp
pip install -r requirements.txt
```

### Step 2: Configure Claude Desktop

1. Open Claude Desktop configuration file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "planslurpen": {
      "command": "python",
      "args": [
        "/Users/thoretollevik/Desktop/planslurpen_mcp/planslurpen_mcp.py"
      ]
    }
  }
}
```

**Note:** Replace the path with the actual absolute path to `planslurpen_mcp.py`

3. Restart Claude Desktop

### Step 3: Verify Installation

Open Claude and try one of these test queries:

```
Get the plan interpretation for kommune 1106, plan RL791
```

or

```
What fields are available for plan RL791 in kommune 1106?
```

If you see results, congratulations! 🎉 The server is working.

## ✅ Quick Test Checklist

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Config file updated with correct path
- [ ] Claude Desktop restarted
- [ ] Test query returns results

## 🔧 Troubleshooting

### "Module not found" error

**Problem:** Missing dependencies

**Solution:**
```bash
pip install --upgrade mcp httpx pydantic
```

### Server not appearing in Claude

**Problem:** Configuration not loaded

**Solution:**
1. Check that the path in `claude_desktop_config.json` is absolute and correct
2. Verify JSON syntax is valid (no trailing commas, proper quotes)
3. Restart Claude Desktop completely (quit and reopen)
4. Check Claude Desktop logs for errors

### "Plan not found" error

**Problem:** Invalid kommune number or plan ID

**Solution:**
1. Visit https://planslurpen.no/
2. Search for the plan you want
3. Copy the exact kommune number and plan ID from the URL
4. Try again with verified IDs

## 📚 Next Steps

1. **Read the README:** Learn about all available tools
2. **Check USAGE_EXAMPLES:** See practical examples
3. **Try different queries:** Experiment with various plans
4. **Explore the API:** Visit https://planslurpen.no/api/swagger/index.html

## 💡 First Queries to Try

### 1. Explore a Plan
```
Get plan interpretation for kommune 1106, plan RL791
```

### 2. Look Up a Property
```
What plans apply to property 1106-45-123?
```

### 3. Get Available Fields
```
What fields are available for plan RL791 in kommune 1106?
```

### 4. Get Human-Readable Summary
```
Give me a markdown summary of plan RL791 in Haugesund
```

## 🎯 Pro Tips

1. **Start Broad:** First get the plan, then ask for specific details
2. **Use Filters:** For large plans, request specific fields to avoid truncation
3. **Check Fields First:** Use `planslurpen_get_plan_fields` before requesting filtered data
4. **Specify Format:** Ask for "markdown" when you want readable summaries

## 📖 Documentation

- **Full Documentation:** See `README.md`
- **Usage Examples:** See `USAGE_EXAMPLES.md`
- **API Reference:** https://planslurpen.no/api/swagger/index.html

## 🆘 Getting Help

**For this MCP server issues:**
- Check `README.md` for detailed documentation
- Review `USAGE_EXAMPLES.md` for query examples

**For Planslurpen service issues:**
- Visit https://planslurpen.no/
- Check their documentation and feedback form

**For MCP protocol questions:**
- Visit https://modelcontextprotocol.io/

## ⚙️ Configuration Options

### Custom Python Path

If you use a specific Python interpreter:

```json
{
  "mcpServers": {
    "planslurpen": {
      "command": "/path/to/your/python",
      "args": [
        "/Users/thoretollevik/Desktop/planslurpen_mcp/planslurpen_mcp.py"
      ]
    }
  }
}
```

### Virtual Environment

If using a virtual environment:

```json
{
  "mcpServers": {
    "planslurpen": {
      "command": "/Users/thoretollevik/Desktop/planslurpen_mcp/venv/bin/python",
      "args": [
        "/Users/thoretollevik/Desktop/planslurpen_mcp/planslurpen_mcp.py"
      ]
    }
  }
}
```

## 🔍 Verify Installation

Run this command to check syntax:

```bash
python -m py_compile planslurpen_mcp.py
```

No output means success! ✅

## 🎉 You're Ready!

The server is now configured and ready to use. Start asking Claude about Norwegian regulation plans!

---

**Happy Planning! 🏗️🇳🇴**