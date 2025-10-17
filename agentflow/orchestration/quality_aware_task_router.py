"""
Quality-Aware Task Router - Phase 0 Implementation

Extends AgentFlow with quality prediction and task rejection capabilities.

Architecture:
    User Task
        ↓
    QualityAwareTaskRouter (THIS MODULE)
        ├─ Classify task type (GENERATIVE vs ANALYTICAL)
        ├─ Predict quality (0-100 score)
        └─ Route decision (delegate/reject/escalate/hybrid)
        ↓
    SmartOrchestrator (if delegated)
        ↓
    HybridOrchestrator (if hybrid)

Key Insight: Not all tasks are equal - analytical tasks (audits, reviews)
            need different routing than generative tasks (code, docs).

Root Cause Addressed: Code audit failure (DeepSeek V3 produced generic
                      templates instead of real analysis) due to analytical
                      task with 119KB embedded code exceeding FREE model
                      capabilities.

Solution: Reject unsuitable tasks BEFORE delegation to prevent wasted resources.
"""

import re
import structlog
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger(__name__)


class TaskType(Enum):
    """Task classification types"""
    GENERATIVE = "generative"  # Create new content (code, docs, specs)
    ANALYTICAL = "analytical"   # Examine existing content (audit, review)
    HYBRID = "hybrid"           # Both generation and analysis


class RoutingAction(Enum):
    """Routing decision actions"""
    DELEGATE = "delegate"       # Standard delegation to cost-effective model
    REJECT = "reject"           # Task unsuitable for cost-effective delegation
    ESCALATE = "escalate"       # Route to premium model (guaranteed quality)
    HYBRID = "hybrid"           # FREE generation + premium validation


@dataclass
class RoutingDecision:
    """
    Routing decision with quality prediction.

    Attributes:
        action: What to do with this task
        predicted_quality: Expected quality score (0-100)
        reasoning: Why this decision was made
        provider: Model provider (if delegating)
        model: Model ID (if delegating)
        workflow: Workflow type (if hybrid)
        metadata: Additional decision metadata
    """
    action: RoutingAction
    predicted_quality: int
    reasoning: str
    provider: Optional[str] = None
    model: Optional[str] = None
    workflow: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'action': self.action.value,
            'predicted_quality': self.predicted_quality,
            'reasoning': self.reasoning,
            'provider': self.provider,
            'model': self.model,
            'workflow': self.workflow,
            'metadata': self.metadata or {}
        }


class TaskRejectionError(Exception):
    """Raised when task is rejected as unsuitable for delegation"""

    def __init__(self, decision: RoutingDecision):
        self.decision = decision
        super().__init__(
            f"Task rejected: {decision.reasoning} "
            f"(predicted quality: {decision.predicted_quality}/100)"
        )


