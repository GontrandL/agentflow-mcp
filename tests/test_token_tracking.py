"""
Test suite for Phase 2: Token Usage Tracking

Tests comprehensive cost tracking functionality including:
- Token parsing from API responses
- Cost calculation accuracy
- Per-task cost tracking
- Accumulation across operations
- Cost summary export
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from agentflow.orchestration.smart_orchestrator import (
    SmartOrchestrator,
    TaskCost,
    Plan,
    Subtask
)


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response with usage data"""
    response = Mock()
    response.usage = Mock()
    response.usage.input_tokens = 1000
    response.usage.output_tokens = 500
    response.content = [Mock(text='{"complexity": "low", "decompose": false, "subtasks": [], "requirements": {}}')]
    return response


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response with usage data"""
    response = Mock()
    response.usage = Mock()
    response.usage.prompt_tokens = 2000
    response.usage.completion_tokens = 800
    response.choices = [Mock(message=Mock(content='{"assignments": []}'))]
    return response


@pytest.fixture
def orchestrator_anthropic():
    """Create SmartOrchestrator with Anthropic provider"""
    with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
        with patch('anthropic.Anthropic'):
            orch = SmartOrchestrator(provider='anthropic', enable_fallback=False)
            return orch


@pytest.fixture
def orchestrator_deepseek():
    """Create SmartOrchestrator with DeepSeek provider"""
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'}):
        with patch('openai.OpenAI'):
            orch = SmartOrchestrator(provider='deepseek', enable_fallback=False)
            return orch


class TestTokenParsing:
    """Test token usage parsing from API responses"""

    def test_anthropic_token_parsing(self, orchestrator_anthropic, mock_anthropic_response):
        """Test parsing tokens from Anthropic response"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            orchestrator_anthropic._set_operation('test_operation')
            result = orchestrator_anthropic._call_llm("test prompt")

            # Verify tokens were tracked
            assert orchestrator_anthropic.input_tokens == 1000
            assert orchestrator_anthropic.output_tokens == 500
            assert len(orchestrator_anthropic.task_costs) == 1

    def test_openai_token_parsing(self, orchestrator_deepseek, mock_openai_response):
        """Test parsing tokens from OpenAI-compatible response"""
        with patch.object(orchestrator_deepseek.client.chat.completions, 'create',
                         return_value=mock_openai_response):
            orchestrator_deepseek._set_operation('test_operation')
            result = orchestrator_deepseek._call_llm("test prompt")

            # Verify tokens were tracked
            assert orchestrator_deepseek.input_tokens == 2000
            assert orchestrator_deepseek.output_tokens == 800
            assert len(orchestrator_deepseek.task_costs) == 1


class TestCostCalculation:
    """Test accurate cost calculation"""

    def test_anthropic_cost_calculation(self, orchestrator_anthropic, mock_anthropic_response):
        """Test cost calculation accuracy for Anthropic"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            orchestrator_anthropic._set_operation('test_operation')
            orchestrator_anthropic._call_llm("test prompt")

            # Calculate expected costs
            # Anthropic: $3/1M input, $15/1M output
            expected_input_cost = 1000 * (3.00 / 1_000_000)
            expected_output_cost = 500 * (15.00 / 1_000_000)
            expected_total = expected_input_cost + expected_output_cost

            # Verify cost calculation (within 0.1% tolerance)
            actual_cost = orchestrator_anthropic.get_cost()
            assert abs(actual_cost - expected_total) / expected_total < 0.001

    def test_deepseek_cost_calculation(self, orchestrator_deepseek, mock_openai_response):
        """Test cost calculation accuracy for DeepSeek"""
        with patch.object(orchestrator_deepseek.client.chat.completions, 'create',
                         return_value=mock_openai_response):
            orchestrator_deepseek._set_operation('test_operation')
            orchestrator_deepseek._call_llm("test prompt")

            # Calculate expected costs
            # DeepSeek: $0.14/1M input, $0.28/1M output
            expected_input_cost = 2000 * (0.14 / 1_000_000)
            expected_output_cost = 800 * (0.28 / 1_000_000)
            expected_total = expected_input_cost + expected_output_cost

            # Verify cost calculation (within 0.1% tolerance)
            actual_cost = orchestrator_deepseek.get_cost()
            assert abs(actual_cost - expected_total) / expected_total < 0.001

    def test_all_providers_pricing(self):
        """Test that all providers have correct pricing configured"""
        expected_pricing = {
            'deepseek': {'input': 0.14, 'output': 0.28},
            'gpt-mini': {'input': 0.15, 'output': 0.60},
            'anthropic': {'input': 3.00, 'output': 15.00},
            'grok-fast': {'input': 5.00, 'output': 15.00}
        }

        for provider, pricing in expected_pricing.items():
            config = SmartOrchestrator.PROVIDERS[provider]
            actual_input = config['input_price'] * 1_000_000
            actual_output = config['output_price'] * 1_000_000

            assert abs(actual_input - pricing['input']) < 0.01, \
                f"{provider} input pricing mismatch"
            assert abs(actual_output - pricing['output']) < 0.01, \
                f"{provider} output pricing mismatch"


class TestTaskCostTracking:
    """Test per-task cost tracking"""

    def test_task_cost_structure(self, orchestrator_anthropic, mock_anthropic_response):
        """Test TaskCost dataclass structure"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            orchestrator_anthropic._set_operation('analyze_and_plan')
            orchestrator_anthropic._call_llm("test prompt")

            task_cost = orchestrator_anthropic.task_costs[0]

            # Verify all fields are present
            assert isinstance(task_cost, TaskCost)
            assert task_cost.provider == 'anthropic'
            assert task_cost.operation == 'analyze_and_plan'
            assert task_cost.input_tokens == 1000
            assert task_cost.output_tokens == 500
            assert task_cost.total_cost > 0
            assert task_cost.latency_ms >= 0

    def test_multiple_operations_tracking(self, orchestrator_anthropic, mock_anthropic_response):
        """Test tracking multiple operations"""
        operations = ['analyze_and_plan', 'assign_workers', 'validate_outputs']

        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            for op in operations:
                orchestrator_anthropic._set_operation(op)
                orchestrator_anthropic._call_llm("test prompt")

        # Verify all operations tracked
        assert len(orchestrator_anthropic.task_costs) == 3
        tracked_ops = [tc.operation for tc in orchestrator_anthropic.task_costs]
        assert tracked_ops == operations


