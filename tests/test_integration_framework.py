"""
Comprehensive tests for Integration Framework

Tests cover:
- Pattern matching and selection
- Integration generation
- Utility library components
- Cost and performance metrics
- Error handling

Target: 90%+ code coverage
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from agentflow.orchestration import SmartOrchestrator
from agentflow.orchestration.integration_patterns import (
    APIIntegrationPattern,
    DatabaseIntegrationPattern,
    IntegrationPackage,
    get_integration_pattern,
    select_best_pattern
)
from agentflow.orchestration.integration_builder import IntegrationBuilder, BuildMetrics
from agentflow.orchestration.utils import (
    RetryHelper,
    RateLimiter,
    MetricsCollector,
    SecretManager,
    CacheManager,
    ErrorHandler,
    IntegrationError,
    APIError,
    AuthenticationError
)


class TestIntegrationPatterns:
    """Test integration pattern functionality"""

    def test_api_pattern_matches(self):
        """Test API pattern matching"""
        pattern = APIIntegrationPattern()

        # Strong match
        requirements = {
            'type': 'api',
            'base_url': 'https://api.example.com',
            'auth_type': 'bearer'
        }
        score = pattern.matches(requirements)
        assert score >= 0.8

        # Weak match
        requirements = {'type': 'database'}
        score = pattern.matches(requirements)
        assert score < 0.5

    def test_api_pattern_decomposition(self):
        """Test API pattern task decomposition"""
        pattern = APIIntegrationPattern()
        requirements = {'base_url': 'https://api.example.com'}

        subtasks = pattern.decompose(requirements)

        assert len(subtasks) == 6
        assert subtasks[0].id == 'api_client_setup'
        assert subtasks[1].id == 'api_methods'
        assert subtasks[1].dependencies == ['api_client_setup']

    def test_database_pattern_matches(self):
        """Test database pattern matching"""
        pattern = DatabaseIntegrationPattern()

        requirements = {
            'type': 'database',
            'connection_string': 'postgresql://localhost/db'
        }
        score = pattern.matches(requirements)
        assert score >= 0.8

    def test_pattern_selection(self):
        """Test automatic pattern selection"""
        # Should select API pattern
        requirements = {'type': 'api', 'base_url': 'https://api.example.com'}
        pattern = select_best_pattern(requirements)
        assert isinstance(pattern, APIIntegrationPattern)

        # Should select database pattern
        requirements = {'type': 'database', 'host': 'localhost'}
        pattern = select_best_pattern(requirements)
        assert isinstance(pattern, DatabaseIntegrationPattern)

    def test_get_pattern_by_type(self):
        """Test getting pattern by explicit type"""
        pattern = get_integration_pattern('api')
        assert isinstance(pattern, APIIntegrationPattern)

        with pytest.raises(ValueError):
            get_integration_pattern('nonexistent')


class TestIntegrationBuilder:
    """Test integration builder functionality"""

    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for testing"""
        orchestrator = Mock(spec=SmartOrchestrator)

        # Mock analyze_and_plan
        mock_plan = Mock()
        mock_plan.subtasks = []
        mock_plan.requirements = {}
        orchestrator.analyze_and_plan.return_value = mock_plan

        # Mock validate_outputs
        mock_validation = Mock()
        mock_validation.all_passed = True
        mock_validation.avg_score = 95.0
        mock_validation.results = []
        mock_validation.failed_tasks = []
        orchestrator.validate_outputs.return_value = mock_validation

        # Mock cost tracking
        orchestrator.get_cost.return_value = 0.019
        orchestrator.get_stats.return_value = {'cost': 0.019}

        return orchestrator

    def test_builder_initialization(self, mock_orchestrator):
        """Test builder initialization"""
        builder = IntegrationBuilder(mock_orchestrator)
        assert builder.orchestrator == mock_orchestrator
        assert len(builder.build_history) == 0

    def test_build_integration_with_type(self, mock_orchestrator):
        """Test building integration with explicit type"""
        builder = IntegrationBuilder(mock_orchestrator)

        package = builder.build_integration(
            service_name='TestAPI',
            integration_type='api',
            requirements={'base_url': 'https://api.test.com'}
        )

        assert isinstance(package, IntegrationPackage)
        assert package.service_name == 'TestAPI'
        assert package.pattern_type == 'APIIntegrationPattern'
        assert len(builder.build_history) == 1

    def test_build_integration_auto_detect(self, mock_orchestrator):
        """Test building integration with auto-detection"""
        builder = IntegrationBuilder(mock_orchestrator)

        package = builder.build_integration(
            service_name='TestAPI',
            requirements={
                'type': 'api',
                'base_url': 'https://api.test.com'
            }
        )

        assert isinstance(package, IntegrationPackage)
        assert 'API' in package.pattern_type

    def test_build_metrics_tracking(self, mock_orchestrator):
        """Test metrics tracking during build"""
        builder = IntegrationBuilder(mock_orchestrator)

        start = time.time()
        package = builder.build_integration(
            service_name='TestAPI',
            integration_type='api',
            requirements={'base_url': 'https://api.test.com'}
        )
        end = time.time()

        metrics = package.metadata['build_metrics']
        assert 'total_cost' in metrics
        assert 'duration_seconds' in metrics
        assert 'validation_score' in metrics
        assert metrics['duration_seconds'] <= (end - start) + 0.1

    def test_get_average_metrics(self, mock_orchestrator):
        """Test average metrics calculation"""
        builder = IntegrationBuilder(mock_orchestrator)

        # Build multiple integrations
        for i in range(3):
            builder.build_integration(
                service_name=f'TestAPI{i}',
                integration_type='api',
                requirements={'base_url': f'https://api{i}.test.com'}
            )

        avg_metrics = builder.get_average_metrics()
        assert avg_metrics['build_count'] == 3
        assert 'avg_cost' in avg_metrics
        assert 'avg_duration_seconds' in avg_metrics


