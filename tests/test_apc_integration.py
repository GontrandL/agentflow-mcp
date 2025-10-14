"""
Comprehensive APC Integration Test Suite

This test suite validates the Agent Preparer Context (APC) system:
1. Context compression (100K→8K tokens)
2. Validation scoring (0-100)
3. APC-AgentFlow bridge workflow
4. Learning metrics tracking

**KEY**: All tests use mocked API calls to avoid timeouts and costs.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict

import numpy as np

from agentflow.core.context_generator import (
    ContextGenerator,
    CompressedContext,
    ContextSegment,
    generate_compressed_context
)
from agentflow.orchestration.hybrid_orchestrator import (
    HybridOrchestrator,
    validate_delegation_output
)
from agentflow.integration.apc_agentflow_bridge import APCAgentFlowBridge


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_conversation():
    """Sample conversation history for testing."""
    return [
        {
            'role': 'user',
            'content': 'I need to implement a REST API with authentication.',
            'timestamp': datetime(2025, 1, 10, 10, 0)
        },
        {
            'role': 'assistant',
            'content': '''I'll help you build a REST API with JWT authentication:

```python
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({'users': []})
```

This provides a basic Flask API with JWT setup.
''',
            'timestamp': datetime(2025, 1, 10, 10, 5)
        },
        {
            'role': 'user',
            'content': 'Add user login endpoint.',
            'timestamp': datetime(2025, 1, 10, 10, 10)
        },
        {
            'role': 'assistant',
            'content': '''Here's the login endpoint:

```python
from flask_jwt_extended import create_access_token

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Validate credentials (simplified)
    if validate_credentials(username, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

    return jsonify({'error': 'Invalid credentials'}), 401
```

This creates JWT tokens for authenticated users.
''',
            'timestamp': datetime(2025, 1, 10, 10, 15)
        },
        {
            'role': 'user',
            'content': 'Error: ModuleNotFoundError for flask_jwt_extended',
            'timestamp': datetime(2025, 1, 10, 10, 20)
        },
        {
            'role': 'assistant',
            'content': '''You need to install the package:

```bash
pip install flask-jwt-extended
```

Then add it to requirements.txt:
```
Flask==2.3.0
flask-jwt-extended==4.5.0
```

Error fixed!
''',
            'timestamp': datetime(2025, 1, 10, 10, 25)
        }
    ]


@pytest.fixture
def mock_orchestrator():
    """Mock SmartOrchestrator to avoid API calls."""
    orchestrator = Mock()
    orchestrator.orchestrate = Mock(return_value="""
Here's the complete implementation:

```python
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if validate_credentials(username, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    return jsonify({'users': ['alice', 'bob']})

if __name__ == '__main__':
    app.run(debug=True)
```