class QualityAwareTaskRouter:
    """
    Quality-aware task router that predicts success before delegation.

    Phase 0: Rule-based quality prediction (no ML required)

    Capabilities:
    - Task type classification (GENERATIVE vs ANALYTICAL)
    - Quality prediction (0-100 score based on heuristics)
    - Task rejection for unsuitable delegations
    - Routing recommendations (delegate/reject/escalate/hybrid)

    Usage:
        router = QualityAwareTaskRouter()

        try:
            decision = router.route_task(
                task="Audit this code for bugs...",
                requirements={'needs_file_line_refs': True}
            )

            if decision.action == RoutingAction.DELEGATE:
                # Proceed with standard delegation
                orchestrator.orchestrate(task)

            elif decision.action == RoutingAction.HYBRID:
                # Use hybrid workflow
                hybrid_orchestrator.orchestrate_with_validation(task)

        except TaskRejectionError as e:
            # Task unsuitable for cost-effective delegation
            print(f"Rejected: {e.decision.reasoning}")
    """

    # Model capability matrix (learned from real delegation results)
    MODEL_CAPABILITIES = {
        'meta-llama/llama-3.3-70b-instruct:free': {
            'strengths': [
                'code_generation_simple',
                'documentation',
                'async_code'
            ],
            'weaknesses': [
                'code_audit',           # Produces generic templates
                'large_context',        # >50KB struggles
                'file_line_precision'   # Hard to get exact refs
            ],
            'max_effective_context': 50_000,  # bytes
            'quality_ceiling': 70  # Max quality score achievable
        },
        'deepseek/deepseek-chat': {
            'strengths': [
                'code_generation_complex',
                'reasoning',
                'async_code'
            ],
            'weaknesses': [
                'code_audit',            # Still struggles with analytical
                'embedded_code_analysis'  # Ignores provided code
            ],
            'max_effective_context': 100_000,
            'quality_ceiling': 75
        },
        'anthropic/claude-sonnet-4-20250514': {
            'strengths': [
                'code_audit',
                'code_review',
                'analytical_tasks',
                'file_line_precision',
                'large_context'
            ],
            'weaknesses': [
                'cost'  # Expensive ($3/M vs $0.14/M)
            ],
            'max_effective_context': 200_000,
            'quality_ceiling': 95
        }
    }

    # Default thresholds
    REJECTION_THRESHOLD = 60   # Reject if predicted quality < 60
    HYBRID_THRESHOLD = 80      # Use hybrid if < 80 but > 60

    def __init__(
        self,
        rejection_threshold: int = REJECTION_THRESHOLD,
        hybrid_threshold: int = HYBRID_THRESHOLD,
        default_provider: str = "deepseek",
        default_model: str = "deepseek-chat"
    ):
        """
        Initialize QualityAwareTaskRouter.

        Args:
            rejection_threshold: Minimum quality to avoid rejection (default: 60)
            hybrid_threshold: Minimum quality to avoid hybrid (default: 80)
            default_provider: Default model provider for delegation
            default_model: Default model for delegation
        """
        self.rejection_threshold = rejection_threshold
        self.hybrid_threshold = hybrid_threshold
        self.default_provider = default_provider
        self.default_model = default_model

        logger.info(
            "quality_router_initialized",
            rejection_threshold=rejection_threshold,
            hybrid_threshold=hybrid_threshold,
            default_provider=default_provider
        )

    def route_task(
        self,
        task: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Route task with quality awareness.

        Args:
            task: Task description
            requirements: Optional requirements dict with keys:
                - needs_file_line_refs: bool (requires file:line precision)
                - no_placeholders: bool (requires complete code)
                - allow_premium: bool (allow escalation to premium model)
                - input_size: int (input size in bytes)

        Returns:
            RoutingDecision with action, predicted_quality, reasoning

        Raises:
            TaskRejectionError: If task should be rejected
        """
        requirements = requirements or {}

        # Phase 0: Classify and predict quality
        task_type = self._classify_task_type(task, requirements)
        task_metadata = self._extract_metadata(task, requirements)
        predicted_quality = self._predict_quality(
            task_type, task_metadata, requirements
        )

        logger.info(
            "task_analysis_complete",
            task_type=task_type.value,
            predicted_quality=predicted_quality,
            input_size=task_metadata.get('input_size_bytes', 0),
            has_embedded_code=task_metadata.get('has_embedded_code', False)
        )

        # Phase 1: Decision logic
        if predicted_quality >= self.hybrid_threshold:
            # High confidence → Standard delegation
            return RoutingDecision(
                action=RoutingAction.DELEGATE,
                predicted_quality=predicted_quality,
                reasoning=f"High quality prediction ({predicted_quality}/100) with cost-effective model",
                provider=self.default_provider,
                model=self.default_model,
                metadata=task_metadata
            )

        elif predicted_quality >= self.rejection_threshold:
            # Medium confidence → Hybrid workflow
            return RoutingDecision(
                action=RoutingAction.HYBRID,
                predicted_quality=predicted_quality,
                reasoning=f"Analytical task requires validation ({predicted_quality}/100 predicted)",
                workflow="free_gen_premium_validation",
                metadata=task_metadata
            )

        else:
            # Low confidence → Reject or escalate
            if requirements.get('allow_premium', False):
                return RoutingDecision(
                    action=RoutingAction.ESCALATE,
                    predicted_quality=predicted_quality,
                    reasoning=f"Complex analytical task requires premium model ({predicted_quality}/100 with FREE)",
                    provider="anthropic",
                    model="claude-sonnet-4-20250514",
                    metadata=task_metadata
                )
            else:
                decision = RoutingDecision(
                    action=RoutingAction.REJECT,
                    predicted_quality=predicted_quality,
                    reasoning=f"Task unsuitable for cost-effective delegation ({predicted_quality}/100 predicted). Consider: (1) Use Claude directly, (2) Enable premium escalation, (3) Simplify task",
                    metadata=task_metadata
                )
                raise TaskRejectionError(decision)

    def _classify_task_type(
        self,
        task: str,
        requirements: Dict[str, Any]
    ) -> TaskType:
        """
        Classify task as GENERATIVE, ANALYTICAL, or HYBRID.

        GENERATIVE: Create new content
        - Code generation (implement X)
        - Documentation (write guide for Y)
        - Specs (create implementation spec)

        ANALYTICAL: Examine existing content
        - Code audit (find bugs in provided code)
        - Code review (analyze quality)
        - Research (investigate and analyze)

        HYBRID: Both generation and analysis
        - Generate with validation
        - Research then implement

        Args:
            task: Task description
            requirements: Task requirements

        Returns:
            TaskType enum value
        """
        task_lower = task.lower()

        # Keywords for analytical tasks
        analytical_keywords = [
            'audit', 'review', 'analyze', 'find bugs',
            'identify issues', 'examine', 'investigate',
            'evaluate', 'assess', 'validate existing'
        ]

        # Keywords for generative tasks
        generative_keywords = [
            'implement', 'create', 'build', 'generate',
            'write', 'design', 'develop', 'code'
        ]

        # Check for embedded code (sign of analytical task)
        has_embedded_code = (
            '```' in task and
            len(task) > 10_000  # Large code blocks
        )

        # Check for file:line requirements (analytical)
        needs_precise_refs = (
            requirements.get('needs_file_line_refs', False) or
            'file:line' in task_lower or
            'specific line' in task_lower
        )

        # Scoring
        analytical_score = sum(
            1 for keyword in analytical_keywords
            if keyword in task_lower
        )
        generative_score = sum(
            1 for keyword in generative_keywords
            if keyword in task_lower
        )

        if has_embedded_code or needs_precise_refs:
            analytical_score += 3

        # Classification
        if analytical_score > generative_score + 1:
            return TaskType.ANALYTICAL
        elif generative_score > analytical_score:
            return TaskType.GENERATIVE
        else:
            return TaskType.HYBRID

    def _extract_metadata(
        self,
        task: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract task metadata for quality prediction.

        Args:
            task: Task description
            requirements: Task requirements

        Returns:
            Dict with metadata:
                - input_size_bytes: int
                - has_embedded_code: bool
                - code_block_count: int
                - estimated_output_lines: int
        """
        # Input size
        input_size_bytes = len(task.encode('utf-8'))

        # Embedded code detection
        code_blocks = re.findall(r'```[\s\S]*?```', task)
        has_embedded_code = len(code_blocks) > 0
        code_block_count = len(code_blocks)

        # Estimate output size
        if 'comprehensive' in task.lower() or 'detailed' in task.lower():
            estimated_output_lines = 1000
        elif 'simple' in task.lower() or 'basic' in task.lower():
            estimated_output_lines = 200
        else:
            estimated_output_lines = 500

        return {
            'input_size_bytes': input_size_bytes,
            'has_embedded_code': has_embedded_code,
            'code_block_count': code_block_count,
            'estimated_output_lines': estimated_output_lines
        }

    def _predict_quality(
        self,
        task_type: TaskType,
        metadata: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> int:
        """
        Predict quality score (0-100) for task with cost-effective model.

        Phase 0: Rule-based heuristics (no ML)

        Factors:
        - Task type match (ANALYTICAL tasks fail on FREE models)
        - Context size (large contexts reduce quality)
        - Output requirements (file:line refs are hard)
        - Embedded code (harder to analyze than generate)

        Args:
            task_type: Classification result
            metadata: Extracted metadata
            requirements: Task requirements

        Returns:
            Quality score 0-100
        """
        base_score = 85  # Start optimistic for cost-effective models
        reasoning_parts = []

        # Task type penalties
        if task_type == TaskType.ANALYTICAL:
            # CRITICAL: Analytical tasks are hard for cost-effective models
            # Evidence: Code audit failure (119KB → generic templates)
            base_score -= 30  # Down to 55
            reasoning_parts.append("Analytical task (-30 points)")

        if task_type == TaskType.HYBRID:
            base_score -= 15  # Down to 70
            reasoning_parts.append("Hybrid task (-15 points)")

        # Context size penalties
        input_size = metadata.get('input_size_bytes', 0)
        if input_size > 100_000:  # >100KB
            base_score -= 20  # Large contexts reduce quality
            reasoning_parts.append(f"Large context {input_size//1000}KB (-20 points)")
        elif input_size > 50_000:  # >50KB
            base_score -= 10
            reasoning_parts.append(f"Medium context {input_size//1000}KB (-10 points)")

        # Embedded code penalty (analytical tasks with code are hardest)
        if metadata.get('has_embedded_code', False):
            base_score -= 15
            reasoning_parts.append(f"Embedded code blocks ({metadata.get('code_block_count', 0)}) (-15 points)")

        # Output requirement penalties
        if requirements.get('needs_file_line_refs', False):
            base_score -= 15  # Precise refs are hard for FREE models
            reasoning_parts.append("Requires file:line precision (-15 points)")

        if requirements.get('no_placeholders', False):
            base_score -= 10  # Complete code is hard
            reasoning_parts.append("No placeholders allowed (-10 points)")

        # Log reasoning
        predicted_quality = max(0, min(100, base_score))
        logger.info(
            "quality_prediction",
            predicted_quality=predicted_quality,
            reasoning=" | ".join(reasoning_parts) if reasoning_parts else "No penalties"
        )

        return predicted_quality

    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        """
        Get capabilities for specific model.

        Args:
            model: Model identifier (e.g., 'deepseek/deepseek-chat')

        Returns:
            Dict with strengths, weaknesses, limits
        """
        return self.MODEL_CAPABILITIES.get(model, {
            'strengths': [],
            'weaknesses': [],
            'max_effective_context': 50_000,
            'quality_ceiling': 70
        })

    def explain_decision(self, decision: RoutingDecision) -> str:
        """
        Get human-readable explanation of routing decision.

        Args:
            decision: Routing decision to explain

        Returns:
            Multi-line explanation string
        """
        lines = [
            "=" * 80,
            "ROUTING DECISION",
            "=" * 80,
            f"Action: {decision.action.value.upper()}",
            f"Predicted Quality: {decision.predicted_quality}/100",
            f"Reasoning: {decision.reasoning}",
        ]

        if decision.provider:
            lines.append(f"Provider: {decision.provider}")

        if decision.model:
            lines.append(f"Model: {decision.model}")

        if decision.workflow:
            lines.append(f"Workflow: {decision.workflow}")

        if decision.metadata:
            lines.append("")
            lines.append("Task Metadata:")
            for key, value in decision.metadata.items():
                lines.append(f"  {key}: {value}")

        lines.append("=" * 80)

        return "\n".join(lines)
