# AgentFlow Setup avec OpenRouter (FREE Models!)

## 🎯 Setup Rapide (5 minutes)

### 1. Obtenir votre clé API OpenRouter (GRATUIT!)

```bash
# Créer un compte OpenRouter (gratuit)
# https://openrouter.ai/keys
#
# ✅ Modèles GRATUITS disponibles:
# - meta-llama/llama-3.2-3b-instruct:free (3B, recommandé)
# - meta-llama/llama-3.2-1b-instruct:free (1B, le plus rapide)
# - qwen/qwen-2-7b-instruct:free (7B, meilleure qualité)
# - google/gemma-2-9b-it:free (9B, Google)
```

### 2. Configurer la clé API

```bash
# Éditer le fichier .env
nano .env

# Remplacer:
OPENROUTER_API_KEY=your-openrouter-key-here
# Par:
OPENROUTER_API_KEY=sk-or-v1-votre-clé-ici
```

### 3. Tester l'installation

```bash
# Activer l'environnement Python
source .venv/bin/activate

# Test avec OpenRouter (FREE!)
python agentflow_universal_adapter.py openrouter

# Test avec un modèle spécifique
python agentflow_universal_adapter.py openrouter meta-llama/llama-3.2-3b-instruct:free
python agentflow_universal_adapter.py openrouter qwen/qwen-2-7b-instruct:free
```

**Résultat attendu:**
```
✅ Universal LLM Engine initialized
   Provider: openrouter
   Model: meta-llama/llama-3.2-3b-instruct:free
   API Key: ✓

📝 Test 1: Simple Generation
Query: What is 2+2? Answer briefly.
✅ Response: 2 + 2 equals 4.

💬 Test 2: Chat Format
Query: Capital of France?
✅ Response: Paris

✅ All tests passed!
```

---

## 🚀 Utilisation

### API Simple (Python)

```python
from agentflow_universal_adapter import UniversalLLMEngine

# Initialiser avec OpenRouter (FREE!)
engine = UniversalLLMEngine(provider="openrouter")

# Query simple
response = engine.generate("What is the capital of France?", max_tokens=100)
print(response)

# Chat format
messages = [
    {"role": "user", "content": "What is 2+2?"}
]
response = engine.chat(messages, max_tokens=100)
print(response)
```

### Choisir un modèle spécifique

```python
# Modèle 3B (recommandé, équilibré)
engine = UniversalLLMEngine(
    provider="openrouter",
    model="meta-llama/llama-3.2-3b-instruct:free"
)

# Modèle 1B (le plus rapide)
engine = UniversalLLMEngine(
    provider="openrouter",
    model="meta-llama/llama-3.2-1b-instruct:free"
)

# Modèle 7B (meilleure qualité)
engine = UniversalLLMEngine(
    provider="openrouter",
    model="qwen/qwen-2-7b-instruct:free"
)
```

---

## 🔄 Autres Providers (Optionnel)

### Claude API (Anthropic)

```bash
# Ajouter dans .env
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Tester
python agentflow_universal_adapter.py claude
```

```python
engine = UniversalLLMEngine(provider="claude")
response = engine.generate("What is 2+2?")
```

### OpenAI

```bash
# Ajouter dans .env
OPENAI_API_KEY=sk-your-key-here

# Tester
python agentflow_universal_adapter.py openai
```

```python
engine = UniversalLLMEngine(provider="openai", model="gpt-4o-mini")
response = engine.generate("What is 2+2?")
```

### LiteLLM (Router Universel)

```bash
# Installer LiteLLM
pip install litellm

# Tester
python agentflow_universal_adapter.py litellm
```

```python
engine = UniversalLLMEngine(provider="litellm", model="gpt-4o-mini")
response = engine.generate("What is 2+2?")
```

---

## 📊 Comparaison Modèles Gratuits

| Modèle | Taille | Vitesse | Qualité | Usage Recommandé |
|--------|--------|---------|---------|------------------|
| **llama-3.2-1b:free** | 1B | ⚡⚡⚡ Très rapide | ⭐⭐ Basique | Tests rapides, queries simples |
| **llama-3.2-3b:free** | 3B | ⚡⚡ Rapide | ⭐⭐⭐ Bon | **Recommandé** - Usage général |
| **qwen-2-7b:free** | 7B | ⚡ Moyen | ⭐⭐⭐⭐ Excellent | Tasks complexes, meilleure qualité |
| **gemma-2-9b:free** | 9B | ⚡ Moyen | ⭐⭐⭐⭐ Excellent | Alternative à Qwen |

**Recommandation:** Commencer avec `llama-3.2-3b-instruct:free` (meilleur équilibre vitesse/qualité)

---

## 🎯 Prochaines Étapes

Une fois le test OpenRouter réussi:

1. **Créer config map AgentFlow** pour automation complète
2. **Intégrer avec AutoCoder-Next** (ClaudeFlow + AgentFlow + SpecsKit)
3. **Tester cas d'usage réels:**
   - Analyse config maps
   - Planning multi-étapes
   - Orchestration génération code
4. **Optionnel:** Intégrer LiteLLM comme router universel

---

## ❓ Troubleshooting

**Erreur: "No auth credentials found"**
→ Vérifier que `OPENROUTER_API_KEY` est bien configurée dans `.env`

**Erreur: "Rate limit exceeded"**
→ Les modèles gratuits ont des limites. Attendre quelques secondes et réessayer.

**Erreur: "Model not found"**
→ Vérifier le nom du modèle (doit inclure `:free` pour les gratuits)

**Module not found**
→ Activer l'environnement virtuel: `source .venv/bin/activate`

---

**Status:** ✅ Setup complet, prêt pour tests avec votre clé OpenRouter!
