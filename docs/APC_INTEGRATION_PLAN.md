# APC Integration Plan - Context Curator Optimization

**Date**: 2025-10-14
**Status**: 🔄 IN PROGRESS
**Target**: Transform SessionContextCurator into production-grade APC system

---

## 🎯 Executive Summary

The French APC (Agent Préparateur de Contexte) design provides **battle-tested algorithms and architecture** that directly address our Context Curator's optimization needs (62.5% → >90% accuracy, 65KB → <30KB contexts).

**Key Insight:** Our SessionContextCurator is a **working prototype** of the APC concept. The report provides the **production-grade algorithms** we need.

---

## 📊 Gap Analysis: Current vs APC Design

### What We Have ✅

| Feature | Current Implementation | Status |
|---------|----------------------|--------|
| Session Classification | Rule-based keywords | ✅ Working (62.5%) |
| Context Selection | Basic file matching | ✅ Working (67.5% reduction) |
| Interactive Refinement | Q&A system | ✅ Functional |
| RO/RW Separation | Implicit | ⚠️ Not enforced |
| Token Budgeting | Max size limits | ⚠️ Simple |
| Evidence/Citations | None | ❌ Missing |

### What We Need (from APC) 🎯

| Feature | APC Design | Impact | Priority |
|---------|-----------|--------|----------|
| **MMR Ranking** | Diversity-aware selection | 🎯 Fixes classification (62.5% → 85%+) | 🔴 HIGH |
| **Chain-of-Density** | Iterative summarization | 🎯 Reduces context (65KB → <30KB) | 🔴 HIGH |
| **Knapsack Packing** | Budget-optimized selection | 🎯 Guarantees size targets | 🔴 HIGH |
| **Evidence System** | Verifiable citations | 🎯 Quality validation | 🟡 MEDIUM |
| **Entailment Check** | Fact verification | 🎯 Prevents hallucinations | 🟡 MEDIUM |
| **Contradiction Sweep** | Conflict detection | 🎯 Quality improvement | 🟢 LOW |
| **Drift Watch** | Context freshness | 🎯 Maintenance automation | 🟢 LOW |

---

## 🔬 APC Algorithms Analysis

### 1. MMR (Maximal Marginal Relevance) - **GAME CHANGER**

**Problem it Solves:**
- Our current cherry-picker uses simple relevance scoring
- Results in redundant files (e.g., all 10 test files → 187 KB)
- No diversity optimization

**APC Solution:**
```python
def mmr_rank(items, λ=0.7):
    """
    Balances relevance vs diversity
    λ=0.7 → 70% relevance, 30% diversity
    """
    S, R = [], items[:]  # S=selected, R=remaining
    while R:
        # Score = λ*relevance - (1-λ)*max_similarity_to_selected
        x = max(R, key=lambda i:
            λ*i.rel - (1-λ)*max(sim(i,s) for s in S) if S else i.rel)
        S.append(x)
        R.remove(x)
    return S
```

**Expected Impact:**
- Testing sessions: 10 redundant test files → 2 diverse tests (187KB → 30KB)
- Classification: Better feature detection → 62.5% → 85%+

**Implementation Complexity:** 🟡 MEDIUM (need similarity function)

---

### 2. Chain-of-Density - **SUMMARIZATION POWERHOUSE**

**Problem it Solves:**
- Large files bloat context (single file can be 50-100KB)
- No intelligent summarization

**APC Solution:**
```python
def density_summarize(fragments, target_tokens):
    """
    Iteratively adds key points until budget reached
    Each iteration adds the MOST IMPORTANT missing detail
    """
    summary = seed_brief(fragments[:k])  # Start with overview
    for chunk in fragments[k:]:
        proposal = try_add_key_points(summary, chunk)
        if tokens(proposal) <= target_tokens:
            summary = proposal
        else:
            break
    return summary
```

**Expected Impact:**
- Large files: 100KB → 5KB (95% reduction while preserving key info)
- Total context: 65KB → 20KB

**Implementation Complexity:** 🟢 LOW (can use AgentFlow delegation!)

---

### 3. Knapsack Budgeted Packing - **GUARANTEE SIZE TARGETS**

**Problem it Solves:**
- Current max_size_kb is a soft limit (often exceeded)
- No optimization for value/size ratio

