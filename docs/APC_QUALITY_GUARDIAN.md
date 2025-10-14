# APC Quality Guardian - Quality Assurance & Learning Loops

**Date**: 2025-10-14
**Status**: 🔄 DESIGN PHASE
**Complements**: APC_INTEGRATION_PLAN.md (Phase 1 algorithms)

---

## 🎯 Executive Summary

This document extends the Session Context Curator from a **context optimizer** into a **Quality Guardian** with:
- **Quality Gates** (PRE/RUN/POST audit)
- **Tool Policies** (allowlist, parameter bounds, anti-risk rules)
- **Metrics & SLOs** (Integrity Score, Context Efficiency, Tool Hygiene)
- **Learning Loops** (auto-tuning, knowledge gaps, playbook)

**Integration with Phase 1:**
- Phase 1 (algorithms): MMR + Chain-of-Density + Knapsack = **optimize context**
- Phase 2 (quality): Quality Gates + Metrics + Learning = **guarantee quality**
- Result: **Self-improving, production-grade system**

---

## 📊 Extended APC Roles

### Current Role (Phase 1)
✅ **Prepare Context**: Curate minimal relevant context per session

### New Roles (Phase 2-3)

1. **Guard Tool Compliance** (Phase 2)
   - Allowlist tools per ticket type
   - Enforce parameter bounds (timeouts, scopes, quotas)
   - Block dangerous operations (writes with low integrity)

2. **Audit Sessions** (Phase 2)
   - PRE gate: Validate context quality before execution
   - RUN gate: Monitor runtime behavior (tool calls, budget)
   - POST gate: Review outcomes vs acceptance criteria

3. **Learn Continuously** (Phase 3)
   - Post-mortems on failed sessions
   - Auto-tune caps based on waste tokens
   - Build playbook of best practices
   - Detect knowledge gaps

---

## 🚦 Quality Gates System

### Gate 1: PRE-EXECUTION (Before Session Starts)

**Purpose:** Ensure context quality and safety before agent execution

**Checks:**

1. **Tool Policy Validation**
   ```python
   # Verify agent only has access to allowed tools
   allowed_tools = TOOL_POLICIES[ticket.type]
   if tool not in allowed_tools:
       raise PolicyViolation(f"Tool {tool} not allowed for {ticket.type}")
   ```

2. **Context Lint**
   ```python
   violations = []
   # Check section caps
   if len(pack.problem_brief) > 350:
       violations.append("problem_brief_exceeds_cap")

   # Check evidence coverage
   if evidence_coverage(pack) < 0.95:
       violations.append("insufficient_evidence_coverage")

   # Check deduplication
   if has_redundancy(pack, threshold=0.85):
       violations.append("high_redundancy_detected")
   ```

3. **Grounding Check**
   ```python
   # Every factual statement must have evidence
   for statement in extract_facts(pack):
       if not has_evidence(statement, pack.evidence):
           violations.append(f"ungrounded_fact: {statement[:50]}...")
   ```

4. **Risk Scan**
   ```python
   risks = []
   # Detect contradictions
   if has_contradictions(pack.sources):
       risks.append("contradicting_sources_detected")

   # Check for deprecated APIs
   if uses_deprecated_apis(pack.relevant_files):
       risks.append("deprecated_api_usage")

   # Verify dependencies exist
   if missing_dependencies(pack.dependencies):
       risks.append("missing_dependencies")
   ```

**Outcome:**
- ✅ **PASS**: Session can proceed
- ⚠️ **WARN**: Issues logged, session proceeds with caution
- ❌ **FAIL**: Session blocked, pack_delta required

---

### Gate 2: RUNTIME (During Execution)

**Purpose:** Monitor agent behavior and enforce guardrails

**Monitoring:**

1. **Tool Call Monitoring**
   ```python
   for call in session.tool_calls:
       # Check latency
       if call.latency_ms > LATENCY_THRESHOLD:
           alert("high_latency_tool_call", call)

       # Check errors
       if call.status == "error":
           log_error(call)
           if error_rate > 0.10:  # 10% error rate
               trigger_escalation()

       # Detect retry storms
       if consecutive_retries(call.tool) > 5:
           circuit_break(call.tool)
   ```

2. **Budget Watch**
   ```python
   # Track token consumption
   if session.tokens_used > session.token_budget * 0.90:
       warn("approaching_budget_limit")

   if session.tokens_used > session.token_budget:
       # Soft cutoff: offer RFC
       offer_rfc("budget_exceeded", session)
       pause_execution()
   ```

3. **Behavior Anomalies**
   ```python
   # Detect unusual patterns
   if accessing_files_outside_scope(session):
       alert("scope_violation", session)

   if excessive_file_modifications(session):
       alert("high_change_rate", session)
   ```

**Outcome:**
- ✅ **NORMAL**: Continue execution
- ⚠️ **ANOMALY**: Log warning, may adjust guardrails
- ❌ **VIOLATION**: Pause/terminate session

