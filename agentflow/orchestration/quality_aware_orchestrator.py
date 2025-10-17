"""
Quality-Aware Orchestrator - SmartOrchestrator + QualityAwareTaskRouter Integration

Wraps SmartOrchestrator with quality-aware routing to prevent delegation failures.

Architecture:
    User Task
        ↓
    QualityAwareOrchestrator (THIS MODULE)
        ├─ Quality prediction & routing decision
        ├─ Task rejection for unsuitable tasks
        └─ Route to appropriate handler:
            ├─ DELEGATE → SmartOrchestrator
            ├─ HYBRID → HybridOrchestrator
            ├─ ESCALATE → Premium model
            └─ REJECT → Raise TaskRejectionError
        ↓
    Results

Benefits:
- Prevents failures like code audit ($0.17 wasted)
- Routes tasks to optimal handlers
- Provides quality predictions before delegation
- Transparent cost/quality tradeoffs

Usage:
    orchestrator = QualityAwareOrchestrator()

    try:
        result = orchestrator.orchestrate(
            task="Audit this code...",
            requirements={'needs_file_line_refs': True}
        )
        print(result)

    except TaskRejectionError as e:
        print(f"Task rejected: {e.decision.reasoning}")
        # User can: (1) Use Claude directly, (2) Enable premium, (3) Simplify task
"""

import structlog
from typing import Dict, Any, Optional

from agentflow.orchestration.smart_orchestrator import SmartOrchestrator
from agentflow.orchestration.hybrid_orchestrator import HybridOrchestrator
from agentflow.orchestration.quality_aware_task_router import (
    QualityAwareTaskRouter,
    TaskRejectionError,
    RoutingAction,
    RoutingDecision
)

logger = structlog.get_logger(__name__)


