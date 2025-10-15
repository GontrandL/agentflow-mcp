# APC Project Coherence Enhancement - Design Document

**Date**: 2025-10-14
**Status**: 🎯 **DESIGN PHASE**
**User Insight**: "APC should be the warrant of project coherence"

---

## 🎯 Vision: APC as Project Coherence Warranty

### Current State (What APC Does Today)

**✅ Context Compression:**
- Compresses 100K → 8K tokens (12x reduction)
- Preserves key decisions and code snippets
- Uses MMR + Chain-of-Density
- **BUT**: Only operates on conversation history (ephemeral)

**✅ Quality Validation:**
- Scores output 0-100
- Checks completeness, correctness, production-readiness
- **BUT**: No persistent memory of what was validated before

**✅ Workflow Integration:**
- Context → Delegate → Validate pipeline
- Tracks metrics (total_requests, success_rate, etc.)
- **BUT**: Metrics are session-scoped, not project-persistent

### Missing Capabilities (Project Coherence)

**❌ NO Project Structure Awareness:**
- Doesn't know which files exist in the project
- Can't map code files, UI files, specs, docs
- No understanding of project architecture

**❌ NO Persistent Memory:**
- No `.apc/` directory for structured storage
- No knowledge base of past sessions
- Can't track what was built, when, by whom

**❌ NO Project Scanning:**
- Can't review codebase structure
- Can't index files by type (code, tests, docs, configs)
- No dependency graph

**❌ NO Session Continuity:**
- Doesn't maintain session logs
- Can't bridge between sessions automatically
- No PROJECT_STATE.md management

**❌ NO Task Tracking:**
- Doesn't know what tasks are pending
- Can't update task status automatically
- No integration with TodoWrite

---

## 🏗️ Proposed Architecture: APC as Coherence Warranty

### Core Principle

**APC = Project's Single Source of Truth**
- Knows EVERYTHING about the project
- Maintains coherence across sessions
- Acts as "project memory" and "quality gatekeeper"

### New Directory Structure

```
<project-root>/
├── .apc/                                # APC Project Memory
│   ├── config.json                      # APC project configuration
│   ├── project_index.json               # File index (code, tests, docs, UI)
│   ├── dependency_graph.json            # Dependency relationships
│   ├── sessions/                        # Session history
│   │   ├── 2025-10-14_session_001.json
│   │   └── 2025-10-14_session_002.json
│   ├── tasks/                           # Task tracking
│   │   ├── pending.json
│   │   ├── in_progress.json
│   │   └── completed.json
│   ├── knowledge/                       # Project knowledge base
│   │   ├── architecture.md
│   │   ├── decisions.json               # ADRs (Architecture Decision Records)
│   │   └── patterns.json                # Code patterns learned
│   ├── metrics/                         # Performance metrics
│   │   ├── cost_tracking.json
│   │   ├── delegation_history.json
│   │   └── quality_scores.json
│   └── context/                         # Compressed context snapshots
│       ├── 2025-10-14_context.json
│       └── current_context.json
├── PROJECT_STATE.md                     # Human-readable state (APC-managed)
└── CLAUDE.md                            # Project rules
```

### New MCP Tools Needed

**Tool 5: `mcp__apc__scan_project`**
```json
{
  "name": "scan_project",
  "description": "Scan project structure and create/update .apc/ index",
  "inputSchema": {
    "project_root": "string",
    "scan_depth": "number (default: 5)",
    "include_patterns": "array (default: ['**/*.py', '**/*.js', '**/*.ts'])",
    "exclude_patterns": "array (default: ['**/node_modules/**', '**/.venv/**'])"
  },
  "output": {
    "project_index": {
      "total_files": 142,
      "code_files": 87,
      "test_files": 32,
      "doc_files": 15,
      "config_files": 8
    },
    "dependency_graph": "Generated graph.json",
    "scan_duration": "2.3s"
  }
}
```