---

### Gate 3: POST-EXECUTION (After Session Ends)

**Purpose:** Validate outcomes and extract learning

**Checks:**

1. **Outcome Lint**
   ```python
   # Verify deliverables match acceptance criteria
   for criterion in ticket.acceptance_criteria:
       if not criterion.satisfied(outcome):
           violations.append(f"acceptance_not_met: {criterion}")

   # Check code quality
   if has_code_smells(outcome.modified_files):
       recommendations.append("refactor_suggested")
   ```

2. **Diff Review**
   ```python
   # Ensure changes match problem scope
   if scope_creep_detected(outcome.diffs, ticket.scope):
       violations.append("scope_creep")

   # Verify all changes documented
   if undocumented_changes(outcome.diffs):
       recommendations.append("add_change_documentation")
   ```

3. **Debrief Generation**
   ```python
   debrief = {
       "anomalies": session.anomalies,
       "recommendations": [
           "Reduce recent_changes by 15% (redundancy)",
           "Add excerpt from auth.py:L90-L120 (called but not cited)"
       ],
       "lessons_learned": extract_lessons(session),
       "pack_improvements": suggest_pack_optimizations(session)
   }
   ```

**Outcome:**
- ✅ **SUCCESS**: All criteria met, lessons extracted
- ⚠️ **PARTIAL**: Some criteria met, improvements needed
- ❌ **FAILURE**: Major issues, session marked for review

---

## 📏 Metrics & Scoring System

### Core Metrics

1. **Integrity Score** (0-100)
   ```python
   integrity = 100 - (
       grounding_penalties +
       contradiction_penalties +
       orphan_ref_penalties
   )

   # Example:
   # - 5 ungrounded facts × 3 pts = -15
   # - 2 contradictions × 5 pts = -10
   # - 3 orphan refs × 2 pts = -6
   # Integrity = 100 - 31 = 69 ❌ (below 85 threshold)
   ```

2. **Context Efficiency** (0-1)
   ```python
   efficiency = useful_facts / total_tokens

   # Example:
   # - 45 useful facts, 8000 tokens
   # - Efficiency = 45/8000 = 0.0056
   # - Target: >0.005 (5+ facts per 1000 tokens)
   ```

3. **Retrieval Precision@k** (0-1)
   ```python
   precision_at_k = excerpts_actually_used / k_provided

   # Example:
   # - Provided 12 excerpts
   # - Agent used 8 excerpts
   # - P@12 = 8/12 = 0.67 ⚠️ (target: >0.70)
   ```

4. **Tool Hygiene** (0-1)
   ```python
   hygiene = 1 - (weighted_errors / total_tool_calls)

   # Example:
   # - 50 tool calls
   # - 1 timeout (weight 2) + 1 auth error (weight 3)
   # - Hygiene = 1 - (5/50) = 0.90 ⚠️ (target: ≥0.95)
   ```

5. **Convergence Time** (seconds)
   ```python
   convergence = time(pack_v1 → pack_final)

   # Target: <60 seconds (fast convergence)
   # If >120 seconds: investigate pack quality issues
   ```

6. **RFC Rate** (0-1)
   ```python
   rfc_rate = num_rfcs / num_tickets

   # Example:
   # - 5 tickets processed
   # - 2 RFCs requested
   # - RFC Rate = 2/5 = 0.40 ❌ (target: ≤0.20)
   ```

7. **Waste Tokens** (absolute)
   ```python
   waste = tokens_explored - tokens_delivered

   # Example:
   # - Explored 15,000 tokens during preparation
   # - Delivered 8,000 token pack
   # - Waste = 7,000 tokens (47% efficiency loss)
   ```

### Service Level Objectives (SLOs)

**By Ticket Type:**

| Metric | Bug | Feature | Docs | Ops | Test |
|--------|-----|---------|------|-----|------|
| Integrity Score | ≥90 | ≥85 | ≥95 | ≥90 | ≥85 |
| Context Efficiency | ≥0.006 | ≥0.005 | ≥0.008 | ≥0.005 | ≥0.004 |
| Tool Hygiene | ≥0.98 | ≥0.95 | ≥0.99 | ≥0.97 | ≥0.93 |
| RFC Rate | ≤0.15 | ≤0.25 | ≤0.10 | ≤0.20 | ≤0.30 |
| Convergence Time | ≤45s | ≤90s | ≤30s | ≤60s | ≤120s |

**Rationale:**
- Docs require highest integrity (95%) - factual accuracy critical
- Tests tolerate more RFCs (30%) - exploratory nature
- Bugs need fast convergence (45s) - urgency
- Features allow more waste (90s) - complexity

---

## 🔐 Tool Policies System

### Policy Structure

