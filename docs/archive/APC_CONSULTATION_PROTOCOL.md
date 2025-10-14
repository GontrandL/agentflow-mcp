# APC Consultation Protocol - Mandatory Before All Development

**Date**: 2025-10-14
**Status**: ✅ ACTIVE - RÈGLE OBLIGATOIRE
**Priority**: CRITIQUE

---

## 🚨 Pourquoi Cette Règle Existe

### Incident Déclencheur (2025-10-14)

Pendant le développement de Phase 2, `MonitoredDelegationWorkflow` a failli dupliquer des features APC MCP existantes:

**Ce qui a failli être dupliqué:**
- Context compression → **Existait déjà** dans `apc_mcp_server.py:281` (`_prepare_context`)
- Output validation → **Existait déjà** dans `apc_mcp_server.py:330` (`_validate_output`)
- Workflow execution → **Existait déjà** dans `apc_mcp_server.py:364` (`_execute_workflow`)

**Impact potentiel si non détecté:**
- ❌ Code dupliqué difficile à maintenir
- ❌ Comportements incohérents entre implémentations
- ❌ Tests redondants
- ❌ Confusion pour développeurs futurs

**Ce qui s'est passé:**
L'utilisateur a interrompu: "nous avons un outil acp mcp qui devrait être en charge de la génération des contextes... assure toi de ne pas développer ce qui existe stp"

**Résultat:**
MonitoredDelegationWorkflow a été **corrigé** pour utiliser APC MCP existant via `asyncio.run()`.

---

## 📋 La Nouvelle Règle Obligatoire

**AVANT toute création de fonctionnalité, Claude Code DOIT:**

### 1. Consulter APC MCP

```python
from agentflow.mcp.apc_mcp_server import APCMCPServer
import asyncio

apc = APCMCPServer()

# Scanner le projet (si pas déjà fait)
asyncio.run(apc._scan_project({
    'project_root': '/path/to/project'
}))

# Query pour vérifier existence
result = asyncio.run(apc._query_project({
    'query_type': 'find_pattern',
    'query': 'nom_de_feature',  # e.g., 'validation', 'context_compression'
    'file_type': 'py'
}))

# Analyser résultat
if result.get('results'):
    # Feature EXISTE → UTILISER l'existant
    print(f"Feature trouvée: {result['results']}")
    # Import et utilisation via asyncio.run()
else:
    # Feature N'EXISTE PAS → OK pour développer
    print("Feature inexistante, procéder avec développement")
```

### 2. Validation Alignement Projet

Si feature n'existe pas, vérifier l'alignement architectural:

```python
# Vérifier structure projet
structure = asyncio.run(apc._query_project({
    'query_type': 'get_structure',
    'query': '.'
}))

# Vérifier patterns existants
patterns = asyncio.run(apc._query_project({
    'query_type': 'find_pattern',
    'query': 'similar_feature_pattern',
    'file_type': 'py'
}))

# Décision: Où placer le nouveau code?
# Décision: Quel pattern suivre?
```

### 3. Développement avec Références

Si développement autorisé, documenter les vérifications:

```python
"""
[MODULE] New Feature Implementation

APC Consultation Results (2025-10-14):
- Query: 'feature_name'
- Result: Not found in project
- Alignment: Verified with existing patterns in module X
- Location: Chosen based on project structure analysis

This feature does NOT duplicate existing functionality.
"""
```

---

## 🔍 APC MCP Server - Capacités de Consultation

### Features EXISTANTES à NE JAMAIS Dupliquer

| Feature | Méthode | Location | Lines |
|---------|---------|----------|-------|
| **Context Compression** | `_prepare_context` | apc_mcp_server.py | 281-328 |
| **Output Validation** | `_validate_output` | apc_mcp_server.py | 330-362 |
| **Workflow Execution** | `_execute_workflow` | apc_mcp_server.py | 364-403 |
| **Metrics Tracking** | `_get_metrics` | apc_mcp_server.py | 405-416 |
| **Project Scanning** | `_scan_project` | apc_mcp_server.py | 418-483 |
| **Project Queries** | `_query_project` | apc_mcp_server.py | 485-524 |

