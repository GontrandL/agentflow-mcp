#!/usr/bin/env python3
"""Delegate Knapsack budget-optimized packing implementation to AgentFlow"""

import os
from pathlib import Path
from dotenv import load_dotenv
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

task = """
[MISSION]: Implement Knapsack-based file packing with HARD budget guarantee for SessionContextCurator

## Context
- Project: AgentFlow Session Context Curator
- File: agentflow/orchestration/session_recovery/session_context_curator.py
- Current: Soft limit (often exceeded) → 65KB contexts when target is 30KB
- Problem: No guarantee that budget is respected
- Solution: 0/1 Knapsack with greedy approximation → 100% budget compliance

## Requirements

Create file: agentflow/orchestration/session_recovery/knapsack_packer.py

Implement KnapsackPacker class with 1 key method:

1. pack(candidates: List[FileCandidate], budget_kb: int = 30) -> PackResult
   - Input: List of files with (path, value, size_kb)
   - Budget: Hard limit in KB (e.g., 30 KB)
   - Output: PackResult dict with:
     * selected_files: List of files that fit budget
     * total_size_kb: Total size (MUST be <= budget_kb)
     * total_value: Sum of relevance scores
     * utilization: percentage of budget used (target: 95%+)
     * guarantee: "HARD" (never exceeds budget)
   - Algorithm: Greedy approximation (value/size ratio)
   - Constraint: sum(sizes) <= budget_kb (MANDATORY)

## Algorithm (0/1 Knapsack Greedy)

Knapsack Packing:
1. Calculate value density: relevance_score / size_kb for each file
2. Sort files by value density (descending)
3. Greedy selection:
   - For each file (highest density first):
     * If (current_size + file.size_kb) <= budget_kb:
       * Add file to pack
       * Update current_size
     * Else: Skip file
4. Return selected files

Guarantee:
- sum(selected_files.size_kb) <= budget_kb (100% guaranteed)
- No exceptions, no soft limits
- Maximize value while respecting hard constraint

## Deliverables

Complete Python file with:
- KnapsackPacker class
- FileCandidate dataclass (path, relevance_score, size_kb)
- PackResult dataclass (selected_files, total_size_kb, total_value, utilization)
- pack method (greedy knapsack)
- validate_budget method (assert sum(sizes) <= budget)
- 3-5 unit tests (test budget compliance with edge cases)
- Docstrings with examples
- 250-300 lines total

## Success Criteria
- 100% budget compliance (HARD guarantee)
- No file pack exceeds budget_kb
- High utilization (>90% of budget used)
- Value maximization (best value/size ratio files selected)
- Tests verify edge cases (all files too large, exact fit, etc.)
- Ready to integrate into SessionContextCurator

## Edge Cases to Handle
1. All files exceed budget → return empty pack with warning
2. Single file = budget → return that file
3. Many small files → maximize utilization
4. Exact fit → perfect 100% utilization

Generate complete working code.
"""

print("🔄 Delegating Knapsack packing implementation to AgentFlow...")
print("This will take 2-3 hours and cost ~$0.10")
print()

orchestrator = SmartOrchestrator()
result = orchestrator.orchestrate(task)

print("✅ Knapsack packing implementation complete!")
print()
print("=" * 80)
print("RESULT")
print("=" * 80)
print(result)