```python
TOOL_POLICIES = {
    "bug": {
        "allowed": [
            "code.search",
            "git.read",
            "git.blame",
            "tests.run",
            "code.edit.limited"
        ],
        "denied": [
            "package.publish",
            "db.write",
            "api.deploy"
        ],
        "params": {
            "tests.run": {"timeout_max": 480},  # 8 minutes
            "code.search": {"top_k_max": 15},
            "code.edit.limited": {"scope": "src/**"}
        }
    },
    "feature": {
        "allowed": [
            "code.search",
            "git.read",
            "design.note",
            "tests.run",
            "code.edit.limited",
            "doc.generate"
        ],
        "denied": [
            "package.publish",
            "db.migrate",
            "api.deploy"
        ],
        "params": {
            "tests.run": {"timeout_max": 600},  # 10 minutes
            "code.search": {"top_k_max": 20}
        }
    },
    "docs": {
        "allowed": [
            "code.search",
            "git.read",
            "doc.generate",
            "doc.lint"
        ],
        "denied": [
            "code.edit",  # Docs agents shouldn't edit code
            "tests.run",
            "package.*"
        ],
        "params": {
            "code.search": {"top_k_max": 10}
        }
    },
    "ops": {
        "allowed": [
            "git.read",
            "config.validate",
            "deploy.plan",
            "tests.integration"
        ],
        "denied": [
            "code.edit",  # Ops shouldn't edit code directly
            "db.write"
        ],
        "params": {
            "tests.integration": {"timeout_max": 900}  # 15 minutes
        }
    }
}
```

### Anti-Risk Rules

```python
def check_anti_risk_rules(session, pack):
    """Block dangerous operations if quality insufficient"""

    # Rule 1: No writes with low integrity
    if pack.integrity_score < 85:
        if any_write_tools(session.planned_tools):
            raise PolicyViolation(
                "Write operations blocked: integrity too low (< 85)",
                required_action="improve_pack_integrity"
            )

    # Rule 2: No deploys with unresolved contradictions
    if has_contradictions(pack):
        if "deploy" in session.planned_tools:
            raise PolicyViolation(
                "Deploy blocked: unresolved source contradictions",
                required_action="resolve_contradictions"
            )

    # Rule 3: No database operations without explicit approval
    if any_db_tools(session.planned_tools):
        if not session.has_approval("db_operations"):
            raise PolicyViolation(
                "Database operations require explicit approval",
                required_action="request_db_approval"
            )
```

---

## 🔍 Context Linter Implementation

### Linter Rules

```python
class ContextLinter:
    """Lint context packs for quality and compliance"""

    RULES = {
        "section_caps": {
            "problem_brief": 350,      # tokens
            "key_constraints": 200,
            "minimal_API_refs": 500,
            "recent_changes": 1000,
            "test_vectors": 300,
            "risks": 200
        },
        "evidence_coverage": 0.95,  # 95% facts must have evidence
        "dedup_threshold": 0.85,    # Jaccard similarity
        "freshness_ratio": 0.60,    # 60% sources < 30 days (for bugs)
        "orphan_tolerance": 0        # No orphan refs allowed
    }

    def lint(self, pack: ContextPack) -> LintResult:
        """Run all linter rules"""
        violations = []
        warnings = []

        # Check section caps
        for section, cap in self.RULES["section_caps"].items():
            if section in pack.sections:
                tokens = estimate_tokens(pack.sections[section])
                if tokens > cap:
                    violations.append(
                        Violation(
                            rule="section_cap",
                            section=section,
                            actual=tokens,
                            limit=cap,
                            severity="high"
                        )
                    )

        # Check evidence coverage
        coverage = self._calculate_evidence_coverage(pack)
        if coverage < self.RULES["evidence_coverage"]:
            violations.append(
                Violation(
                    rule="evidence_coverage",
                    actual=coverage,
                    required=self.RULES["evidence_coverage"],
                    severity="high"
                )
            )

        # Check for orphans
        orphans = self._find_orphan_refs(pack)
        if orphans:
            for orphan in orphans:
                violations.append(
                    Violation(
                        rule="orphan_ref",
                        ref=orphan,
                        severity="medium"
                    )
                )

        # Check deduplication
        duplicates = self._find_duplicates(pack)
        if duplicates:
            for dup in duplicates:
                warnings.append(
                    Warning(
                        rule="high_similarity",
                        sections=dup.sections,
                        similarity=dup.score,
                        severity="low"
                    )
                )

        # Check freshness (for bugs)
        if pack.ticket_type == "bug":
            freshness = self._calculate_freshness(pack)
            if freshness < self.RULES["freshness_ratio"]:
                warnings.append(
                    Warning(
                        rule="stale_sources",
                        freshness=freshness,
                        required=self.RULES["freshness_ratio"],
                        severity="medium"
                    )
                )

        return LintResult(
            violations=violations,
            warnings=warnings,
            passed=len(violations) == 0,
            score=self._calculate_score(violations, warnings)
        )

    def _calculate_evidence_coverage(self, pack: ContextPack) -> float:
        """Calculate % of facts with evidence"""
        facts = extract_factual_statements(pack)
        grounded = [f for f in facts if has_evidence_tag(f, pack.evidence)]
        return len(grounded) / len(facts) if facts else 1.0

    def _find_orphan_refs(self, pack: ContextPack) -> List[str]:
        """Find references without excerpts/hashes"""
        orphans = []
        for file_ref in pack.relevant_files:
            if not file_ref.get("excerpt"):
                orphans.append(file_ref["path"])
            if not file_ref.get("sha"):
                orphans.append(f"{file_ref['path']} (missing hash)")
        return orphans

    def _find_duplicates(self, pack: ContextPack) -> List[Duplicate]:
        """Find highly similar sections (Jaccard > threshold)"""
        duplicates = []
        sections = list(pack.sections.items())

        for i, (name1, content1) in enumerate(sections):
            for name2, content2 in sections[i+1:]:
                similarity = jaccard_similarity(content1, content2)
                if similarity > self.RULES["dedup_threshold"]:
                    duplicates.append(
                        Duplicate(
                            sections=[name1, name2],
                            score=similarity
                        )
                    )

        return duplicates

    def _calculate_freshness(self, pack: ContextPack) -> float:
        """Calculate % of sources < 30 days old"""
        recent = [
            s for s in pack.sources
            if days_since(s.timestamp) < 30
        ]
        return len(recent) / len(pack.sources) if pack.sources else 1.0
```

