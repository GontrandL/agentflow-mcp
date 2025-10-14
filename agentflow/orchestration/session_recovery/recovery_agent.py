"""
Recovery Agent - Delegation-based session analysis

Uses FREE tier AgentFlow models to analyze session state and generate
minimal recovery manifests (<2KB) for sub-30s bootstrap.

Cost: ~$0.00-0.01 per recovery (99.9% savings vs premium models)
"""

from dotenv import load_dotenv
import json
import os
import re
import subprocess
import time
from typing import Dict, List, Optional
from pathlib import Path


class RecoveryAgent:
    """
    Prepare session recovery using AgentFlow delegation

    Analyzes:
    - Conversation history
    - Git status
    - Modified files
    - Todo list state
    - Project state

    Generates:
    - Minimal recovery manifest (<2KB)
    - Bootstrap instructions
    - Context pointers (not content!)
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize recovery agent

        Args:
            project_root: Project directory (defaults to current directory)
        """
        load_dotenv()

        # Lazy import to avoid circular dependencies
        from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

        self.orchestrator = SmartOrchestrator()
        self.project_root = project_root or os.getcwd()

    def prepare_recovery(
        self,
        session_log_path: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Prepare recovery manifest using delegation

        Args:
            session_log_path: Path to session log file
            conversation_history: Recent conversation messages
            output_path: Where to save manifest (default: session_recovery_latest.json)

        Returns:
            Recovery manifest dictionary
        """
        print("🔄 Preparing session recovery via AgentFlow delegation...")
        print("⏱️  Estimated time: 30-60 seconds")
        print("💰 Estimated cost: $0.00-0.01 (FREE tier models)")
        print("")

        start_time = time.time()

        # Build delegation task
        task = self._build_recovery_task(session_log_path, conversation_history)

        # Delegate to FREE tier models
        try:
            recovery_data = self.orchestrator.orchestrate(task)
        except Exception as e:
            print(f"⚠️  Delegation failed: {e}")
            print("📝 Generating fallback manifest...")
            recovery_data = self._generate_fallback_manifest()

        # Parse and validate
        manifest = self._parse_recovery_data(recovery_data)

        # Save manifest
        output_path = output_path or os.path.join(
            self.project_root,
            'session_recovery_latest.json'
        )
        self._save_manifest(manifest, output_path)

        elapsed = time.time() - start_time
        manifest_size = len(json.dumps(manifest))

        print(f"✅ Recovery manifest prepared in {elapsed:.1f} seconds")
        print(f"📊 Manifest size: {manifest_size:,} bytes")
        print(f"📁 Saved to: {output_path}")
        print(f"🎯 Compression ratio: {self._calculate_compression_ratio(manifest_size):.1%}")

        return manifest

    def _build_recovery_task(
        self,
        log_path: Optional[str],
        history: Optional[List[Dict]]
    ) -> str:
        """Build comprehensive recovery analysis task for delegation"""

        recent_history = self._extract_recent_history(history) if history else "No history provided"
        git_status = self._get_git_status()
        modified_files = self._get_modified_files()
        current_todos = self._get_current_todos()

        return f'''
[MISSION]: Analyze Claude Code session and generate minimal recovery manifest

## Context
Project: AgentFlow Delegation System
Location: {self.project_root}
Session Log: {log_path or 'Not provided'}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Objective
Extract ONLY critical information needed to resume session in <30 seconds.
Target manifest size: <2KB
Compression ratio target: >99%

## Input Data

### Recent Activity
{recent_history}

### Git Status
{git_status}

### Modified Files
{', '.join(modified_files[:10])}

### Current Todos
{current_todos}

## Required Output (Pure JSON)

{{
  "session_metadata": {{
    "project": "AgentFlow",
    "phase": "current development phase (1 line)",
    "timestamp": "{time.time()}",
    "context_usage_before": "estimated percentage"
  }},
  "completed_tasks": [
    "Brief completed task 1",
    "Brief completed task 2"
  ],
  "pending_tasks": [
    {{
      "task": "Next task description (max 50 chars)",
      "priority": "HIGH|MEDIUM|LOW",
      "status": "in_progress|pending",
      "context": "Essential context only (max 100 chars)"
    }}
  ],
  "active_state": {{
    "current_work": "What was being worked on (max 100 chars)",
    "last_file_modified": "path/to/file",
    "last_command_run": "command (if relevant)",
    "environment_status": "tests passing|build failing|etc"
  }},
  "critical_context": {{
    "key_decisions": ["Decision 1 (max 50 chars)", "Decision 2"],
    "blockers": ["Blocker 1 if any"],
    "next_steps": ["Step 1 (max 50 chars)", "Step 2"]
  }},
  "memory_pointers": {{
    "project_state_file": "PROJECT_STATE.md",
    "session_logs": ["{log_path or 'session.log'}"],
    "modified_files": {json.dumps(modified_files[:5])},
    "git_branch": "{self._get_current_branch()}"
  }},
  "bootstrap_instructions": [
    "cd {self.project_root}",
    "Read PROJECT_STATE.md",
    "Verify environment health",
    "Resume with [specific action]"
  ]
}}

## Rules
- Output ONLY valid JSON (no markdown, no explanations)
- Keep ALL strings under specified character limits
- Store file REFERENCES, not file CONTENTS
- Prioritize actionable info over historical details
- Total output must be <2KB

## Success Criteria
✅ Valid JSON only
✅ Total size <2KB
✅ All essential state captured
✅ No redundant information
✅ Bootstrap instructions actionable
'''

    def _extract_recent_history(self, history: List[Dict]) -> str:
        """Extract last 5-10 messages for analysis"""
        if not history:
            return "No history"

        recent = history[-10:] if len(history) > 10 else history
        return '\n'.join([
            f"- {msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}..."
            for msg in recent
        ])

    def _get_git_status(self) -> str:
        """Get current git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            return result.stdout or "Clean working tree"
        except Exception as e:
            return f"Git status unavailable: {e}"

    def _get_modified_files(self) -> List[str]:
        """List modified files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            files = [f for f in result.stdout.split('\n') if f]

            # Also check unstaged
            result2 = subprocess.run(
                ['git', 'ls-files', '--others', '--exclude-standard'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            files.extend([f for f in result2.stdout.split('\n') if f])

            return list(set(files))[:20]  # Max 20 files
        except Exception:
            return []

    def _get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            return result.stdout.strip() or "unknown"
        except Exception:
            return "unknown"

    def _get_current_todos(self) -> str:
        """Get current todo list state"""
        # TODO: Integrate with actual TodoWrite system
        return "Check TodoWrite for current tasks"

    def _parse_recovery_data(self, raw_data: str) -> Dict:
        """Parse JSON recovery data from delegation response"""
        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw_data)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to find raw JSON
            json_match = re.search(r'\{[\s\S]*\}', raw_data)
            if json_match:
                return json.loads(json_match.group(0))

            # Try parsing entire response
            return json.loads(raw_data)

        except Exception as e:
            print(f"⚠️  JSON parsing failed: {e}")
            return self._generate_fallback_manifest()

    def _generate_fallback_manifest(self) -> Dict:
        """Generate basic fallback manifest if delegation fails"""
        return {
            "session_metadata": {
                "project": "AgentFlow",
                "phase": "Unknown (fallback manifest)",
                "timestamp": time.time(),
                "context_usage_before": "unknown"
            },
            "completed_tasks": [],
            "pending_tasks": [{
                "task": "Review session state manually",
                "priority": "HIGH",
                "status": "pending",
                "context": "Delegation failed - manual review needed"
            }],
            "active_state": {
                "current_work": "Unknown",
                "last_file_modified": "unknown",
                "environment_status": "unknown"
            },
            "critical_context": {
                "key_decisions": ["Manual review required"],
                "blockers": ["Recovery delegation failed"],
                "next_steps": ["Check logs", "Review git status"]
            },
            "memory_pointers": {
                "project_state_file": "PROJECT_STATE.md",
                "session_logs": [],
                "modified_files": self._get_modified_files(),
                "git_branch": self._get_current_branch()
            },
            "bootstrap_instructions": [
                f"cd {self.project_root}",
                "Read PROJECT_STATE.md",
                "Check git status",
                "Resume work"
            ]
        }

    def _save_manifest(self, manifest: Dict, output_path: str):
        """Save recovery manifest to file"""
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def _calculate_compression_ratio(self, manifest_size: int) -> float:
        """Calculate context compression ratio"""
        # Assume original context is ~200KB
        original_size = 200000 * 4  # ~200K tokens * 4 chars/token
        return 1 - (manifest_size / original_size)


# Example usage
if __name__ == "__main__":
    agent = RecoveryAgent()
    manifest = agent.prepare_recovery(
        session_log_path="./session_2025-10-14.log",
        conversation_history=[
            {"role": "user", "content": "Fix the test errors"},
            {"role": "assistant", "content": "I'll fix the import errors..."}
        ]
    )
    print(json.dumps(manifest, indent=2))