**Tool 6: `mcp__apc__query_project`**
```json
{
  "name": "query_project",
  "description": "Query project structure, files, dependencies, history",
  "inputSchema": {
    "query_type": "enum: [structure, files, dependencies, sessions, tasks]",
    "filter": "object (optional)",
    "limit": "number (default: 50)"
  },
  "output": {
    "results": [...],
    "total": 142,
    "query_duration": "0.1s"
  }
}
```

**Tool 7: `mcp__apc__update_project_state`**
```json
{
  "name": "update_project_state",
  "description": "Update PROJECT_STATE.md and .apc/ knowledge base",
  "inputSchema": {
    "updates": {
      "status": "string (optional)",
      "phase": "string (optional)",
      "last_task": "string (optional)",
      "pending_tasks": "array (optional)",
      "decisions": "array (optional)"
    }
  },
  "output": {
    "updated": true,
    "state_file": "PROJECT_STATE.md",
    "timestamp": "2025-10-14T10:30:00Z"
  }
}
```

**Tool 8: `mcp__apc__session_bridge`**
```json
{
  "name": "session_bridge",
  "description": "Bridge from previous session to current session",
  "inputSchema": {
    "previous_session_id": "string (optional, uses latest if not specified)"
  },
  "output": {
    "compressed_context": {...},
    "pending_tasks": [...],
    "last_state": {...},
    "recommendations": ["Continue with E2E testing", "Review PR #42"]
  }
}
```

---

## 🔍 Detailed Capabilities

### 1. Project Structure Awareness

**What APC Knows:**
- All files in project (code, tests, docs, UI, configs)
- File relationships (imports, dependencies)
- Project architecture (modules, layers, patterns)
- Tech stack (languages, frameworks, tools)

**How:**
```python
# Initial scan
apc.scan_project(
    project_root="/path/to/project",
    scan_depth=5,
    include_patterns=["**/*.py", "**/*.js", "**/*.ts", "**/*.md"]
)

# Creates .apc/project_index.json:
{
  "scanned_at": "2025-10-14T10:00:00Z",
  "total_files": 142,
  "structure": {
    "src/": {
      "code": 67,
      "tests": 25,
      "docs": 5
    },
    "agentflow/": {
      "core": 12,
      "orchestration": 15,
      "integration": 8,
      "mcp": 4
    }
  },
  "file_index": [
    {
      "path": "agentflow/mcp/apc_mcp_server.py",
      "type": "code",
      "language": "python",
      "lines": 400,
      "last_modified": "2025-10-14T09:00:00Z",
      "imports": ["agentflow.core.context_generator", "..."],
      "exports": ["APCMCPServer"],
      "tests": ["tests/test_apc_integration.py::TestAPCMCPServer"]
    },
    ...
  ]
}
```

### 2. Persistent Memory

**Session History:**
```json
// .apc/sessions/2025-10-14_session_001.json
{
  "session_id": "2025-10-14_session_001",
  "started_at": "2025-10-14T08:00:00Z",
  "ended_at": "2025-10-14T12:00:00Z",
  "duration_hours": 4,
  "tasks_completed": [
    {
      "task": "Create APC test suite",
      "status": "completed",
      "files_modified": ["tests/test_apc_integration.py"],
      "tests_added": 28,
      "validation_score": 100
    },
    {
      "task": "Package APC as MCP server",
      "status": "completed",
      "files_created": ["agentflow/mcp/apc_mcp_server.py"],
      "lines_added": 400
    }
  ],
  "decisions": [
    {
      "decision": "Use stdio protocol for MCP server",
      "rationale": "Claude Code MCP standard",
      "alternatives": ["HTTP server", "WebSocket"],
      "timestamp": "2025-10-14T09:30:00Z"
    }
  ],
  "cost": {
    "delegation_cost": "$0.08",
    "direct_cost": "$1.20",
    "total": "$1.28",
    "savings": "93.8%"
  },
  "compressed_context": {
    "summary": "Completed APC deployment with 28 tests passing...",
    "key_decisions": [...],
    "code_snippets": [...]
  }
}
```

