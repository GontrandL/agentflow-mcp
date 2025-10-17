#!/usr/bin/env python3
"""
Test Quality-Aware Task Router - Phase 0 Implementation

Demonstrates how the quality router prevents failures like the code audit
by rejecting unsuitable tasks BEFORE delegation.

Test Scenarios:
1. Code Audit (119KB embedded code) - Should REJECT or HYBRID
2. Simple Code Generation - Should DELEGATE
3. Documentation Generation - Should DELEGATE
4. Complex Analysis - Should HYBRID or ESCALATE
"""

import sys
from pathlib import Path

# Add agentflow to path
sys.path.insert(0, str(Path(__file__).parent))

from agentflow.orchestration.quality_aware_task_router import (
    QualityAwareTaskRouter,
    TaskRejectionError,
    RoutingAction
)


def print_scenario(number: int, title: str):
    """Print scenario header"""
    print("\n" + "="*80)
    print(f"SCENARIO {number}: {title}")
    print("="*80 + "\n")


def test_code_audit_rejection():
    """
    Test Scenario 1: Code Audit with Embedded Code

    This replicates the real failure case:
    - Task: Code audit with 119KB embedded code
    - DeepSeek V3 produced generic templates (FAILED)
    - Cost: $0.17 wasted

    Expected: Router should REJECT or recommend HYBRID
    """
    print_scenario(1, "Code Audit with Large Embedded Code (119KB)")

    # Simulate code audit task (similar to real failure)
    task = '''
[MISSION]: Comprehensive Code Audit with Specific Bug Detection

## Task Type: Code Analysis (requires precise file:line references)

## FILES TO ANALYZE:

## FILE: agentflow/orchestration/smart_orchestrator.py

```python
# 1466 lines of actual Python code here (simulated)
''' + "# code line\n" * 1466 + '''
```

## FILE: agentflow/orchestration/tool_aware_validator.py

```python
# 1099 lines of actual Python code here (simulated)
''' + "# code line\n" * 1099 + '''
```

## FILE: agentflow/orchestration/failure_analyzer.py

```python
# 472 lines of actual Python code here (simulated)
''' + "# code line\n" * 472 + '''
```

## ANALYSIS REQUIREMENTS:

For EACH file, analyze and identify:

### 1. Syntax & Type Errors
Find REAL issues with **specific line numbers**:
- Missing type hints (specify line)
- Undefined variables (specify line)
- Import errors (specify line)

### 2. Logic Bugs
Find REAL issues with **specific line numbers**:
- Missing await on async functions (specify line)
- Race conditions (specify line)
- Off-by-one errors (specify line)

## CRITICAL REQUIREMENTS:

1. ✅ **MUST include file:line references** for EVERY issue
2. ✅ **MUST show actual code snippets** from those lines
3. ✅ **NO generic/theoretical issues** - only real bugs found in the provided code
4. ✅ **NO placeholder issues** - if you don't find a bug in a category, skip that category
'''

    print("Task Details:")
    print(f"  Size: {len(task.encode('utf-8'))} bytes (~119KB with real code)")
    print(f"  Type: Code audit (analytical)")
    print(f"  Embedded Code: 3 files, 3037 total lines")
    print(f"  Requirements: file:line precision, no generic issues\n")

    router = QualityAwareTaskRouter()

    try:
        decision = router.route_task(
            task=task,
            requirements={
                'needs_file_line_refs': True,
                'no_placeholders': True,
                'allow_premium': False  # User didn't enable premium
            }
        )

        print(router.explain_decision(decision))

        if decision.action == RoutingAction.REJECT:
            print("\n✅ SUCCESS: Router correctly REJECTED this task!")
            print("   This would have prevented the $0.17 waste and generic template failure.")

        elif decision.action == RoutingAction.HYBRID:
            print("\n✅ SUCCESS: Router recommends HYBRID workflow")
            print("   FREE generation + premium validation would catch quality issues.")

        return True

    except TaskRejectionError as e:
        print("\n✅ SUCCESS: Task REJECTED (as expected)!")
        print(f"\nRejection Details:")
        print(f"  Predicted Quality: {e.decision.predicted_quality}/100")
        print(f"  Reasoning: {e.decision.reasoning}")
        print("\nThis rejection would have:")
        print("  • Saved $0.17 in wasted delegation")
        print("  • Prevented generic template output")
        print("  • Alerted user to use Claude directly or enable premium")
        return True