class QualityAwareOrchestrator:
    """
    Quality-aware orchestrator with pre-delegation quality prediction.

    Integrates:
    - QualityAwareTaskRouter (quality prediction)
    - SmartOrchestrator (cost-effective delegation)
    - HybridOrchestrator (validation workflow)

    Workflow:
    1. Analyze task and predict quality
    2. Make routing decision (delegate/reject/escalate/hybrid)
    3. Execute with appropriate orchestrator
    4. Return result with metadata

    Cost Savings:
    - REJECT unsuitable tasks: $0 vs $0.17+ wasted
    - DELEGATE suitable tasks: $0.10 vs $3+ (97% savings)
    - HYBRID medium tasks: $0.25 vs $3+ (92% savings)
    - ESCALATE critical tasks: $3 with quality guarantee
    """

    def __init__(
        self,
        enable_quality_routing: bool = True,
        rejection_threshold: int = 60,
        hybrid_threshold: int = 80,
        default_provider: str = "deepseek",
        project_root: Optional[str] = None
    ):
        """
        Initialize QualityAwareOrchestrator.

        Args:
            enable_quality_routing: Enable quality-aware routing (default: True)
            rejection_threshold: Min quality to avoid rejection (default: 60)
            hybrid_threshold: Min quality to avoid hybrid (default: 80)
            default_provider: Default model provider (default: "deepseek")
            project_root: Project root for QualityGuardian (optional)
        """
        self.enable_quality_routing = enable_quality_routing

        # Initialize orchestrators
        self.smart_orchestrator = SmartOrchestrator(provider=default_provider)
        self.hybrid_orchestrator = HybridOrchestrator(
            smart_orchestrator=self.smart_orchestrator,
            project_root=project_root
        )

        # Initialize quality router (if enabled)
        if enable_quality_routing:
            self.quality_router = QualityAwareTaskRouter(
                rejection_threshold=rejection_threshold,
                hybrid_threshold=hybrid_threshold,
                default_provider=default_provider
            )
        else:
            self.quality_router = None

        logger.info(
            "quality_aware_orchestrator_initialized",
            enable_quality_routing=enable_quality_routing,
            rejection_threshold=rejection_threshold,
            hybrid_threshold=hybrid_threshold,
            default_provider=default_provider
        )

    def orchestrate(
        self,
        task: str,
        requirements: Optional[Dict[str, Any]] = None,
        force_delegate: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrate task with quality-aware routing.

        Args:
            task: Task description
            requirements: Optional requirements dict:
                - needs_file_line_refs: bool
                - no_placeholders: bool
                - allow_premium: bool
                - input_size: int (bytes)
            force_delegate: Skip quality routing and delegate directly
                           (for testing or when user overrides)

        Returns:
            Dict with:
                - result: Task output
                - routing_decision: Quality prediction & routing info
                - cost_estimate: Estimated cost
                - quality_score: Predicted or actual quality (0-100)
                - metadata: Additional execution metadata

        Raises:
            TaskRejectionError: If task rejected by quality router
        """
        requirements = requirements or {}

        # Phase 0: Quality-aware routing (if enabled)
        if self.enable_quality_routing and not force_delegate:
            try:
                decision = self.quality_router.route_task(task, requirements)

                logger.info(
                    "routing_decision_made",
                    action=decision.action.value,
                    predicted_quality=decision.predicted_quality,
                    reasoning=decision.reasoning
                )

                # Execute based on routing decision
                if decision.action == RoutingAction.DELEGATE:
                    return self._execute_delegation(task, decision, requirements)

                elif decision.action == RoutingAction.HYBRID:
                    return self._execute_hybrid(task, decision, requirements)

                elif decision.action == RoutingAction.ESCALATE:
                    return self._execute_premium(task, decision, requirements)

                elif decision.action == RoutingAction.REJECT:
                    # This should be unreachable (route_task raises TaskRejectionError)
                    # But handle defensively
                    raise TaskRejectionError(decision)

            except TaskRejectionError:
                # Re-raise rejection errors
                raise

        else:
            # Quality routing disabled or forced delegation
            logger.info(
                "quality_routing_bypassed",
                force_delegate=force_delegate,
                enable_quality_routing=self.enable_quality_routing
            )

            # Create dummy decision for metadata
            decision = RoutingDecision(
                action=RoutingAction.DELEGATE,
                predicted_quality=85,  # Optimistic default
                reasoning="Quality routing bypassed (force_delegate or disabled)",
                provider="deepseek",
                model="deepseek-chat"
            )

            return self._execute_delegation(task, decision, requirements)

    def _execute_delegation(
        self,
        task: str,
        decision: RoutingDecision,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute standard delegation with SmartOrchestrator.

        Args:
            task: Task description
            decision: Routing decision
            requirements: Task requirements

        Returns:
            Result dict with metadata
        """
        logger.info(
            "executing_delegation",
            provider=decision.provider,
            model=decision.model,
            predicted_quality=decision.predicted_quality
        )

        # Delegate to SmartOrchestrator
        result = self.smart_orchestrator.orchestrate(task)

        return {
            'result': result,
            'routing_decision': decision.to_dict(),
            'orchestrator': 'SmartOrchestrator',
            'cost_estimate': 0.10,  # DeepSeek V3 typical cost
            'quality_score': decision.predicted_quality,
            'metadata': {
                'provider': decision.provider,
                'model': decision.model,
                'workflow': 'standard_delegation'
            }
        }

    def _execute_hybrid(
        self,
        task: str,
        decision: RoutingDecision,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute hybrid workflow with validation.

        Workflow:
        1. Delegate to cheap model (DeepSeek V3)
        2. Validate with Claude (quality check)
        3. Auto-fix if score < threshold

        Args:
            task: Task description
            decision: Routing decision
            requirements: Task requirements

        Returns:
            Result dict with metadata
        """
        logger.info(
            "executing_hybrid_workflow",
            predicted_quality=decision.predicted_quality,
            workflow=decision.workflow
        )

        # Use HybridOrchestrator for validation workflow
        result = self.hybrid_orchestrator.orchestrate_with_validation(
            task=task,
            max_retries=2,
            use_quality_guardian=True
        )

        return {
            'result': result.get('code', result.get('result', 'No output')),
            'routing_decision': decision.to_dict(),
            'orchestrator': 'HybridOrchestrator',
            'cost_estimate': 0.25,  # Delegation + validation
            'quality_score': result.get('validation_score', decision.predicted_quality),
            'metadata': {
                'workflow': 'hybrid_validation',
                'iterations': result.get('iteration', 1),
                'validation_passed': result.get('validation_score', 0) >= 80
            }
        }

    def _execute_premium(
        self,
        task: str,
        decision: RoutingDecision,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute with premium model (escalation).

        Note: This creates a new SmartOrchestrator with premium provider.

        Args:
            task: Task description
            decision: Routing decision
            requirements: Task requirements

        Returns:
            Result dict with metadata
        """
        logger.info(
            "executing_premium_escalation",
            provider=decision.provider,
            model=decision.model,
            predicted_quality=decision.predicted_quality
        )

        # Create premium orchestrator
        premium_orchestrator = SmartOrchestrator(
            provider=decision.provider,
            model=decision.model
        )

        # Delegate to premium model
        result = premium_orchestrator.orchestrate(task)

        return {
            'result': result,
            'routing_decision': decision.to_dict(),
            'orchestrator': 'SmartOrchestrator (Premium)',
            'cost_estimate': 3.00,  # Claude Sonnet 4 typical cost
            'quality_score': 95,  # Premium models have high quality ceiling
            'metadata': {
                'provider': decision.provider,
                'model': decision.model,
                'workflow': 'premium_escalation'
            }
        }

    def explain_routing(self, task: str, requirements: Optional[Dict[str, Any]] = None) -> str:
        """
        Explain routing decision without executing task.

        Useful for:
        - Understanding why a task would be rejected
        - Previewing cost before execution
        - Debugging routing logic

        Args:
            task: Task description
            requirements: Task requirements

        Returns:
            Human-readable explanation string
        """
        if not self.enable_quality_routing:
            return "Quality routing is disabled. Task would be delegated directly."

        try:
            decision = self.quality_router.route_task(task, requirements or {})
            return self.quality_router.explain_decision(decision)

        except TaskRejectionError as e:
            return (
                f"TASK WOULD BE REJECTED\n\n"
                f"{self.quality_router.explain_decision(e.decision)}\n\n"
                f"Alternatives:\n"
                f"1. Use Claude Code directly for this task\n"
                f"2. Enable premium escalation (allow_premium=True)\n"
                f"3. Simplify task requirements\n"
            )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get orchestration statistics.

        Returns:
            Dict with usage statistics
        """
        return {
            'quality_routing_enabled': self.enable_quality_routing,
            'rejection_threshold': self.quality_router.rejection_threshold if self.quality_router else None,
            'hybrid_threshold': self.quality_router.hybrid_threshold if self.quality_router else None,
            'default_provider': self.smart_orchestrator.provider,
            'orchestrators': {
                'smart': 'SmartOrchestrator',
                'hybrid': 'HybridOrchestrator',
                'quality_router': 'QualityAwareTaskRouter' if self.quality_router else None
            }
        }