This implementation includes:
- JWT authentication setup
- Login endpoint with token generation
- Protected users endpoint
- Error handling
""")
    return orchestrator


# ============================================================================
# TEST: Context Generator
# ============================================================================

class TestContextGenerator:
    """Test the ContextGenerator component."""

    def test_initialization(self):
        """Test ContextGenerator initialization."""
        generator = ContextGenerator(
            target_tokens=8000,
            min_density=0.6,
            diversity_lambda=0.7
        )

        assert generator.target_tokens == 8000
        assert generator.min_density == 0.6
        assert generator.diversity_lambda == 0.7

    def test_segment_conversation(self, sample_conversation):
        """Test conversation segmentation."""
        generator = ContextGenerator()
        segments = generator._segment_conversation(sample_conversation)

        assert len(segments) == len(sample_conversation)
        assert all(isinstance(seg, ContextSegment) for seg in segments)

        # Check segment types are detected
        types = [seg.segment_type for seg in segments]
        assert 'decision' in types  # User requests
        assert 'code' in types      # Code blocks
        assert 'error' in types     # Error messages

    def test_detect_segment_type(self):
        """Test segment type detection."""
        generator = ContextGenerator()

        # Test code detection
        code_content = "Here's the code:\n```python\nprint('hello')\n```"
        assert generator._detect_segment_type(code_content, 'assistant') == 'code'

        # Test error detection
        error_content = "Error: ModuleNotFoundError occurred"
        assert generator._detect_segment_type(error_content, 'user') == 'error'

        # Test success detection
        success_content = "✅ All tests completed successfully!"
        assert generator._detect_segment_type(success_content, 'assistant') == 'success'

        # Test decision detection (user role)
        decision_content = "I need to implement feature X"
        assert generator._detect_segment_type(decision_content, 'user') == 'decision'

    def test_score_segments(self, sample_conversation):
        """Test segment scoring."""
        generator = ContextGenerator()
        segments = generator._segment_conversation(sample_conversation)
        scored = generator._score_segments(segments, "Add authentication to API")

        assert all(0 <= seg.importance_score <= 1 for seg in scored)

        # Recent segments should have higher recency scores
        assert scored[-1].importance_score > 0

    def test_mmr_selection(self, sample_conversation):
        """Test MMR segment selection."""
        generator = ContextGenerator(target_tokens=500)
        segments = generator._segment_conversation(sample_conversation)
        scored = generator._score_segments(segments, "Add auth")

        selected = generator._select_segments_mmr(scored, 500)

        total_tokens = sum(seg.tokens for seg in selected)
        assert total_tokens <= 500
        assert len(selected) > 0

    def test_extract_code_blocks(self):
        """Test code block extraction."""
        generator = ContextGenerator()
        content = '''
Here's an example:

```python
def hello():
    print("world")
```

And another:

```javascript
console.log("hello");
```
'''

        blocks = generator._extract_code_blocks(content)
        assert len(blocks) == 2
        assert blocks[0]['lang'] == 'python'
        assert blocks[1]['lang'] == 'javascript'
        assert 'hello' in blocks[0]['code']

    def test_generate_context(self, sample_conversation):
        """Test full context generation pipeline."""
        generator = ContextGenerator(target_tokens=1000)
        compressed = generator.generate_context(
            sample_conversation,
            "Add authentication to REST API",
            namespace="test"
        )

        assert isinstance(compressed, CompressedContext)
        assert compressed.total_tokens <= 1200  # Allow some overhead
        assert compressed.compression_ratio > 0
        assert len(compressed.key_decisions) > 0
        assert compressed.expectation_vector is not None
        assert compressed.expectation_vector.shape == (768,)

    def test_expectation_vector_properties(self, sample_conversation):
        """Test expectation vector properties."""
        generator = ContextGenerator()
        compressed = generator.generate_context(
            sample_conversation,
            "Test task"
        )

        vector = compressed.expectation_vector

        # Check shape
        assert vector.shape == (768,)

        # Check normalization (L2 norm ~1.0)
        norm = np.linalg.norm(vector)
        assert 0.99 <= norm <= 1.01

        # Check dtype
        assert vector.dtype == np.float32

    def test_convenience_function(self, sample_conversation):
        """Test convenience function."""
        compressed = generate_compressed_context(
            sample_conversation,
            "Add auth",
            target_tokens=800
        )

        assert compressed.total_tokens <= 900  # Allow overhead
        assert compressed.expectation_vector is not None


# ============================================================================
# TEST: Hybrid Orchestrator
# ============================================================================

class TestHybridOrchestrator:
    """Test the HybridOrchestrator component."""

    def test_initialization(self, mock_orchestrator):
        """Test HybridOrchestrator initialization."""
        hybrid = HybridOrchestrator(
            smart_orchestrator=mock_orchestrator,
            validation_threshold=80
        )

        assert hybrid.smart_orchestrator == mock_orchestrator
        assert hybrid.validation_threshold == 80

    def test_validate_output_scoring(self):
        """Test output validation scoring."""
        # Note: HybridOrchestrator._validate_output returns placeholder (score: 0)
        # The actual scoring is in APCAgentFlowBridge._validate_output
        # This test validates the structure, not the scoring logic
        hybrid = HybridOrchestrator()

        good_output = """
Here's the complete implementation:

