# APC + AgentFlow MCP Servers 🚀

**100% Cost Savings with FREE Models - Production-Ready MCP Servers for Claude Code**

[![Tests](https://img.shields.io/badge/tests-28%2F28%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Version](https://img.shields.io/badge/version-0.1.0--beta.1-orange)]()

[Quick Start](#-quick-start-5-minutes) • [Features](#-key-features) • [Examples](#-usage-examples) • [Cost Savings](#-cost-comparison) • [Documentation](#-documentation)

---

## 🎯 What Is This?

Two MCP servers that deliver **100% cost savings** by automatically routing to FREE models:

**APC MCP** - Context compression (12x) + quality validation (0-100 scoring)
**AgentFlow MCP** - FREE model routing + parallel execution

---

## 🌟 The Game Changer

**AgentFlow auto-selects FREE Llama 3.3 70B for your tasks!**

```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator
result = SmartOrchestrator().orchestrate("Create REST API")
# ✅ Uses FREE model automatically
# ✅ Cost: $0.00 (vs $0.50+ with Claude)
# ✅ Quality: 85+/100 production-ready
```

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Clone & install
git clone https://github.com/GontrandL/agentflow-mcp.git
cd agentflow-mcp/agentflow-src
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure (get FREE key at https://openrouter.ai/keys)
echo "OPENROUTER_API_KEY=sk-or-v1-your-key" > .env

# 3. Test
python3 -c "from agentflow.orchestration.smart_orchestrator import SmartOrchestrator; print(SmartOrchestrator().orchestrate('Hello world'))"
# Should generate code using FREE model! 🎉
```

---

## 💰 Cost Savings

**Traditional (Claude Sonnet 4):** $0.0135/task → **$486/year** (100 tasks/day)
**AgentFlow (FREE Models):** $0.00/task → **$0/year**

**SAVINGS: 100%** 🚀

---

## 💡 Usage Examples

**Generate Code (FREE):**
```python
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator
code = SmartOrchestrator().orchestrate("Create async URL fetch function")
# Cost: $0.00, Time: ~13s, Quality: 85+/100
```

**Compress Context (12x):**
```python
from agentflow.core.context_generator import generate_compressed_context
compressed = generate_compressed_context(long_conversation, task, 8000)
# 100K tokens → 8K tokens in <1 second
```

**Validate Quality:**
```python
from agentflow.orchestration.hybrid_orchestrator import HybridOrchestrator
result = HybridOrchestrator(80).validate_worker_output('worker', task, code)
# Score: 85/100, Issues: [], Passed: True
```

---

## 🎯 Key Features

### APC MCP (6 Tools)
- 🗜️ **12x Context Compression** - 100K → 8K tokens
- ✅ **Quality Validation** - 0-100 scoring
- 🔄 **Full Workflow** - Prepare → Delegate → Validate
- 📊 **Metrics Tracking**

### AgentFlow MCP (4 Tools)
- 💰 **100% FREE** - Auto FREE model selection
- ⚡ **Parallel Execution** - 3-8 workers
- 🎯 **Smart Routing** - Task type → Best FREE model
- 🌐 **96 Models** - OpenRouter integration

---

## 🧪 Testing

```bash
./.venv/bin/python3 -m pytest tests/test_apc_integration.py -v
# Result: 28/28 passing (100%) ✅
```

---

## 📚 Documentation

### User Guides
- [Installation Guide](INSTALL.md) - Detailed setup instructions
- [Quick Start](docs/guides/QUICK_INSTALL.md) - Get running in 5 minutes
- [Examples](docs/guides/EXAMPLES.md) - 14 working code examples
- [Setup OpenRouter](docs/guides/SETUP_OPENROUTER.md) - Configure FREE models

### Developer Docs
- [Architecture](docs/architecture/) - System architecture & design
- [Development](docs/development/) - Development process & milestones
- [Research](docs/research/) - Research papers & design decisions

### More
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Changelog](CHANGELOG.md) - Version history
- [Full Documentation Index](docs/README.md) - Complete docs

---

## 📝 License

MIT - See [LICENSE](LICENSE)

---

## 🚀 Get Started!

```bash
git clone https://github.com/GontrandL/agentflow-mcp.git
cd agentflow-mcp/agentflow-src && pip install -r requirements.txt
echo "OPENROUTER_API_KEY=your-key" > .env
python3 -c "from agentflow.orchestration.smart_orchestrator import SmartOrchestrator; print(SmartOrchestrator().orchestrate('Hello!'))"
```

**Star ⭐ if useful! Made with ❤️ for AI developers**