class TestCostAccumulation:
    """Test cost accumulation across operations"""

    def test_cumulative_cost_tracking(self, orchestrator_anthropic, mock_anthropic_response):
        """Test that costs accumulate correctly"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            # Make 3 calls
            for i in range(3):
                orchestrator_anthropic._set_operation(f'operation_{i}')
                orchestrator_anthropic._call_llm("test prompt")

            # Each call: 1000 input + 500 output tokens
            # Anthropic: $3/1M input, $15/1M output
            expected_per_call = (1000 * 3.00 / 1_000_000) + (500 * 15.00 / 1_000_000)
            expected_total = expected_per_call * 3

            actual_total = orchestrator_anthropic.get_cost()
            assert abs(actual_total - expected_total) / expected_total < 0.001

    def test_token_accumulation(self, orchestrator_anthropic, mock_anthropic_response):
        """Test that tokens accumulate across calls"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            for i in range(5):
                orchestrator_anthropic._set_operation(f'operation_{i}')
                orchestrator_anthropic._call_llm("test prompt")

            # Each call: 1000 input + 500 output
            assert orchestrator_anthropic.input_tokens == 5000
            assert orchestrator_anthropic.output_tokens == 2500


class TestCostSummaryExport:
    """Test cost summary export functionality"""

    def test_cost_summary_structure(self, orchestrator_anthropic, mock_anthropic_response):
        """Test cost summary contains all required fields"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            orchestrator_anthropic._set_operation('test_op')
            orchestrator_anthropic._call_llm("test prompt")

            summary = orchestrator_anthropic.get_cost_summary()

            # Verify top-level structure
            assert 'total_cost' in summary
            assert 'task_count' in summary
            assert 'average_cost' in summary
            assert 'by_provider' in summary
            assert 'by_operation' in summary
            assert 'efficiency_metrics' in summary
            assert 'tasks' in summary

    def test_by_provider_grouping(self, orchestrator_anthropic, mock_anthropic_response):
        """Test costs grouped by provider"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            for i in range(3):
                orchestrator_anthropic._set_operation(f'op_{i}')
                orchestrator_anthropic._call_llm("test")

            summary = orchestrator_anthropic.get_cost_summary()
            by_provider = summary['by_provider']

            assert 'anthropic' in by_provider
            assert by_provider['anthropic']['task_count'] == 3
            assert by_provider['anthropic']['total_cost'] > 0
            assert by_provider['anthropic']['input_tokens'] == 3000
            assert by_provider['anthropic']['output_tokens'] == 1500

    def test_by_operation_grouping(self, orchestrator_anthropic, mock_anthropic_response):
        """Test costs grouped by operation type"""
        operations = ['analyze_and_plan', 'analyze_and_plan', 'validate_outputs']

        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            for op in operations:
                orchestrator_anthropic._set_operation(op)
                orchestrator_anthropic._call_llm("test")

            summary = orchestrator_anthropic.get_cost_summary()
            by_operation = summary['by_operation']

            # Verify analyze_and_plan called twice
            assert by_operation['analyze_and_plan']['count'] == 2
            assert by_operation['validate_outputs']['count'] == 1

    def test_efficiency_metrics(self, orchestrator_anthropic, mock_anthropic_response):
        """Test efficiency metrics calculation"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            orchestrator_anthropic._set_operation('test')
            orchestrator_anthropic._call_llm("test")

            summary = orchestrator_anthropic.get_cost_summary()
            metrics = summary['efficiency_metrics']

            assert 'cost_per_1k_tokens' in metrics
            assert 'avg_tokens_per_task' in metrics
            assert 'input_output_ratio' in metrics
            assert 'total_input_tokens' in metrics
            assert 'total_output_tokens' in metrics
            assert 'total_tokens' in metrics

            # Verify calculations
            assert metrics['total_input_tokens'] == 1000
            assert metrics['total_output_tokens'] == 500
            assert metrics['total_tokens'] == 1500
            assert metrics['input_output_ratio'] == 2.0  # 1000/500


class TestResetStats:
    """Test statistics reset functionality"""

    def test_reset_clears_all_tracking(self, orchestrator_anthropic, mock_anthropic_response):
        """Test that reset_stats clears all tracking data"""
        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         return_value=mock_anthropic_response):
            # Generate some activity
            for i in range(3):
                orchestrator_anthropic._set_operation(f'op_{i}')
                orchestrator_anthropic._call_llm("test")

            # Verify data exists
            assert orchestrator_anthropic.total_cost > 0
            assert len(orchestrator_anthropic.task_costs) > 0

            # Reset
            orchestrator_anthropic.reset_stats()

            # Verify everything cleared
            assert orchestrator_anthropic.input_tokens == 0
            assert orchestrator_anthropic.output_tokens == 0
            assert orchestrator_anthropic.total_cost == 0.0
            assert len(orchestrator_anthropic.task_costs) == 0


class TestCostAccuracyValidation:
    """Test cost calculation accuracy within 5% tolerance"""

    @pytest.mark.parametrize("provider,input_tokens,output_tokens", [
        ('anthropic', 10000, 5000),
        ('deepseek', 50000, 20000),
        ('gpt-mini', 8000, 3000),
    ])
    def test_cost_accuracy_5_percent(self, provider, input_tokens, output_tokens):
        """Test cost calculations are accurate within 5%"""
        # Mock the appropriate environment variable
        env_vars = {
            'anthropic': {'ANTHROPIC_API_KEY': 'test-key'},
            'deepseek': {'OPENROUTER_API_KEY': 'test-key'},
            'gpt-mini': {'OPENAI_API_KEY': 'test-key'}
        }

        with patch.dict(os.environ, env_vars[provider]):
            # Mock the appropriate client
            if provider == 'anthropic':
                with patch('anthropic.Anthropic'):
                    orch = SmartOrchestrator(provider=provider, enable_fallback=False)
            else:
                with patch('openai.OpenAI'):
                    orch = SmartOrchestrator(provider=provider, enable_fallback=False)

            # Manually track usage
            orch._set_operation('test')
            orch._track_usage(input_tokens, output_tokens)

            # Calculate expected cost
            config = SmartOrchestrator.PROVIDERS[provider]
            expected_cost = (
                input_tokens * config['input_price'] +
                output_tokens * config['output_price']
            )

            # Verify accuracy within 5%
            actual_cost = orch.get_cost()
            if expected_cost > 0:
                error_percent = abs(actual_cost - expected_cost) / expected_cost * 100
                assert error_percent < 5.0, \
                    f"Cost error {error_percent}% exceeds 5% tolerance"


class TestIntegrationScenarios:
    """Test real-world usage scenarios"""

    def test_full_orchestration_workflow(self, orchestrator_anthropic):
        """Test cost tracking through full orchestration workflow"""
        # Mock different responses for different operations
        plan_response = Mock()
        plan_response.usage = Mock(input_tokens=2000, output_tokens=1000)
        plan_response.content = [Mock(text='''
        {
            "complexity": "medium",
            "decompose": true,
            "subtasks": [
                {
                    "id": "task1",
                    "description": "Test task",
                    "dependencies": [],
                    "difficulty": "low",
                    "error_risk": "low",
                    "estimated_tokens": 500
                }
            ],
            "requirements": {"quality_threshold": 0.9}
        }
        ''')]

        workers_response = Mock()
        workers_response.usage = Mock(input_tokens=1500, output_tokens=800)
        workers_response.content = [Mock(text='''
        {
            "assignments": [
                {"subtask_id": "task1", "worker": "worker1", "rationale": "Fast"}
            ]
        }
        ''')]

        with patch.object(orchestrator_anthropic.client.messages, 'create',
                         side_effect=[plan_response, workers_response]):
            # Run planning
            plan = orchestrator_anthropic.analyze_and_plan(
                task="Test task",
                capabilities=["coding"],
                context={}
            )

            # Run worker assignment
            assignments = orchestrator_anthropic.assign_workers(
                subtasks=plan.subtasks,
                available_workers={
                    'worker1': {
                        'price': 'free',
                        'quality': 95,
                        'speed': 'fast',
                        'best_for': 'general',
                        'weaknesses': 'none'
                    }
                }
            )

            # Verify comprehensive tracking
            summary = orchestrator_anthropic.get_cost_summary()
            assert summary['task_count'] == 2
            assert 'analyze_and_plan' in summary['by_operation']
            assert 'assign_workers' in summary['by_operation']
            assert summary['total_cost'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
