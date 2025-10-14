#!/usr/bin/env python3
"""
Comprehensive Test Suite for Pattern Replication Fixes

Tests the delegation system fixes implemented 2025-10-14:
1. ContextGenerator preserve_system_messages flag
2. PatternReplicationOrchestrator
3. APCAgentFlowBridge pattern preservation
4. Generated AgentFlow MCP server structure

Date: 2025-10-14
Status: Validates critical fixes for pattern replication
"""

import os
import sys
import pytest
import inspect
from typing import Dict, List

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestContextGeneratorPatternPreservation:
    """Test ContextGenerator preserve_system_messages flag"""

    def test_context_generator_imports(self):
        """Verify ContextGenerator can be imported"""
        from agentflow.core.context_generator import ContextGenerator, CompressedContext
        assert ContextGenerator is not None
        assert CompressedContext is not None

    def test_preserve_system_messages_parameter_exists(self):
        """Verify preserve_system_messages parameter exists in generate_context"""
        from agentflow.core.context_generator import ContextGenerator

        sig = inspect.signature(ContextGenerator.generate_context)
        params = sig.parameters

        assert 'preserve_system_messages' in params, \
            "preserve_system_messages parameter missing from generate_context()"

        # Verify default value is False
        param = params['preserve_system_messages']
        assert param.default is False, \
            "preserve_system_messages should default to False"

    def test_pattern_preservation_enabled(self):
        """Test that system messages are preserved when flag is True"""
        from agentflow.core.context_generator import ContextGenerator

        cg = ContextGenerator(target_tokens=8000)

        # Create conversation with system message containing pattern
        conversation_history = [
            {
                "role": "system",
                "content": "```python\nclass ExamplePattern:\n    def __init__(self):\n        self.value = 42\n    \n    def process(self):\n        return self.value * 2\n```"
            },
            {
                "role": "user",
                "content": "Create a similar class called NewPattern"
            }
        ]

        # Generate context WITH preservation
        compressed = cg.generate_context(
            conversation_history=conversation_history,
            current_task="Create similar class",
            namespace="test",
            preserve_system_messages=True
        )

        # Check that code_snippets contains preserved content
        has_preserved = any('ExamplePattern' in str(snippet.get('code', ''))
                           for snippet in compressed.code_snippets)

        assert has_preserved, \
            "Pattern code should be preserved in code_snippets when preserve_system_messages=True"

        # Verify it's marked as reference pattern
        has_reference_marker = any('REFERENCE_PATTERN' in str(snippet.get('context', ''))
                                   for snippet in compressed.code_snippets)

        assert has_reference_marker, \
            "Preserved patterns should be marked with REFERENCE_PATTERN context"

    def test_pattern_compression_without_flag(self):
        """Test that patterns ARE compressed when flag is False"""
        from agentflow.core.context_generator import ContextGenerator

        cg = ContextGenerator(target_tokens=8000)

        conversation_history = [
            {
                "role": "system",
                "content": "```python\nclass ExamplePattern:\n    def __init__(self):\n        pass\n```"
            },
            {
                "role": "user",
                "content": "Create a similar class"
            }
        ]

        # Generate context WITHOUT preservation (default behavior)
        compressed = cg.generate_context(
            conversation_history=conversation_history,
            current_task="Create similar class",
            namespace="test",
            preserve_system_messages=False
        )

        # Should complete without error
        assert compressed is not None
        assert hasattr(compressed, 'code_snippets')


class TestAPCAgentFlowBridge:
    """Test APCAgentFlowBridge pattern preservation integration"""

    def test_bridge_imports(self):
        """Verify APCAgentFlowBridge can be imported"""
        from agentflow.integration.apc_agentflow_bridge import APCAgentFlowBridge
        assert APCAgentFlowBridge is not None

    def test_bridge_initialization(self):
        """Test bridge initializes correctly"""
        from agentflow.integration.apc_agentflow_bridge import APCAgentFlowBridge

        bridge = APCAgentFlowBridge()
        assert bridge is not None
        assert hasattr(bridge, 'context_generator')
        assert hasattr(bridge, 'hybrid_orchestrator')

    def test_preserve_system_messages_parameter_in_execute(self):
        """Verify execute() accepts preserve_system_messages parameter"""
        from agentflow.integration.apc_agentflow_bridge import APCAgentFlowBridge

        sig = inspect.signature(APCAgentFlowBridge.execute)
        params = sig.parameters

        assert 'preserve_system_messages' in params, \
            "preserve_system_messages parameter missing from execute()"

        # Verify default value is False
        param = params['preserve_system_messages']
        assert param.default is False, \
            "preserve_system_messages should default to False"