---

## 📊 Session Audit Schema

### Complete Audit JSON

```json
{
  "session_id": "S-2025-10-14-042",
  "ticket_id": "T-2025-10-14-001",
  "agent_id": "dev-agent-01",
  "session_type": "feature_dev",
  "start_time": "2025-10-14T08:30:00Z",
  "end_time": "2025-10-14T09:45:00Z",
  "duration_seconds": 4500,

  "pre_gate": {
    "timestamp": "2025-10-14T08:29:50Z",
    "policies_checked": [
      "tool_allowlist",
      "parameter_bounds",
      "section_caps",
      "grounding_check",
      "freshness_check"
    ],
    "lint_result": {
      "passed": false,
      "violations": [
        {
          "rule": "section_cap",
          "section": "recent_changes",
          "actual": 1250,
          "limit": 1000,
          "severity": "high"
        }
      ],
      "warnings": [
        {
          "rule": "stale_sources",
          "freshness": 0.52,
          "required": 0.60,
          "severity": "medium"
        }
      ]
    },
    "scores": {
      "integrity": 88,
      "context_efficiency": 0.0052,
      "evidence_coverage": 0.94
    },
    "action": "pack_delta_v2",
    "status": "retry_with_fixes"
  },

  "runtime": {
    "token_usage": {
      "budget": 8000,
      "used": 6840,
      "utilization": 0.855
    },
    "tool_calls": [
      {
        "id": "call_001",
        "timestamp": "2025-10-14T08:35:12Z",
        "tool": "code.search",
        "args_hash": "sha256:abc...",
        "status": "ok",
        "latency_ms": 210,
        "tokens_used": 450
      },
      {
        "id": "call_002",
        "timestamp": "2025-10-14T08:42:30Z",
        "tool": "tests.run",
        "args": {"timeout": 300, "suite": "unit"},
        "status": "error",
        "error": "timeout_exceeded",
        "latency_ms": 300000,
        "tokens_used": 0
      },
      {
        "id": "call_003",
        "timestamp": "2025-10-14T08:50:15Z",
        "tool": "code.edit.limited",
        "args_hash": "sha256:def...",
        "status": "ok",
        "latency_ms": 1850,
        "tokens_used": 1200
      }
    ],
    "anomalies": [
      {
        "type": "tool_timeout",
        "tool": "tests.run",
        "timestamp": "2025-10-14T08:42:30Z",
        "severity": "medium"
      },
      {
        "type": "high_token_burst",
        "tokens": 2500,
        "timestamp": "2025-10-14T09:15:00Z",
        "severity": "low"
      }
    ]
  },

  "post_gate": {
    "timestamp": "2025-10-14T09:45:10Z",
    "outcome_lint": {
      "acceptance_criteria_met": true,
      "deliverables_complete": true,
      "code_quality": {
        "complexity": "medium",
        "test_coverage": 0.87,
        "linting_passed": true
      }
    },
    "diff_review": {
      "scope_creep": false,
      "files_modified": 3,
      "lines_added": 245,
      "lines_removed": 87,
      "undocumented_changes": []
    },
    "scores": {
      "tool_hygiene": 0.93,  # 1 error out of 15 calls
      "retrieval_p_at_k": 0.75,  # 9/12 excerpts used
      "context_efficiency": 0.0058
    },
    "recommendations": [
      "Reduce recent_changes section by 20% (redundancy detected)",
      "Add excerpt from utils/validator.py:L45-L60 (called but not cited)",
      "Consider caching test.run results for faster iterations"
    ],
    "lessons_learned": [
      {
        "pattern": "tests.run timeout on large suites",
        "cause": "suite selection too broad",
        "remedy": "use targeted test selection with --focus flag",
        "tags": ["testing", "performance"]
      }
    ],
    "note_globale": 8.2
  },

  "summary": {
    "status": "success_with_warnings",
    "overall_score": 8.2,
    "slo_compliance": {
      "integrity": "✓ pass (88 ≥ 85)",
      "tool_hygiene": "⚠ warn (0.93 < 0.95)",
      "rfc_rate": "✓ pass (0/1 = 0.00 ≤ 0.25)"
    },
    "recommended_actions": [
      "Review test.run timeouts in future sessions",
      "Apply pack_delta optimizations from recommendations"
    ]
  }
}
```

