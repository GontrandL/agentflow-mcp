#!/usr/bin/env python3
"""
Compare Llama 3.2 3B vs Gemma 2 9B on realistic tasks
"""

from agentflow_universal_adapter import UniversalLLMEngine
import time
import json

# Test queries (realistic use cases)
test_queries = [
    {
        "name": "Code Analysis",
        "query": """Analyze this bash command and explain what it does:
find . -type f \\( -name "*.js" -o -name "*.ts" \\) -not -path "*/node_modules/*" | wc -l

Answer in 2-3 sentences.""",
        "max_tokens": 200
    },
    {
        "name": "Config Map Suggestion",
        "query": """I'm creating a config map for PostgreSQL integration. What are the 3 most important sections to include? List them briefly.""",
        "max_tokens": 150
    },
    {
        "name": "Error Diagnosis",
        "query": """Error: "No endpoints found for qwen/qwen-2-7b-instruct:free"
What does this error mean and how to fix it? Answer briefly.""",
        "max_tokens": 150
    },
    {
        "name": "Architecture Decision",
        "query": """Should I use OpenRouter with FREE models or run local LLMs with VLLM? Consider: no GPU, 64GB RAM. Answer in 2-3 sentences.""",
        "max_tokens": 200
    }
]

models = [
    ("meta-llama/llama-3.2-3b-instruct:free", "Llama 3.2 3B"),
    ("google/gemma-2-9b-it:free", "Gemma 2 9B")
]

print("\n🔬 Model Comparison: Llama 3.2 3B vs Gemma 2 9B")
print("=" * 70)

results = {}

for model_id, model_name in models:
    print(f"\n\n{'=' * 70}")
    print(f"🤖 Testing: {model_name}")
    print(f"   Model ID: {model_id}")
    print("=" * 70)

    engine = UniversalLLMEngine(provider="openrouter", model=model_id)
    model_results = []

    for i, test in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/4: {test['name']}")
        print(f"Query: {test['query'][:60]}...")

        start_time = time.time()

        try:
            response = engine.generate(
                test['query'],
                max_tokens=test['max_tokens'],
                temperature=0.7
            )
            elapsed = time.time() - start_time

            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"✅ Response ({len(response)} chars):")
            print(f"   {response[:150]}...")

            model_results.append({
                "test": test['name'],
                "success": True,
                "response": response,
                "time": elapsed,
                "length": len(response)
            })

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error: {str(e)[:100]}")

            model_results.append({
                "test": test['name'],
                "success": False,
                "error": str(e),
                "time": elapsed
            })

        time.sleep(1)  # Rate limiting

    results[model_name] = model_results

# Summary comparison
print("\n\n" + "=" * 70)
print("📊 COMPARISON SUMMARY")
print("=" * 70)

for model_name in [m[1] for m in models]:
    model_results = results[model_name]
    successful = [r for r in model_results if r.get('success')]

    print(f"\n🤖 {model_name}:")
    print(f"   Success Rate: {len(successful)}/{len(model_results)} ({len(successful)*100//len(model_results)}%)")

    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        avg_length = sum(r['length'] for r in successful) / len(successful)
        print(f"   Avg Response Time: {avg_time:.2f}s")
        print(f"   Avg Response Length: {avg_length:.0f} chars")

# Detailed comparison
print("\n\n📋 Test-by-Test Comparison:")
print("-" * 70)

for i, test in enumerate(test_queries, 1):
    print(f"\n{i}. {test['name']}:")

    for model_name in [m[1] for m in models]:
        result = results[model_name][i-1]

        if result.get('success'):
            print(f"   {model_name}: ✅ {result['time']:.2f}s, {result['length']} chars")
        else:
            print(f"   {model_name}: ❌ Failed")

# Recommendation
print("\n\n" + "=" * 70)
print("💡 RECOMMENDATION")
print("=" * 70)

llama_results = results["Llama 3.2 3B"]
gemma_results = results["Gemma 2 9B"]

llama_success = len([r for r in llama_results if r.get('success')])
gemma_success = len([r for r in gemma_results if r.get('success')])

llama_avg_time = sum(r['time'] for r in llama_results if r.get('success')) / max(llama_success, 1)
gemma_avg_time = sum(r['time'] for r in gemma_results if r.get('success')) / max(gemma_success, 1)

print(f"\n📈 Performance:")
print(f"   Llama 3.2 3B: {llama_success}/4 tests, avg {llama_avg_time:.2f}s")
print(f"   Gemma 2 9B:   {gemma_success}/4 tests, avg {gemma_avg_time:.2f}s")

if llama_success == gemma_success:
    if llama_avg_time < gemma_avg_time:
        print(f"\n✅ WINNER: Llama 3.2 3B (faster by {gemma_avg_time - llama_avg_time:.2f}s)")
    else:
        print(f"\n✅ WINNER: Gemma 2 9B (better quality, worth the extra {gemma_avg_time - llama_avg_time:.2f}s)")
else:
    winner = "Llama 3.2 3B" if llama_success > gemma_success else "Gemma 2 9B"
    print(f"\n✅ WINNER: {winner} (more reliable)")

print("\n" + "=" * 70)
