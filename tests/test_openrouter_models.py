#!/usr/bin/env python3
"""
Test different OpenRouter models to find which ones work
"""

from agentflow_universal_adapter import UniversalLLMEngine
import time

# Models to test
models_to_test = [
    # Llama models
    ("meta-llama/llama-3.2-3b-instruct:free", "Llama 3.2 3B FREE"),
    ("meta-llama/llama-3.2-1b-instruct:free", "Llama 3.2 1B FREE"),
    ("meta-llama/llama-3.1-8b-instruct:free", "Llama 3.1 8B FREE"),

    # Qwen models
    ("qwen/qwen-2-7b-instruct:free", "Qwen 2 7B FREE"),
    ("qwen/qwen-2.5-7b-instruct:free", "Qwen 2.5 7B FREE"),

    # Google models
    ("google/gemma-2-9b-it:free", "Gemma 2 9B FREE"),
    ("google/gemma-7b-it:free", "Gemma 7B FREE"),

    # Microsoft models
    ("microsoft/phi-3-mini-128k-instruct:free", "Phi 3 Mini FREE"),
    ("microsoft/phi-3-medium-128k-instruct:free", "Phi 3 Medium FREE"),
]

print("\n🧪 Testing OpenRouter FREE Models")
print("━" * 60)

working_models = []
failed_models = []

for model_id, model_name in models_to_test:
    print(f"\n📝 Testing: {model_name}")
    print(f"   Model ID: {model_id}")

    try:
        engine = UniversalLLMEngine(provider="openrouter", model=model_id)

        # Simple test query
        response = engine.generate("What is 2+2? Answer in one word.", max_tokens=50)

        print(f"   ✅ WORKS - Response: {response[:50]}")
        working_models.append((model_id, model_name, response))

        time.sleep(1)  # Rate limiting

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"   ❌ NOT AVAILABLE (404)")
        elif "429" in error_msg:
            print(f"   ⚠️  RATE LIMITED")
        else:
            print(f"   ❌ ERROR: {error_msg[:80]}")
        failed_models.append((model_id, model_name, str(e)))

print("\n\n" + "━" * 60)
print("📊 RESULTS SUMMARY")
print("━" * 60)

print(f"\n✅ Working Models ({len(working_models)}):")
for model_id, model_name, response in working_models:
    print(f"   • {model_name}")
    print(f"     ID: {model_id}")
    print(f"     Sample: {response[:60]}...")

print(f"\n❌ Failed Models ({len(failed_models)}):")
for model_id, model_name, error in failed_models:
    print(f"   • {model_name}")
    if "404" in error:
        print(f"     Reason: Not available on OpenRouter")

print("\n\n💡 RECOMMENDATION:")
if working_models:
    best_model_id, best_model_name, _ = working_models[0]
    print(f"   Use: {best_model_name}")
    print(f"   Model ID: {best_model_id}")
else:
    print("   No working models found!")

print("\n" + "━" * 60)
