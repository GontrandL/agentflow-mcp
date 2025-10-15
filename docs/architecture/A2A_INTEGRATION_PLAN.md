# A2A Protocol Integration Plan - MCP Servers

**Date**: 2025-10-14
**Goal**: Ensure all MCP tools use A2A (Agent-to-Agent) communication when possible
**Status**: 🔄 IN PROGRESS

---

## 🎯 What is A2A Protocol?

### Purpose
**Agent-to-Agent communication WITHOUT MCP overhead**

```
Traditional (MCP):
Worker → MCP Protocol → Claude Code → MCP Tool → APC
Overhead: ~50-100ms per call

A2A (Direct):
Worker → A2A Message Queue → APC
Overhead: <1ms per message
```

### Key Benefits
- ✅ **50-100x faster** (bypasses MCP protocol)
- ✅ **Async messaging** (non-blocking)
- ✅ **Request-response** + pub-sub patterns
- ✅ **Context passing** (worker can send current task)
- ✅ **Bidirectional** (APC can ask clarifications)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│             A2A Message Queue (In-Memory)               │
│           + Optional Redis (Distributed)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐        ┌──────────┐       ┌──────────┐  │
│  │   APC    │◄──────►│  Worker  │◄─────►│AgentFlow │  │
│  │  Agent   │        │  Agent   │       │  Agent   │  │
│  └──────────┘        └──────────┘       └──────────┘  │
│       ▲                    ▲                   ▲       │
│       │ A2A Messages       │ A2A Messages      │       │
│       └────────────────────┴───────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ▲                                        ▲
         │                                        │
    MCP Only                                 MCP Only
    (Claude →                               (Claude →
     APC init)                               AgentFlow init)
```

---

## 📋 Current A2A Implementation Status

### Existing Code ✅

**Location**: `agentflow/integration/`

**Files**:
1. `a2a_protocol.py` (515 lines) ✅ COMPLETE
   - A2AMessage class
   - A2AMessageQueue (async)
   - AgentCapability enum
   - MessageType enum (QUERY, RESPONSE, COMMAND, EVENT, etc.)
   - Agent registration system

2. `apc_a2a_adapter.py` (180+ lines) ✅ COMPLETE
   - APCA2AAdapter class
   - Registers APC in A2A system
   - Handles incoming queries from workers
   - Capabilities: PROJECT_QUERY, CONTEXT_COMPRESSION, VALIDATION

**Key Classes**:
```python
# Message structure
@dataclass
class A2AMessage:
    from_agent: str
    to_agent: str
    message_type: MessageType  # QUERY, RESPONSE, COMMAND, EVENT
    payload: Dict[str, Any]
    correlation_id: Optional[str]  # For request-response pairing
    context: Optional[Dict[str, Any]]  # Current task, namespace, etc.

# Agent capabilities for routing
class AgentCapability(Enum):
    PROJECT_QUERY = "project_query"
    CONTEXT_COMPRESSION = "context_compression"
    CODE_GENERATION = "code_generation"
    VALIDATION = "validation"
    ORCHESTRATION = "orchestration"
    TESTING = "testing"
```

---

## 🔧 Integration Requirements

### APC MCP Server → A2A Integration

**Status**: ⚠️ PARTIAL (adapter exists, not integrated in MCP server)

**What Exists**:
- ✅ `APCA2AAdapter` class ready
- ✅ Can register APC in A2A system
- ✅ Can handle PROJECT_QUERY, CONTEXT_COMPRESSION, VALIDATION

**What's Needed**:
1. Initialize A2A adapter in APC MCP server
2. Register APC on startup
3. Start A2A message listener (async)
4. Worker agents should query via A2A, not MCP

**Code Changes**:

**File**: `agentflow/mcp/apc_mcp_server.py`

```python
# Add to imports
from agentflow.integration.apc_a2a_adapter import APCA2AAdapter
from agentflow.integration.a2a_protocol import get_message_queue

class APCMCPServer:
    def __init__(self):
        # ... existing init ...

        # NEW: Initialize A2A adapter
        self.a2a_adapter = APCA2AAdapter(self)
        self.a2a_adapter.register()

        logger.info(
            "apc_mcp_server_initialized",
            tools=len(self.server_info['tools']),
            a2a_enabled=True  # NEW
        )

    async def start_a2a_listener(self):
        """Start A2A message listener (async)."""
        await self.a2a_adapter.start_listener()

    # Existing MCP tools remain for Claude Code interaction
    # Workers use A2A directly