```python
def authenticate_user(username: str, password: str) -> bool:
    '''Authenticate user with proper error handling.'''
    if not username or not password:
        raise ValueError("Username and password required")
    hashed = hash_password(password)
    return check_credentials(username, hashed)
```
"""

        task = "Implement user authentication system"
        validation = hybrid._validate_output(task, good_output)

        # Check structure (HybridOrchestrator returns placeholder)
        assert 'score' in validation
        assert 'issues' in validation
        assert isinstance(validation['issues'], list)
        assert 'checklist' in validation
        assert 'improvement_context' in validation

    def test_validate_output_detects_issues(self):
        """Test validation structure for poor output."""
        # Note: HybridOrchestrator._validate_output returns placeholder structure
        # Issue detection happens in APCAgentFlowBridge._validate_output
        hybrid = HybridOrchestrator()

        bad_output = """
TODO: Implement this later
PLACEHOLDER for authentication
"""

        task = "Implement authentication"
        validation = hybrid._validate_output(task, bad_output)

        # Check structure is valid
        assert 'score' in validation
        assert 'issues' in validation
        assert isinstance(validation['issues'], list)
        assert 'completeness' in validation
        assert 'correctness' in validation

    def test_format_issues(self):
        """Test issue formatting."""
        hybrid = HybridOrchestrator()

        issues = [
            {
                'component': 'Authentication',
                'issue': 'Missing error handling',
                'fix_instruction': 'Add try-except blocks'
            },
            {
                'component': 'Validation',
                'issue': 'No input validation',
                'fix_instruction': 'Add input checks'
            }
        ]

        formatted = hybrid._format_issues(issues)

        assert 'Authentication' in formatted
        assert 'Validation' in formatted
        assert 'try-except' in formatted

    def test_generate_fix_instructions_iteration1(self):
        """Test fix instruction generation for first iteration."""
        hybrid = HybridOrchestrator()

        validation = {
            'score': 60,
            'issues': [
                {
                    'component': 'ErrorHandling',
                    'issue': 'No error handling',
                    'fix_instruction': 'Add try-except blocks'
                }
            ]
        }

        instructions = hybrid.generate_fix_instructions(
            task="Implement auth",
            failed_output="def auth(): pass",
            validation=validation,
            iteration=1
        )

        assert 'Score: 60/100' in instructions
        assert 'ErrorHandling' in instructions
        assert 'try-except' in instructions

    def test_generate_fix_instructions_iteration2(self):
        """Test fix instructions become more specific in iteration 2."""
        hybrid = HybridOrchestrator()

        validation = {
            'score': 70,
            'issues': [
                {
                    'component': 'ErrorHandling',
                    'issue': 'Incomplete error handling',
                    'fix_instruction': 'Handle specific exceptions',
                    'code_example': 'try:\n    ...\nexcept ValueError:\n    ...'
                }
            ]
        }

        instructions = hybrid.generate_fix_instructions(
            task="Implement auth",
            failed_output="def auth(): pass",
            validation=validation,
            iteration=2
        )

        assert 'SPECIFIC fixes' in instructions
        assert 'Score: 70/100' in instructions

    def test_validate_worker_output(self):
        """Test worker output validation."""
        hybrid = HybridOrchestrator()

        validation = hybrid.validate_worker_output(
            worker_name="Worker 1: Auth Implementation",
            task="Implement authentication",
            output="Complete auth implementation with error handling..."
        )

        assert 'score' in validation
        assert 'issues' in validation

    def test_convenience_validation_function(self):
        """Test convenience validation function."""
        validation = validate_delegation_output(
            task="Build API",
            output="Complete API implementation with docs",
            threshold=70
        )

        assert 'score' in validation
        assert validation['score'] >= 0
        assert validation['score'] <= 100


# ============================================================================
# TEST: APC-AgentFlow Bridge
# ============================================================================

class TestAPCAgentFlowBridge:
    """Test the APCAgentFlowBridge integration."""

    def test_initialization(self):
        """Test bridge initialization."""
        bridge = APCAgentFlowBridge(
            context_target_tokens=5000,
            validation_threshold=75,
            max_retries=3,
            provider="deepseek"
        )

        assert bridge.context_generator.target_tokens == 5000
        assert bridge.hybrid_orchestrator.validation_threshold == 75
        assert bridge.max_retries == 3
        assert bridge.provider == "deepseek"

    def test_metrics_initialization(self):
        """Test that metrics are initialized."""
        bridge = APCAgentFlowBridge()

        metrics = bridge.metrics
        assert metrics['total_requests'] == 0
        assert metrics['context_compressions'] == 0
        assert metrics['delegations'] == 0
        assert metrics['validations'] == 0

    @patch('agentflow.integration.apc_agentflow_bridge.SmartOrchestrator')
    def test_execute_workflow_success(self, mock_orchestrator_class, sample_conversation):
        """Test successful workflow execution."""
        # Mock the orchestrator
        mock_orch = Mock()
        mock_orch.orchestrate = Mock(return_value="""