---

## 🔄 Learning Loops

### 1. Auto-Tuning Caps

```python
class CapAutoTuner:
    """Automatically adjust section caps based on waste tokens"""

    def analyze_waste(self, sessions: List[SessionAudit]) -> Dict:
        """Identify sections with high waste"""
        section_waste = defaultdict(list)

        for session in sessions:
            for section, content in session.pack.sections.items():
                # Calculate waste: tokens in pack vs actually used
                delivered = estimate_tokens(content)
                used = session.post_gate.retrieval_metrics.get(section, 0)
                waste = delivered - used

                if waste > 0:
                    section_waste[section].append({
                        "session": session.id,
                        "waste": waste,
                        "waste_ratio": waste / delivered
                    })

        return section_waste

    def propose_adjustments(self, waste_analysis: Dict) -> List[CapAdjustment]:
        """Propose cap reductions for high-waste sections"""
        adjustments = []

        for section, waste_records in waste_analysis.items():
            avg_waste_ratio = mean([w["waste_ratio"] for w in waste_records])

            # If avg waste > 30%, reduce cap
            if avg_waste_ratio > 0.30:
                current_cap = ContextLinter.RULES["section_caps"].get(section)
                if current_cap:
                    proposed_cap = int(current_cap * (1 - avg_waste_ratio * 0.5))
                    adjustments.append(
                        CapAdjustment(
                            section=section,
                            current_cap=current_cap,
                            proposed_cap=proposed_cap,
                            reason=f"avg_waste={avg_waste_ratio:.1%}",
                            confidence=0.8 if len(waste_records) > 5 else 0.5
                        )
                    )

        return adjustments
```

### 2. Knowledge Gap Detection

```python
class KnowledgeGapDetector:
    """Detect recurring RFCs and create Intent Notes"""

    def analyze_rfcs(self, sessions: List[SessionAudit]) -> List[KnowledgeGap]:
        """Find recurring RFC patterns"""
        rfc_patterns = defaultdict(list)

        for session in sessions:
            for rfc in session.runtime.rfcs:
                # Cluster RFCs by topic
                topic = extract_topic(rfc.question)
                rfc_patterns[topic].append({
                    "session": session.id,
                    "question": rfc.question,
                    "module": rfc.context.module
                })

        # Identify gaps (topics with ≥3 RFCs)
        gaps = []
        for topic, rfcs in rfc_patterns.items():
            if len(rfcs) >= 3:
                gaps.append(
                    KnowledgeGap(
                        topic=topic,
                        frequency=len(rfcs),
                        affected_modules=set(r["module"] for r in rfcs),
                        sample_questions=[r["question"] for r in rfcs[:3]],
                        recommended_action="create_intent_note"
                    )
                )

        return gaps

    def create_intent_note(self, gap: KnowledgeGap) -> IntentNote:
        """Generate Intent Note to fill knowledge gap"""
        # Delegate to AgentFlow for comprehensive note generation
        task = f"""
        Create an Intent Note for recurring knowledge gap.

        Topic: {gap.topic}
        Frequency: {gap.frequency} RFCs across sessions
        Sample questions:
        {chr(10).join('- ' + q for q in gap.sample_questions)}

        Generate comprehensive note covering:
        1. Topic overview
        2. Common patterns
        3. Best practices
        4. Code examples
        5. Related APIs

        Output: Markdown format, 500-800 tokens
        """

        content = self.orchestrator.orchestrate(task)

        return IntentNote(
            topic=gap.topic,
            content=content,
            created_from="recurring_rfcs",
            frequency=gap.frequency,
            tags=list(gap.affected_modules)
        )
```

### 3. Tool Coaching