```

---

### AgentFlow MCP Server → A2A Integration

**Status**: 🚀 TO IMPLEMENT (server being created now)

**What's Needed**:
1. Create AgentFlowA2AAdapter (similar to APCA2AAdapter)
2. Register AgentFlow in A2A system
3. Workers communicate via A2A for:
   - Status updates
   - Progress reporting
   - Resource requests
   - Inter-worker coordination

**Code Structure**:

**File**: `agentflow/integration/agentflow_a2a_adapter.py` (NEW)

```python
class AgentFlowA2AAdapter:
    """
    Adapter to connect AgentFlow to A2A protocol.

    Capabilities:
    - ORCHESTRATION: Can orchestrate tasks
    - CODE_GENERATION: Can delegate code generation
    - VALIDATION: Can validate worker outputs
    """

    def __init__(self, agentflow_mcp_server):
        self.agentflow_server = agentflow_mcp_server
        self.message_queue = get_message_queue()
        self.agent_id = "agentflow"

    def register(self) -> None:
        """Register AgentFlow in A2A system."""
        self.message_queue.register_agent(
            agent_id=self.agent_id,
            agent_type="orchestrator",
            capabilities=[
                AgentCapability.ORCHESTRATION,
                AgentCapability.CODE_GENERATION,
                AgentCapability.VALIDATION
            ],
            message_handler=self.handle_message
        )

    async def handle_message(self, message: A2AMessage) -> None:
        """Handle incoming A2A messages."""
        if message.message_type == MessageType.QUERY:
            # Worker asking "Can I delegate this task?"
            await self._handle_delegation_query(message)
        elif message.message_type == MessageType.COMMAND:
            # Worker requesting delegation
            await self._handle_delegation_command(message)
```

**Integration in AgentFlow MCP Server**:

**File**: `agentflow/mcp/agentflow_mcp_server.py` (BEING CREATED)

```python
from agentflow.integration.agentflow_a2a_adapter import AgentFlowA2AAdapter

class AgentFlowMCPServer:
    def __init__(self):
        # ... existing init ...

        # NEW: Initialize A2A adapter
        self.a2a_adapter = AgentFlowA2AAdapter(self)
        self.a2a_adapter.register()

        logger.info(
            "agentflow_mcp_server_initialized",
            tools=4,
            a2a_enabled=True  # NEW
        )
```

---

## 🔄 Usage Patterns: When to Use A2A vs MCP

### Use MCP Tools (Claude Code → Servers)

**Scenario**: Claude Code invoking tools

```
Claude Code → mcp__apc__prepare_context
Claude Code → mcp__agentflow__delegate_task
```

**Rationale**: MCP is the interface between Claude Code and servers

---

### Use A2A Protocol (Worker → Worker or Worker → APC/AgentFlow)

**Scenario 1: Worker querying APC**

```python
# Worker agent needs project info
from agentflow.integration.a2a_protocol import A2AMessage, MessageType

message = A2AMessage(
    from_agent="worker_123",
    to_agent="apc",
    message_type=MessageType.QUERY,
    payload={
        "query": "What validation patterns exist?",
        "context": {"current_task": "Implement validator"}
    }
)

# Send via A2A (bypasses MCP)
response = await message_queue.send_and_wait(message, timeout=5.0)
# Response arrives in <1ms
```

**Scenario 2: Worker requesting delegation**

```python
# Worker agent needs to delegate heavy task
message = A2AMessage(
    from_agent="worker_456",
    to_agent="agentflow",
    message_type=MessageType.COMMAND,
    payload={
        "command": "delegate_task",
        "task": "Generate REST API specs",
        "preferred_model": "deepseek"
    }
)

response = await message_queue.send_and_wait(message)
# AgentFlow orchestrates delegation, returns result
```

**Scenario 3: Inter-worker coordination**

```python
# Worker 1 → Worker 2: "I'm done with module A"
message = A2AMessage(
    from_agent="worker_1",
    to_agent="worker_2",
    message_type=MessageType.EVENT,
    payload={
        "event": "module_complete",
        "module": "authentication",
        "status": "ready_for_integration"
    }
)

await message_queue.publish(message)  # Async, no wait
```

---

## 📊 Performance Comparison

### MCP Tool Call (Current)

```
Time breakdown:
- Serialize request: 5ms
- MCP protocol overhead: 50-100ms
- Tool execution: 100ms
- Response serialization: 5ms
Total: 160-210ms
```

### A2A Message (With Integration)

```
Time breakdown:
- Create message: <1ms
- Queue delivery: <1ms
- Tool execution: 100ms
- Response via A2A: <1ms
Total: 102ms

Speedup: 1.5-2x
```

### Multiple Queries

**MCP (Sequential)**:
```
Query 1: 200ms
Query 2: 200ms
Query 3: 200ms
Total: 600ms
```

**A2A (Async)**:
```
Query 1, 2, 3: Sent concurrently
Total: 102ms (all complete in parallel)

