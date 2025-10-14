#!/usr/bin/env python3
"""
Session Tag Parser - Extract tagged data from previous sessions

Usage:
    python3 parse_session_tags.py <session_log_file>

Output: Lightweight JSON with only tagged data (< 2KB target)

Tags supported:
    [SESSION_STATE] ... [/SESSION_STATE]
    [PENDING_TASKS] ... [/PENDING_TASKS]
    [NEXT_ACTIONS] ... [/NEXT_ACTIONS]
    [DECISIONS] ... [/DECISIONS]
    [BLOCKED] ... [/BLOCKED]
    [CONTEXT_MINIMAL_ARCH] ... [/CONTEXT_MINIMAL_ARCH]
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class SessionTagParser:
    """Parse session logs and extract tagged data for context-minimal recovery"""

    SUPPORTED_TAGS = [
        "SESSION_STATE",
        "PENDING_TASKS",
        "NEXT_ACTIONS",
        "DECISIONS",
        "BLOCKED",
        "CONTEXT_MINIMAL_ARCH",
        "KEY_FILES",
        "COST_SAVINGS",
    ]

    def __init__(self, session_file: str):
        self.session_file = Path(session_file)
        self.parsed_data = {}

    def parse(self) -> Dict[str, Any]:
        """Parse session file and extract all tagged sections"""
        if not self.session_file.exists():
            return {"error": "Session file not found"}

        content = self.session_file.read_text()

        for tag in self.SUPPORTED_TAGS:
            pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

            if matches:
                # Take the LAST occurrence (most recent)
                self.parsed_data[tag.lower()] = self._clean_content(matches[-1])

        # Add metadata
        self.parsed_data['_metadata'] = {
            'source_file': str(self.session_file),
            'parsed_at': datetime.now().isoformat(),
            'byte_size': len(json.dumps(self.parsed_data))
        }

        return self.parsed_data

    def _clean_content(self, content: str) -> str:
        """Clean and trim content"""
        return content.strip()

    def save_json(self, output_file: str = "session_recovery.json"):
        """Save parsed data to JSON"""
        output_path = Path(output_file)
        output_path.write_text(json.dumps(self.parsed_data, indent=2))
        print(f"✅ Saved to: {output_path}")
        print(f"📏 Size: {len(json.dumps(self.parsed_data))} bytes")

    def print_summary(self):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("📋 SESSION RECOVERY DATA")
        print("="*60)

        for tag, content in self.parsed_data.items():
            if tag == '_metadata':
                continue
            print(f"\n[{tag.upper()}]")
            print(content)

        print("\n" + "="*60)
        print(f"📊 Metadata: {self.parsed_data.get('_metadata', {})}")
        print("="*60)


def parse_claude_code_session(session_dir: str = ".") -> Dict[str, Any]:
    """
    Parse the most recent Claude Code session log

    Claude Code stores logs in ~/.local/share/claude-code/
    This looks for SESSION_STATE tags in recent files
    """
    # Common locations for session data
    possible_locations = [
        Path.home() / ".local/share/claude-code/",
        Path(session_dir),
        Path("/tmp/"),
    ]

    # Look for files with session tags
    for location in possible_locations:
        if not location.exists():
            continue

        # Search for log files or markdown files
        for pattern in ["*.log", "*.md", "*.txt"]:
            for file in location.glob(pattern):
                try:
                    content = file.read_text()
                    if "[SESSION_STATE]" in content or "[PENDING_TASKS]" in content:
                        print(f"🔍 Found tagged session: {file}")
                        parser = SessionTagParser(str(file))
                        return parser.parse()
                except Exception as e:
                    continue

    return {"error": "No tagged session found"}


def create_example_tagged_session():
    """Create an example session with tags for demonstration"""
    example = """
# Claude Code Session - 2025-10-13

[SESSION_STATE]
- project: AutoCoder-Next
- phase: Phase 2 - Context Management Implementation
- last_task: Delegated 8 workers for waterfall system
- context_usage: 45% (below 80% threshold ✓)
- cost_today: $0.08
[/SESSION_STATE]