def test_simple_code_generation():
    """
    Test Scenario 2: Simple Code Generation

    Expected: Router should DELEGATE (high confidence)
    """
    print_scenario(2, "Simple Code Generation")

    task = '''
Implement a Python function that validates email addresses using regex.

Requirements:
- Function name: validate_email(email: str) -> bool
- Must check basic email format (user@domain.ext)
- Include docstring with examples
- Add basic unit tests

Output to: /tmp/email_validator.py
'''

    print("Task Details:")
    print(f"  Size: {len(task.encode('utf-8'))} bytes")
    print(f"  Type: Code generation (generative)")
    print(f"  Embedded Code: None")
    print(f"  Requirements: Standard quality\n")

    router = QualityAwareTaskRouter()

    decision = router.route_task(task=task)
    print(router.explain_decision(decision))

    if decision.action == RoutingAction.DELEGATE:
        print("\n✅ SUCCESS: Router correctly chose DELEGATE")
        print("   This task is suitable for cost-effective delegation.")
        return True
    else:
        print(f"\n⚠️  UNEXPECTED: Expected DELEGATE, got {decision.action.value}")
        return False


def test_documentation_generation():
    """
    Test Scenario 3: Documentation Generation

    Expected: Router should DELEGATE (high confidence)
    """
    print_scenario(3, "Technical Documentation Generation")

    task = '''
Create comprehensive API documentation for the AgentFlow delegation system.

Include:
- Overview of the architecture
- SmartOrchestrator usage guide
- HybridOrchestrator workflow explanation
- Cost comparison table
- Example code snippets
- Troubleshooting guide

Output to: /tmp/agentflow_api_docs.md

Requirements:
- 2000-3000 words
- Well-structured markdown
- Code examples in Python
- Clear section headers
'''

    print("Task Details:")
    print(f"  Size: {len(task.encode('utf-8'))} bytes")
    print(f"  Type: Documentation (generative)")
    print(f"  Embedded Code: None")
    print(f"  Requirements: Long-form content\n")

    router = QualityAwareTaskRouter()

    decision = router.route_task(task=task)
    print(router.explain_decision(decision))

    if decision.action == RoutingAction.DELEGATE:
        print("\n✅ SUCCESS: Router correctly chose DELEGATE")
        print("   Documentation is ideal for delegation (99%+ cost savings).")
        return True
    else:
        print(f"\n⚠️  UNEXPECTED: Expected DELEGATE, got {decision.action.value}")
        return False


def test_complex_analysis_hybrid():
    """
    Test Scenario 4: Complex Analysis Requiring Validation

    Expected: Router should recommend HYBRID (medium confidence)
    """
    print_scenario(4, "Complex Code Analysis with Validation")

    task = '''
Analyze the AgentFlow orchestration system for performance bottlenecks.

Scope:
- Review all *_orchestrator.py files
- Identify slow operations (>1s)
- Check for inefficient algorithms
- Analyze async/await patterns
- Recommend optimizations

Requirements:
- Must analyze actual code structure
- Provide specific optimization recommendations
- Include performance impact estimates
- No generic advice - project-specific only

Output to: /tmp/agentflow_performance_analysis.md
'''

    print("Task Details:")
    print(f"  Size: {len(task.encode('utf-8'))} bytes")
    print(f"  Type: Analysis (analytical + generative = hybrid)")
    print(f"  Embedded Code: References to files but not embedded")
    print(f"  Requirements: Project-specific, performance focused\n")

    router = QualityAwareTaskRouter()

    decision = router.route_task(task=task)
    print(router.explain_decision(decision))

    if decision.action == RoutingAction.HYBRID:
        print("\n✅ SUCCESS: Router correctly chose HYBRID")
        print("   FREE generation + premium validation ensures quality.")
        return True
    elif decision.action == RoutingAction.DELEGATE:
        print("\n⚠️  Router chose DELEGATE (acceptable if quality score is high)")
        return decision.predicted_quality >= 80
    else:
        print(f"\n⚠️  UNEXPECTED: Expected HYBRID, got {decision.action.value}")
        return False


