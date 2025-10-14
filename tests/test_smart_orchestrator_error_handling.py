"""
Tests for SmartOrchestrator error handling and retry logic

Tests cover:
1. Retry decorator with exponential backoff
2. Fallback chain execution
3. Cost tracking preservation across fallbacks
4. Error logging and reporting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator


class TestRetryLogic:
    """Test exponential backoff retry mechanism"""

    @patch('agentflow.orchestration.smart_orchestrator.anthropic')
    def test_retry_succeeds_on_second_attempt(self, mock_anthropic):
        """Test that retry succeeds after initial failure"""
        # Setup mock to fail once then succeed
        mock_response = Mock()
        mock_response.content = [Mock(text="Success")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)

        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            Exception("Temporary failure"),
            mock_response
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        # Create orchestrator
        orchestrator = SmartOrchestrator(
            provider='anthropic',
            api_key='test-key',
            enable_fallback=False
        )

        # Call should succeed on retry
        result = orchestrator._call_llm("test prompt")
        assert result == "Success"
        assert mock_client.messages.create.call_count == 2

    @patch('agentflow.orchestration.smart_orchestrator.anthropic')
    def test_retry_exhausts_after_three_attempts(self, mock_anthropic):
        """Test that retry stops after 3 attempts"""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Persistent failure")
        mock_anthropic.Anthropic.return_value = mock_client

        orchestrator = SmartOrchestrator(
            provider='anthropic',
            api_key='test-key',
            enable_fallback=False
        )

        # Should raise after 3 attempts
        with pytest.raises(Exception, match="Persistent failure"):
            orchestrator._call_llm("test prompt")

        assert mock_client.messages.create.call_count == 3


class TestFallbackChain:
    """Test automatic fallback to alternative providers"""

    def test_fallback_to_next_provider(self):
        """Test fallback switches to next available provider"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'anthropic-key',
            'DEEPSEEK_API_KEY': 'deepseek-key'
        }):
            with patch('agentflow.orchestration.smart_orchestrator.anthropic') as mock_anthropic:
                with patch('agentflow.orchestration.smart_orchestrator.openai') as mock_openai:
                    # Anthropic fails
                    mock_anthropic_client = Mock()
                    mock_anthropic_client.messages.create.side_effect = Exception("Anthropic down")
                    mock_anthropic.Anthropic.return_value = mock_anthropic_client

                    # DeepSeek succeeds
                    mock_deepseek_response = Mock()
                    mock_deepseek_response.choices = [Mock(message=Mock(content="Fallback success"))]
                    mock_deepseek_response.usage = Mock(prompt_tokens=100, completion_tokens=50)

                    mock_deepseek_client = Mock()
                    mock_deepseek_client.chat.completions.create.return_value = mock_deepseek_response
                    mock_openai.OpenAI.return_value = mock_deepseek_client

                    orchestrator = SmartOrchestrator(
                        provider='anthropic',
                        api_key='anthropic-key',
                        enable_fallback=True
                    )

                    result = orchestrator._call_llm("test prompt")

                    assert result == "Fallback success"
                    assert orchestrator.fallback_attempts == 1
                    assert 'anthropic' in orchestrator.failed_providers
                    assert orchestrator.provider == 'deepseek'

    def test_fallback_preserves_cost_tracking(self):
        """Test that cost tracking continues across fallback providers"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'anthropic-key',
            'DEEPSEEK_API_KEY': 'deepseek-key'
        }):
            with patch('agentflow.orchestration.smart_orchestrator.anthropic'):
                with patch('agentflow.orchestration.smart_orchestrator.openai') as mock_openai:
                    # DeepSeek response
                    mock_response = Mock()
                    mock_response.choices = [Mock(message=Mock(content="Success"))]
                    mock_response.usage = Mock(prompt_tokens=200, completion_tokens=100)

                    mock_client = Mock()
                    mock_client.chat.completions.create.return_value = mock_response
                    mock_openai.OpenAI.return_value = mock_client

                    orchestrator = SmartOrchestrator(
                        provider='deepseek',
                        api_key='deepseek-key',
                        enable_fallback=True
                    )

                    # Make multiple calls
                    orchestrator._call_llm("prompt 1")
                    orchestrator._call_llm("prompt 2")

                    # Check cost tracking
                    assert orchestrator.input_tokens == 400
                    assert orchestrator.output_tokens == 200
                    cost = orchestrator.get_cost()
                    assert cost > 0

    def test_all_fallbacks_exhausted(self):
        """Test error when all providers in fallback chain fail"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'anthropic-key',
            'DEEPSEEK_API_KEY': 'deepseek-key',
            'OPENAI_API_KEY': 'openai-key'
        }):
            with patch('agentflow.orchestration.smart_orchestrator.anthropic') as mock_anthropic:
                with patch('agentflow.orchestration.smart_orchestrator.openai') as mock_openai:
                    # All providers fail
                    mock_anthropic.Anthropic.return_value.messages.create.side_effect = Exception("Fail")
                    mock_openai.OpenAI.return_value.chat.completions.create.side_effect = Exception("Fail")

                    orchestrator = SmartOrchestrator(
                        provider='anthropic',
                        api_key='anthropic-key',
                        enable_fallback=True
                    )

                    with pytest.raises(RuntimeError, match="All providers failed"):
                        orchestrator._call_llm("test prompt")

                    # Should have attempted fallbacks
                    assert orchestrator.fallback_attempts > 0
                    assert len(orchestrator.failed_providers) > 0


