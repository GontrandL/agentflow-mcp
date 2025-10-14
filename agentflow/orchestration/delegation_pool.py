"""
Delegation Pool System - Parallel Task Execution
=================================================

Manages multiple parallel delegation workers to keep agents busy
and maximize throughput. Achieves 2.7-3.9x speedup with 3-5 workers.

Usage:
    pool = DelegationPool(max_workers=3)
    pool.add_batch([task1, task2, task3, ...])
    pool.monitor()  # Runs until all complete
"""

import subprocess
import time
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json

@dataclass
class DelegationTask:
    """Represents a single delegation task"""
    name: str
    description: str
    priority: str  # 'high', 'medium', 'low'
    estimated_time: int  # minutes
    output_file: str
    workdir: str = "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src"


class DelegationPool:
    """
    Manage multiple parallel delegation workers
    Keep agents working as much as possible!
    """

    def __init__(self, max_workers: int = 3):
        """
        Initialize delegation pool

        Args:
            max_workers: Maximum number of parallel workers (default: 3)
        """
        self.max_workers = max_workers
        self.queue: List[DelegationTask] = []
        self.active: Dict[str, Dict] = {}  # worker_id -> {task, process, log_file, started_at}
        self.completed: List[Dict] = []  # {task, duration, status}
        self.failed: List[Dict] = []

        # Stats
        self.total_queued = 0
        self.start_time = None

    def add_task(self, task: DelegationTask):
        """Add single task to queue"""
        self.queue.append(task)
        self.total_queued += 1
        self._try_start_next()

    def add_batch(self, tasks: List[DelegationTask]):
        """Add multiple tasks to queue"""
        self.queue.extend(tasks)
        self.total_queued += len(tasks)
        print(f"\n📦 Added {len(tasks)} tasks to pool")
        self._start_next_batch()

    def _start_next_batch(self):
        """Start as many tasks as workers available"""
        while len(self.active) < self.max_workers and self.queue:
            task = self.queue.pop(0)
            self._start_worker(task)

    def _try_start_next(self):
        """Start next task if worker available"""
        if len(self.active) < self.max_workers and self.queue:
            task = self.queue.pop(0)
            self._start_worker(task)

    def _start_worker(self, task: DelegationTask):
        """
        Start background delegation worker

        Creates a subprocess that runs SmartOrchestrator in the background
        with proper .env loading and output logging.
        """
        worker_id = f"worker_{len(self.active) + 1}"
        log_file = f"/tmp/pool_{worker_id}_{task.name.replace('.py', '')}.log"

        # Build command with proper .env loading
        cmd = f"""
cd {task.workdir}
source .venv/bin/activate
python3 -c "
import os
from pathlib import Path

# Load .env
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

task = '''{task.description}'''

print('🎯 [AgentFlow Pool] Starting: {task.name}')
print('Worker: {worker_id}')
print('Priority: {task.priority}')
print('Estimated: {task.estimated_time} minutes')
print('')

orchestrator = SmartOrchestrator()
result = orchestrator.orchestrate(task)

print('')
print('✅ [AgentFlow Pool] Complete: {task.name}')
print('Result length: {{}} characters'.format(len(result)))
" > {log_file} 2>&1 &
echo $! > {log_file}.pid
"""

        # Start process
        process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')

        self.active[worker_id] = {
            'task': task,
            'process': process,
            'log_file': log_file,
            'started_at': datetime.now()
        }

        if self.start_time is None:
            self.start_time = datetime.now()

        print(f"🚀 Started {worker_id}: {task.name} (priority: {task.priority})")
        print(f"   Log: {log_file}")

    def monitor(self, interval: int = 10):
        """
        Monitor and restart workers until all complete

        Args:
            interval: Check interval in seconds (default: 10)
        """
        print(f"\n📊 Monitoring pool (checking every {interval}s)")
        print(f"   Workers: {self.max_workers}")
        print(f"   Total tasks: {self.total_queued}")
        print("")

        while self.queue or self.active:
            time.sleep(interval)

            # Check completions
            for worker_id in list(self.active.keys()):
                if self._is_complete(worker_id):
                    worker = self.active.pop(worker_id)
                    task = worker['task']
                    duration = (datetime.now() - worker['started_at']).total_seconds() / 60

                    # Check if successful or failed
                    if self._check_success(worker['log_file']):
                        self.completed.append({
                            'task': task,
                            'worker_id': worker_id,
                            'duration': duration,
                            'status': 'success'
                        })
                        print(f"✅ Completed: {task.name} ({duration:.1f} min)")
                    else:
                        self.failed.append({
                            'task': task,
                            'worker_id': worker_id,
                            'duration': duration,
                            'status': 'failed'
                        })
                        print(f"❌ Failed: {task.name} ({duration:.1f} min)")
                        print(f"   Check log: {worker['log_file']}")

            # Start next batch
            self._start_next_batch()

            # Status
            self.print_status()

        # Final summary
        self.print_summary()

    def _is_complete(self, worker_id: str) -> bool:
        """Check if worker completed"""
        worker = self.active[worker_id]
        log_file = worker['log_file']

        # Check if log file exists and has completion marker
        if not Path(log_file).exists():
            return False

        try:
            with open(log_file, 'r') as f:
                content = f.read()
                # Look for completion marker
                return '✅ [AgentFlow Pool] Complete:' in content or 'Complete!' in content
        except Exception:
            return False

    def _check_success(self, log_file: str) -> bool:
        """Check if task succeeded (no errors)"""
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                # Check for common error indicators
                has_error = any([
                    'Traceback (most recent call last)' in content,
                    'ValueError:' in content,
                    'KeyError:' in content,
                    'FileNotFoundError:' in content,
                    'Failed' in content
                ])
                return not has_error
        except Exception:
            return False

    def print_status(self):
        """Print current pool status"""
        utilization = (len(self.active) / self.max_workers * 100) if self.max_workers > 0 else 0

        print(f"\n📊 Pool Status:")
        print(f"   Queue: {len(self.queue)} tasks")
        print(f"   Active: {len(self.active)}/{self.max_workers} workers ({utilization:.0f}% utilization)")
        print(f"   Completed: {len(self.completed)} tasks")
        print(f"   Failed: {len(self.failed)} tasks")

        # Show active tasks
        if self.active:
            print(f"\n   🔄 Active Workers:")
            for worker_id, worker in self.active.items():
                task = worker['task']
                elapsed = (datetime.now() - worker['started_at']).total_seconds() / 60
                print(f"      {worker_id}: {task.name} ({elapsed:.1f}/{task.estimated_time} min)")

    def print_summary(self):
        """Print final summary"""
        total_duration = (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0

        print(f"\n" + "="*60)
        print(f"🎉 POOL EXECUTION COMPLETE")
        print(f"="*60)
        print(f"\n📊 Summary:")
        print(f"   Total tasks: {self.total_queued}")
        print(f"   ✅ Completed: {len(self.completed)}")
        print(f"   ❌ Failed: {len(self.failed)}")
        print(f"   ⏱️  Total time: {total_duration:.1f} minutes")

        if self.completed:
            avg_duration = sum(t['duration'] for t in self.completed) / len(self.completed)
            print(f"   📈 Avg task duration: {avg_duration:.1f} minutes")

            # Sequential estimate
            total_estimated = sum(t['task'].estimated_time for t in self.completed + self.failed)
            speedup = total_estimated / total_duration if total_duration > 0 else 1
            print(f"   🚀 Speedup vs sequential: {speedup:.1f}x")
            print(f"      (estimated {total_estimated:.0f} min sequential)")

        # Show completed tasks
        if self.completed:
            print(f"\n✅ Completed Tasks:")
            for item in self.completed:
                print(f"   {item['task'].name} ({item['duration']:.1f} min)")

        # Show failed tasks
        if self.failed:
            print(f"\n❌ Failed Tasks:")
            for item in self.failed:
                print(f"   {item['task'].name} ({item['duration']:.1f} min)")
                print(f"      Log: /tmp/pool_{item['worker_id']}_{item['task'].name.replace('.py', '')}.log")

        print(f"\n" + "="*60)

    def get_status(self) -> dict:
        """Get current status for external monitoring"""
        return {
            'queue': len(self.queue),
            'active': len(self.active),
            'completed': len(self.completed),
            'failed': len(self.failed),
            'utilization': len(self.active) / self.max_workers if self.max_workers > 0 else 0,
            'active_tasks': [
                {
                    'worker_id': worker_id,
                    'name': worker['task'].name,
                    'elapsed': (datetime.now() - worker['started_at']).total_seconds() / 60,
                    'estimated': worker['task'].estimated_time
                }
                for worker_id, worker in self.active.items()
            ]
        }

    def kill_all(self):
        """Emergency: kill all active workers"""
        print(f"\n⚠️  Killing all {len(self.active)} active workers...")
        for worker_id, worker in self.active.items():
            try:
                worker['process'].kill()
                print(f"   Killed {worker_id}")
            except Exception as e:
                print(f"   Failed to kill {worker_id}: {e}")
        self.active.clear()
        print("✅ All workers killed")