class TestPatternReplicationOrchestrator:
    """Test PatternReplicationOrchestrator implementation"""

    def test_orchestrator_imports(self):
        """Verify PatternReplicationOrchestrator can be imported"""
        from agentflow.orchestration.pattern_replication_orchestrator import (
            PatternReplicationOrchestrator,
            replicate_pattern
        )
        assert PatternReplicationOrchestrator is not None
        assert replicate_pattern is not None

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with default settings"""
        from agentflow.orchestration.pattern_replication_orchestrator import PatternReplicationOrchestrator

        orchestrator = PatternReplicationOrchestrator(provider="deepseek")
        assert orchestrator is not None
        assert hasattr(orchestrator, 'provider')
        assert orchestrator.provider == "deepseek"

    def test_required_methods_exist(self):
        """Verify all required methods are present"""
        from agentflow.orchestration.pattern_replication_orchestrator import PatternReplicationOrchestrator

        orchestrator = PatternReplicationOrchestrator()

        required_methods = [
            'replicate_pattern',
            '_build_pattern_replication_prompt',
            '_is_tutorial_format',
            '_extract_code_from_tutorial',
            '_validate_pattern_replication'
        ]

        for method in required_methods:
            assert hasattr(orchestrator, method), \
                f"PatternReplicationOrchestrator missing required method: {method}"

    def test_tutorial_format_detection(self):
        """Test tutorial format detection logic"""
        from agentflow.orchestration.pattern_replication_orchestrator import PatternReplicationOrchestrator

        orchestrator = PatternReplicationOrchestrator()

        # Tutorial format examples (should be detected)
        tutorial1 = "### Implementation\n\nHere's the code:\n\n```python\nprint('hello')\n```"
        tutorial3 = "Here is the implementation:\n\n```python\nclass Foo:\n    pass\n```"

        assert orchestrator._is_tutorial_format(tutorial1), \
            "Should detect tutorial with markdown headers and code fences"
        assert orchestrator._is_tutorial_format(tutorial3), \
            "Should detect tutorial with explanatory text and code fences"

        # Code format examples (should NOT be detected as tutorial)
        code1 = "#!/usr/bin/env python3\nimport os\n\nclass Foo:\n    pass"
        code2 = "import sys\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()"

        assert not orchestrator._is_tutorial_format(code1), \
            "Pure code with shebang should not be detected as tutorial"
        assert not orchestrator._is_tutorial_format(code2), \
            "Pure code should not be detected as tutorial"

    def test_code_extraction_from_tutorial(self):
        """Test code extraction from tutorial format"""
        from agentflow.orchestration.pattern_replication_orchestrator import PatternReplicationOrchestrator

        orchestrator = PatternReplicationOrchestrator()

        tutorial = """### Implementation

Here's the complete implementation:

```python
#!/usr/bin/env python3
import os

def main():
    print("Hello")

if __name__ == "__main__":
    main()
```

This implements the required functionality."""

        extracted = orchestrator._extract_code_from_tutorial(tutorial)

        # Verify code was extracted
        assert extracted.strip().startswith('#!/usr/bin/env python3'), \
            "Should extract shebang from code block"
        assert 'def main():' in extracted, \
            "Should extract function definition"
        assert '```' not in extracted, \
            "Should remove markdown fences"
        assert '###' not in extracted, \
            "Should remove markdown headers"
        assert 'Here\'s the complete' not in extracted, \
            "Should remove explanatory text"

    def test_validation_checks_structure(self):
        """Test that validation checks key structural elements"""
        from agentflow.orchestration.pattern_replication_orchestrator import PatternReplicationOrchestrator

        orchestrator = PatternReplicationOrchestrator()

        pattern = """#!/usr/bin/env python3
import os

class OldClass:
    def old_method(self):
        pass
"""

        replacements = {
            "OldClass": "NewClass",
            "old_method": "new_method"
        }

        generated = """#!/usr/bin/env python3
import os

class NewClass:
    def new_method(self):
        pass
