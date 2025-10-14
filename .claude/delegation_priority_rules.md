# Règles de Priorité de Délégation - Mode Développement

**Status**: 🔧 DÉVELOPPEMENT ACTIF
**Date**: 2025-10-14
**Session**: Phase 2 Complete + Specialized Routing

---

## ⚠️ MODE DÉVELOPPEMENT ACTIF

**ATTENTION**: Système en cours de développement et débogage.

### Comportement Attendu de Claude Code

1. **TOUJOURS vérifier les outputs** - Nous sommes en phase de test
2. **VALIDER avant d'exécuter** - Demander confirmation pour opérations critiques
3. **LOGGER tout** - Maximum de verbosité pour débogage
4. **UTILISER délégation en priorité** - Sauf si explicitement désactivé

---

## 🚨 Règle #0: TOUJOURS Consulter APC AVANT Développement

**PRIORITÉ ABSOLUE - NOUVELLE RÈGLE 2025-10-14**

**AVANT toute création de code, Claude DOIT:**

```python
# 1. Import APC server
from agentflow.mcp.apc_mcp_server import APCMCPServer
import asyncio

apc = APCMCPServer()

# 2. Query pour vérifier si feature existe
result = asyncio.run(apc._query_project({
    'query_type': 'find_pattern',
    'query': '[nom_feature]',  # e.g., 'validation', 'context compression'
    'file_type': 'py'
}))

# 3. Si trouvé → UTILISER existant (via asyncio.run())
# 4. Si non trouvé → Procéder avec développement
```

**Incident qui a créé cette règle:**

MonitoredDelegationWorkflow a dupliqué des features APC MCP existantes:
- Context compression (`_prepare_context` existait déjà)
- Output validation (`_validate_output` existait déjà)
- Workflow execution (`_execute_workflow` existait déjà)

**Features APC MCP à NE JAMAIS dupliquer:**

| Feature | Méthode | Location |
|---------|---------|----------|
| Context Compression | `_prepare_context` | apc_mcp_server.py:281-328 |
| Output Validation | `_validate_output` | apc_mcp_server.py:330-362 |
| Workflow Execution | `_execute_workflow` | apc_mcp_server.py:364-403 |
| Metrics Tracking | `_get_metrics` | apc_mcp_server.py:405-416 |
| Project Scanning | `_scan_project` | apc_mcp_server.py:418-483 |
| Project Queries | `_query_project` | apc_mcp_server.py:485-524 |

**Voir aussi**: `APC_MCP_INTEGRATION.md` et `CLAUDE.md` (section "MANDATORY: APC CONSULTATION")

---

## 🎯 Règles de Délégation (PRIORITÉ ABSOLUE)

### Règle #1: Déléguer par Défaut

**TOUJOURS déléguer si la tâche correspond à:**

```
✅ Code generation (>50 lines)
✅ Documentation (>500 words)
✅ Multi-file features
✅ Research (3+ sources)
✅ Complex analysis
✅ Test suites (comprehensive)
```

**NE PAS déléguer si:**

```
❌ Quick edits (<50 lines)
❌ Interactive debugging
❌ Simple file operations
❌ Direct Q&A
❌ Configuration changes
```

### Règle #2: Utiliser Specialized Routing

**DEFAULT**: `enable_specialized_routing=True`

**Modèles FREE prioritaires:**
- Llama-4 Maverick (agentic complex)
- Llama-3.3 70B (code generation)
- Dolphin 3.0 (document parsing)
- DeepSeek R1 Distill (deep reasoning)

### Règle #3: Monitoring Automatique

**DEFAULT**: Utiliser MonitoredDelegationWorkflow

```python
from agentflow.orchestration.monitored_delegation_workflow import execute_monitored_delegation

result = execute_monitored_delegation(
    task=task_description,
    enable_apc=True,                    # Context compression
    enable_specialized_routing=True,     # FREE models
    validation_threshold=80              # Quality gate
)
```

### Règle #4: Validation Systématique

**TOUJOURS valider les outputs** avec:
- Score 0-100 (threshold: 80)
- Check completeness
- Check correctness
- Check production-ready

**Si score < 80**: Retry automatique avec feedback

---

## 🔧 Configuration Actuelle

### Session En Cours

```yaml
project: tech-watch-portal/agentflow-src
phase: Phase 2 Complete + Specialized Routing
status: DEVELOPMENT & TESTING

components_operational:
  - SessionHistoryManager ✅
  - TaskTracker ✅
  - KnowledgeBase ✅
  - SessionContinuityProtocol ✅
  - SpecializedModelRouter ✅ (8 models, 6 FREE)
  - MonitoredDelegationWorkflow ✅

tests: 12/12 passing (100%)
docs: 4 guides complets créés

delegation_settings:
  default_routing: specialized (FREE models)
  monitoring: enabled
  validation: enabled (threshold: 80)
  retry: enabled (max: 2)

api_keys_location: .env file
environment: Development
```

