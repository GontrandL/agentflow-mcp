# Collaborative Design Session: Meta-Context & CRC Cognitif

**Date**: 2025-10-14
**Participants**: Gontrand (Human) + Claude (AI) + AgentFlow (Delegation System)
**Goal**: Refine Meta-Context/CRC architecture using validated insights from Perplexity report

---

## Session Context

**What We Have:**
- ✅ Phase 1 algorithms validated (MMR, Chain-of-Density, Knapsack) - 20/20 tests passing
- ✅ CRC Cognitif policy designed (hierarchical, adaptive, hybrid)
- ✅ External validation from Perplexity (96.5% alignment with production systems)
- ✅ Clear gaps identified (embeddings, logging) with roadmap

**What We're Designing:**
- 🎯 **Meta-Context Architecture**: How CRC layers interact with 4 meta-levels
- 🎯 **Drift Detection Strategy**: When/how to trigger CRC checks
- 🎯 **AutoFix Boundaries**: What can be auto-corrected vs requires validation
- 🎯 **Integration Path**: How to integrate into SessionContextCurator

---

## 1. Meta-Context Architecture Review

### Current 4-Layer Structure

From Perplexity synthesis, we align with hierarchical control pattern:

```yaml
# Layer 1: Fundamental (Executive Layer)
- Canonical rules (RuleDigest + SHA256 CRC)
- Global constraints (tools_allowlist, safety policies)
- Immutable objectives (problem_brief)

# Layer 2: Structural (Working Memory)
- Context sections (problem_brief, constraints, acceptance, evidence_map, recent_changes, relevant_files)
- Section-level CRCs for integrity
- Budget management (30 KB hard limit via Knapsack)

# Layer 3: Cognitive (Operational Layer)
- Focal attention tracking (what agent is working on RIGHT NOW)
- Drift detection (every 1800 tokens adaptive)
- Real-time corrections (cascade nudges: warning → soft → hard)

# Layer 4: Emergent (Learning Layer)
- Adaptive threshold tuning (based on history)
- Pattern recognition (recurring drift patterns)
- Performance optimization (relax/tighten check frequency)
```

### Design Questions for Collaboration

**Question 1: Inter-Layer Communication**

How should layers communicate CRC violations?

**Option A: Bubble-Up (Bottom-to-Top)**
```
Cognitive layer detects drift →
  Informs Structural layer (section CRC check) →
    Informs Fundamental layer (global rule violation?) →
      Decision: Warning, Soft Block, or Hard Block
```

**Option B: Broadcast (All layers notified simultaneously)**
```
Cognitive layer detects drift →
  Broadcast to all layers immediately →
    Each layer decides its own response
```

**Option C: Hierarchical Decision Tree**
```
Cognitive layer detects drift (5%) →
  IF section-level CRC violated → Structural layer handles (nudge)
  ELSE IF global rule violated → Fundamental layer handles (block)
  ELSE → Cognitive layer handles (self-correct)
```

**Claude's Recommendation**: Option C (Hierarchical Decision Tree)
- Most aligned with Perplexity's hierarchical control pattern
- Avoids cascading all minor issues to top layer
- Each layer has clear responsibility

**Gontrand's Input Needed**: Which option do you prefer? Or a hybrid approach?

---

**Question 2: CRC Check Granularity**

When should we compute CRCs?

**Current Design**:
```yaml
check_frequency:
  milestones: [PRE, RUN_mid, RUN_precommit, POST]
  tokens_window:
    default: 1800
    tighten_on_nudge: 900
    relax_on_green: 3000
```

**Perplexity Insight**: LangGraph validates at every graph node transition

**Design Question**: Should we add "micro-checkpoints" between milestones?

**Option A: Current (4 milestones + adaptive windows)**
- PRE: Before execution starts
- RUN_mid: At 50% completion
- RUN_precommit: Before writing outputs
- POST: After completion

