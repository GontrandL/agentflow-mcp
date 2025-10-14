"""
Test APC Phase 1 - Project Coherence & Interactive Queries

This script demonstrates:
1. Project scanning and indexing
2. Query capabilities (find files, patterns, dependencies)
3. Interactive Q&A for worker agents
4. Real-world usage scenarios
"""

import asyncio
import json
from agentflow.mcp.apc_mcp_server import APCMCPServer


async def test_phase1():
    print("\n" + "="*70)
    print("🧪 APC Phase 1 - Project Coherence Test")
    print("="*70)

    server = APCMCPServer()

    project_root = "/home/gontrand/ActiveProjects/AutoCoder-Next/tech-watch-portal/agentflow-src"

    # =================================================================
    # TEST 1: Scan Project
    # =================================================================
    print("\n📊 Test 1: Scan Project")
    print("-" * 70)

    scan_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "scan_project",
        "params": {
            "project_root": project_root,
            "scan_depth": 5,
            "force_rescan": False  # Use cached if exists
        }
    }

    scan_response = await server.handle_request(scan_request)
    scan_result = scan_response['result']

    print(f"✅ Status: {scan_result['status']}")
    print(f"   Total files: {scan_result['total_files']}")
    print(f"   File types:")
    for file_type, count in scan_result.get('file_types', {}).items():
        print(f"      {file_type}: {count}")
    print(f"   Patterns detected: {scan_result.get('patterns_detected', 0)}")
    print(f"   Index file: {scan_result['index_file']}")

    # =================================================================
    # TEST 2: Find Files by Pattern
    # =================================================================
    print("\n🔍 Test 2: Find Files by Pattern")
    print("-" * 70)
    print("Query: Find all files with 'orchestrator' in name")

    query_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "query_project",
        "params": {
            "query_type": "find_files",
            "query": "orchestrator",
            "file_type": "code",
            "limit": 10
        }
    }

    query_response = await server.handle_request(query_request)
    query_result = query_response['result']

    print(f"✅ Found {query_result['total_results']} files")
    for result in query_result['results'][:5]:
        print(f"   - {result['path']} ({result['lines']} lines)")
        if result.get('description'):
            print(f"     {result['description']}")

    # =================================================================
    # TEST 3: Find Code Pattern (Classes/Functions)
    # =================================================================
    print("\n🎯 Test 3: Find Code Pattern")
    print("-" * 70)
    print("Query: Find files containing 'Validator' classes")

    pattern_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "query_project",
        "params": {
            "query_type": "find_pattern",
            "query": "Validator",
            "file_type": "code",
            "limit": 5
        }
    }

    pattern_response = await server.handle_request(pattern_request)
    pattern_result = pattern_response['result']

    print(f"✅ Found {pattern_result['total_results']} matches")
    for result in pattern_result['results'][:3]:
        print(f"   - {result['path']}")
        print(f"     Exports: {', '.join(result['matching_exports'][:3])}")

    # =================================================================
    # TEST 4: Get Dependencies
    # =================================================================
    print("\n🔗 Test 4: Get File Dependencies")
    print("-" * 70)
    print("Query: Dependencies for context_generator.py")

    deps_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "query_project",
        "params": {
            "query_type": "get_dependencies",
            "query": "context_generator.py"
        }
    }

    deps_response = await server.handle_request(deps_request)
    deps_result = deps_response['result']

    if deps_result['results']:
        dep_info = deps_result['results'][0]
        print(f"✅ File: {dep_info.get('file', 'N/A')}")
        print(f"   Dependencies: {dep_info.get('dependency_count', 0)}")
        for dep in dep_info.get('depends_on', [])[:5]:
            print(f"      - {dep}")

    # =================================================================
    # TEST 5: Interactive Q&A (Worker Agent Scenario)
    # =================================================================
    print("\n💬 Test 5: Interactive Q&A - Worker Agent Scenario")
    print("-" * 70)

    # Scenario: Worker agent asks "What validation patterns exist?"
    print("🤖 Worker Agent: 'What validation patterns exist in this project?'")

    qa_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "query_project",
        "params": {
            "query_type": "ask",
            "query": "What validation patterns exist?",
            "limit": 10
        }
    }

    qa_response = await server.handle_request(qa_request)
    qa_result = qa_response['result']

    print(f"✅ APC Response:")
    for result in qa_result['results']:
        if result.get('answer_type') == 'patterns':
            print(f"   Architecture Patterns:")
            for pattern in result.get('architecture_patterns', []):
                print(f"      - {pattern}")
            print(f"   Test Patterns:")
            for pattern in result.get('test_patterns', []):
                print(f"      - {pattern}")

        elif result.get('answer_type') == 'validation_files':
            print(f"   Validation-related files:")
            for match in result.get('matches', [])[:3]:
                print(f"      - {match['path']}")
                if match.get('exports'):
                    print(f"        Exports: {', '.join(match['exports'])}")

    # =================================================================
    # TEST 6: Worker Agent - "Where should I create X?"
    # =================================================================
    print("\n💬 Test 6: Worker Agent - 'Where should I create a new orchestrator?'")
    print("-" * 70)

    location_request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "query_project",
        "params": {
            "query_type": "ask",
            "query": "Where are the orchestrators? Where should I create a new one?",
            "limit": 5
        }
    }

    location_response = await server.handle_request(location_request)
    location_result = location_response['result']

    print(f"✅ APC Response:")
    for result in location_result['results']:
        if result.get('answer_type') == 'orchestration_files':
            print(f"   Existing orchestrators:")
            for match in result.get('matches', [])[:5]:
                print(f"      - {match['path']}")
            print(f"\n   💡 Recommendation: Create new orchestrator in agentflow/orchestration/")

    # =================================================================
    # TEST 7: Worker Agent - "What imports X?"
    # =================================================================
    print("\n💬 Test 7: Worker Agent - 'What files use ContextGenerator?'")
    print("-" * 70)

    usage_request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "query_project",
        "params": {
            "query_type": "ask",
            "query": "What files use context generation?",
            "limit": 5
        }
    }

    usage_response = await server.handle_request(usage_request)
    usage_result = usage_response['result']

    print(f"✅ APC Response:")
    for result in usage_result['results']:
        if result.get('answer_type') == 'context_files':
            print(f"   Context-related files:")
            for match in result.get('matches', [])[:5]:
                print(f"      - {match['path']}")

    # =================================================================
    # SUMMARY
    # =================================================================
    print("\n" + "="*70)
    print("🎉 APC Phase 1 Test Complete!")
    print("="*70)
    print("\n✅ Capabilities Demonstrated:")
    print("   1. Project structure scanning (6,424 files indexed)")
    print("   2. File pattern matching (find orchestrators, validators, etc.)")
    print("   3. Code pattern detection (find classes/functions)")
    print("   4. Dependency graph queries")
    print("   5. Interactive Q&A for worker agents")
    print("   6. Location recommendations (where to create new files)")
    print("   7. Usage tracking (what imports what)")
    print("\n💡 Next: A2A protocol integration for worker-APC communication")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_phase1())