**APC Solution:**
```python
def pack_sections(candidates, token_budget):
    """
    0/1 Knapsack: maximize value under budget constraint
    Greedy approximation: sort by value/size ratio
    """
    selected = []
    tokens = 0
    # Sort by utility density (bang for buck)
    for c in sorted(candidates, key=lambda x: x.score/x.tokens, reverse=True):
        if tokens + c.tokens <= token_budget and not violates_caps(c, selected):
            selected.append(c)
            tokens += c.tokens
    return selected
```

**Expected Impact:**
- **GUARANTEED** size targets (<30KB)
- Optimal file selection (max relevance per token)

**Implementation Complexity:** 🟢 LOW (straightforward algorithm)

---

### 4. Evidence System - **QUALITY VALIDATION**

**Problem it Solves:**
- No traceability (which files came from where?)
- Can't validate context quality

**APC Solution:**
```yaml
Evidence:
  bundle_id: EV-2025-10-14-001
  items:
    - source: "repo://src/thermal/centering.py#L120-L182"
      excerpt: "..."
      embedding_id: "emb_9sd..."
      hash: "sha256:..."
```

**Expected Impact:**
- Full traceability (every file has source + hash)
- Quality validation (can verify excerpts)
- Debugging (see why files were selected)

**Implementation Complexity:** 🟡 MEDIUM (data structure + tracking)

---

### 5. RO/RW Separation - **SAFETY & CLARITY**

**Problem it Solves:**
- Unclear ownership (who can modify what?)
- Risk of corruption

**APC Solution:**
```
RO (read-only):  corpora/shared/*  (project files)
RW (APC owned):  apc/notes/          (intent notes)
                 apc/context_packs/  (curated contexts)
                 apc/evidence/       (citations)
```

**Expected Impact:**
- Clear boundaries
- Safe concurrent access
- Auditable changes

**Implementation Complexity:** 🟢 LOW (directory structure + ACL checks)

---

## 🏗️ Implementation Strategy

### Phase 1: Core Algorithms (Week 1) 🔴 HIGH PRIORITY

**Goal:** Fix the 3 biggest issues (classification, size, quality)

**Tasks:**
1. **Implement MMR Ranking** (2-3 days)
   - Add similarity function (file path overlap + keyword overlap)
   - Replace current relevance-only sorting
   - Expected: 62.5% → 85%+ classification accuracy

2. **Implement Knapsack Packing** (1 day)
   - Replace max_size_kb soft limit
   - Add utility/size ratio scoring
   - Expected: GUARANTEE <30KB contexts

3. **Add Chain-of-Density Summarization** (2-3 days)
   - Delegate to AgentFlow (FREE models!)
   - Summarize large files before inclusion
   - Expected: 65KB → 20KB average context

**Deliverable:** `session_context_curator_v2.py` with core algorithms

---

### Phase 2: Evidence System (Week 2) 🟡 MEDIUM PRIORITY

**Goal:** Add traceability and quality validation

**Tasks:**
1. **Evidence Data Model** (1 day)
   - Create `Evidence` dataclass
   - Track source, excerpt, hash for each file

2. **Citation Tracking** (2 days)
   - Store evidence bundles alongside context packs
   - Add provenance to ContextPack

3. **Validation Pipeline** (1 day)
   - Verify excerpts match sources
   - Check hash consistency

**Deliverable:** Evidence system integrated into curator

---

### Phase 3: Advanced Features (Week 3) 🟢 LOW PRIORITY

**Goal:** Production polish and maintenance automation

**Tasks:**
1. **Entailment Check** (2 days)
   - Verify facts are supported by evidence
   - Flag unsupported claims

2. **Contradiction Sweep** (2 days)
   - Detect conflicting information
   - Generate RFC for resolution

3. **Drift Watch** (1 day)
   - Daily job to check context freshness
   - Alert when context outdated

**Deliverable:** Production-grade APC system

---

## 📐 Detailed Algorithm Implementations

### MMR Implementation Plan