**Option B: Add Tool Call Checkpoints**
```yaml
check_frequency:
  milestones: [PRE, RUN_mid, RUN_precommit, POST]
  tool_triggers: [Read, Write, Edit, Bash, Task]  # Check before each tool call
```

**Option C: Hybrid (milestones + adaptive + critical tools)**
```yaml
check_frequency:
  milestones: [PRE, RUN_mid, RUN_precommit, POST]
  tokens_window: {default: 1800, tighten_on_nudge: 900}
  critical_tools: [Write, Edit, Bash]  # Only check before dangerous tools
```

**Claude's Recommendation**: Option C (Hybrid)
- Balances thoroughness with performance
- Aligns with guard rail best practice (check before Write/Bash)
- Doesn't slow down safe operations (Read, Grep)

**Gontrand's Input Needed**: Do you want CRC checks before EVERY tool call, or just critical ones?

---

**Question 3: ExpectationVectors Implementation**

How to represent "good output"?

**Phase 1 (Current)**: Heuristics only
```python
def check_output_quality(output: str) -> float:
    score = 0.0
    if "def " in output: score += 0.2  # Has functions
    if "class " in output: score += 0.2  # Has classes
    if len(output) > 100: score += 0.2  # Sufficient length
    # ... more heuristics
    return score
```

**Phase 2 (Planned)**: Embeddings + Heuristics
```python
def check_output_quality(output: str, expectation: str) -> float:
    # Semantic similarity
    output_emb = embed(output, model="bge-small-int8")
    expect_emb = embed(expectation, model="bge-small-int8")
    semantic_score = cosine_similarity(output_emb, expect_emb)

    # Heuristic checks
    heuristic_score = check_heuristics(output)

    # Weighted combination
    return 0.7 * semantic_score + 0.3 * heuristic_score
```

**Perplexity Insight**: AutoGPT uses FAISS vector store for similarity search

**Design Question**: Should we cache embeddings to avoid recomputation?

**Option A: No Cache (Compute Every Check)**
- Pros: Always fresh, no stale data
- Cons: Slower (10-50ms per check)

**Option B: LRU Cache (Last 100 outputs)**
- Pros: Fast for repeated checks
- Cons: Memory overhead (~10 MB)

**Option C: Persistent Cache (PostgreSQL/pgvector)**
```yaml
expectation_vectors:
  embeddings:
    model: "bge-small-int8"
    store: "pgvector"  # ← Persistent across sessions
    cache: true
    cache_size: 1000  # Keep 1000 most recent
```

**Claude's Recommendation**: Option C (Persistent Cache)
- Aligns with Perplexity's recommendation for long-term memory
- Enables learning across sessions (Phase 4 benefit)
- pgvector is production-ready (used by LangChain)

**Gontrand's Input Needed**: Do you want to set up PostgreSQL + pgvector, or start with simple LRU cache in Phase 2?

---

## 2. Drift Detection Strategy Refinement

### Current Detection Methods

From `apc_crc_policy.yaml`:

```yaml
nudge_severity:
  warning:
    thresholds:
      drift: 0.05           # 5% drift from reference
      fidelity_min: 0.90    # 90% coverage of expectations
      evidence_min: 0.95    # 95% factual citations
```

### Perplexity Insights on Thresholds

**AutoGPT Learning**: Fixed thresholds caused false positives
**BabyAGI Learning**: Tuned similarity thresholds reduced drift

**Design Question**: Should thresholds be static or adaptive?

**Option A: Static (Current)**
```yaml
thresholds:
  drift: 0.05  # Always 5%
  fidelity_min: 0.90  # Always 90%
```

**Option B: Task-Dependent**
```yaml
thresholds:
  default: {drift: 0.05, fidelity: 0.90}
  creative_tasks: {drift: 0.15, fidelity: 0.80}  # More lenient for creative work
  critical_tasks: {drift: 0.02, fidelity: 0.95}  # Strict for security/safety
```