**Total**: 6 features critiques, ~250 lines de code

### Query Types Disponibles

**1. `find_pattern`** - Chercher code patterns
```python
result = asyncio.run(apc._query_project({
    'query_type': 'find_pattern',
    'query': 'validate_output',  # class name, function name, etc.
    'file_type': 'py'
}))
```

**2. `find_files`** - Chercher fichiers par nom
```python
result = asyncio.run(apc._query_project({
    'query_type': 'find_files',
    'query': 'validation',
    'file_type': 'py'
}))
```

**3. `get_dependencies`** - Obtenir dépendances fichier
```python
result = asyncio.run(apc._query_project({
    'query_type': 'get_dependencies',
    'query': 'path/to/file.py'
}))
```

**4. `get_structure`** - Structure projet
```python
result = asyncio.run(apc._query_project({
    'query_type': 'get_structure',
    'query': '.'
}))
```

**5. `ask`** - Questions natural language
```python
result = asyncio.run(apc._query_project({
    'query_type': 'ask',
    'query': 'Where should I add validation logic?'
}))
```

---

## 🔄 Nouveau Workflow de Développement

### Avant Cette Règle (PROBLÉMATIQUE)

```
User: "Create validation system"
    ↓
Claude: [Starts coding ValidationEngine...]  ❌ RISQUE DE DUPLICATION
    ↓
User: [Doit interrompre et corriger]
```

### Après Cette Règle (CORRECT)

```
User: "Create validation system"
    ↓
Claude: [Consulte APC MCP]
    ↓
APC Query: 'validation'
    ↓
    ├─ TROUVÉ → "validation exists in apc_mcp_server.py:330"
    │   ↓
    │   Claude: "Validation déjà implémentée. Utilisons l'existant:"
    │   └─ Import APCMCPServer
    │       Use asyncio.run(apc._validate_output(...))
    │
    └─ NON TROUVÉ → "No validation found"
        ↓
        Claude: "Feature inexistante, procéder avec développement."
        └─ Vérifier alignement architectural
            Développer nouvelle feature
```

---

## 📚 Documentation Mise à Jour

### 1. CLAUDE.md (Règles Projet)

**Section ajoutée**: "🚨 MANDATORY: APC CONSULTATION BEFORE DEVELOPMENT"

**Contenu**:
- Problème expliqué
- Solution (APC-First Development)
- Checklist obligatoire
- Exemples WRONG vs RIGHT
- Quick reference commands

**Location**: `/home/gontrand/CLAUDE.md:92-257`

### 2. delegation_priority_rules.md (Règles Délégation)

**Nouvelle Règle #0**: "TOUJOURS Consulter APC AVANT Développement"

**Contenu**:
- Incident déclencheur
- Table des features APC MCP existantes
- Code examples
- Références croisées

**Location**: `.claude/delegation_priority_rules.md:22-66`

### 3. SESSION_CONTEXT.json (Context Session)

**Ajouts**:
```json
{
  "current_state": {
    "apc_consultation_mandatory": true,
    "new_rule_added": "2025-10-14 - APC consultation before all development"
  },
  "next_session_quickstart": {
    "steps": [{
      "step": 5,
      "critical": "NEW RULE: Always consult APC before development!"
    }]
  }
}
```

### 4. APC_MCP_INTEGRATION.md (Guide Intégration)

**Déjà existant** - Guide complet d'utilisation APC MCP

**Content**:
- Fonctionnalités existantes détaillées
- Usage examples pour chaque méthode
- Guidelines "CE QU'ON FAIT" vs "CE QU'ON NE FAIT PAS"
- Checklist intégration

**Location**: `APC_MCP_INTEGRATION.md:1-423`