```python
class MMRRanker:
    """Maximal Marginal Relevance for diverse file selection"""

    def __init__(self, lambda_param: float = 0.7):
        self.lambda_param = lambda_param  # Balance relevance vs diversity

    def compute_similarity(self, file1: str, file2: str) -> float:
        """
        Compute similarity between two files
        Uses: path overlap + keyword overlap + semantic similarity
        """
        # Path similarity (same directory = high similarity)
        path_sim = self._path_overlap(file1, file2)

        # Keyword similarity (from file content/name)
        keyword_sim = self._keyword_overlap(file1, file2)

        # Semantic similarity (if embeddings available)
        semantic_sim = self._semantic_similarity(file1, file2)

        return (path_sim + keyword_sim + semantic_sim) / 3

    def rank(self, candidates: List[FileCandidate]) -> List[FileCandidate]:
        """
        MMR ranking: balance relevance vs diversity

        Returns files that are:
        - Highly relevant to task
        - Diverse from already selected files
        """
        selected = []
        remaining = candidates[:]

        while remaining:
            if not selected:
                # First item: just pick most relevant
                best = max(remaining, key=lambda f: f.relevance_score)
            else:
                # Subsequent items: balance relevance vs diversity
                best = max(remaining, key=lambda f: self._mmr_score(f, selected))

            selected.append(best)
            remaining.remove(best)

            # Stop if we have enough diversity
            if len(selected) >= 10 or self._sufficient_diversity(selected):
                break

        return selected

    def _mmr_score(self, candidate: FileCandidate, selected: List[FileCandidate]) -> float:
        """
        MMR score = λ * relevance - (1-λ) * max_similarity_to_selected

        High λ (0.7-0.9): Favor relevance
        Low λ (0.3-0.5): Favor diversity
        """
        relevance = candidate.relevance_score

        # Find maximum similarity to any selected file
        max_sim = max(
            self.compute_similarity(candidate.path, s.path)
            for s in selected
        )

        return self.lambda_param * relevance - (1 - self.lambda_param) * max_sim
```

**Expected Results:**
- Testing sessions: Select `test_feature.py` + `conftest.py` (2 files)
  - NOT all 10 test files (redundant)
- Feature dev: Select core implementation + 1-2 dependencies
  - NOT all dependencies (overkill)

---

### Chain-of-Density Implementation Plan

```python
class ChainOfDensitySummarizer:
    """Iteratively summarize large files to fit token budget"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator  # AgentFlow delegation

    def summarize(self, file_content: str, target_tokens: int) -> str:
        """
        Chain-of-Density: Start broad, add details iteratively

        Process:
        1. Generate seed summary (200 tokens)
        2. Identify missing key points
        3. Add most important details
        4. Repeat until budget reached
        """
        current_tokens = 0
        summary = self._generate_seed_summary(file_content)
        current_tokens = estimate_tokens(summary)

        # Identify key points not yet covered
        missing_points = self._identify_key_points(file_content, summary)

        # Add points iteratively until budget reached
        for point in sorted(missing_points, key=lambda p: p.importance, reverse=True):
            proposal = self._try_add_point(summary, point)
            new_tokens = estimate_tokens(proposal)

            if new_tokens <= target_tokens:
                summary = proposal
                current_tokens = new_tokens
            else:
                break  # Budget reached

        return summary

    def _generate_seed_summary(self, content: str) -> str:
        """
        Generate initial broad summary
        Delegation task: "Summarize this file in 200 tokens"
        """
        task = f"""
        Generate a 200-token summary of this file.
        Focus on: purpose, main functions, key dependencies.

        File content:
        {content[:5000]}  # First 5000 chars for context
        """
        return self.orchestrator.orchestrate(task)

    def _identify_key_points(self, content: str, current_summary: str) -> List[KeyPoint]:
        """
        Find important details missing from summary
        Delegation task: "What key points are missing?"
        """
        task = f"""
        Compare file content vs current summary.
        List key details missing from summary.
        Rank by importance.

        Content: {content[:5000]}
        Summary: {current_summary}
        """
        result = self.orchestrator.orchestrate(task)
        return parse_key_points(result)
```

**Expected Results:**
- Large file (100KB) → Summary (5KB)
- Preserves: API signatures, key logic, dependencies
- Removes: Implementation details, comments, boilerplate

---

### Knapsack Packing Implementation Plan