### Fichiers Critiques

```
agentflow/orchestration/smart_orchestrator.py
agentflow/orchestration/specialized_model_router.py
agentflow/orchestration/monitored_delegation_workflow.py
agentflow/phase2/ (4 components)
tests/test_phase2_integration.py
```

---

## 🚀 Quick Start Pour Nouvelle Session

### 1. Vérifier Environnement

```bash
cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src

# Check Python env
source .venv/bin/activate

# Verify API keys
cat .env | grep -E "(OPENROUTER|ANTHROPIC|OPENAI)_API_KEY"

# Run tests
python -m pytest tests/test_phase2_integration.py -v
```

**Expected**: 12/12 tests passing

### 2. Lire Documentation de Session

```bash
# Priority order:
1. SESSION_SUMMARY_2025-10-14.md          # Quick overview
2. COMPLETE_DELEGATION_ARCHITECTURE.md    # Full architecture
3. SPECIALIZED_MODEL_ROUTING.md           # Routing details
4. PHASE2_COMPLETION_REPORT.md            # Phase 2 details
```

**Time**: <5 minutes pour recontextualisation complète

### 3. Tester Délégation

```bash
# Quick test
python -c "
from agentflow.orchestration.monitored_delegation_workflow import execute_monitored_delegation

result = execute_monitored_delegation(
    task='Write a Python function to calculate factorial',
    enable_specialized_routing=True
)

print(f'Success: {result.success}')
print(f'Cost: \${result.total_cost:.4f}')
print(f'Model: {result.workers[0].model_id}')
"
```

**Expected**:
- Success: True
- Cost: $0.00 (FREE model)
- Model: meta-llama/llama-3.3-70b-instruct:free

---

## 📋 Protocole de Délégation Standard

### Pattern: Simple Task

```python
# User request: "Write a function to parse JSON"

# Claude Code MUST:
1. Detect: code_generation task
2. Check: >50 lines? → YES, delegate
3. Route: Llama 3.3 70B FREE
4. Execute: MonitoredDelegationWorkflow
5. Validate: Score > 80
6. Return: Result to user

# Log:
INFO: Task detected: code_generation
INFO: Routing to: meta-llama/llama-3.3-70b-instruct:free (FREE)
INFO: Delegating to AgentFlow...
INFO: Worker completed in 24s
INFO: Validation score: 88/100 ✅
```

### Pattern: Complex Feature

```python
# User request: "Build authentication system"

# Claude Code MUST:
1. Detect: complex code_generation
2. Prepare context with APC (if conversation >50K tokens)
3. Route: Llama 3.3 70B FREE
4. Orchestrator decomposes: 4 subtasks
5. Spawn: 4 workers parallel
6. Monitor: Real-time status
7. Validate: Each worker score > 80
8. Retry: If any score < 80
9. Return: Complete system

# Log:
INFO: Complex task detected
INFO: APC context compression: 80K → 6.5K (12x)
INFO: Decomposed into 4 subtasks
INFO: Spawning 4 parallel workers...
INFO: Worker 1/4: ✓ (score: 85)
INFO: Worker 2/4: ✓ (score: 88)
INFO: Worker 3/4: ✓ (score: 92)
INFO: Worker 4/4: ⚠ (score: 75) → Retrying...
INFO: Worker 4/4 retry: ✓ (score: 87)
INFO: All workers completed successfully
```

---

## 🐛 Mode Débogage

### Logging Maximal

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# All components will log verbosely
```

### Vérifications Systématiques

**Avant chaque délégation:**

```
✓ Check API keys loaded
✓ Check .env file exists
✓ Check SmartOrchestrator initialized
✓ Check SpecializedRouter available
✓ Check model availability on OpenRouter
```

**Pendant délégation:**

```
✓ Log routing decision
✓ Log model selection
✓ Log worker spawn
✓ Log API calls
✓ Log response tokens
✓ Log costs
```

**Après délégation:**

```
✓ Log completion status
✓ Log validation score
✓ Log retry attempts
✓ Log final result
✓ Save to session history
```

### Outputs à Surveiller

**⚠️ ATTENTION SPÉCIALE:**

```
1. Worker failures (status: failed)
   → Check API key, model availability

2. Low validation scores (<70)
   → Check task clarity, model selection

3. Timeouts (>120s for simple tasks)
   → Check network, API rate limits

4. Empty outputs
   → Check prompt construction, model response

5. Cost spikes (>$0.01 for FREE models)
   → Should be $0.00, investigate routing
