# Change Proposal: Complete APC MCP Tools Testing

**Proposed**: 2025-10-14
**Status**: In Progress
**Priority**: High

---

## Change Summary

Complete testing of APC MCP server tools 5 and 6 (`scan_project` and `query_project`) to make APC fully operational.

---

## Motivation

APC MCP server has 6 tools, but only 4 are fully tested:
- ✅ prepare_context (tested, working)
- ✅ validate_output (tested, working)
- ✅ execute_workflow (tested, working)
- ✅ get_metrics (tested, working)
- ⚠️ scan_project (needs E2E testing)
- ⚠️ query_project (needs E2E testing)

Testing tools 5 and 6 will enable:
- Project-aware context preparation
- Worker agents can query project structure
- Better delegation with full project knowledge

---

## Proposed Changes

### Change 1: Test `scan_project` Tool

**File**: `agentflow/mcp/apc_mcp_server.py` (tool already exists)

**Test Requirements**:
1. Scan agentflow-src (6,971 Python files)
2. Create `.apc/project_index.json`
3. Verify index contains file paths, dependencies
4. Measure scan time (target: < 5 seconds)
5. Test incremental updates

**Expected Behavior**:
```python
# Input
{
  "project_path": "/path/to/agentflow-src",
  "include_patterns": ["*.py"],
  "exclude_patterns": ["__pycache__", ".venv"]
}

# Output
{
  "files_scanned": 6971,
  "index_location": ".apc/project_index.json",
  "scan_time": 2.3,
  "status": "complete"
}
```

### Change 2: Test `query_project` Tool

**File**: `agentflow/mcp/apc_mcp_server.py` (tool already exists)

**Test Requirements**:
1. Query "Find all files importing SmartOrchestrator"
2. Query "List all test files"
3. Query "Find files with TODO comments"
4. Verify result accuracy (100%)
5. Measure query time (target: < 1 second)

**Expected Behavior**:
```python
# Input
{
  "query": "Find all files importing SmartOrchestrator",
  "filters": {"file_type": "py"}
}

# Output
{
  "results": [
    {"file": "tests/test_smart_orchestrator.py", "line": 5},
    {"file": "run_delegation_pool.py", "line": 3},
    ...
  ],
  "count": 12
}
```

### Change 3: E2E Integration Test

**New File**: `tests/test_apc_mcp_project_tools.py`

**Test Cases**:
1. `test_scan_large_project()`: Scan 6,971 files
2. `test_query_accuracy()`: Verify 100% accurate results
3. `test_scan_incremental()`: Update only changed files
4. `test_query_performance()`: Measure < 1 second queries
5. `test_integration()`: scan → query → prepare_context workflow

---

## Tasks

### Phase 1: Testing (1-2 hours)

- [ ] Run `scan_project` on agentflow-src
- [ ] Verify `.apc/project_index.json` created
- [ ] Test 5 different queries with `query_project`
- [ ] Verify query accuracy
- [ ] Measure performance

### Phase 2: Fix Issues (if any) (1 hour)

- [ ] Address performance bottlenecks
- [ ] Fix accuracy issues
- [ ] Improve error handling

### Phase 3: Documentation (30 min)

- [ ] Update `MCP_INTEGRATION_GUIDE.md`
- [ ] Mark tools 5 and 6 as ✅ WORKING
- [ ] Add usage examples

---

## Success Criteria

- ✅ `scan_project` scans 6,971 files in < 5 seconds
- ✅ Index file created at `.apc/project_index.json`
- ✅ `query_project` returns 100% accurate results
- ✅ Query performance < 1 second
- ✅ All 6 APC tools marked as WORKING
- ✅ E2E integration test passing

---

## Implementation Notes

**Delegation Opportunity**: ❌ NO
- Interactive testing required
- Need to verify actual file system operations
- Need to validate query accuracy manually

**Estimated Time**: 2-3 hours total

**Blocked By**: None (tools already implemented, just need testing)

---

## Risk Assessment

**Risk**: Low
- Tools are already implemented
- Just need to verify they work correctly
- No changes to existing working tools

**Mitigation**:
- Test in isolated directory first
- Backup `.apc/` directory if it exists
- Validate results before marking as complete