class TestUtilities:
    """Test utility library components"""

    def test_retry_helper_success(self):
        """Test retry helper with successful call"""
        call_count = 0

        @RetryHelper(max_attempts=3)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_helper_failure_then_success(self):
        """Test retry helper with eventual success"""
        call_count = 0

        @RetryHelper(max_attempts=3, base_delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        result = test_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_helper_all_failures(self):
        """Test retry helper with all failures"""
        call_count = 0

        @RetryHelper(max_attempts=3, base_delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Permanent failure")

        with pytest.raises(ValueError):
            test_function()

        assert call_count == 3

    def test_rate_limiter_basic(self):
        """Test basic rate limiting"""
        limiter = RateLimiter(calls_per_minute=60)  # 1 per second

        # First call should succeed immediately
        start = time.time()
        with limiter:
            pass
        duration = time.time() - start
        assert duration < 0.1

    def test_rate_limiter_enforcement(self):
        """Test rate limiter enforcement"""
        limiter = RateLimiter(calls_per_minute=120)  # 2 per second

        # Make 3 calls - third should be delayed
        start = time.time()
        for i in range(3):
            with limiter:
                pass
        duration = time.time() - start

        # Should take at least 0.5 seconds (for 3rd call)
        assert duration >= 0.4

    def test_metrics_collector_tracking(self):
        """Test metrics collector tracking"""
        metrics = MetricsCollector()

        # Track successful operation
        with metrics.track('test_operation', cost=0.001):
            time.sleep(0.01)

        stats = metrics.get_metrics('test_operation')
        assert stats['test_operation']['total_calls'] == 1
        assert stats['test_operation']['successful_calls'] == 1
        assert stats['test_operation']['total_cost'] == 0.001

    def test_metrics_collector_failure(self):
        """Test metrics collector with failure"""
        metrics = MetricsCollector()

        try:
            with metrics.track('test_operation'):
                raise ValueError("Test error")
        except ValueError:
            pass

        stats = metrics.get_metrics('test_operation')
        assert stats['test_operation']['failed_calls'] == 1
        assert stats['test_operation']['success_rate'] == 0.0

    def test_secret_manager_get(self):
        """Test secret manager get"""
        secrets = SecretManager()

        # Set test secret
        secrets.set('TEST_KEY', 'test_value')
        value = secrets.get('TEST_KEY')
        assert value == 'test_value'

    def test_secret_manager_required(self):
        """Test secret manager required validation"""
        secrets = SecretManager()

        with pytest.raises(ValueError):
            secrets.get('NONEXISTENT_KEY', required=True)

    def test_secret_manager_default(self):
        """Test secret manager default value"""
        secrets = SecretManager()

        value = secrets.get('NONEXISTENT_KEY', required=False, default='default')
        assert value == 'default'

    def test_cache_manager_basic(self):
        """Test cache manager basic operations"""
        cache = CacheManager(default_ttl=60)

        # Set and get
        cache.set('test_key', 'test_value')
        value = cache.get('test_key')
        assert value == 'test_value'

        # Miss
        value = cache.get('nonexistent', default='default')
        assert value == 'default'

    def test_cache_manager_expiration(self):
        """Test cache TTL expiration"""
        cache = CacheManager(default_ttl=0.1)

        cache.set('test_key', 'test_value', ttl=0.1)
        value = cache.get('test_key')
        assert value == 'test_value'

        # Wait for expiration
        time.sleep(0.2)
        value = cache.get('test_key', default='expired')
        assert value == 'expired'

    def test_cache_manager_decorator(self):
        """Test cache manager decorator"""
        cache = CacheManager()
        call_count = 0

        @cache.cached(ttl=60)
        def expensive_function(arg):
            nonlocal call_count
            call_count += 1
            return f"result_{arg}"

        # First call
        result1 = expensive_function('test')
        assert result1 == "result_test"
        assert call_count == 1

        # Second call (cached)
        result2 = expensive_function('test')
        assert result2 == "result_test"
        assert call_count == 1  # Not called again

    def test_error_handler_handling(self):
        """Test error handler basic handling"""
        handler = ErrorHandler()

        error = ValueError("Test error")
        with pytest.raises(ValueError):
            handler.handle(error, context={'operation': 'test'}, reraise=True)

        # Should not raise
        handler.handle(error, context={'operation': 'test'}, reraise=False)

    def test_error_handler_retry_decision(self):
        """Test error handler retry decision"""
        handler = ErrorHandler()

        # Should retry API errors
        error = APIError("API failure")
        assert handler.should_retry(error, attempt=0, max_attempts=3)

        # Should not retry auth errors
        error = AuthenticationError("Auth failed")
        assert not handler.should_retry(error, attempt=0, max_attempts=3)

        # Should not retry on last attempt
        error = APIError("API failure")
        assert not handler.should_retry(error, attempt=2, max_attempts=3)

    def test_error_handler_stats(self):
        """Test error handler statistics"""
        handler = ErrorHandler()

        # Handle some errors
        handler.handle(ValueError("Error 1"), reraise=False)
        handler.handle(ValueError("Error 2"), reraise=False)
        handler.handle(TypeError("Error 3"), reraise=False)

        stats = handler.get_error_stats()
        assert stats['total_errors'] == 3
        assert stats['by_type']['ValueError'] == 2
        assert stats['by_type']['TypeError'] == 1


class TestIntegrationPackage:
    """Test integration package functionality"""

    def test_package_creation(self):
        """Test integration package creation"""
        package = IntegrationPackage(
            service_name='TestAPI',
            pattern_type='APIIntegrationPattern',
            adapter_code='# adapter code',
            test_code='# test code',
            documentation='# docs',
            config_schema={'key': 'value'},
            examples='# examples'
        )

        assert package.service_name == 'TestAPI'
        assert package.adapter_code == '# adapter code'

    def test_package_to_dict(self):
        """Test package serialization"""
        package = IntegrationPackage(
            service_name='TestAPI',
            pattern_type='APIIntegrationPattern',
            adapter_code='code',
            test_code='tests',
            documentation='docs',
            config_schema={},
            examples='examples'
        )

        data = package.to_dict()
        assert data['service_name'] == 'TestAPI'
        assert 'adapter_code' in data
        assert 'test_code' in data

    @pytest.mark.skip(reason="Requires file system operations")
    def test_package_save_to_directory(self, tmp_path):
        """Test saving package to directory"""
        package = IntegrationPackage(
            service_name='TestAPI',
            pattern_type='APIIntegrationPattern',
            adapter_code='code',
            test_code='tests',
            documentation='docs',
            config_schema={'key': 'value'},
            examples='examples'
        )

        output_dir = tmp_path / "integration"
        package.save_to_directory(str(output_dir))

        assert (output_dir / "testapi_adapter.py").exists()
        assert (output_dir / "test_testapi_adapter.py").exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=agentflow.orchestration', '--cov-report=term-missing'])