**Option C: Adaptive (Learning)**
```python
class AdaptiveThresholds:
    def __init__(self):
        self.drift_threshold = 0.05  # Start at 5%

    def adjust_based_on_history(self, task_type, success_rate):
        if success_rate > 0.95:
            self.drift_threshold *= 1.1  # Relax (working well)
        elif success_rate < 0.80:
            self.drift_threshold *= 0.9  # Tighten (too many failures)
```

**Claude's Recommendation**: Option B (Task-Dependent) for Phase 2, Option C (Adaptive) for Phase 4
- Phase 2: Start with 3 threshold profiles (default, creative, critical)
- Phase 4: Learn optimal thresholds per task type over time

**Gontrand's Input Needed**: Do you want static thresholds (simpler) or task-dependent (more powerful)?

---

### Drift Detection Formula

**Current (Implicit)**:
```python
drift = max_similarity_to_reference  # From MMR algorithm
if drift > threshold:
    trigger_nudge()
```

**Perplexity Alternative**: Multi-factor drift score
```python
def compute_drift_score(current_output, reference, context):
    # Factor 1: Semantic drift (embedding similarity)
    semantic_drift = 1.0 - cosine_similarity(
        embed(current_output),
        embed(reference)
    )

    # Factor 2: Topic drift (keyword overlap)
    topic_drift = 1.0 - jaccard_similarity(
        keywords(current_output),
        keywords(reference)
    )

    # Factor 3: Scope drift (context relevance)
    scope_drift = 1.0 - relevance_score(current_output, context)

    # Weighted combination
    return 0.5 * semantic_drift + 0.3 * topic_drift + 0.2 * scope_drift
```

**Design Question**: Use simple similarity (Phase 1) or multi-factor drift (Phase 2)?

**Claude's Recommendation**:
- Phase 1: Keep simple (1 - similarity) for now
- Phase 2: Add multi-factor when embeddings are available

**Gontrand's Input Needed**: Do you want to implement multi-factor drift in Phase 2, or keep it simple?

---

## 3. AutoFix Boundaries

### Current AutoFix Policy

From `apc_crc_policy.yaml`:

```yaml
autofix:
  minor:
    auto_apply: true
    limits:
      excerpt_lines_max: 10       # Max 10 lines per excerpt
      section_reduction_max_pct: 15  # Max 15% section reduction
  major:
    require_validation: true
```

### Perplexity Insights on AutoFix

**LangChain Pattern**: Automated retries with backoff
**AutoGPT Pattern**: Goal re-validation before committing

**Design Question**: What exactly is "minor" vs "major"?

**Proposed Classification**:

```yaml
autofix:
  # MINOR (auto-apply without asking)
  minor_corrections:
    - type: "format_fix"
      examples: ["fix indentation", "add missing quotes", "correct capitalization"]
      max_changes: 5

    - type: "excerpt_trimming"
      examples: ["remove verbose explanation", "shorten example"]
      max_lines_removed: 10

    - type: "citation_addition"
      examples: ["add source reference", "link to file"]
      max_additions: 3

  # MAJOR (require validation)
  major_corrections:
    - type: "logic_change"
      examples: ["rewrite algorithm", "change data structure"]
      always_validate: true

    - type: "scope_expansion"
      examples: ["add new requirement", "expand context"]
      always_validate: true

    - type: "rule_violation_fix"
      examples: ["remove forbidden tool", "revert out-of-scope change"]
      always_validate: true
```

**Design Question**: Should AutoFix attempt repairs, or just block and request manual fix?

**Option A: Attempt Repair (LangChain pattern)**
```python
if drift_detected:
    # Try to fix automatically
    fixed_output = auto_correct(output, reference)
    if validate(fixed_output):
        apply(fixed_output)
    else:
        block_and_request_manual()
```

**Option B: Block and Guide (AutoGPT pattern)**
```python
if drift_detected:
    # Don't fix, just guide
    block_with_message(
        "Drift detected: output diverged from reference by 15%\n"
        "Expected: focus on authentication logic\n"
        "Got: database schema discussion\n"
        "Please refocus on authentication."
    )
```