```python
class ToolCoach:
    """Add hints to packs for frequently failing tools"""

    def analyze_tool_failures(self, sessions: List[SessionAudit]) -> Dict:
        """Identify tools with high failure rates"""
        tool_failures = defaultdict(lambda: {"total": 0, "errors": []})

        for session in sessions:
            for call in session.runtime.tool_calls:
                tool_failures[call.tool]["total"] += 1
                if call.status == "error":
                    tool_failures[call.tool]["errors"].append({
                        "error": call.error,
                        "session": session.id,
                        "context": call.args_hash
                    })

        # Calculate failure rates
        problematic_tools = {}
        for tool, data in tool_failures.items():
            error_rate = len(data["errors"]) / data["total"]
            if error_rate > 0.15:  # >15% failure rate
                problematic_tools[tool] = {
                    "error_rate": error_rate,
                    "common_errors": Counter([e["error"] for e in data["errors"]]).most_common(3),
                    "sample_contexts": data["errors"][:3]
                }

        return problematic_tools

    def generate_hints(self, problematic_tools: Dict) -> Dict[str, List[str]]:
        """Generate coaching hints for problematic tools"""
        hints = {}

        for tool, data in problematic_tools.items():
            tool_hints = []

            # Common patterns
            if tool == "tests.run":
                if "timeout" in str(data["common_errors"]):
                    tool_hints.append(
                        "TIP: Use --focus flag to run subset of tests"
                    )
                    tool_hints.append(
                        "TIP: Set timeout based on suite size (unit:300s, integration:600s)"
                    )

            if tool == "code.search":
                if "too_many_results" in str(data["common_errors"]):
                    tool_hints.append(
                        "TIP: Use more specific query terms"
                    )
                    tool_hints.append(
                        "TIP: Limit top_k to 10-15 for focused results"
                    )

            hints[tool] = tool_hints

        return hints
```

### 4. Playbook Integration

```python
class PlaybookManager:
    """Maintain and inject best practices playbook"""

    def __init__(self):
        self.playbook_path = "apc/notes/playbook.md"
        self.lessons = self.load_lessons()

    def add_lesson(self, lesson: Lesson):
        """Add lesson to playbook"""
        self.lessons.append(lesson)
        self._persist_playbook()

    def get_relevant_lessons(self, ticket_type: str, context: str) -> List[Lesson]:
        """Get lessons relevant to current context"""
        relevant = []

        for lesson in self.lessons:
            # Match by ticket type
            if ticket_type not in lesson.applicable_to:
                continue

            # Match by keywords
            if any(kw in context.lower() for kw in lesson.keywords):
                relevant.append(lesson)

        # Sort by relevance/frequency
        relevant.sort(key=lambda l: l.frequency, reverse=True)

        return relevant[:5]  # Top 5 most relevant

    def inject_into_pack(self, pack: ContextPack, lessons: List[Lesson]):
        """Inject relevant lessons into pack's key_constraints"""
        if not lessons:
            return

        lesson_hints = [
            f"💡 {lesson.title}: {lesson.remedy}"
            for lesson in lessons
        ]

        # Add to key_constraints section
        if "key_constraints" not in pack.sections:
            pack.sections["key_constraints"] = []

        pack.sections["key_constraints"].extend(lesson_hints)
```

---

## 🔌 MCP Integration

### New Tool Definitions

```typescript
// tools.json additions

{
  "tools": [
    {
      "name": "lint_pack",
      "description": "Audit context pack quality (PRE gate)",
      "inputSchema": {
        "type": "object",
        "properties": {
          "pack_id": {"type": "string"},
          "strict": {"type": "boolean", "default": true}
        },
        "required": ["pack_id"]
      }
    },
    {
      "name": "enforce_policy",
      "description": "Validate tool call against policies",
      "inputSchema": {
        "type": "object",
        "properties": {
          "ticket_id": {"type": "string"},
          "tool_name": {"type": "string"},
          "tool_args": {"type": "object"}
        },
        "required": ["ticket_id", "tool_name"]
      }
    },
    {
      "name": "review_session",
      "description": "Complete POST-gate audit",
      "inputSchema": {
        "type": "object",
        "properties": {
          "session_id": {"type": "string"},
          "include_recommendations": {"type": "boolean", "default": true}
        },
        "required": ["session_id"]
      }
    },
    {
      "name": "lessons_learned.add",
      "description": "Add lesson to playbook",
      "inputSchema": {
        "type": "object",
        "properties": {
          "pattern": {"type": "string"},
          "cause": {"type": "string"},
          "remedy": {"type": "string"},
          "tags": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["pattern", "remedy"]
      }
    }
  ]
}
```

### New Resource Definitions

```typescript
// resources.json additions

{
  "resources": [
    {
      "uri": "resource://audits/{session_id}",
      "name": "Session Audit Report",
      "description": "Complete audit JSON for a session",
      "mimeType": "application/json"
    },
    {
      "uri": "resource://lessons/{topic}",
      "name": "Lessons Learned Corpus",
      "description": "Lessons for a specific topic",
      "mimeType": "text/markdown"
    },
    {
      "uri": "resource://metrics/dashboard",
      "name": "Quality Metrics Dashboard",
      "description": "Real-time quality metrics",
      "mimeType": "application/json"
    },
    {
      "uri": "resource://playbook",
      "name": "Best Practices Playbook",
      "description": "Complete playbook with all lessons",
      "mimeType": "text/markdown"
    }
  ]
}
```