**Knowledge Base:**
```json
// .apc/knowledge/decisions.json
{
  "decisions": [
    {
      "id": "ADR-001",
      "date": "2025-10-13",
      "title": "Use DeepSeek V3 as primary delegation model",
      "status": "accepted",
      "context": "Need 99%+ cost savings for heavy workloads",
      "decision": "DeepSeek V3 via OpenRouter ($0.14/M vs $3/M)",
      "consequences": {
        "positive": ["99.6% cost reduction", "8-10 min generation time"],
        "negative": ["Slightly lower quality than Claude", "Requires validation"]
      },
      "validation": "Quality score 8.3/10 average - acceptable for delegation"
    },
    {
      "id": "ADR-002",
      "date": "2025-10-14",
      "title": "APC as MCP server vs Python scripts",
      "status": "accepted",
      "context": "Need APC available in all Claude sessions",
      "decision": "Implement as MCP server with stdio protocol",
      "consequences": {
        "positive": ["Available in all sessions", "Standard protocol"],
        "negative": ["Requires MCP config update", "Session restart needed"]
      }
    }
  ]
}
```

### 3. Task Tracking Integration

**Automatic TodoWrite Integration:**
```python
# APC monitors TodoWrite and maintains task state

# .apc/tasks/pending.json
{
  "pending_tasks": [
    {
      "id": "task-004",
      "content": "Deploy E2E testing with ClaudeFlow swarm",
      "priority": "high",
      "added_at": "2025-10-14T10:00:00Z",
      "dependencies": ["task-002", "task-003"],
      "estimated_effort": "2-3 hours",
      "assigned_to": "ClaudeFlow swarm"
    }
  ]
}

# .apc/tasks/completed.json
{
  "completed_tasks": [
    {
      "id": "task-001",
      "content": "Create APC test suite",
      "completed_at": "2025-10-14T11:00:00Z",
      "validation_score": 100,
      "files_affected": ["tests/test_apc_integration.py"],
      "session_id": "2025-10-14_session_001"
    }
  ]
}
```

### 4. Quality & Coherence Validation

**Automatic Coherence Checks:**
```python
def validate_project_coherence(self):
    """
    APC runs coherence checks on project state.

    Checks:
    - All imports are valid (no missing files)
    - Test coverage for new code
    - Documentation exists for public APIs
    - No orphaned files (unreferenced)
    - Consistent coding patterns
    - Architecture principles followed
    """
    return {
        "coherence_score": 92,  # 0-100
        "issues": [
            {
                "severity": "warning",
                "type": "missing_tests",
                "file": "agentflow/mcp/apc_mcp_server.py",
                "message": "No integration test for Tool 8 (session_bridge)",
                "recommendation": "Add test in tests/test_apc_integration.py"
            }
        ],
        "suggestions": [
            "Consider adding architecture diagram to .apc/knowledge/",
            "Update ADR-002 with deployment results"
        ]
    }
```

---

## 🚀 Implementation Plan

### Phase 1: Project Structure Awareness (2-3 hours)

**Tasks:**
1. Create `.apc/` directory structure
2. Implement `scan_project` function
3. Generate `project_index.json`
4. Add `mcp__apc__scan_project` MCP tool
5. Test on agentflow-src project

**Deliverables:**
- `.apc/` directory with config and project_index
- New MCP tool for scanning
- Documentation of structure

### Phase 2: Persistent Memory (3-4 hours)

**Tasks:**
1. Implement session logging to `.apc/sessions/`
2. Create knowledge base structure (`.apc/knowledge/`)
3. Add `mcp__apc__query_project` MCP tool
4. Implement `mcp__apc__update_project_state` MCP tool
5. Auto-update PROJECT_STATE.md

**Deliverables:**
- Session history tracking
- Knowledge base (decisions, patterns)
- Automatic PROJECT_STATE.md updates

### Phase 3: Task Integration (2-3 hours)

**Tasks:**
1. Create `.apc/tasks/` structure
2. Integrate with TodoWrite
3. Track task completion automatically
4. Add dependency tracking
5. Generate task reports

**Deliverables:**
- Task tracking in `.apc/tasks/`
- TodoWrite integration
- Automatic task status updates

### Phase 4: Session Bridging (3-4 hours)

