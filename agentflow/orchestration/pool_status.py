"""
Pool Status Monitor - Communication Interface for Claude
========================================================

This file serves as the communication point between Claude and the
delegation pool. Claude reads this regularly to check progress.

Design by User: "The agent pool can be your communication point too
as you have to read the status regularly based on timing"
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class PoolStatusMonitor:
    """Monitor delegation pool status - Claude's window into pool activity"""

    def __init__(self, status_file: str = "/tmp/pool_status.json"):
        self.status_file = Path(status_file)

    def write_status(self, status: Dict):
        """Pool writes status for Claude to read"""
        status['last_update'] = datetime.now().isoformat()

        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)

    def read_status(self) -> Dict:
        """Claude reads current pool status"""
        if not self.status_file.exists():
            return {
                'status': 'not_started',
                'message': 'Pool not yet initialized'
            }

        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to read status: {str(e)}'
            }

    def get_summary(self) -> str:
        """Get human-readable summary for Claude"""
        status = self.read_status()

        if status['status'] == 'not_started':
            return "🔴 Pool not started yet"

        if status['status'] == 'error':
            return f"❌ Error: {status['message']}"

        # Format active pool status
        queue = status.get('queue', 0)
        active = status.get('active', 0)
        completed = status.get('completed', 0)
        failed = status.get('failed', 0)
        utilization = status.get('utilization', 0) * 100

        summary = f"""
📊 Delegation Pool Status (Last update: {status.get('last_update', 'unknown')})

   Queue: {queue} tasks waiting
   Active: {active} workers busy ({utilization:.0f}% utilization)
   ✅ Completed: {completed}
   ❌ Failed: {failed}
"""

        # Show active tasks
        active_tasks = status.get('active_tasks', [])
        if active_tasks:
            summary += "\n   🔄 Active Workers:\n"
            for task in active_tasks:
                elapsed = task.get('elapsed', 0)
                estimated = task.get('estimated', 0)
                progress = (elapsed / estimated * 100) if estimated > 0 else 0
                summary += f"      {task['worker_id']}: {task['name']} ({elapsed:.1f}/{estimated}min, {progress:.0f}%)\n"

        return summary.strip()

# Global instance for easy access
monitor = PoolStatusMonitor()