---

## 📊 Dashboard Design

### Metrics Dashboard (Real-time)

```
┌─────────────────────────────────────────────────────────────┐
│  APC Quality Guardian Dashboard                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊 Overall Health                                            │
│  ├─ Integrity Score:        91/100  ✓                       │
│  ├─ Tool Hygiene:           0.97    ✓                       │
│  ├─ RFC Rate:               0.18    ✓                       │
│  └─ Avg Convergence:        42s     ✓                       │
│                                                               │
│  🎯 SLO Compliance (Last 24h)                                │
│  ├─ Bug tickets:    15/16 compliant   (93.75%) ✓           │
│  ├─ Feature tickets: 8/10 compliant   (80.00%) ⚠           │
│  ├─ Docs tickets:    5/5 compliant    (100%)   ✓           │
│  └─ Ops tickets:     3/4 compliant    (75.00%) ⚠           │
│                                                               │
│  ⚠️  Recent Violations (Last 7 days)                         │
│  ├─ section_cap exceeded:     12 occurrences               │
│  ├─ integrity_low:            3 occurrences                │
│  ├─ high_rfc_rate:            5 occurrences                │
│  └─ tool_timeout:             8 occurrences                │
│                                                               │
│  💡 Top Lessons Applied (Last 30 days)                       │
│  ├─ "Use targeted test selection" (32×)                     │
│  ├─ "Cache API responses" (18×)                             │
│  ├─ "Reduce recent_changes verbosity" (15×)                 │
│  └─ "Add missing type hints" (12×)                          │
│                                                               │
│  📈 Trends (7-day moving avg)                                │
│  ├─ Integrity:       ↗ +2.3 points                         │
│  ├─ RFC Rate:        ↘ -0.05                               │
│  ├─ Waste Tokens:    ↘ -850 tokens                         │
│  └─ Tool Hygiene:    ↗ +0.02                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Session Detail View

```
┌─────────────────────────────────────────────────────────────┐
│  Session: S-2025-10-14-042                                   │
│  Ticket: T-2025-10-14-001 (Feature: Add JWT auth)          │
│  Agent: dev-agent-01                                         │
│  Duration: 75 minutes                                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🚦 Quality Gates                                             │
│  ├─ PRE:  ⚠ Retry required (section_cap violation)         │
│  ├─ RUN:  ✓ Normal execution                               │
│  └─ POST: ✓ Success with recommendations                   │
│                                                               │
│  📊 Scores                                                    │
│  ├─ Integrity:           88/100  ✓ (≥85)                   │
│  ├─ Context Efficiency:  0.0058  ✓ (≥0.005)                │
│  ├─ Tool Hygiene:        0.93    ⚠ (≥0.95)                 │
│  ├─ Retrieval P@k:       0.75    ✓ (≥0.70)                 │
│  └─ Overall:             8.2/10  ✓                          │
│                                                               │
│  🔧 Tool Usage                                                │
│  ├─ code.search:    3 calls, 100% success                  │
│  ├─ tests.run:      2 calls, 50% success (1 timeout)       │
│  ├─ code.edit:      5 calls, 100% success                  │
│  └─ git.commit:     1 call, 100% success                   │
│                                                               │
│  💡 Recommendations (3)                                       │
│  ├─ Reduce recent_changes by 20% (redundancy)              │
│  ├─ Add excerpt from validator.py:L45-L60                  │
│  └─ Cache test.run results for faster iterations           │
│                                                               │
│  📚 Lessons Learned (1)                                       │
│  └─ Pattern: "tests.run timeout on large suites"           │
│     Remedy: "use targeted test selection with --focus"     │
│     Applied to playbook ✓                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Implementation Roadmap

### Phase 2: Quality Gates (Weeks 2-3)

**Week 2:**
- [ ] Implement ContextLinter (section caps, evidence, orphans)
- [ ] Implement PRE gate (tool policy + lint)
- [ ] Implement runtime monitoring (tool calls, budget)
- [ ] Basic metrics collection (integrity, efficiency)

**Week 3:**
- [ ] Implement POST gate (outcome lint, diff review)
- [ ] Session audit JSON generation
- [ ] MCP tool/resource integration
- [ ] Basic dashboard (CLI)

**Deliverables:**
- Complete quality gates system
- Session auditing
- Real-time metrics
- MCP integration

**Delegation:**
- Context Linter: $0.15 (4-5 hours)
- Quality Gates: $0.20 (5-6 hours)
- Metrics System: $0.10 (3-4 hours)
- **Total: $0.45**

---

