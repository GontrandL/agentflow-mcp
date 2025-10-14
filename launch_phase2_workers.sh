#!/bin/bash
# Launch Phase 2 workers with pre-flight validation
# This script properly handles bash variables and Python f-strings

cd /home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src

echo "=== Phase 2 Worker Launch (with APIValidator) ==="
echo ""

# Kill any existing workers
pkill -f "phase2_worker" 2>/dev/null || true
sleep 1

# Launch 4 workers in parallel
for i in 1 2 3 4; do
  ./.venv/bin/python3 << PYEOF > /tmp/phase2_worker${i}_v3.log 2>&1 &
import json
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

# Load task
with open('phase2_delegation_tasks.json') as f:
    tasks = json.load(f)['tasks']
    task = tasks[$i-1]

print(f'Starting worker $i: {task["name"]}')

# Delegate to AgentFlow (with pre-flight validation)
orchestrator = SmartOrchestrator()
result = orchestrator.orchestrate(task['description'])

print(f'Worker $i completed!')
print(result)
PYEOF
  PID=$!
  echo "✓ Launched worker $i (PID: $PID) -> /tmp/phase2_worker${i}_v3.log"
done

echo ""
echo "All 4 workers launched!"
echo "Monitor: tail -f /tmp/phase2_worker*_v3.log"
echo ""
echo "Check status: ps aux | grep phase2_worker"