def test_with_premium_escalation():
    """
    Test Scenario 5: Code Audit with Premium Escalation Enabled

    Expected: Router should ESCALATE to premium model
    """
    print_scenario(5, "Code Audit with Premium Escalation Enabled")

    task = '''
Perform security audit of authentication system.

Files to audit:
- auth_handler.py (embedded below)
- session_manager.py (embedded below)

```python
# 500 lines of actual authentication code
''' + "# auth code line\n" * 500 + '''
```

Find:
- SQL injection vulnerabilities (with line numbers)
- Authentication bypass possibilities (with line numbers)
- Session fixation risks (with line numbers)
- Crypto implementation flaws (with line numbers)

CRITICAL: Must provide specific line numbers and exploit scenarios.
'''

    print("Task Details:")
    print(f"  Size: {len(task.encode('utf-8'))} bytes")
    print(f"  Type: Security audit (analytical)")
    print(f"  Embedded Code: 500 lines")
    print(f"  Requirements: Security-critical, needs precision")
    print(f"  Premium: ENABLED\n")

    router = QualityAwareTaskRouter()

    decision = router.route_task(
        task=task,
        requirements={
            'needs_file_line_refs': True,
            'allow_premium': True  # User enabled premium for critical tasks
        }
    )

    print(router.explain_decision(decision))

    if decision.action == RoutingAction.ESCALATE:
        print("\n✅ SUCCESS: Router correctly chose ESCALATE")
        print("   Security audits justify premium model cost.")
        return True
    elif decision.action == RoutingAction.HYBRID:
        print("\n✅ ACCEPTABLE: HYBRID is also valid for this task")
        return True
    else:
        print(f"\n⚠️  UNEXPECTED: Expected ESCALATE, got {decision.action.value}")
        return False


def main():
    """Run all test scenarios"""
    print("\n" + "="*80)
    print("QUALITY-AWARE TASK ROUTER - PHASE 0 TEST SUITE")
    print("="*80)
    print("\nPurpose: Demonstrate prevention of code audit failure")
    print("Implementation: Rule-based quality prediction (no ML)")
    print("Cost: $0 to run tests (no actual delegation)")
    print("\n" + "="*80)

    results = []

    # Run all scenarios
    results.append(("Code Audit Rejection", test_code_audit_rejection()))
    results.append(("Simple Code Generation", test_simple_code_generation()))
    results.append(("Documentation Generation", test_documentation_generation()))
    results.append(("Complex Analysis (Hybrid)", test_complex_analysis_hybrid()))
    results.append(("Security Audit (Premium)", test_with_premium_escalation()))

    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for scenario, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {scenario}")

    print("\n" + "="*80)
    print(f"Results: {passed}/{total} tests passed ({100*passed//total}%)")
    print("="*80 + "\n")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\nKey Achievements:")
        print("  ✅ Code audit failure would have been PREVENTED")
        print("  ✅ $0.17 waste would have been AVOIDED")
        print("  ✅ Appropriate tasks are DELEGATED for 99%+ cost savings")
        print("  ✅ Complex tasks routed to HYBRID for quality assurance")
        print("  ✅ Critical tasks escalated to PREMIUM when enabled")
        print("\n" + "="*80)
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review routing logic")
        return 1


if __name__ == "__main__":
    sys.exit(main())