### Phase 3: Learning Loops (Weeks 4-5)

**Week 4:**
- [ ] Auto-tuning caps based on waste
- [ ] Knowledge gap detection (RFC analysis)
- [ ] Tool coaching (failure analysis)
- [ ] Playbook infrastructure

**Week 5:**
- [ ] Intent Note generation (for gaps)
- [ ] Lesson extraction from sessions
- [ ] Playbook injection into packs
- [ ] Dashboard (web UI)

**Deliverables:**
- Self-improving system
- Automated learning
- Best practices playbook
- Full dashboard

**Delegation:**
- Auto-tuning: $0.12 (3-4 hours)
- Gap Detection: $0.15 (4-5 hours)
- Tool Coaching: $0.10 (3 hours)
- Playbook: $0.15 (4-5 hours)
- **Total: $0.52**

---

## 💰 Total Cost Analysis

### Implementation Costs

| Phase | Components | Delegation Cost | Duration |
|-------|------------|----------------|----------|
| Phase 1 | MMR + CoD + Knapsack | $0.45 | Week 1 |
| Phase 2 | Quality Gates + Metrics | $0.45 | Weeks 2-3 |
| Phase 3 | Learning Loops + Playbook | $0.52 | Weeks 4-5 |
| **Total** | **Complete APC System** | **$1.42** | **5 weeks** |

**Comparison:**
- Claude direct: ~$142 (100× delegation cost)
- Savings: 99% ($140.58)

### Runtime Costs (Per Session)

| Component | Cost | Frequency |
|-----------|------|-----------|
| PRE gate lint | $0.00 | Every session |
| Runtime monitoring | $0.00 | Every session |
| POST gate review | $0.00 | Every session |
| Chain-of-Density | $0.002 | 2-3 files/session |
| Lesson generation | $0.01 | 1/20 sessions |
| **Avg per session** | **$0.003** | **Negligible** |

---

## 🎓 Success Criteria

### Phase 2 Complete When:

- ✅ All 3 quality gates operational (PRE/RUN/POST)
- ✅ Context Linter passes on 95% of packs
- ✅ Metrics dashboard shows real-time data
- ✅ Session audits stored and retrievable
- ✅ MCP tools/resources functional

### Phase 3 Complete When:

- ✅ Auto-tuning reduces waste tokens by >30%
- ✅ Knowledge gaps detected and filled (RFC rate <0.15)
- ✅ Tool coaching reduces failure rates by >40%
- ✅ Playbook contains >20 validated lessons
- ✅ System demonstrably self-improving

### Production Ready When:

- ✅ Classification accuracy >92% (Phase 1)
- ✅ Context size <20 KB (Phase 1)
- ✅ All SLOs met 90%+ of time (Phase 2)
- ✅ Auto-tuning operational (Phase 3)
- ✅ Learning loops reducing errors over time (Phase 3)
- ✅ Dashboard operational (Phase 3)
- ✅ Comprehensive documentation (All phases)

---

## 🚀 Next Actions

### Immediate (After Phase 1 Complete)

1. **Design Phase 2 delegation tasks**
   - Context Linter implementation
   - Quality Gates system
   - Metrics collection

2. **Create MCP schema** for new tools/resources

3. **Plan Phase 2 testing strategy**

### Week 2 (Phase 2 Start)

1. **Delegate Context Linter** (4-5 hours, $0.15)
2. **Delegate Quality Gates** (5-6 hours, $0.20)
3. **Delegate Metrics System** (3-4 hours, $0.10)

### Week 4 (Phase 3 Start)

1. **Delegate Learning Loops** (parallel tasks)
2. **Build dashboard UI**
3. **Comprehensive system testing**

---

## 📚 Integration with Phase 1

### How They Work Together

**Phase 1 (Algorithms):**
- MMR: Selects **diverse** files → reduces redundancy
- Chain-of-Density: Compresses **large** files → reduces size
- Knapsack: Guarantees **budget** compliance → meets targets

**Phase 2 (Quality):**
- PRE gate: **Validates** Phase 1 output → catches issues
- RUN gate: **Monitors** execution → detects anomalies
- POST gate: **Reviews** outcomes → extracts learning

**Phase 3 (Learning):**
- Auto-tuning: **Optimizes** Phase 1 parameters → improves over time
- Gap detection: **Fills** knowledge holes → reduces RFCs
- Tool coaching: **Guides** better usage → reduces errors
- Playbook: **Injects** best practices → prevents issues

**Synergy:** Phase 1 optimizes context, Phase 2 guarantees quality, Phase 3 continuously improves both. Result: **Self-improving, production-grade system**.

---

**Status**: 🔄 Design complete, ready for Phase 2 delegation
**Expected Timeline**: 5 weeks total (Phase 1-3)
**Expected Outcome**: Self-improving Context Curator with guaranteed quality

**This completes the production-grade APC architecture!** 🚀