```python
class KnapsackPacker:
    """Budget-optimized file selection using 0/1 Knapsack"""

    def pack(
        self,
        candidates: List[FileCandidate],
        token_budget: int,
        section_caps: Dict[str, int] = None
    ) -> PackResult:
        """
        Select files to maximize relevance under token budget

        Greedy approximation (exact 0/1 Knapsack is NP-hard):
        Sort by value/weight ratio, pack greedily
        """
        # Calculate utility density (value per token)
        for c in candidates:
            c.density = c.relevance_score / max(c.size_tokens, 1)

        # Sort by density (best bang for buck)
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.density,
            reverse=True
        )

        selected = []
        total_tokens = 0
        section_tokens = defaultdict(int)

        for candidate in sorted_candidates:
            # Check if adding this file violates constraints
            if not self._can_add(candidate, total_tokens, section_tokens,
                                 token_budget, section_caps):
                continue

            # Add file to pack
            selected.append(candidate)
            total_tokens += candidate.size_tokens
            section_tokens[candidate.section] += candidate.size_tokens

        return PackResult(
            files=selected,
            total_tokens=total_tokens,
            utilization=total_tokens / token_budget
        )

    def _can_add(
        self,
        candidate: FileCandidate,
        current_total: int,
        section_totals: Dict[str, int],
        budget: int,
        section_caps: Dict[str, int]
    ) -> bool:
        """Check if adding file violates constraints"""
        # Check global budget
        if current_total + candidate.size_tokens > budget:
            return False

        # Check section caps (e.g., core_files ≤ 10KB)
        if section_caps:
            section = candidate.section
            cap = section_caps.get(section, float('inf'))
            if section_totals[section] + candidate.size_tokens > cap:
                return False

        return True
```

**Expected Results:**
- **GUARANTEED** token budget compliance
- Optimal file selection (max value per token)
- Section caps enforced (no single section dominates)

---

## 🎯 Integration with Existing System

### Backward Compatibility

**Keep:**
- `SessionType` enum (all 9 types)
- `CuratedContext` dataclass (add Evidence field)
- `SessionContextCurator` API (internal improvements only)

**Enhance:**
- `SessionClassifier` → add MMR-based feature extraction
- `ContextCherryPicker` → replace with MMR + Knapsack + Chain-of-Density
- `InteractiveContextRefiner` → keep Q&A, add Evidence tracking

### Migration Path

```python
# V1 (current) - simple relevance
curated = cherry_picker.cherry_pick(task, session_type, max_size_kb=30)

# V2 (APC-enhanced) - MMR + Knapsack + Chain-of-Density
curated = cherry_picker.cherry_pick_v2(
    task=task,
    session_type=session_type,
    token_budget=8000,           # Hard budget (Knapsack)
    diversity_lambda=0.7,        # MMR parameter
    summarize_large_files=True,  # Chain-of-Density
    generate_evidence=True       # Traceability
)
```

---

## 📊 Expected Performance Improvements

### Before (Current System)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Classification Accuracy | 62.5% | >90% | -27.5% |
| Context Size Reduction | 67.5% | >85% | -17.5% |
| Avg Context Size | 65.1 KB | <30 KB | +35.1 KB |
| Quality Score | 6.2/10 | >8/10 | -1.8 |

### After (APC-Enhanced)

| Metric | Expected | Target | Status |
|--------|----------|--------|--------|
| Classification Accuracy | **92%** | >90% | ✅ EXCEEDS |
| Context Size Reduction | **91%** | >85% | ✅ EXCEEDS |
| Avg Context Size | **18 KB** | <30 KB | ✅ EXCEEDS |
| Quality Score | **8.7/10** | >8/10 | ✅ EXCEEDS |

**Rationale:**
- **MMR** fixes redundant file selection → +30% classification accuracy
- **Knapsack** guarantees size targets → -72% context size
- **Chain-of-Density** compresses large files → -45% token usage
- **Evidence** improves quality validation → +2.5 quality points

---

## 🚀 Delegation Tasks for AgentFlow

### Task 1: Implement MMR Ranking (HIGH PRIORITY)

**Complexity:** MEDIUM (3-4 hours)
**Cost:** $0.15 (DeepSeek V3)

```
[MISSION]: Implement MMR (Maximal Marginal Relevance) file ranking

## Context
- Project: AgentFlow Session Context Curator
- File: agentflow/orchestration/session_recovery/session_context_curator.py
- Current: Simple relevance scoring (all files scored independently)
- Problem: Redundant file selection (e.g., all 10 test files selected)

## Requirements
Implement MMRRanker class with:
1. compute_similarity(file1, file2) → float
   - Path similarity (same directory = high similarity)
   - Keyword similarity (file name overlap)
   - Return 0.0-1.0 score

2. rank(candidates: List[FileCandidate]) → List[FileCandidate]
   - MMR formula: λ*relevance - (1-λ)*max_similarity
   - λ=0.7 (70% relevance, 30% diversity)
   - Return sorted list (most diverse + relevant first)

## Deliverables
Output to: agentflow/orchestration/session_recovery/mmr_ranker.py

Include:
1. MMRRanker class with methods above
2. Unit tests (3-5 test cases)
3. Integration with ContextCherryPicker
4. Docstrings with examples

## Output Format
- Python 3.11+ compatible
- Type hints required
- 200-300 lines of code

## Success Criteria
- [ ] MMR formula correctly implemented
- [ ] Similarity function works for file paths
- [ ] Tests pass
- [ ] Reduces redundant file selection
```

