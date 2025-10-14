# Installation Guide

Complete installation instructions for APC + AgentFlow MCP Servers.

---

## Prerequisites

- **Python 3.11+** 
- **pip** (Python package manager)
- **Git**
- **Claude Code** (or any MCP-compatible client)
- **OpenRouter API Key** (FREE - get at https://openrouter.ai/keys)

---

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone repository
git clone https://github.com/GontrandL/agentflow-mcp.git
cd agentflow-mcp/agentflow-src

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env

# Test installation
python3 -c "from agentflow.orchestration.smart_orchestrator import SmartOrchestrator; print('✅ Installation successful!')"
```

### Method 2: Development Install

```bash
# Clone and enter directory
git clone https://github.com/GontrandL/agentflow-mcp.git
cd agentflow-mcp/agentflow-src

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode
pip install -e .

# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

---

## Configuration

### 1. API Keys

Create `.env` file in `agentflow-src/` directory:

```bash
# Required (FREE models - 100% cost savings!)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

# Optional (paid fallbacks - only if needed)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=xxxxxxxxxxxxxx
```

**Get FREE OpenRouter key:** https://openrouter.ai/keys

### 2. Claude Code Integration

Add to `~/.claude.json` (create if doesn't exist):

```json
{
  "mcpServers": {
    "apc": {
      "command": "/absolute/path/to/agentflow-src/apc_mcp_wrapper.sh",
      "description": "Context compression and quality validation"
    },
    "agentflow": {
      "command": "/absolute/path/to/agentflow-src/agentflow_mcp_wrapper.sh",
      "description": "Cost-free task delegation with FREE models"
    }
  }
}
```

**Important:** Use ABSOLUTE paths! Replace `/absolute/path/to/` with your actual path.

### 3. Make Wrapper Scripts Executable

```bash
chmod +x apc_mcp_wrapper.sh
chmod +x agentflow_mcp_wrapper.sh
```

---

## Verification

### Test 1: Python Imports

```bash
source .venv/bin/activate

python3 << 'PYEOF'
print("Testing imports...")
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator
from agentflow.core.context_generator import generate_compressed_context
from agentflow.orchestration.hybrid_orchestrator import HybridOrchestrator
print("✅ All imports successful!")
PYEOF
```

### Test 2: MCP Server Connection

```bash
# Start new Claude Code session
claude mcp list

# Should show:
# apc: ✓ Connected
# agentflow: ✓ Connected
```

### Test 3: AgentFlow Delegation

```bash
source .venv/bin/activate

python3 -c "
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator
result = SmartOrchestrator().orchestrate('Write hello world in Python')
print(result)
"

# Should generate code using FREE model in ~10-15 seconds
```

### Test 4: Run Test Suite

```bash
pytest tests/test_apc_integration.py -v

# Expected: 28/28 tests passing (100%)
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
# Make sure you're in virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "MCP server not connected"

**Solution:**
1. Check absolute paths in `~/.claude.json`
2. Verify wrapper scripts are executable: `ls -la *_mcp_wrapper.sh`
3. Check logs: `~/.cache/claude-cli-nodejs/.../mcp-logs-*/`

### Issue: "API key not found"

**Solution:**
```bash
# Verify .env file exists
cat .env

# Should show: OPENROUTER_API_KEY=sk-or-v1-...

# If missing, create it:
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

### Issue: "Tests failing"

**Solution:**
```bash
# Check Python version (needs 3.11+)
python3 --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run specific test
pytest tests/test_apc_integration.py::TestContextGenerator -v
```

---

## Platform-Specific Notes

### macOS

```bash
# Use Python 3.11+ (install via Homebrew if needed)
brew install python@3.11

# Create venv with specific Python version
python3.11 -m venv .venv
source .venv/bin/activate
```

### Linux

```bash
# Install Python 3.11+ if needed
sudo apt update
sudo apt install python3.11 python3.11-venv

# Create venv
python3.11 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
# Create venv
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Note: Use full Windows paths in Claude config
# Example: C:\Users\YourName\agentflow-mcp\agentflow-src\apc_mcp_wrapper.sh
```

---

## Uninstallation

```bash
# Remove from Claude Code config
# Delete "apc" and "agentflow" sections from ~/.claude.json

# Remove virtual environment
rm -rf .venv

# Remove repository (if desired)
cd .. && rm -rf agentflow-mcp
```

---

## Next Steps

After installation:

1. ✅ Read [README.md](README.md) for overview
2. ✅ Check [EXAMPLES.md](EXAMPLES.md) for usage examples
3. ✅ Start using FREE models for 100% cost savings!

---

## Getting Help

- **Issues:** https://github.com/GontrandL/agentflow-mcp/issues
- **Discussions:** https://github.com/GontrandL/agentflow-mcp/discussions
- **Email:** gontrand@local

---

**Installation complete! Enjoy FREE models! 🎉**