**Tasks:**
1. Implement `mcp__apc__session_bridge` MCP tool
2. Auto-load previous session context
3. Generate "what's next" recommendations
4. Compress multi-session context
5. Test <5 min bootstrap time

**Deliverables:**
- Seamless session continuity
- <5 min new session startup
- Automatic context recovery

### Phase 5: Coherence Validation (4-5 hours)

**Tasks:**
1. Implement project coherence checks
2. Validate file relationships (imports, deps)
3. Check test coverage
4. Verify documentation completeness
5. Add coherence scoring (0-100)

**Deliverables:**
- Automatic coherence validation
- Issue detection and recommendations
- Quality gate before commits

---

## 📊 Expected Benefits

### For Development

**Before (Current State):**
- Manual PROJECT_STATE.md updates
- No automatic task tracking
- Session context lost between sessions
- No project structure awareness
- Manual coherence validation

**After (With Enhancements):**
- ✅ Automatic PROJECT_STATE.md updates
- ✅ Automatic task tracking via TodoWrite
- ✅ <5 min session bootstrap (automatic context recovery)
- ✅ Complete project structure awareness
- ✅ Automatic coherence validation (0-100 score)
- ✅ Knowledge base with ADRs and patterns
- ✅ Session history with cost tracking

### For Claude Sessions

**APC becomes:**
1. **Project Memory** - Knows everything about the project
2. **Quality Gatekeeper** - Validates coherence automatically
3. **Session Bridge** - Seamless continuity between sessions
4. **Knowledge Curator** - Maintains decisions and patterns
5. **Task Coordinator** - Tracks what's done, what's next

### Metrics

**Time Savings:**
- Session bootstrap: 20 min → <5 min (75% reduction)
- Project onboarding: 2 hours → 15 min (87% reduction)
- Task status update: 10 min → automatic (100% reduction)

**Quality Improvements:**
- Coherence score: N/A → 0-100 automatic
- Missing tests detection: Manual → Automatic
- Orphaned files: Manual → Automatic detection
- Architecture drift: Undetected → Automatic alerts

---

## 🎯 Success Criteria

**APC is the Project Coherence Warranty when:**

1. ✅ **Knows Project Structure** - Can list all files, dependencies, architecture
2. ✅ **Maintains Persistent Memory** - Session history, knowledge base, decisions
3. ✅ **Tracks Tasks Automatically** - TodoWrite integration, dependency tracking
4. ✅ **Bridges Sessions** - <5 min bootstrap with full context recovery
5. ✅ **Validates Coherence** - Automatic checks, issue detection, scoring
6. ✅ **Allowed to Review All Resources** - File access, scanning, indexing

**User Confidence:**
- "APC knows my project better than I do"
- "APC catches issues before I commit"
- "APC makes every session feel like continuation"
- "APC is the single source of truth"

---

## 🚨 Current Status

**What Works Today:**
- ✅ Context compression (12x)
- ✅ Quality validation (0-100)
- ✅ Workflow integration
- ✅ Metrics tracking (session-scoped)

**What's Missing (Critical Gap!):**
- ❌ No .apc/ directory
- ❌ No project structure awareness
- ❌ No persistent memory
- ❌ No session bridging
- ❌ No coherence validation

**Recommendation:**
**IMPLEMENT PHASE 1-2 IMMEDIATELY** (Project Structure + Persistent Memory)

This makes APC the true "warranty of project coherence" as you envisioned!

---

## 📚 Documentation Updates Needed

1. **APC_MCP_README.md** - Add new tools (scan_project, query_project, etc.)
2. **CLAUDE.md** - Add "APC as Coherence Warranty" section
3. **PROJECT_STATE.md** - Add .apc/ directory reference
4. **DEPLOYMENT_COMPLETE_2025-10-14.md** - Note enhancement opportunity

---

**BOTTOM LINE:** APC has the POTENTIAL to be the project coherence warranty, but needs **Project Structure Awareness + Persistent Memory** implementation to fulfill that role!

Should we implement Phase 1-2 now? (6-7 hours total, MASSIVE value)