---

### Task 2: Implement Chain-of-Density Summarization (HIGH PRIORITY)

**Complexity:** MEDIUM (4-5 hours)
**Cost:** $0.20 (DeepSeek V3)

```
[MISSION]: Implement Chain-of-Density file summarization

## Context
- Project: AgentFlow Session Context Curator
- Problem: Large files (50-100KB) bloat context
- Solution: Iterative summarization that adds details until budget reached

## Requirements
Implement ChainOfDensitySummarizer class with:
1. summarize(file_content: str, target_tokens: int) → str
   - Start with seed summary (200 tokens)
   - Identify missing key points
   - Add points iteratively until budget reached
   - Use AgentFlow delegation for LLM calls

2. _generate_seed_summary(content: str) → str
   - Delegate to FREE models (qwen-2.5-coder-32b)
   - Extract: purpose, main functions, dependencies

3. _identify_key_points(content, current_summary) → List[KeyPoint]
   - Find important details missing from summary
   - Rank by importance

## Deliverables
Output to: agentflow/orchestration/session_recovery/chain_of_density.py

Include:
1. ChainOfDensitySummarizer class
2. Integration with SmartOrchestrator
3. Tests with sample files
4. Performance metrics (compression ratio)

## Success Criteria
- [ ] 100KB file → 5-10KB summary
- [ ] Preserves API signatures and key logic
- [ ] Uses delegation (not direct LLM calls)
- [ ] Token budget strictly enforced
```

---

### Task 3: Implement Knapsack Budgeted Packing (MEDIUM PRIORITY)

**Complexity:** LOW (2-3 hours)
**Cost:** $0.10 (DeepSeek V3)

```
[MISSION]: Implement 0/1 Knapsack file selection algorithm

## Context
- Project: AgentFlow Session Context Curator
- Problem: max_size_kb is soft limit (often exceeded)
- Solution: Hard budget guarantee via Knapsack algorithm

## Requirements
Implement KnapsackPacker class with:
1. pack(candidates, token_budget, section_caps) → PackResult
   - Greedy approximation: sort by value/weight ratio
   - Guarantee: total_tokens ≤ token_budget
   - Respect section caps (e.g., core_files ≤ 10KB)

2. _can_add(candidate, current, budget, caps) → bool
   - Check global budget
   - Check section caps
   - Return True if file can be added

## Deliverables
Output to: agentflow/orchestration/session_recovery/knapsack_packer.py

Include:
1. KnapsackPacker class
2. PackResult dataclass
3. Tests verifying budget guarantee
4. Integration example

## Success Criteria
- [ ] NEVER exceeds token_budget
- [ ] Maximizes relevance score under budget
- [ ] Respects section caps
- [ ] Tests prove guarantee holds
```

---

## 📈 Testing Strategy

### Unit Tests (Per Algorithm)

**MMR Ranking:**
```python
def test_mmr_selects_diverse_files():
    # Given: 10 test files in same directory
    candidates = [
        FileCandidate("tests/test_auth.py", relevance=0.9),
        FileCandidate("tests/test_login.py", relevance=0.85),
        # ... 8 more similar files
    ]

    # When: MMR ranking with λ=0.7
    ranked = mmr_ranker.rank(candidates)

    # Then: Should select only 2-3 most diverse
    assert len(ranked) <= 3
    assert ranked[0].path == "tests/test_auth.py"  # Most relevant
    assert "conftest.py" in [r.path for r in ranked]  # Diverse
```

**Chain-of-Density:**
```python
def test_chain_of_density_respects_budget():
    # Given: Large file (100KB)
    file_content = read_file("agentflow/core/delegator.py")

    # When: Summarize to 5KB
    summary = summarizer.summarize(file_content, target_tokens=1250)

    # Then: Size ≤ budget, key info preserved
    assert estimate_tokens(summary) <= 1250
    assert "class Delegator" in summary
    assert "orchestrate" in summary
```

**Knapsack Packing:**
```python
def test_knapsack_never_exceeds_budget():
    # Given: 20 file candidates
    candidates = generate_test_candidates(20)

    # When: Pack with budget=8000
    result = packer.pack(candidates, token_budget=8000)

    # Then: GUARANTEE budget not exceeded
    assert result.total_tokens <= 8000
    assert all(f.size_tokens > 0 for f in result.files)
```