```

---

## 🔄 Recontextualisation Session

### Fichier: SESSION_CONTEXT.json

```json
{
  "session_id": "2025-10-14_phase2_complete",
  "status": "DEVELOPMENT",
  "phase": "Phase 2 Complete + Specialized Routing",

  "completed": [
    "SessionHistoryManager implementation",
    "TaskTracker implementation",
    "KnowledgeBase implementation",
    "SessionContinuityProtocol implementation",
    "SpecializedModelRouter (8 models, 6 FREE)",
    "MonitoredDelegationWorkflow (full pipeline)",
    "Integration tests (12/12 passing)",
    "Documentation (4 guides)"
  ],

  "operational": {
    "delegation": true,
    "specialized_routing": true,
    "monitoring": true,
    "validation": true,
    "free_models": 6
  },

  "metrics": {
    "cost_savings": "95-100%",
    "quality": "88-91%",
    "speedup": "3-5x",
    "tests_passing": "100%"
  },

  "next_session": {
    "priority": [
      "Vérifier tests (should be 12/12)",
      "Tester délégation simple",
      "Lire SESSION_SUMMARY_2025-10-14.md",
      "Continuer développement ou Phase 3"
    ],
    "time_to_context": "<5 minutes",
    "files_to_read": [
      "SESSION_SUMMARY_2025-10-14.md",
      "COMPLETE_DELEGATION_ARCHITECTURE.md"
    ]
  },

  "debugging": {
    "mode": "active",
    "verbosity": "high",
    "validate_outputs": true,
    "log_all_delegations": true
  }
}
```

---

## 📊 Checklist Démarrage Session

```
Session Start Checklist:
─────────────────────────────────────────

Environment:
  [ ] cd /home/gontrand/.../agentflow-src
  [ ] source .venv/bin/activate
  [ ] Check .env file exists

Tests:
  [ ] pytest tests/test_phase2_integration.py
  [ ] Expected: 12/12 passing

Context:
  [ ] Read SESSION_SUMMARY_2025-10-14.md
  [ ] Read .claude/delegation_priority_rules.md
  [ ] Total time: <5 minutes

Delegation Test:
  [ ] Run simple delegation test
  [ ] Verify FREE model used
  [ ] Verify cost: $0.00

Ready to Work:
  [ ] All checks passed
  [ ] Context loaded
  [ ] Delegation operational
  [ ] Time elapsed: <5 minutes ✅
```

---

## 🎯 Guidelines Pour Claude Code

### Comportement Attendu

**TOUJOURS:**
- ✅ Proposer délégation pour tâches >50 lines
- ✅ Utiliser FREE models (specialized routing)
- ✅ Valider outputs (score > 80)
- ✅ Logger tous les événements
- ✅ Demander confirmation avant operations critiques
- ✅ Expliquer décisions de routing

**JAMAIS:**
- ❌ Générer code >50 lines directement
- ❌ Ignorer validation score < 80
- ❌ Utiliser modèles payants si FREE disponible
- ❌ Exécuter sans logging
- ❌ Modifier fichiers critiques sans validation

### Format Communications

**Lors de délégation:**

```
🔄 DÉLÉGATION DÉTECTÉE
Task: [description]
Type: code_generation
Model: Llama 3.3 70B (FREE)
Estimated: ~2-3 minutes

Procéder avec délégation? [Y/n]
```

**Résultat:**

```
✅ DÉLÉGATION COMPLÈTE
Duration: 24s
Cost: $0.00
Model: meta-llama/llama-3.3-70b-instruct:free
Score: 88/100
Status: PASSED (>80)

[Output présenté à l'utilisateur]
```

---

## 🔐 Sécurité & Validation

### API Keys

```
Location: .env file
Required:
  - OPENROUTER_API_KEY (pour FREE models)
  - ANTHROPIC_API_KEY (optional)
  - OPENAI_API_KEY (optional)

Loaded by: load_dotenv() in smart_orchestrator.py (line 33)
```

### Validation Outputs

```
Score Components:
  - Completeness: 30 points
  - Correctness: 40 points
  - Production-ready: 30 points

Threshold: 80/100
Retry: Max 2 attempts avec feedback
```

---

## 📞 Support & Debugging

### Problèmes Communs

**1. Tests failing**
```bash
# Solution:
cd /home/gontrand/.../agentflow-src
source .venv/bin/activate
pytest tests/test_phase2_integration.py -v
```

**2. Delegation failing**
```bash
# Check:
- .env file exists
- API keys valid
- Network connection
- OpenRouter status
```

**3. Wrong model used**
```bash
# Verify:
- enable_specialized_routing=True
- Router initialized
- Model available on OpenRouter
```

---

**Mode**: 🔧 DÉVELOPPEMENT ACTIF
**Validation**: OBLIGATOIRE
**Logging**: MAXIMUM
**Délégation**: PRIORITÉ #1

**Prochaine session**: Lire SESSION_SUMMARY_2025-10-14.md + run tests (<5 min)