**Option C: Hybrid (our current design)**
```python
if drift_detected:
    if is_minor(drift):
        auto_fix_and_notify()  # Fix + tell user
    else:
        block_and_guide()  # Block + provide guidance
```

**Claude's Recommendation**: Option C (Hybrid)
- Minor issues: Auto-fix (saves time, reduces context usage)
- Major issues: Block + guide (safety critical)

**Gontrand's Input Needed**: Do you trust AutoFix for minor corrections, or prefer manual review always?

---

## 4. Integration Path

### SessionContextCurator Integration

**Current Architecture**:
```
SessionMonitor (no CRC yet)
    ↓
SessionContextCurator (no CRC yet)
    ↓ uses
MMR Ranker + Chain-of-Density + Knapsack (✅ validated)
```

**Target Architecture** (with CRC):
```
SessionMonitor
    ↓ generates
RuleDigest + ContextDigest (CRC checksums)
    ↓
CRCValidator (PRE gate)
    ↓
SessionContextCurator (with CRC-aware ranking)
    ↓ uses
MMR Ranker + Chain-of-Density + Knapsack
    ↓ produces
ContextPack (with ExpectationVectors)
    ↓
CRCValidator (POST gate)
    ↓ monitors
DriftDetector (RUN gates every 1800 tokens)
```

**Integration Steps**:

**Step 1: Add CRC to SessionMonitor**
```python
# File: agentflow/orchestration/session_monitor.py

from hashlib import sha256
import json

class SessionMonitor:
    def __init__(self):
        self.context_buffer = []
        self.rule_digest = {}  # ← Add this
        self.rule_crc = ""     # ← Add this

    def initialize_session(self, rules: dict):
        """Compute RuleDigest CRC at session start."""
        self.rule_digest = rules
        # Compute SHA256 of canonical rules
        canonical = json.dumps(rules, sort_keys=True)
        self.rule_crc = sha256(canonical.encode()).hexdigest()
```

**Step 2: Add PRE Gate Validation**
```python
# File: agentflow/orchestration/crc_validator.py (NEW)

class CRCValidator:
    def __init__(self, rule_crc: str):
        self.rule_crc = rule_crc

    def validate_pre_execution(self, context: dict) -> bool:
        """PRE gate: Validate context before execution."""
        # Check 1: Rule integrity
        if not self._verify_rule_crc():
            raise CRCViolation("Rule digest corrupted")

        # Check 2: Context completeness
        required = ["problem_brief", "constraints", "acceptance"]
        if not all(k in context for k in required):
            raise CRCViolation("Incomplete context")

        return True
```

**Step 3: Add RUN Gate Monitoring**
```python
# File: agentflow/orchestration/drift_detector.py (NEW)

class DriftDetector:
    def __init__(self, reference_context: dict):
        self.reference = reference_context
        self.tokens_since_check = 0
        self.check_interval = 1800  # Default

    def check_drift(self, current_output: str) -> dict:
        """RUN gate: Check drift every N tokens."""
        self.tokens_since_check += len(current_output.split())

        if self.tokens_since_check >= self.check_interval:
            drift_score = self._compute_drift(current_output)

            if drift_score > 0.05:  # 5% drift threshold
                return {
                    "status": "warning",
                    "drift": drift_score,
                    "message": "Output drifting from reference"
                }

            self.tokens_since_check = 0

        return {"status": "ok"}
```

**Step 4: Add POST Gate Verification**
```python
# File: agentflow/orchestration/crc_validator.py

class CRCValidator:
    def validate_post_execution(self, output: str, expectations: dict) -> dict:
        """POST gate: Validate output quality."""
        # Check 1: Fidelity (coverage of expectations)
        fidelity = self._compute_fidelity(output, expectations)

        # Check 2: Evidence coverage
        evidence = self._check_citations(output)

        # Check 3: Rule adherence
        rule_compliance = self._check_rules(output)

        return {
            "fidelity": fidelity,
            "evidence_coverage": evidence,
            "rule_adherence": rule_compliance,
            "overall_score": (fidelity + evidence + rule_compliance) / 3
        }
```