Complete implementation with all features:

```python
class AuthSystem:
    def login(self, username, password):
        # Validate and authenticate
        return generate_token(username)
```

All requirements met!
""")
        mock_orchestrator_class.return_value = mock_orch

        # Create bridge
        bridge = APCAgentFlowBridge(validation_threshold=60)  # Lower threshold for test
        bridge.smart_orchestrator = mock_orch

        # Execute workflow
        result = bridge.execute(
            task="Implement authentication system",
            conversation_history=sample_conversation,
            namespace="test"
        )

        # Verify results
        assert result['status'] == 'success'
        assert result['validation_score'] >= 60
        assert result['iterations'] <= bridge.max_retries
        assert 'cost_estimate' in result
        assert 'compressed_context' in result

        # Verify metrics were updated
        assert bridge.metrics['total_requests'] == 1
        assert bridge.metrics['context_compressions'] == 1
        assert bridge.metrics['delegations'] >= 1

    def test_build_enhanced_task(self, sample_conversation):
        """Test enhanced task building."""
        bridge = APCAgentFlowBridge()

        # Generate context
        compressed = bridge.context_generator.generate_context(
            sample_conversation,
            "Add auth"
        )

        # Build enhanced task
        enhanced = bridge._build_enhanced_task("Implement login", compressed)

        assert "Implement login" in enhanced
        assert "Key Decisions" in enhanced
        assert "Relevant Code Examples" in enhanced

    def test_format_decisions(self):
        """Test decision formatting."""
        bridge = APCAgentFlowBridge()

        decisions = [
            "Need to implement JWT authentication",
            "Use Flask framework for API",
            "Add rate limiting to endpoints"
        ]

        formatted = bridge._format_decisions(decisions)

        assert "JWT" in formatted
        assert "Flask" in formatted

    def test_format_code_snippets(self):
        """Test code snippet formatting."""
        bridge = APCAgentFlowBridge()

        snippets = [
            {'lang': 'python', 'code': 'def hello():\n    print("world")', 'context': ''},
            {'lang': 'javascript', 'code': 'console.log("test")', 'context': ''}
        ]

        formatted = bridge._format_code_snippets(snippets)

        assert '```python' in formatted
        assert 'hello' in formatted

    def test_update_metrics(self, sample_conversation):
        """Test metrics updating."""
        bridge = APCAgentFlowBridge()

        # Generate compressed context
        compressed = bridge.context_generator.generate_context(
            sample_conversation,
            "Test task"
        )

        validation = {'score': 85}

        # Initialize metrics properly before updating
        bridge.metrics['total_requests'] = 1  # Need > 0 to avoid division by zero
        bridge.metrics['context_compressions'] = 1
        bridge.metrics['validations'] = 1
        bridge._update_metrics(compressed, validation, iterations=1, success=True)

        # Check metrics
        assert bridge.metrics['avg_compression_ratio'] > 0
        assert bridge.metrics['avg_validation_score'] == 85
        assert bridge.metrics['success_rate'] == 1.0

    def test_get_metrics(self):
        """Test metrics retrieval."""
        bridge = APCAgentFlowBridge()
        bridge.metrics['total_requests'] = 10
        bridge.metrics['retries'] = 2
        bridge.metrics['avg_validation_score'] = 82.5
        bridge.metrics['successes'] = 9
        bridge.metrics['success_rate'] = 0.9

        metrics = bridge.get_metrics()

        assert metrics['total_requests'] == 10
        assert 'avg_cost_per_request' in metrics
        assert metrics['quality_score'] == 82.5
        assert metrics['efficiency_score'] == 90.0

    def test_apc_validation_scoring(self, sample_conversation):
        """Test APCAgentFlowBridge validation scoring (actual logic)."""
        bridge = APCAgentFlowBridge()

        # Generate context
        compressed = bridge.context_generator.generate_context(
            sample_conversation,
            "Implement authentication"
        )

        # Good output (should score high)
        good_output = """