"""

        validation = orchestrator._validate_pattern_replication(
            generated,
            pattern,
            replacements
        )

        # Verify validation structure (flattened dict, not nested 'checks')
        assert 'score' in validation, "Validation should include numeric score"
        assert 'pattern_preserved' in validation, "Validation should include pattern_preserved flag"

        # Verify key checks (at top level of dict)
        assert 'has_shebang' in validation, "Should include has_shebang check"
        assert 'no_markdown' in validation, "Should include no_markdown check"
        assert 'has_definitions' in validation, "Should include has_definitions check"

        assert validation['has_shebang'] is True, "Should detect shebang"
        assert validation['no_markdown'] is True, "Should verify no markdown"
        assert validation['has_definitions'] is True, "Should detect class definition"

        # Should have high score for correct replacements
        assert validation['score'] >= 50, \
            f"Should score well for correct replacements (got {validation['score']})"


class TestGeneratedAgentFlowMCPServer:
    """Test the generated AgentFlow MCP server code"""

    def test_file_exists(self):
        """Verify generated file exists"""
        filepath = 'agentflow/mcp/agentflow_mcp_server.py'
        assert os.path.exists(filepath), \
            f"Generated file should exist at {filepath}"

    def test_python_syntax_valid(self):
        """Verify Python syntax is valid"""
        import py_compile
        filepath = 'agentflow/mcp/agentflow_mcp_server.py'

        try:
            py_compile.compile(filepath, doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Syntax error in generated file: {e}")

    def test_file_structure(self):
        """Verify file has correct structure"""
        filepath = 'agentflow/mcp/agentflow_mcp_server.py'

        with open(filepath) as f:
            content = f.read()

        # Key structural checks
        checks = {
            "shebang": content.startswith('#!/usr/bin/env python3'),
            "no_markdown": '```' not in content,
            "has_class": 'class AgentFlowMCPServer' in content,
            "has_init": 'def __init__(self)' in content,
            "has_async": 'async def' in content,
            "has_main": 'if __name__ == "__main__":' in content,
        }

        failed = [k for k, v in checks.items() if not v]

        assert not failed, \
            f"Structure checks failed: {', '.join(failed)}"

    def test_replacements_applied(self):
        """Verify key replacements were applied"""
        filepath = 'agentflow/mcp/agentflow_mcp_server.py'

        with open(filepath) as f:
            content = f.read()

        # Key replacements that should be present
        required = [
            'SmartOrchestrator',
            'DelegationPool',
            'AgentFlowMCPServer',
            'delegate_task',
            'delegate_parallel',
            'check_delegation_status',
            'list_models'
        ]

        missing = [r for r in required if r not in content]

        assert not missing, \
            f"Missing required replacements: {', '.join(missing)}"

    def test_mcp_tools_defined(self):
        """Verify all 4 MCP tools are defined"""
        filepath = 'agentflow/mcp/agentflow_mcp_server.py'

        with open(filepath) as f:
            content = f.read()

        tools = [
            'delegate_task',
            'delegate_parallel',
            'check_delegation_status',
            'list_models'
        ]

        # Check tool names appear in server_info or as methods
        for tool in tools:
            tool_defined = (
                f'"{tool}"' in content or
                f"'{tool}'" in content or
                f'def _{tool}' in content or
                f'async def _{tool}' in content
            )

            assert tool_defined, \
                f"Tool {tool} not found in generated server"

    def test_stdio_communication_present(self):
        """Verify stdio communication loop is present"""
        filepath = 'agentflow/mcp/agentflow_mcp_server.py'

        with open(filepath) as f:
            content = f.read()

        # Check for stdio communication patterns
        checks = {
            "stdin_read": 'sys.stdin' in content or 'stdin.readline' in content,
            "stdout_print": 'print(' in content and 'flush=True' in content,
            "json_parse": 'json.loads' in content,
            "json_dump": 'json.dumps' in content,
        }

        failed = [k for k, v in checks.items() if not v]

        assert not failed, \
            f"stdio communication checks failed: {', '.join(failed)}"


class TestEndToEndIntegration:
    """Integration tests for the complete pattern replication workflow"""

    def test_all_components_importable(self):
        """Verify all components can be imported together"""
        try:
            from agentflow.core.context_generator import ContextGenerator, CompressedContext
            from agentflow.integration.apc_agentflow_bridge import APCAgentFlowBridge
            from agentflow.orchestration.pattern_replication_orchestrator import (
                PatternReplicationOrchestrator,
                replicate_pattern
            )
        except ImportError as e:
            pytest.fail(f"Import error in integration: {e}")

    def test_mock_pattern_replication_workflow(self):
        """Mock test of complete pattern replication workflow"""
        from agentflow.orchestration.pattern_replication_orchestrator import PatternReplicationOrchestrator

        orchestrator = PatternReplicationOrchestrator()

        # Mock pattern
        pattern = """#!/usr/bin/env python3
class OldClass:
    def old_method(self):
        return "old"
"""

        # Mock replacements
        replacements = {
            "OldClass": "NewClass",
            "old_method": "new_method",
            "old": "new"
        }

        # Mock generated code (what we expect)
        mock_generated = """#!/usr/bin/env python3
class NewClass:
    def new_method(self):
        return "new"
"""

        # Test validation
        validation = orchestrator._validate_pattern_replication(
            mock_generated,
            pattern,
            replacements
        )

        # Should have good score for correct replacements
        assert validation['score'] >= 50, \
            f"Mock workflow should validate well (got score: {validation['score']})"

        assert validation['pattern_preserved'] is True, \
            "Pattern should be marked as preserved"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
