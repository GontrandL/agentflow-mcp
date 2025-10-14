#!/usr/bin/env python3
"""
AgentFlow MCP Server Creation - Attempt 4

CHANGES FROM PREVIOUS ATTEMPTS:
1. Uses new PatternReplicationOrchestrator (specialized for pattern tasks)
2. ContextGenerator fix: preserve_system_messages flag prevents pattern compression
3. Explicit anti-tutorial prompts
4. Code extraction post-processing if LLM returns tutorial
5. Architectural validation instead of quality scoring

EXPECTED:
- ✅ Runnable Python code (not tutorial)
- ✅ Follows apc_mcp_server.py pattern
- ✅ Has 4 delegation tools
- ✅ stdio communication
- ✅ async handlers

PREVIOUS ATTEMPTS:
- Attempt 1: No context → socket server (wrong)
- Attempt 2: APCAgentFlowBridge → pattern compressed out → tutorial
- Attempt 3: Inline pattern → still tutorial (33% validation)

THIS ATTEMPT:
- Pattern preserved by ContextGenerator
- Pattern-specific prompts
- Code extraction fallback
- Should work!

Date: 2025-10-14
Status: FIXING THE DELEGATION SYSTEM
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

from agentflow.orchestration.pattern_replication_orchestrator import replicate_pattern

print("=" * 80)
print("AGENTFLOW MCP SERVER CREATION - ATTEMPT 4")
print("Using PatternReplicationOrchestrator (NEW)")
print("=" * 80)
print()

# Read the pattern file
print("📖 Reading pattern file: agentflow/mcp/apc_mcp_server.py")
with open('agentflow/mcp/apc_mcp_server.py') as f:
    pattern_code = f.read()

print(f"   Pattern length: {len(pattern_code)} characters")
print(f"   Pattern lines: {len(pattern_code.splitlines())}")
print()

# Define replacements
replacements = {
    # Core components
    "ContextGenerator": "SmartOrchestrator",
    "HybridOrchestrator": "DelegationPool",
    "APCAgentFlowBridge": "AgentFlowDelegationSystem",

    # Tool names
    "prepare_context": "delegate_task",
    "validate_output": "delegate_parallel",
    "execute_workflow": "check_delegation_status",
    "get_metrics": "list_models",

    # Classes/methods
    "compressed_context": "delegation_result",
    "context_preparation": "task_delegation",
    "compression_ratio": "cost_estimate",

    # Server name
    "APCMCPServer": "AgentFlowMCPServer",
    "apc": "agentflow",
    "APC": "AgentFlow",
}

print("🔄 Replacements to make:")
for old, new in replacements.items():
    print(f"   {old:30s} → {new}")
print()

# Task description
task_description = """
You are creating an AgentFlow MCP Server following the exact pattern of apc_mcp_server.py.

AgentFlow MCP Server provides 4 delegation tools:
1. delegate_task - Delegate single task to cost-effective model
2. delegate_parallel - Spawn 3-8 parallel workers
3. check_delegation_status - Monitor task progress
4. list_models - Show available models and pricing

Keep the EXACT SAME structure as APC MCP server:
- stdio communication (NOT socket)
- async def tool handlers
- MCP tool schemas with inputSchema
- structlog logging
- Same error handling patterns
"""

# Additional context
additional_context = """
CRITICAL REQUIREMENTS:
1. Use SmartOrchestrator for delegation (not ContextGenerator)
2. Use DelegationPool for parallel tasks (not HybridOrchestrator)
3. Keep stdio communication pattern EXACTLY
4. Keep all async handlers
5. Keep same logging structure
6. Keep same error handling

FILE STRUCTURE:
#!/usr/bin/env python3
imports...
class AgentFlowMCPServer:
    def __init__(self):
        # Initialize SmartOrchestrator
        # Initialize DelegationPool
        # Setup logging

    async def tool_delegate_task(self, params):
        # Delegate single task

    async def tool_delegate_parallel(self, params):
        # Delegate to parallel pool

    async def tool_check_delegation_status(self, params):
        # Check status

    async def tool_list_models(self, params):
        # List models

async def main():
    # stdio loop (like APC)

if __name__ == "__main__":
    asyncio.run(main())
"""

# Output file
output_file = 'agentflow/mcp/agentflow_mcp_server.py'

print(f"🎯 Output file: {output_file}")
print()

print("🚀 Starting pattern replication with PatternReplicationOrchestrator...")
print("   This will:")
print("   1. Build pattern-specific prompt with anti-tutorial safeguards")
print("   2. Delegate to DeepSeek V3 (cost-effective)")
print("   3. Extract code if tutorial format returned")
print("   4. Validate architectural correctness")
print("   5. Save to output file")
print()

# Replicate the pattern
result = replicate_pattern(
    pattern_code=pattern_code,
    replacements=replacements,
    task_description=task_description,
    output_file=output_file,
    additional_context=additional_context,
    provider="deepseek"
)

print()
print("=" * 80)
print("RESULTS")
print("=" * 80)
print()

print(f"✅ Output saved to: {result['output_file']}")
print(f"📝 Code extracted from tutorial: {result['extracted']}")
print(f"📊 Pattern preserved: {result['pattern_preserved']}")
print()

print("VALIDATION RESULTS:")
validation = result['validation']
for check, value in validation.items():
    if check == 'replacements_applied':
        print(f"  Replacements:")
        for repl, applied in value.items():
            status = "✅" if applied else "❌"
            print(f"    {status} {repl}")
    elif check == 'score':
        print(f"  Overall Score: {value}/100")
    elif check == 'pattern_preserved':
        status = "✅" if value else "❌"
        print(f"  {status} Pattern Preserved: {value}")
    else:
        status = "✅" if value else "❌"
        print(f"  {status} {check}: {value}")

print()

# Show file stats
import os
file_size = os.path.getsize(output_file)
with open(output_file) as f:
    lines = f.readlines()
    line_count = len(lines)

print(f"📄 Generated file stats:")
print(f"   Size: {file_size / 1024:.1f} KB")
print(f"   Lines: {line_count}")
print()

# Show first 50 lines
print("📄 First 50 lines of generated code:")
print("-" * 80)
for i, line in enumerate(lines[:50]):
    print(f"{i+1:3d}: {line}", end='')

print()
print("=" * 80)
print("ATTEMPT 4 COMPLETE")
print()

if result['pattern_preserved']:
    print("✅ SUCCESS: Pattern replication successful!")
    print("   Validation score: {}/100".format(validation['score']))
    print("   Next step: Test the MCP server")
else:
    print("⚠️  WARNING: Pattern may not be fully preserved")
    print("   Validation score: {}/100".format(validation['score']))
    print("   Review the generated code manually")

print()
print("To test:")
print("  python3 agentflow/mcp/agentflow_mcp_server.py")
print()