**Design Question**: Should integration be:

**Option A: Incremental (gate by gate)**
- Week 1: Add PRE gate only
- Week 2: Add RUN gate monitoring
- Week 3: Add POST gate verification
- Week 4: Integration testing

**Option B: All-at-once (full system)**
- Week 1-2: Implement all 4 components (SessionMonitor CRC, PRE, RUN, POST)
- Week 3-4: Integration testing

**Claude's Recommendation**: Option A (Incremental)
- Safer (test each gate independently)
- Faster feedback (see PRE gate working after week 1)
- Aligns with Perplexity's recommendation for phased rollout

**Gontrand's Input Needed**: Incremental (safer) or all-at-once (faster)?

---

## 5. Open Questions for Collaboration

### High-Priority Questions

1. **Inter-Layer Communication**: Bubble-up, Broadcast, or Hierarchical?
2. **CRC Check Granularity**: Every tool call, or just critical tools?
3. **ExpectationVectors Cache**: PostgreSQL+pgvector now, or simple LRU first?
4. **Drift Thresholds**: Static, task-dependent, or adaptive?
5. **AutoFix Trust Level**: Auto-apply minor fixes, or always ask?
6. **Integration Pace**: Incremental (gate-by-gate) or all-at-once?

### Medium-Priority Questions

7. **Multi-Factor Drift**: Implement in Phase 2, or keep simple for now?
8. **Micro-Checkpoints**: Add tool-call triggers, or stick with milestones?
9. **Logging Depth**: Basic (events only) or comprehensive (full CRC audit trail)?
10. **Performance Metrics**: Add latency tracking now, or Phase 3?

### Low-Priority Questions

11. **CRC Algorithm**: SHA256 (current) or faster hash (xxHash)?
12. **Nudge Format**: Plain text or structured JSON?
13. **Dashboard UI**: Terminal output or web interface?

---

## 6. Recommended Discussion Format

**Iterative Q&A Process**:

1. **Claude asks question** (with context and recommendations)
2. **Gontrand provides input** (preference, constraints, new requirements)
3. **Claude updates design** (incorporates feedback)
4. **Repeat** until all questions resolved

**Example Exchange**:

```
Claude: "Question 1: Inter-layer communication - I recommend Option C
(Hierarchical Decision Tree) because it aligns with Perplexity's
pattern and gives each layer clear responsibility. What do you think?"

Gontrand: "I agree with Option C, but I want to add a 'emergency broadcast'
mode for critical violations that bypasses the hierarchy."

Claude: "Excellent idea! I'll add:
```yaml
emergency_broadcast:
  triggers: [security_violation, data_corruption, infinite_loop]
  notify_all_layers: true
  immediate_hard_block: true
```

This gives us both hierarchical efficiency AND safety escape hatch."
```

**Goal**: Refine all design questions through collaborative dialogue

---

## 7. Next Steps After This Session

Once we resolve the 6 high-priority questions:

### Immediate (Today)
1. Update `config/apc_crc_policy.yaml` with agreed design
2. Create integration plan with specific week-by-week tasks
3. Document all design decisions in `DESIGN_DECISIONS.md`

### Short-term (This Week)
4. Implement PRE gate (SessionMonitor CRC + validator)
5. Write integration tests for PRE gate
6. Add RuleDigest schema validation

### Medium-term (Next 2 Weeks)
7. Implement RUN gate (DriftDetector with adaptive windows)
8. Implement POST gate (IO Scorecard validator)
9. Full integration testing (all 3 gates)

---

## Session Status

**Current Status**: ⏸️ **AWAITING GONTRAND'S INPUT**

**Questions to Answer**: 6 high-priority questions above

**Next Action**: Gontrand responds with preferences → Claude updates design → Continue iteration

---

**Ready for collaboration! 🤝**
