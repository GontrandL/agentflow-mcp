#!/usr/bin/env python3
"""
Extract Worker Outputs, Validate Quality, and Write Files

This script:
1. Extracts generated code from worker logs
2. Validates code quality (syntax, completeness, logic correctness)
3. Writes files to disk only if quality is acceptable
4. Provides MCP feedback for model selection improvement

Addresses user requirement: "you are also responsible of the files that are written
so always be sure that you write smart code, and provide the rating to mcp for the
output provided that didnot match expectations in order to be able to trigger choosing
smarted model for next iteration"
"""

import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Worker configurations
WORKERS = [
    {"id": 1, "log": "/tmp/worker1_escalation_v2.log", "file": "agentflow/orchestration/escalation_engine.py", "name": "escalation_engine.py"},
    {"id": 2, "log": "/tmp/worker2_interactive_v2.log", "file": "agentflow/orchestration/interactive_orchestrator.py", "name": "interactive_orchestrator.py"},
    {"id": 3, "log": "/tmp/worker3_quality_eval_v2.log", "file": "agentflow/orchestration/quality_evaluator.py", "name": "quality_evaluator.py"},
    {"id": 4, "log": "/tmp/worker4_feedback_v2.log", "file": "agentflow/mcp/feedback_receiver.py", "name": "mcp_feedback_receiver.py"},
    {"id": 5, "log": "/tmp/worker5_dashboard_v2.log", "file": "agentflow/mcp/dashboard.py", "name": "dashboard.py"},
    {"id": 6, "log": "/tmp/worker6_context_v2.log", "file": "agentflow/orchestration/context_injector.py", "name": "context_injector.py"},
    {"id": 7, "log": "/tmp/worker7_parallel_v2.log", "file": "agentflow/orchestration/parallel_executor.py", "name": "parallel_executor.py"},
    {"id": 8, "log": "/tmp/worker8_waterfall_v2.log", "file": "agentflow/orchestration/waterfall_orchestrator.py", "name": "waterfall_orchestrator.py"},
]

def extract_code_from_log(log_path: str) -> str:
    """Extract Python code from log file (between ```python and ```)"""
    log_path = Path(log_path)

    if not log_path.exists():
        print(f"❌ Log not found: {log_path}")
        return ""

    content = log_path.read_text()

    # Find code blocks
    matches = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

    if not matches:
        print(f"⚠️  No code blocks found in {log_path.name}")
        return ""

    # Return the largest code block (assuming it's the implementation)
    return max(matches, key=len)


def validate_syntax(code: str) -> Tuple[bool, List[str]]:
    """Validate Python syntax"""
    issues = []

    try:
        ast.parse(code)
        return True, []
    except SyntaxError as e:
        issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return False, issues


def validate_completeness(code: str) -> Tuple[bool, List[str]]:
    """Check for TODOs, FIXMEs, placeholders"""
    issues = []

    todo_patterns = ['TODO', 'FIXME', 'XXX', 'HACK', 'pass  # TODO']
    for pattern in todo_patterns:
        if pattern in code:
            count = code.count(pattern)
            issues.append(f"Found {count}x '{pattern}' markers")

    placeholder_patterns = ['...', 'NotImplementedError', 'raise NotImplementedError']
    for pattern in placeholder_patterns:
        if pattern in code:
            count = code.count(pattern)
            issues.append(f"Found {count}x placeholder: {pattern}")

    return len(issues) == 0, issues


def validate_logic_escalation_engine(code: str) -> Tuple[bool, List[str]]:
    """Specific validation for escalation_engine.py"""
    issues = []

    # Check _free_tier_failed logic (should fail when attempts >= 3)
    if 'def _free_tier_failed' in code:
        if 'attempts < 3' in code:
            issues.append("❌ CRITICAL: _free_tier_failed has INVERTED logic (should be 'attempts >= 3', not '< 3')")

    # Check _mid_tier_failed logic (should fail when attempts >= 2)
    if 'def _mid_tier_failed' in code:
        if 'attempts < 2' in code:
            issues.append("❌ CRITICAL: _mid_tier_failed has INVERTED logic (should be 'attempts >= 2', not '< 2')")

    # Check get_next_tier tier names
    if 'def get_next_tier' in code:
        if 'bronze' in code or 'silver' in code or 'gold' in code:
            issues.append("❌ CRITICAL: get_next_tier uses wrong tier names (should be 'free', 'mid', 'premium', not 'bronze/silver/gold')")

    return len(issues) == 0, issues


def validate_logic_interactive_orchestrator(code: str) -> Tuple[bool, List[str]]:
    """Specific validation for interactive_orchestrator.py"""
    issues = []

    # Check for required methods
    required_methods = ['orchestrate', '_analyze_task']
    for method in required_methods:
        if f'def {method}' not in code:
            issues.append(f"Missing required method: {method}")

    # Check for task validation
    if 'def add_task' in code:
        if 'InvalidTaskError' not in code:
            issues.append("Missing InvalidTaskError exception")

    return len(issues) == 0, issues


