"""
Test A2A Protocol - Worker-APC Communication

This test demonstrates:
1. A2A protocol message passing
2. Worker agent querying APC
3. APC responding via A2A (no MCP)
4. Context-aware recommendations
5. Multiple workers communicating simultaneously
"""

import asyncio
from agentflow.mcp.apc_mcp_server import APCMCPServer
from agentflow.integration.a2a_protocol import (
    A2AMessage,
    MessageType,
    AgentCapability,
    get_message_queue,
    query_apc
)
from agentflow.integration.apc_a2a_adapter import (
    APCA2AAdapter,
    ask_apc,
    find_files_in_project
)


async def simulate_worker_agent(worker_id: str, task: str):
    """
    Simulate a worker agent asking APC questions.

    Args:
        worker_id: Worker ID
        task: Task the worker is working on
    """
    print(f"\n{'='*70}")
    print(f"🤖 Worker {worker_id}")
    print(f"   Task: {task}")
    print(f"{'='*70}")

    context = {"task": task, "worker_id": worker_id}

    # ==================================================================
    # Scenario 1: Worker asks "What validation patterns exist?"
    # ==================================================================
    print(f"\n💬 {worker_id}: 'What validation patterns exist?'")

    response = await ask_apc(
        worker_id=worker_id,
        question="What validation patterns exist?",
        context=context,
        timeout=10.0
    )

    if 'results' in response:
        print(f"✅ APC Response:")
        for result in response['results'][:2]:
            if result.get('answer_type') == 'patterns':
                print(f"   Architecture Patterns: {result.get('architecture_patterns', [])}")
                print(f"   Test Patterns: {result.get('test_patterns', [])}")
            elif result.get('answer_type') == 'validation_files':
                print(f"   Validation Files:")
                for match in result.get('matches', [])[:2]:
                    print(f"      - {match['path']}")

        if 'recommendations' in response:
            print(f"\n   💡 APC Recommendations:")
            for rec in response['recommendations']:
                print(f"      - {rec}")

    # ==================================================================
    # Scenario 2: Worker asks "Where should I create X?"
    # ==================================================================
    print(f"\n💬 {worker_id}: 'Where should I create a new validator module?'")

    response = await ask_apc(
        worker_id=worker_id,
        question="Where are the validators?",
        context=context,
        timeout=10.0
    )

    if 'results' in response:
        print(f"✅ APC Response:")
        for result in response['results'][:1]:
            if result.get('answer_type') == 'validation_files':
                print(f"   Existing validators:")
                for match in result.get('matches', [])[:3]:
                    print(f"      - {match['path']}")

        if 'recommendations' in response:
            print(f"\n   💡 APC Recommendations:")
            for rec in response['recommendations']:
                print(f"      - {rec}")

    # ==================================================================
    # Scenario 3: Worker finds files by pattern
    # ==================================================================
    print(f"\n💬 {worker_id}: 'Find orchestrator files'")

    response = await find_files_in_project(
        worker_id=worker_id,
        pattern="orchestrator",
        file_type="code",
        limit=5,
        context=context
    )

    if 'results' in response:
        print(f"✅ APC Found {response.get('total_results', 0)} files:")
        for result in response['results'][:3]:
            print(f"      - {result['path']} ({result['lines']} lines)")


async def test_a2a_protocol():
    """Test A2A protocol with multiple workers."""
    print("\n" + "="*70)
    print("🧪 A2A Protocol Test - Worker-APC Communication")
    print("="*70)

    # ==================================================================
    # Setup: Initialize APC and A2A System
    # ==================================================================
    print("\n📋 Setup: Initializing APC and A2A System")
    print("-" * 70)

    # 1. Create APC MCP Server
    apc_server = APCMCPServer()
    print("✅ APC MCP Server initialized")

    # 2. Scan project first (so APC knows the structure)
    project_root = "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src"

    scan_result = await apc_server._scan_project({
        "project_root": project_root,
        "scan_depth": 5,
        "force_rescan": False
    })
    print(f"✅ Project scanned: {scan_result['total_files']} files indexed")

    # 3. Create A2A adapter and register APC
    apc_adapter = APCA2AAdapter(apc_server)
    apc_adapter.register()
    print(f"✅ APC registered in A2A system with capabilities: project_query, context_compression, validation")

    # 4. Start APC listener in background
    listener_task = asyncio.create_task(apc_adapter.start_listener())
    print(f"✅ APC listener started (background task)")

    # Give listener a moment to start
    await asyncio.sleep(0.1)

    # ==================================================================
    # Test 1: Single Worker Query
    # ==================================================================
    print("\n" + "="*70)
    print("📋 Test 1: Single Worker Query")
    print("="*70)

    await simulate_worker_agent(
        worker_id="worker-001",
        task="Creating a new validation module for output quality checking"
    )

    # ==================================================================
    # Test 2: Multiple Workers in Parallel
    # ==================================================================
    print("\n" + "="*70)
    print("📋 Test 2: Multiple Workers in Parallel")
    print("="*70)

    # Spawn 3 workers simultaneously
    worker_tasks = [
        simulate_worker_agent(
            "worker-002",
            "Creating orchestrator for parallel task execution"
        ),
        simulate_worker_agent(
            "worker-003",
            "Writing tests for context compression module"
        ),
        simulate_worker_agent(
            "worker-004",
            "Implementing validator for code quality checks"
        )
    ]

    # Wait for all workers to complete
    await asyncio.gather(*worker_tasks)

    # ==================================================================
    # Test 3: Check A2A Message Queue State
    # ==================================================================
    print("\n" + "="*70)
    print("📋 Test 3: A2A Message Queue State")
    print("="*70)

    queue = get_message_queue()
    all_agents = queue.get_all_agents()

    print(f"\n✅ Registered Agents: {len(all_agents)}")
    for agent_info in all_agents:
        print(f"   - {agent_info['agent_id']} ({agent_info['agent_type']})")
        print(f"     Capabilities: {', '.join(agent_info['capabilities'])}")

    print(f"\n✅ Message History: {len(queue.message_history)} messages")
    print(f"   (Workers sent queries, APC sent responses)")

    # ==================================================================
    # Summary
    # ==================================================================
    print("\n" + "="*70)
    print("🎉 A2A Protocol Test Complete!")
    print("="*70)

    print("\n✅ Capabilities Demonstrated:")
    print("   1. Worker → APC: Natural language questions via A2A")
    print("   2. APC → Worker: Responses with project knowledge")
    print("   3. Context-aware recommendations (based on worker task)")
    print("   4. Multiple workers in parallel (no MCP overhead)")
    print("   5. Direct agent-to-agent messaging (async)")

    print("\n💡 Benefits of A2A:")
    print("   - Faster: No MCP protocol overhead")
    print("   - Contextual: Worker sends current task with query")
    print("   - Scalable: Multiple workers simultaneously")
    print("   - Bidirectional: APC can ask clarifications (future)")

    print("\n🚀 A2A is the foundation for Phase 2!")
    print("   - Session history via A2A")
    print("   - Task tracking via A2A")
    print("   - Agent coordination via A2A")
    print("="*70 + "\n")

    # Cleanup
    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(test_a2a_protocol())