class TestFallbackOrder:
    """Test fallback chain order and priorities"""

    def test_fallback_order_correct(self):
        """Test that fallback follows correct order"""
        orchestrator = SmartOrchestrator(
            provider='anthropic',
            api_key='test-key',
            enable_fallback=True
        )

        expected_order = ['deepseek', 'grok-fast', 'gpt-mini', 'anthropic']
        assert orchestrator.FALLBACK_ORDER == expected_order

    def test_skips_already_failed_providers(self):
        """Test that fallback skips providers that already failed"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'anthropic-key',
            'DEEPSEEK_API_KEY': 'deepseek-key',
            'OPENAI_API_KEY': 'openai-key'
        }):
            with patch('agentflow.orchestration.smart_orchestrator.anthropic'):
                with patch('agentflow.orchestration.smart_orchestrator.openai') as mock_openai:
                    orchestrator = SmartOrchestrator(
                        provider='deepseek',
                        api_key='deepseek-key',
                        enable_fallback=True
                    )

                    # Mark deepseek as already failed
                    orchestrator.failed_providers.append('deepseek')

                    # Mock gpt-mini to succeed
                    mock_response = Mock()
                    mock_response.choices = [Mock(message=Mock(content="Success"))]
                    mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)
                    mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response

                    result = orchestrator._call_llm("test")

                    # Should skip deepseek and go to next provider
                    assert result == "Success"


class TestLoggingAndMetrics:
    """Test logging and metrics during error handling"""

    @patch('agentflow.orchestration.smart_orchestrator.anthropic')
    def test_logs_retry_attempts(self, mock_anthropic):
        """Test that retry attempts are logged"""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Error")
        mock_anthropic.Anthropic.return_value = mock_client

        orchestrator = SmartOrchestrator(
            provider='anthropic',
            api_key='test-key',
            enable_fallback=False
        )

        with patch.object(orchestrator.logger, 'error') as mock_log_error:
            with pytest.raises(Exception):
                orchestrator._call_llm("test")

            # Should log errors
            assert mock_log_error.call_count >= 3

    def test_stats_include_fallback_info(self):
        """Test that get_stats includes fallback statistics"""
        orchestrator = SmartOrchestrator(
            provider='anthropic',
            api_key='test-key',
            enable_fallback=True
        )

        stats = orchestrator.get_stats()

        assert 'fallback_attempts' in stats
        assert 'failed_providers' in stats
        assert 'enable_fallback' in stats
        assert stats['enable_fallback'] is True

    def test_reset_stats_clears_fallback_data(self):
        """Test that reset_stats clears fallback information"""
        orchestrator = SmartOrchestrator(
            provider='anthropic',
            api_key='test-key',
            enable_fallback=True
        )

        orchestrator.fallback_attempts = 5
        orchestrator.failed_providers = ['deepseek', 'grok-fast']

        orchestrator.reset_stats()

        assert orchestrator.fallback_attempts == 0
        assert orchestrator.failed_providers == []


class TestProviderConfigurations:
    """Test provider-specific configurations"""

    def test_all_providers_configured(self):
        """Test that all providers have required configuration"""
        required_keys = ['default_model', 'input_price', 'output_price', 'max_tokens']

        for provider, config in SmartOrchestrator.PROVIDERS.items():
            for key in required_keys:
                assert key in config, f"{provider} missing {key}"

    def test_deepseek_configuration(self):
        """Test DeepSeek provider configuration"""
        config = SmartOrchestrator.PROVIDERS['deepseek']
        assert config['default_model'] == 'deepseek-chat'
        assert config['input_price'] < SmartOrchestrator.PROVIDERS['anthropic']['input_price']

    def test_fallback_chain_includes_all_providers(self):
        """Test that fallback chain includes cost-effective providers"""
        fallback_order = SmartOrchestrator.FALLBACK_ORDER

        # Should start with cheapest
        assert fallback_order[0] == 'deepseek'
        # Should end with most reliable
        assert fallback_order[-1] == 'anthropic'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
