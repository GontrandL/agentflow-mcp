#!/bin/bash

# Spawn all 8 workers with provider='deepseek' fix

cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src

# Worker 1: escalation_engine.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement EscalationEngine class with methods: should_escalate(result, current_tier) -> bool, _free_tier_failed(result) -> bool (3 attempts or quality<6), _mid_tier_failed(result) -> bool (2 attempts or quality<8), get_next_tier(current_tier) -> str. Output to agentflow/orchestration/escalation_engine.py with type hints, docstrings, logging.'

print('[Worker 1] escalation_engine.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 1] COMPLETE')
print(result)
" > /tmp/worker1_escalation_v2.log 2>&1 &

# Worker 2: interactive_orchestrator.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement InteractiveOrchestrator class with methods: orchestrate(task, interactive=True), _analyze_task(task) -> dict detecting ambiguities (missing tech stack, unclear scope, missing context). Return questions if confidence<80. Uses FREE model for question generation. Output to agentflow/orchestration/interactive_orchestrator.py with type hints, docstrings, logging.'

print('[Worker 2] interactive_orchestrator.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 2] COMPLETE')
print(result)
" > /tmp/worker2_interactive_v2.log 2>&1 &

# Worker 3: quality_evaluator.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement QualityEvaluationOrchestrator class with orchestrate_with_evaluation(task, mode) method. Generates with 2-3 models in parallel (mistralai/mistral-7b-instruct:free, meta-llama/llama-3.2-3b-instruct:free, deepseek/deepseek-chat). FREE model judges all outputs. Tracks model win rates and performance statistics in JSON. Output to agentflow/orchestration/quality_evaluator.py with type hints, docstrings, async support.'

print('[Worker 3] quality_evaluator.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 3] COMPLETE')
print(result)
" > /tmp/worker3_quality_eval_v2.log 2>&1 &

# Worker 4: mcp_feedback_receiver.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement FeedbackManager class for MCP feedback loop with async methods: store_feedback(feedback: dict) -> str (stores with UUID), improve_prompts(validation: dict) (auto-improves based on patterns). Include MCP tool decorator @server.tool() for receive_feedback. Output to agentflow/mcp/feedback_receiver.py with type hints, async/await, storage system.'

print('[Worker 4] mcp_feedback_receiver.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 4] COMPLETE')
print(result)
" > /tmp/worker4_feedback_v2.log 2>&1 &

# Worker 5: dashboard.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement FastAPI + SSE real-time dashboard. DashboardManager class tracks tasks/logs/stats with methods: add_task, update_task, log, get_status. FastAPI app with @app.get(/) serving HTML and @app.get(/events) streaming SSE updates every second. Embedded HTML with dark theme (GitHub style), progress bars, live logs. Output to agentflow/mcp/dashboard.py with FastAPI, async/await, embedded HTML.'

print('[Worker 5] dashboard.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 5] COMPLETE')
print(result)
" > /tmp/worker5_dashboard_v2.log 2>&1 &

# Worker 6: context_injector.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement ContextInjector class with inject_context(task, context_type) method. Analyzes context needs (project/tech_stack/patterns/domain). Methods: _analyze_context_needs, _get_project_context, _get_tech_stack, _get_common_patterns, _build_enriched_prompt. Injects rich context once to save 60-80% tokens on retries. Output to agentflow/orchestration/context_injector.py with type hints, docstrings.'

print('[Worker 6] context_injector.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 6] COMPLETE')
print(result)
" > /tmp/worker6_context_v2.log 2>&1 &

# Worker 7: parallel_executor.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement ParallelExecutor class using ThreadPoolExecutor with execute_parallel(tasks, max_workers=5) method. Methods: _execute_single(task) using SmartOrchestrator. Includes progress tracking, error handling per task, timeout support, resource limits. Returns list of results with status (success/failed). Output to agentflow/orchestration/parallel_executor.py with concurrent.futures, type hints, error handling.'

print('[Worker 7] parallel_executor.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 7] COMPLETE')
print(result)
" > /tmp/worker7_parallel_v2.log 2>&1 &

# Worker 8: waterfall_orchestrator.py
python3 -c "
import os
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = 'Implement WaterfallOrchestrator class with 3-tier escalation (FREE/mid/premium). Init with tier configs: free=[qwen/qwen-2.5-coder-32b-instruct, deepseek/deepseek-r1-distill-qwen-32b], mid=[deepseek/deepseek-chat], premium=[claude-sonnet-4-20250514]. Methods: orchestrate(task), _free_tier_attempt, _mid_tier_attempt, _premium_tier_attempt, _is_perfect, _finalize. Integrates CostTracker, EscalationEngine, QualityValidator. Output to agentflow/orchestration/waterfall_orchestrator.py with type hints, docstrings, LiteLLM.'

print('[Worker 8] waterfall_orchestrator.py - Starting with provider=deepseek...')
orchestrator = SmartOrchestrator(provider='deepseek')
result = orchestrator.orchestrate(task)
print('[Worker 8] COMPLETE')
print(result)
" > /tmp/worker8_waterfall_v2.log 2>&1 &

echo "✅ All 8 workers spawned with provider='deepseek' fix"
echo "Monitor with: tail -f /tmp/worker*_v2.log"
echo "Check completion: ls -lh /tmp/worker*_v2.log"