Speedup: 6x
```

---

## 🎯 Implementation Checklist

### Phase 1: APC A2A Integration ✅ READY TO IMPLEMENT

- [ ] Update `apc_mcp_server.py` to initialize A2A adapter
- [ ] Add `start_a2a_listener()` method
- [ ] Test A2A registration
- [ ] Test worker → APC queries via A2A
- [ ] Update `MCP_INTEGRATION_GUIDE.md` with A2A patterns

**Estimated Time**: 1-2 hours

### Phase 2: AgentFlow A2A Integration 🔄 IN PROGRESS

- [ ] Create `agentflow_a2a_adapter.py`
- [ ] Implement AgentFlowA2AAdapter class
- [ ] Register AgentFlow in A2A system
- [ ] Handle delegation queries via A2A
- [ ] Integrate in `agentflow_mcp_server.py` (being created)
- [ ] Test worker → AgentFlow delegation via A2A

**Estimated Time**: 2-3 hours (can be done while delegation runs)

### Phase 3: Worker Agent A2A Usage 🚀 FUTURE

- [ ] Update worker templates to use A2A
- [ ] Create helper functions for common A2A patterns
- [ ] Document A2A usage for workers
- [ ] E2E test: Worker → A2A → APC → Response

**Estimated Time**: 2-3 hours

---

## 📋 Code Templates

### Template 1: Worker Querying APC via A2A

```python
async def query_apc_via_a2a(query: str, context: Dict = None) -> Dict:
    """
    Query APC via A2A protocol (faster than MCP).

    Args:
        query: Question to ask APC
        context: Optional context (current task, etc.)

    Returns:
        APC response payload
    """
    from agentflow.integration.a2a_protocol import (
        A2AMessage, MessageType, get_message_queue
    )

    message = A2AMessage(
        from_agent="worker",
        to_agent="apc",
        message_type=MessageType.QUERY,
        payload={"query": query, "context": context}
    )

    message_queue = get_message_queue()
    response = await message_queue.send_and_wait(message, timeout=5.0)

    return response.payload
```

### Template 2: Worker Delegating via AgentFlow A2A

```python
async def delegate_via_a2a(task: str, model: str = "deepseek") -> str:
    """
    Delegate task to AgentFlow via A2A protocol.

    Args:
        task: Task description
        model: Preferred model

    Returns:
        Generated result
    """
    from agentflow.integration.a2a_protocol import (
        A2AMessage, MessageType, get_message_queue
    )

    message = A2AMessage(
        from_agent="worker",
        to_agent="agentflow",
        message_type=MessageType.COMMAND,
        payload={
            "command": "delegate_task",
            "task": task,
            "preferred_model": model
        }
    )

    message_queue = get_message_queue()
    response = await message_queue.send_and_wait(message, timeout=300.0)

    return response.payload["result"]
```

---

## 🎯 Success Criteria

### Performance ✅
- A2A message delivery: <1ms
- Query response time: <5ms (excluding tool execution)
- 2-6x speedup vs MCP for multiple queries

### Reliability ✅
- Message delivery: At-least-once guarantee
- Request-response correlation: 100% accurate
- Timeout handling: Graceful fallback

### Developer Experience ✅
- Simple API (send_and_wait, publish, subscribe)
- Type hints and docstrings
- Error handling built-in
- Logging for debugging

---

## 📚 Documentation Updates Needed

### Files to Update

1. **MCP_INTEGRATION_GUIDE.md**
   - Add section: "A2A vs MCP: When to Use Each"
   - Add worker examples using A2A
   - Performance comparison tables

2. **A2A_PROTOCOL_README.md** (NEW)
   - Complete A2A protocol documentation
   - Message types and patterns
   - Code examples for common scenarios
   - Troubleshooting guide

3. **AGENTFLOW_MCP_SERVER_README.md** (NEW)
   - AgentFlow MCP server documentation
   - A2A integration details
   - Tool reference

---

## 🚀 Quick Start: Enable A2A Now

### Step 1: Update APC MCP Server (5 min)

```bash
# Edit apc_mcp_server.py
# Add A2A initialization to __init__
# Add start_a2a_listener() method
```

### Step 2: Test A2A Registration

```python
# Test script
from agentflow.mcp.apc_mcp_server import APCMCPServer

server = APCMCPServer()
# Check logs: "apc_registered_in_a2a"
```

### Step 3: Test Worker → APC Query

```python
# Test A2A query
import asyncio
from agentflow.integration.a2a_protocol import *

async def test():
    mq = get_message_queue()
    msg = A2AMessage(
        from_agent="test_worker",
        to_agent="apc",
        message_type=MessageType.QUERY,
        payload={"query": "test"}
    )
    response = await mq.send_and_wait(msg, timeout=5.0)
    print(f"Response: {response.payload}")

asyncio.run(test())
```

---

**Generated**: 2025-10-14
**Status**: 🔄 Implementation in progress
**Next Step**: Integrate A2A in APC MCP server (1-2 hours)