### Integration Tests

```python
def test_end_to_end_apc_workflow():
    """Test complete APC workflow with all algorithms"""
    # Setup
    curator = SessionContextCuratorV2(
        enable_mmr=True,
        enable_chain_of_density=True,
        enable_knapsack=True
    )

    # Test case: Feature development session
    curated = curator.curate_context(
        task="Implement user authentication with JWT tokens",
        session_type=SessionType.FEATURE_DEV,
        token_budget=8000
    )

    # Assertions
    assert curated.size_bytes / 1024 < 30  # <30 KB
    assert curated.estimated_tokens <= 8000  # Hard budget
    assert len(curated.core_files) >= 1  # At least core files
    assert curated.relevance_score > 0.7  # High relevance
    assert len(curated.evidence) > 0  # Evidence tracked
```

---

## 💰 Cost Analysis

### Implementation Costs (AgentFlow Delegation)

| Task | Complexity | Tokens | Cost | Duration |
|------|------------|--------|------|----------|
| MMR Ranking | MEDIUM | ~50K | $0.15 | 3-4 hours |
| Chain-of-Density | MEDIUM | ~70K | $0.20 | 4-5 hours |
| Knapsack Packing | LOW | ~30K | $0.10 | 2-3 hours |
| Evidence System | MEDIUM | ~40K | $0.12 | 3-4 hours |
| **Total Phase 1-2** | - | **190K** | **$0.57** | **12-17 hours** |

**Comparison:**
- Claude direct: ~$57 (190K tokens × $0.30/1K)
- AgentFlow delegation: ~$0.57 (DeepSeek V3)
- **Savings: 99%**

### Runtime Costs (Per Session)

**Current System:**
- Classification: 0 tokens (rule-based)
- Cherry-picking: 0 tokens (file matching)
- Total: $0.00

**APC-Enhanced System:**
- Classification: 0 tokens (MMR is algorithmic)
- Cherry-picking: 0 tokens (Knapsack is algorithmic)
- Chain-of-Density: ~5K tokens per large file (delegated)
  - Cost: ~$0.0007 per file (DeepSeek V3)
  - Typical: 2-3 large files → $0.002 per session
- Total: **$0.002 per session** (negligible)

---

## 🎓 Success Criteria

### Phase 1 Complete When:

- ✅ MMR ranking reduces redundant files by >70%
- ✅ Chain-of-Density compresses large files by >90%
- ✅ Knapsack GUARANTEES token budget (100% compliance)
- ✅ All unit tests pass
- ✅ Integration tests show improvements:
  - Classification: 62.5% → >85%
  - Context size: 65KB → <30KB
  - Quality: 6.2/10 → >8/10

### Production Ready When:

- ✅ Classification accuracy >90%
- ✅ Average context size <25KB
- ✅ Quality score >8.5/10
- ✅ Evidence system operational
- ✅ Comprehensive test suite (>80% coverage)
- ✅ Documentation complete

---

## 📚 Resources

### APC Report Sections Most Relevant:

1. **Section 6**: Budget-aware packer algorithm → Knapsack implementation
2. **Section 8**: MMR pseudo-code → Direct implementation guide
3. **Section 8**: Chain-of-Density → Summarization strategy
4. **Section 3**: ContextPack data model → Evidence system design
5. **Section 4**: 5-phase pipeline → Overall architecture

### Internal References:

- Current implementation: `agentflow/orchestration/session_recovery/session_context_curator.py`
- Test suite: `test_context_curator_comprehensive.py`
- Test report: `CONTEXT_CURATOR_TEST_REPORT.md`
- SmartOrchestrator: `agentflow/orchestration/smart_orchestrator.py`

---

## 🚀 Next Actions

### Immediate (Today)

1. **Create delegation tasks** for Phase 1 algorithms
2. **Run parallel workers** (3 tasks in parallel)
3. **Monitor progress** via worker logs

### This Week

1. **Integrate** MMR + Knapsack + Chain-of-Density
2. **Re-run tests** to validate improvements
3. **Update** test report with new metrics

### Next Week

1. **Phase 2**: Implement Evidence system
2. **Validation**: Test on real sessions
3. **Documentation**: Update all docs with APC integration

---

**Status**: 🔄 Ready to delegate to AgentFlow
**Expected Timeline**: 2-3 weeks to production
**Expected Outcome**: 62.5% → >90% accuracy, 65KB → <20KB contexts

**This is the production-grade optimization we need!** 🚀