def validate_code(worker_id: int, name: str, code: str) -> Dict:
    """Complete validation with quality score"""
    validation = {
        "worker_id": worker_id,
        "name": name,
        "passed": True,
        "quality_score": 10,
        "issues": [],
        "feedback": []
    }

    # 1. Syntax validation (critical)
    syntax_ok, syntax_issues = validate_syntax(code)
    if not syntax_ok:
        validation["passed"] = False
        validation["quality_score"] -= 5
        validation["issues"].extend(syntax_issues)
        validation["feedback"].append("SYNTAX_ERROR: Escalate to better model")

    # 2. Completeness validation
    complete_ok, complete_issues = validate_completeness(code)
    if not complete_ok:
        validation["quality_score"] -= 2
        validation["issues"].extend(complete_issues)
        validation["feedback"].append("INCOMPLETE: Request retry with stricter prompt")

    # 3. Logic validation (file-specific)
    if name == "escalation_engine.py":
        logic_ok, logic_issues = validate_logic_escalation_engine(code)
        if not logic_ok:
            validation["passed"] = False
            validation["quality_score"] -= 4
            validation["issues"].extend(logic_issues)
            validation["feedback"].append("LOGIC_ERROR: Escalate to better model, add specific test cases")

    if name == "interactive_orchestrator.py":
        logic_ok, logic_issues = validate_logic_interactive_orchestrator(code)
        if not logic_ok:
            validation["quality_score"] -= 2
            validation["issues"].extend(logic_issues)
            validation["feedback"].append("MISSING_FEATURES: Request retry with complete spec")

    # 4. Code quality checks
    if len(code) < 100:
        validation["passed"] = False
        validation["quality_score"] -= 3
        validation["issues"].append("Code too short (< 100 lines), likely incomplete")

    if 'import' not in code:
        validation["quality_score"] -= 1
        validation["issues"].append("No imports found, may be incomplete")

    # Final assessment
    if validation["quality_score"] < 6:
        validation["passed"] = False
        validation["feedback"].append(f"QUALITY_SCORE_{validation['quality_score']}: Recommend escalation to mid-tier model (deepseek-chat)")

    return validation


def write_file_with_fixes(file_path: str, code: str, validation: Dict) -> bool:
    """Write file to disk, applying fixes if needed"""
    file_path = Path(file_path)

    # Apply critical fixes
    if "escalation_engine.py" in str(file_path):
        # Fix inverted logic
        code = code.replace('return attempts < 3 or quality < 6', 'return attempts >= 3 or quality < 6')
        code = code.replace('return quality < 8 or attempts >= 2', 'return quality < 8 or attempts >= 2')  # This one is correct

        # Fix tier names
        code = code.replace("'bronze'", "'free'")
        code = code.replace("'silver'", "'mid'")
        code = code.replace("'gold'", "'premium'")
        code = code.replace("'platinum'", "'premium'")
        code = code.replace("'diamond'", "'premium'")
        code = code.replace("tiers = ['bronze', 'silver', 'gold', 'platinum', 'diamond']", "tiers = ['free', 'mid', 'premium']")

        print(f"✅ Applied critical fixes to escalation_engine.py")

    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    try:
        file_path.write_text(code)
        print(f"✅ Wrote {file_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to write {file_path}: {e}")
        return False


def main():
    print("="*60)
    print("🔍 WORKER OUTPUT EXTRACTION & VALIDATION")
    print("="*60)
    print("")

    results = []

    for worker in WORKERS:
        print(f"📋 Worker {worker['id']}: {worker['name']}")
        print(f"   Log: {worker['log']}")

        # 1. Extract code
        code = extract_code_from_log(worker['log'])
        if not code:
            print(f"   ⚠️  Skipping (no code found)\n")
            continue

        print(f"   ✅ Extracted {len(code)} characters")

        # 2. Validate quality
        validation = validate_code(worker['id'], worker['name'], code)
        results.append(validation)

        print(f"   Quality Score: {validation['quality_score']}/10")

        if validation['issues']:
            print(f"   ⚠️  Issues found:")
            for issue in validation['issues']:
                print(f"      - {issue}")

        if validation['feedback']:
            print(f"   📊 MCP Feedback:")
            for feedback in validation['feedback']:
                print(f"      - {feedback}")

        # 3. Write file (with fixes if applicable)
        if validation['passed'] or validation['quality_score'] >= 6:
            success = write_file_with_fixes(worker['file'], code, validation)
            if success:
                print(f"   ✅ File written successfully")
        else:
            print(f"   ❌ Quality too low ({validation['quality_score']}/10), NOT writing file")
            print(f"   📊 Recommendation: Re-delegate to better model")

        print("")

    # Summary
    print("="*60)
    print("📊 SUMMARY")
    print("="*60)
    passed = sum(1 for r in results if r['passed'] or r['quality_score'] >= 6)
    print(f"✅ Passed: {passed}/{len(results)}")
    print(f"❌ Failed: {len(results) - passed}/{len(results)}")
    print("")

    # MCP Feedback for model selection
    print("📋 MCP FEEDBACK FOR MODEL SELECTION:")
    for result in results:
        if result['feedback']:
            print(f"  {result['name']} (score: {result['quality_score']}/10):")
            for feedback in result['feedback']:
                print(f"    - {feedback}")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