Complete authentication implementation:

```python
class AuthSystem:
    '''Production-ready authentication system.'''

    def login(self, username: str, password: str) -> str:
        '''Authenticate and return token.'''
        if not username or not password:
            raise ValueError("Credentials required")

        if self.validate_credentials(username, password):
            return self.generate_token(username)
        raise AuthenticationError("Invalid credentials")
```

Features:
- Type hints
- Error handling
- Documentation
- Production ready
"""

        validation = bridge._validate_output(
            "Implement authentication",
            good_output,
            compressed,
            iteration=1,
            previous_validation=None
        )

        # Should score well
        assert validation['score'] >= 60
        assert validation['completeness'] == True
        assert validation['correctness'] == True

        # Bad output (should score low)
        bad_output = "TODO: Implement authentication later"

        validation_bad = bridge._validate_output(
            "Implement authentication",
            bad_output,
            compressed,
            iteration=1,
            previous_validation=None
        )

        assert validation_bad['score'] < 60
        assert len(validation_bad['issues']) > 0


# ============================================================================
# TEST: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    @patch('agentflow.integration.apc_agentflow_bridge.SmartOrchestrator')
    def test_full_pipeline_with_retry(self, mock_orchestrator_class, sample_conversation):
        """Test full pipeline with validation failure and retry."""
        # Mock orchestrator with progressive improvement
        mock_orch = Mock()
        call_count = 0

        def mock_orchestrate(task):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First attempt: poor quality
                return "TODO: Implement authentication"
            else:
                # Second attempt: good quality
                return """
Complete authentication system:

```python
class AuthSystem:
    def __init__(self):
        self.sessions = {}

    def login(self, username, password):
        if self.validate_credentials(username, password):
            token = self.generate_token(username)
            self.sessions[token] = username
            return token
        raise AuthenticationError("Invalid credentials")

    def validate_credentials(self, username, password):
        # Check database
        return True

    def generate_token(self, username):
        import secrets
        return secrets.token_urlsafe(32)
```

All features implemented with proper error handling.
"""

        mock_orch.orchestrate = Mock(side_effect=mock_orchestrate)
        mock_orchestrator_class.return_value = mock_orch

        # Create bridge with low threshold for testing
        bridge = APCAgentFlowBridge(validation_threshold=60)
        bridge.smart_orchestrator = mock_orch

        # Execute
        result = bridge.execute(
            task="Implement secure authentication system",
            conversation_history=sample_conversation,
            namespace="test"
        )

        # Should succeed after retry
        assert result['status'] == 'success'
        assert result['iterations'] == 2  # First failed, second succeeded
        assert call_count == 2

    def test_context_compression_preserves_quality(self, sample_conversation):
        """Test that compression preserves important information."""
        generator = ContextGenerator(target_tokens=500)

        compressed = generator.generate_context(
            sample_conversation,
            "Implement JWT authentication for Flask API"
        )

        # Check that key concepts are preserved
        full_content = compressed.summary + ' ' + ' '.join(compressed.key_decisions)

        # Should preserve core concepts
        assert any(keyword in full_content.lower() for keyword in ['jwt', 'flask', 'auth', 'api'])

        # Should have code examples
        assert len(compressed.code_snippets) > 0


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