[PENDING_TASKS]
Worker 1: escalation_engine.py (RUNNING)
Worker 2: interactive_orchestrator.py (RUNNING)
Worker 3: quality_evaluator.py (RUNNING)
Worker 4: mcp_feedback_receiver.py (RUNNING)
Worker 5: dashboard.py (RUNNING)
Worker 6: context_injector.py (RUNNING)
Worker 7: parallel_executor.py (RUNNING)
Worker 8: waterfall_orchestrator.py (RUNNING)
[/PENDING_TASKS]

[NEXT_ACTIONS]
1. Check all worker completion status (use BashOutput tool)
2. Validate generated Python files (syntax, types, docstrings)
3. Run integration tests
4. Update PROJECT_STATE.md
5. Commit changes if all tests pass
[/NEXT_ACTIONS]

[DECISIONS]
- Adopted Hybrid Memory: JSON + Vector + Graph (consensus from 4 AIs)
- Context trigger: 80% proactive offload (validated by Perplexity benchmarks)
- Recovery target: < 30s (ISC pattern from Gemini/ChatGPT)
- Self-evolution: Kaizen Loop + Q-learning
[/DECISIONS]

[CONTEXT_MINIMAL_ARCH]
Phase 1: Core Memory System (Week 1-2)
  - ChromaDB (vector) + ArangoDB (graph) + SQLite (state)
  - Target: < 30s recovery time

Phase 2: Context Manager (Week 2-3) [CURRENT]
  - 4-tier pressure system (Green/Yellow/Orange/Red)
  - 80% proactive offload trigger
  - Predictive lookahead (2-3 operations)

Phase 3: Stateless Ops (Week 3-4)
  - ISC pattern (checkpoint after each operation)
  - Target: 1-12s delta recovery

Phase 4: Self-Evolution (Week 4-6)
  - Kaizen Loop + Q-learning
  - Target: 10%+ efficiency gain
[/CONTEXT_MINIMAL_ARCH]

[KEY_FILES]
- FINAL_RESEARCH_SYNTHESIS.md (845 lines, 4 AI perspectives)
- agentflow/orchestration/smart_orchestrator.py (working, 99.67% savings)
- run_delegation_pool.py (8 workers parallel)
[/KEY_FILES]

[COST_SAVINGS]
- Today: $0.08 vs $18 (99.6% savings)
- Total project: $0.34 vs $120+ (99.7% savings)
- Delegation strategy: DeepSeek V3 ($0.14/M) vs Claude ($3/M)
[/COST_SAVINGS]

Some regular session content here...
More discussion, code, etc...

[BLOCKED]
None currently
[/BLOCKED]
"""

    example_file = Path("/tmp/example_tagged_session.md")
    example_file.write_text(example)
    print(f"📝 Created example: {example_file}")
    return str(example_file)


if __name__ == "__main__":
    print("🏷️  SESSION TAG PARSER")
    print("=" * 60)

    if len(sys.argv) > 1:
        # Parse specific file
        session_file = sys.argv[1]
        parser = SessionTagParser(session_file)
        data = parser.parse()
        parser.print_summary()
        parser.save_json()
    else:
        # Create example and parse it
        print("No session file provided. Creating example...")
        example_file = create_example_tagged_session()

        print("\n" + "="*60)
        print("Parsing example...")
        print("="*60)

        parser = SessionTagParser(example_file)
        data = parser.parse()
        parser.print_summary()
        parser.save_json()

        print("\n" + "="*60)
        print("💡 USAGE:")
        print("="*60)
        print("1. Tag your sessions with [SESSION_STATE] ... [/SESSION_STATE]")
        print("2. Run: python3 parse_session_tags.py <session_log>")
        print("3. Get lightweight JSON (< 2KB) for next session bootstrap")
        print("\nSupported tags:", ", ".join(SessionTagParser.SUPPORTED_TAGS))