---

## ✅ Checklist Nouvelle Feature

**AVANT de coder quoi que ce soit:**

```
[ ] 1. Import APCMCPServer + asyncio
[ ] 2. Scanner projet (_scan_project) si pas fait
[ ] 3. Query existence (_query_project 'find_pattern')
[ ] 4. Si trouvé:
      [ ] Utiliser feature existante via asyncio.run()
      [ ] Documenter utilisation
      [ ] STOP - Ne pas dupliquer
[ ] 5. Si non trouvé:
      [ ] Query structure projet
      [ ] Query patterns similaires
      [ ] Valider alignement architectural
      [ ] Documenter décision (où, pourquoi, comment)
      [ ] Procéder avec développement
```

---

## 🎯 Exemples Concrets

### Exemple 1: Validation (CE QUI S'EST PASSÉ)

**WRONG (Initial approach):**
```python
class OutputValidator:
    def validate(self, output: str, task: str) -> Dict:
        # Custom validation logic...  ❌ DUPLICATION!
```

**RIGHT (After APC consultation):**
```python
from agentflow.mcp.apc_mcp_server import APCMCPServer
import asyncio

apc = APCMCPServer()

# Use existing validation
result = asyncio.run(apc._validate_output({
    'task': task,
    'output': output,
    'threshold': 80
}))  ✅ UTILISE L'EXISTANT
```

### Exemple 2: Context Compression

**WRONG:**
```python
def compress_context(history: List[Dict]) -> str:
    # Custom compression...  ❌ DUPLICATION!
```

**RIGHT:**
```python
# Use existing APC MCP compression
result = asyncio.run(apc._prepare_context({
    'conversation_history': history,
    'current_task': task,
    'target_tokens': 8000
}))  ✅ UTILISE L'EXISTANT
```

### Exemple 3: Nouvelle Feature (Vraiment Nouvelle)

```python
# 1. Query first
result = asyncio.run(apc._query_project({
    'query_type': 'find_pattern',
    'query': 'task_decomposition',
    'file_type': 'py'
}))

# 2. Not found → OK to develop
if not result.get('results'):
    class TaskDecomposer:
        """
        APC Consultation (2025-10-14):
        - Query: 'task_decomposition'
        - Result: Not found
        - New feature approved for development
        """
        def decompose(self, task: str) -> List[str]:
            # Implementation...  ✅ NOUVELLE FEATURE
```

---

## 🚀 Impact Attendu

### Bénéfices

**Court terme:**
- ✅ Zéro duplication de code
- ✅ Utilisation maximale des features existantes
- ✅ Cohérence architecturale

**Long terme:**
- ✅ Codebase maintenable
- ✅ Onboarding développeurs facilité
- ✅ Evolution projet structurée
- ✅ Tests et documentation consolidés

### Métriques de Succès

**Indicateurs:**
- Nombre de queries APC avant développement: **100%** (objectif)
- Taux de duplication détectée: **0%** (objectif)
- Temps consultation APC: **<30 secondes** (acceptable)

---

## 📊 Résumé Exécutif

**Problème Résolu:**
Duplication accidentelle de features existantes dans APC MCP Server

**Solution Implémentée:**
Consultation obligatoire APC MCP avant tout développement

**Documentation Mise à Jour:**
1. ✅ CLAUDE.md (section complète)
2. ✅ delegation_priority_rules.md (Règle #0)
3. ✅ SESSION_CONTEXT.json (flags + quickstart)
4. ✅ APC_CONSULTATION_PROTOCOL.md (ce document)

**Prochaine Session:**
Claude Code **doit lire** les règles mises à jour et **appliquer** la consultation APC systématiquement.

---

**Date Effective**: 2025-10-14
**Status**: ✅ ACTIF
**Priority**: 🚨 CRITIQUE
**Enforcement**: OBLIGATOIRE

*Cette règle est permanente et s'applique à tous les développements futurs.*
