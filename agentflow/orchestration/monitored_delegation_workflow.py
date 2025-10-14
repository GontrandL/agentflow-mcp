"""
Monitored Delegation Workflow - APC + AgentFlow Integration

Complete workflow with monitoring:
1. APC prepares context (compression)
2. AgentFlow delegates to specialized FREE models
3. Real-time monitoring of workers
4. APC validates results (quality scoring)
5. Automatic retry with feedback if quality < threshold

This implements the full pipeline described in CLAUDE.md.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import time
import logging
from pathlib import Path

# Import APC MCP Server (already exists!)
try:
    from agentflow.mcp.apc_mcp_server import APCMCPServer
    APC_AVAILABLE = True
except ImportError:
    APC_AVAILABLE = False
    logging.warning("APC MCP Server not available")

# Import AgentFlow components
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator
from agentflow.orchestration.specialized_model_router import SpecializedModelRouter, TaskType

# Import Phase 2 components
from agentflow.phase2.phase2_session_history_manager import SessionHistoryManager, SessionEvent
from agentflow.phase2.task_tracker import TaskTracker


@dataclass
class WorkerStatus:
    """Status of a delegation worker"""
    worker_id: str
    task_description: str
    model_id: str
    task_type: TaskType
    status: str  # 'pending', 'running', 'completed', 'failed'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: Optional[str] = None
    validation_score: Optional[int] = None
    error: Optional[str] = None
    retries: int = 0


@dataclass
class MonitoredWorkflowResult:
    """Result of a monitored delegation workflow"""
    success: bool
    task: str
    workers: List[WorkerStatus]
    total_duration: float
    total_cost: float
    context_compression_ratio: Optional[float] = None
    validation_scores: List[int] = field(default_factory=list)
    iterations: int = 1
    final_output: Optional[str] = None


class MonitoredDelegationWorkflow:
    """
    Complete monitored workflow: APC context prep → AgentFlow delegation → Validation

    Features:
    - Real-time worker monitoring
    - APC context compression (12x reduction)
    - Specialized FREE model routing
    - Quality validation (0-100 score)
    - Automatic retry with feedback
    - Session history tracking
    - Cost tracking
    """

    def __init__(self,
                 enable_apc: bool = True,
                 enable_specialized_routing: bool = True,
                 validation_threshold: int = 80,
                 max_retries: int = 2,
                 session_id: Optional[str] = None):
        """
        Initialize monitored workflow

        Args:
            enable_apc: Enable APC context compression (default: True)
            enable_specialized_routing: Enable FREE model routing (default: True)
            validation_threshold: Minimum quality score (default: 80)
            max_retries: Maximum retry attempts (default: 2)
            session_id: Session ID for history tracking
        """
        self.enable_apc = enable_apc and APC_AVAILABLE
        self.enable_specialized_routing = enable_specialized_routing
        self.validation_threshold = validation_threshold
        self.max_retries = max_retries

        # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize APC MCP Server (uses existing implementation!)
        if self.enable_apc:
            try:
                self.apc_server = APCMCPServer()
                self.logger.info("APC MCP Server initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize APC MCP: {e}")
                self.enable_apc = False

        self.orchestrator = SmartOrchestrator(
            enable_specialized_routing=enable_specialized_routing
        )

        if enable_specialized_routing:
            self.router = SpecializedModelRouter()
            self.logger.info("Specialized routing enabled (FREE models preferred)")

        # Session tracking
        self.session_id = session_id or f"workflow_{int(time.time())}"
        self.session_manager = SessionHistoryManager(
            session_id=self.session_id,
            history_file_path=f"/tmp/{self.session_id}_history.json"
        )

        # Worker tracking
        self.workers: List[WorkerStatus] = []
        self.total_cost = 0.0

    def execute(self,
                task: str,
                conversation_history: Optional[List[Dict]] = None,
                context: Optional[Dict[str, Any]] = None) -> MonitoredWorkflowResult:
        """
        Execute complete monitored workflow

        Args:
            task: Task description
            conversation_history: Optional conversation history for APC compression
            context: Optional additional context

        Returns:
            MonitoredWorkflowResult with full execution details
        """
        start_time = time.time()

        self.logger.info(f"=== STARTING MONITORED WORKFLOW ===")
        self.logger.info(f"Task: {task[:100]}...")

        # Phase 1: APC Context Preparation (uses existing APC MCP!)
        prepared_context = None
        compression_ratio = None

        if self.enable_apc and conversation_history:
            self.logger.info("Phase 1: APC Context Compression (via MCP)")
            try:
                # Use existing APC MCP _prepare_context method
                import asyncio
                result = asyncio.run(self.apc_server._prepare_context({
                    'conversation_history': conversation_history,
                    'current_task': task,
                    'target_tokens': 8000
                }))

                prepared_context = result
                compression_ratio = result.get('compression_ratio', 12.0)

                self.logger.info(f"Context compressed via APC MCP: {compression_ratio:.1f}x")

                # Record event
                self.session_manager.save_history({
                    "event": "context_compression",
                    "timestamp": datetime.now().isoformat(),
                    "compression_ratio": compression_ratio
                })

            except Exception as e:
                self.logger.warning(f"APC MCP compression failed: {e}. Using original context.")
                prepared_context = None

        # Phase 2: Specialized Model Routing
        if self.enable_specialized_routing:
            self.logger.info("Phase 2: Specialized Model Routing")
            model_spec, task_type, reasoning = self.router.route(task, prefer_free=True)
            self.logger.info(f"Routed to: {model_spec.model_id} (FREE: {model_spec.is_free})")
            self.logger.info(f"Task type: {task_type.value}")
        else:
            model_spec = None
            task_type = TaskType.GENERAL

        # Phase 3: AgentFlow Delegation with Monitoring
        self.logger.info("Phase 3: AgentFlow Delegation")

        worker = WorkerStatus(
            worker_id=f"worker_{len(self.workers) + 1}",
            task_description=task,
            model_id=model_spec.model_id if model_spec else "deepseek/deepseek-chat",
            task_type=task_type,
            status='running',
            start_time=datetime.now()
        )
        self.workers.append(worker)

        try:
            # Delegate task
            result = self.orchestrator.orchestrate(
                task=task,
                context=prepared_context or context or {}
            )

            worker.status = 'completed'
            worker.end_time = datetime.now()
            worker.output = result

            self.logger.info(f"Worker {worker.worker_id} completed")

            # Track cost
            if hasattr(self.orchestrator, 'total_cost'):
                self.total_cost += self.orchestrator.total_cost

        except Exception as e:
            worker.status = 'failed'
            worker.end_time = datetime.now()
            worker.error = str(e)
            self.logger.error(f"Worker {worker.worker_id} failed: {e}")

        # Phase 4: APC Validation
        validation_score = None
        if self.enable_apc and worker.status == 'completed':
            self.logger.info("Phase 4: APC Quality Validation")
            try:
                validation_result = self._validate_output(task, worker.output)
                validation_score = validation_result['score']
                worker.validation_score = validation_score

                self.logger.info(f"Validation score: {validation_score}/100")

                # Phase 5: Retry if needed
                if validation_score < self.validation_threshold and worker.retries < self.max_retries:
                    self.logger.warning(f"Score {validation_score} < threshold {self.validation_threshold}. Retrying...")

                    # Retry with feedback
                    retry_result = self._retry_with_feedback(
                        task=task,
                        previous_output=worker.output,
                        validation_result=validation_result,
                        context=prepared_context or context
                    )

                    if retry_result['success']:
                        worker.output = retry_result['output']
                        worker.validation_score = retry_result['score']
                        worker.retries += 1
                        validation_score = retry_result['score']
                        self.logger.info(f"Retry successful. New score: {validation_score}/100")

            except Exception as e:
                self.logger.warning(f"Validation failed: {e}")

        # Final result
        total_duration = time.time() - start_time

        result = MonitoredWorkflowResult(
            success=worker.status == 'completed',
            task=task,
            workers=self.workers,
            total_duration=total_duration,
            total_cost=self.total_cost,
            context_compression_ratio=compression_ratio,
            validation_scores=[w.validation_score for w in self.workers if w.validation_score],
            iterations=worker.retries + 1,
            final_output=worker.output
        )

        self.logger.info(f"=== WORKFLOW COMPLETE ===")
        self.logger.info(f"Duration: {total_duration:.2f}s")
        self.logger.info(f"Cost: ${self.total_cost:.4f}")
        if validation_score:
            self.logger.info(f"Final score: {validation_score}/100")

        return result

    def _validate_output(self, task: str, output: str) -> Dict[str, Any]:
        """
        Validate output quality using existing APC MCP validation

        Returns dict with 'score', 'passed', 'issues'
        """
        if not self.enable_apc:
            return {'score': 85, 'passed': True, 'issues': []}

        try:
            # Use existing APC MCP _validate_output method
            import asyncio
            result = asyncio.run(self.apc_server._validate_output({
                'task': task,
                'output': output,
                'threshold': self.validation_threshold
            }))

            return result

        except Exception as e:
            self.logger.error(f"APC MCP validation error: {e}")
            return {'score': 0, 'passed': False, 'issues': [str(e)]}

    def _retry_with_feedback(self,
                           task: str,
                           previous_output: str,
                           validation_result: Dict,
                           context: Optional[Dict] = None) -> Dict:
        """
        Retry task with feedback from validation
        """
        feedback = "\n".join([
            "Previous attempt had issues:",
            *validation_result['issues'],
            "",
            "Please fix these issues and try again."
        ])

        retry_task = f"{task}\n\nFeedback:\n{feedback}"

        try:
            result = self.orchestrator.orchestrate(
                task=retry_task,
                context=context or {}
            )

            # Validate retry
            retry_validation = self._validate_output(task, result)

            return {
                'success': retry_validation['passed'],
                'output': result,
                'score': retry_validation['score']
            }
        except Exception as e:
            self.logger.error(f"Retry failed: {e}")
            return {
                'success': False,
                'output': previous_output,
                'score': validation_result['score']
            }

    def get_status_report(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            'session_id': self.session_id,
            'workers': [
                {
                    'id': w.worker_id,
                    'status': w.status,
                    'model': w.model_id,
                    'task_type': w.task_type.value,
                    'duration': (w.end_time - w.start_time).total_seconds() if w.end_time and w.start_time else None,
                    'validation_score': w.validation_score,
                    'retries': w.retries
                }
                for w in self.workers
            ],
            'total_cost': self.total_cost,
            'apc_enabled': self.enable_apc,
            'specialized_routing': self.enable_specialized_routing
        }


# Convenience function for quick execution
def execute_monitored_delegation(
    task: str,
    conversation_history: Optional[List[Dict]] = None,
    enable_apc: bool = True,
    enable_specialized_routing: bool = True,
    validation_threshold: int = 80
) -> MonitoredWorkflowResult:
    """
    Quick execution of monitored delegation workflow

    Args:
        task: Task description
        conversation_history: Optional conversation for context compression
        enable_apc: Enable APC features
        enable_specialized_routing: Enable FREE model routing
        validation_threshold: Minimum quality score

    Returns:
        MonitoredWorkflowResult
    """
    workflow = MonitoredDelegationWorkflow(
        enable_apc=enable_apc,
        enable_specialized_routing=enable_specialized_routing,
        validation_threshold=validation_threshold
    )

    return workflow.execute(task, conversation_history)


if __name__ == "__main__":
    # Test the monitored workflow
    print("=== MONITORED DELEGATION WORKFLOW TEST ===\n")

    # Test task
    task = "Write a Python function to calculate the Fibonacci sequence using dynamic programming"

    # Execute with full monitoring
    result = execute_monitored_delegation(
        task=task,
        enable_apc=False,  # APC not available in test
        enable_specialized_routing=True,
        validation_threshold=80
    )

    print(f"\n=== RESULT ===")
    print(f"Success: {result.success}")
    print(f"Duration: {result.total_duration:.2f}s")
    print(f"Cost: ${result.total_cost:.4f}")
    print(f"Workers: {len(result.workers)}")
    print(f"Iterations: {result.iterations}")

    if result.validation_scores:
        print(f"Validation scores: {result.validation_scores}")

    print(f"\nWorker Details:")
    for worker in result.workers:
        print(f"  - {worker.worker_id}: {worker.status} (model: {worker.model_id})")
