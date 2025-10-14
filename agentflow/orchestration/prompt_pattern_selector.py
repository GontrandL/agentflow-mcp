"""
Prompt Pattern Selector

Automatic selection of optimal prompt patterns based on task analysis.
Integrates with SmartOrchestrator for quality improvement through proven templates.

Discovery: Phase 3 validated 3x quality improvement with template-based prompts
"""

import yaml
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pathlib import Path

try:
    import structlog
    logger = structlog.get_logger(__name__)
    HAS_STRUCTLOG = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    HAS_STRUCTLOG = False


class TaskType(Enum):
    """Task type categories for pattern selection"""
    CODE_REVIEW = 'code_review'
    ARCHITECTURE_DESIGN = 'architecture_design'
    SECURITY_ANALYSIS = 'security_analysis'
    API_DEVELOPMENT = 'api_development'
    TESTING = 'testing'
    DOCUMENTATION = 'documentation'
    PERFORMANCE = 'performance'
    PR_REVIEW = 'pr_review'
    OPTIMIZATION = 'optimization'
    DATABASE_DESIGN = 'database_design'
    CONFIGURATION = 'configuration'
    UNKNOWN = 'unknown'


class PatternComplexity(Enum):
    """Pattern complexity levels"""
    SIMPLE = 'simple'
    MEDIUM = 'medium'
    COMPLEX = 'complex'


class PatternPriority(Enum):
    """Priority optimization targets"""
    QUALITY = 'quality'
    COST = 'cost'
    SPEED = 'speed'
    BALANCED = 'balanced'


@dataclass
class PatternMetrics:
    """Metrics for a prompt pattern"""
    quality_score: float
    success_rate: int
    avg_cost: float
    avg_tokens: int
    avg_latency_ms: int
    revision_rate: str
    use_count: int = 0
    last_used: Optional[str] = None


@dataclass
class PromptPattern:
    """Prompt pattern with metadata and template"""
    name: str
    category: str
    complexity: str
    quality_tier: int
    description: str
    template: str
    variables: Dict[str, str]
    metrics: PatternMetrics
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PatternSelectionResult:
    """Result of pattern selection"""
    pattern: PromptPattern
    confidence: float
    reasoning: str
    fallback_patterns: List[str] = field(default_factory=list)


class PromptPatternSelector:
    """
    Intelligent prompt pattern selection based on task analysis.

    Features:
    - Automatic pattern selection based on task type
    - Complexity-based routing
    - Priority optimization (quality/cost/speed)
    - Quality prediction
    - Pattern performance tracking
    """

    def __init__(self, pattern_library_path: Optional[str] = None):
        """
        Initialize PromptPatternSelector

        Args:
            pattern_library_path: Path to PROMPT_PATTERN_LIBRARY.yaml
        """
        if pattern_library_path is None:
            # Default path relative to this file
            current_dir = Path(__file__).parent.parent.parent.parent
            pattern_library_path = current_dir / "templates" / "PROMPT_PATTERN_LIBRARY.yaml"

        self.pattern_library_path = Path(pattern_library_path)
        self.patterns: Dict[str, PromptPattern] = {}
        self.pattern_selection_rules: Dict[str, Any] = {}
        self.quality_guidelines: Dict[str, Any] = {}

        self._load_pattern_library()

        self.logger = logger

    def _load_pattern_library(self):
        """Load pattern library from YAML file"""
        try:
            with open(self.pattern_library_path, 'r') as f:
                library = yaml.safe_load(f)

            # Load quality guidelines
            self.quality_guidelines = library.get('quality_guidelines', {})

            # Load pattern selection rules
            self.pattern_selection_rules = library.get('pattern_selection', {})

            # Load patterns from each category
            for category in ['analysis_patterns', 'generation_patterns',
                            'review_patterns', 'optimization_patterns']:
                patterns = library.get(category, {})
                for pattern_id, pattern_data in patterns.items():
                    self.patterns[pattern_id] = self._parse_pattern(pattern_id, pattern_data, category)

            if HAS_STRUCTLOG:
                self.logger.info(
                    "pattern_library_loaded",
                    patterns_count=len(self.patterns),
                    library_path=str(self.pattern_library_path)
                )
            else:
                self.logger.info(
                    f"Loaded {len(self.patterns)} patterns from {self.pattern_library_path}"
                )

        except Exception as e:
            self.logger.error(f"Failed to load pattern library: {e}")
            raise

    def _parse_pattern(self, pattern_id: str, data: Dict[str, Any], category: str) -> PromptPattern:
        """Parse pattern data into PromptPattern object"""
        metrics_data = data.get('metrics', {})

        # Parse cost (remove $ sign if present)
        avg_cost_str = str(metrics_data.get('avg_cost', '0'))
        avg_cost = float(avg_cost_str.replace('$', '').replace(',', ''))

        # Parse latency (remove 'ms' if present)
        avg_latency_str = str(data.get('avg_latency_ms', '0'))
        avg_latency = int(avg_latency_str.replace('ms', '').replace(',', ''))

        metrics = PatternMetrics(
            quality_score=data.get('quality_score', 5.0),
            success_rate=data.get('success_rate', 50),
            avg_cost=avg_cost,
            avg_tokens=data.get('avg_tokens', 1000),
            avg_latency_ms=avg_latency,
            revision_rate=metrics_data.get('revision_rate', '50%')
        )

        return PromptPattern(
            name=data.get('name', pattern_id),
            category=data.get('category', category.replace('_patterns', '')),
            complexity=data.get('complexity', 'medium'),
            quality_tier=data.get('quality_tier', 3),
            description=data.get('description', ''),
            template=data.get('template', ''),
            variables=data.get('variables', {}),
            metrics=metrics,
            examples=data.get('examples', [])
        )

    def detect_task_type(self, task: Dict[str, Any]) -> TaskType:
        """
        Detect task type from task description and context

        Args:
            task: Task dictionary with description, context, requirements

        Returns:
            TaskType enum value
        """
        description = str(task.get('description', '')).lower()
        context = str(task.get('context', '')).lower()
        combined_text = f"{description} {context}"

        # Keyword-based detection
        type_keywords = {
            TaskType.CODE_REVIEW: ['review code', 'code review', 'analyze code', 'check code'],
            TaskType.ARCHITECTURE_DESIGN: ['architecture', 'system design', 'design system', 'architectural'],
            TaskType.SECURITY_ANALYSIS: ['security', 'vulnerability', 'audit', 'penetration', 'exploit'],
            TaskType.API_DEVELOPMENT: ['api', 'endpoint', 'rest', 'graphql', 'route'],
            TaskType.TESTING: ['test', 'testing', 'unit test', 'integration test', 'e2e'],
            TaskType.DOCUMENTATION: ['document', 'documentation', 'readme', 'docs', 'api docs'],
            TaskType.PERFORMANCE: ['performance', 'optimize', 'bottleneck', 'latency', 'throughput'],
            TaskType.PR_REVIEW: ['pull request', 'pr review', 'merge request', 'mr review'],
            TaskType.OPTIMIZATION: ['optimize', 'optimization', 'cost reduction', 'improve'],
            TaskType.DATABASE_DESIGN: ['database', 'schema', 'migration', 'sql', 'nosql'],
            TaskType.CONFIGURATION: ['config', 'configuration', 'setup', 'yaml', 'json'],
        }

        # Score each task type
        scores = {}
        for task_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                scores[task_type] = score

        if scores:
            detected_type = max(scores.items(), key=lambda x: x[1])[0]

            if HAS_STRUCTLOG:
                self.logger.info(
                    "task_type_detected",
                    task_type=detected_type.value,
                    confidence=scores[detected_type]
                )

            return detected_type

        return TaskType.UNKNOWN

    def analyze_complexity(self, task: Dict[str, Any]) -> PatternComplexity:
        """
        Analyze task complexity

        Args:
            task: Task dictionary

        Returns:
            PatternComplexity enum value
        """
        score = 0

        # Factor 1: Context size
        context_size = len(str(task.get('description', ''))) + len(str(task.get('context', '')))
        if context_size < 1000:
            score += 1
        elif context_size < 5000:
            score += 2
        else:
            score += 3

        # Factor 2: Requirements count
        requirements = task.get('requirements', {})
        if isinstance(requirements, dict):
            req_count = len(requirements.get('edge_cases', [])) + len(requirements.get('validation_criteria', []))
        else:
            req_count = 0

        if req_count <= 3:
            score += 1
        elif req_count <= 8:
            score += 2
        else:
            score += 3

        # Factor 3: Explicit complexity
        explicit_complexity = task.get('complexity', 'medium').lower()
        if explicit_complexity == 'low':
            score += 1
        elif explicit_complexity == 'high':
            score += 3
        else:
            score += 2

        # Map score to complexity
        if score <= 4:
            return PatternComplexity.SIMPLE
        elif score <= 7:
            return PatternComplexity.MEDIUM
        else:
            return PatternComplexity.COMPLEX

    def select_pattern(
        self,
        task: Dict[str, Any],
        priority: PatternPriority = PatternPriority.BALANCED
    ) -> PatternSelectionResult:
        """
        Select optimal pattern for task

        Args:
            task: Task dictionary with description, context, requirements
            priority: Optimization priority (quality/cost/speed/balanced)

        Returns:
            PatternSelectionResult with selected pattern and metadata
        """
        # Detect task type and complexity
        task_type = self.detect_task_type(task)
        complexity = self.analyze_complexity(task)

        # Get candidate patterns
        candidates = self._get_candidate_patterns(task_type, complexity, priority)

        if not candidates:
            # Fallback to general patterns
            candidates = self._get_fallback_patterns(complexity)

        if not candidates:
            raise ValueError(f"No suitable patterns found for task type {task_type} and complexity {complexity}")

        # Select best pattern based on priority
        selected_pattern = self._select_best_pattern(candidates, priority)

        # Get fallback patterns
        fallback_patterns = [p.name for p in candidates if p.name != selected_pattern.name][:3]

        # Calculate confidence
        confidence = self._calculate_confidence(selected_pattern, task_type, complexity)

        # Generate reasoning
        reasoning = self._generate_reasoning(selected_pattern, task_type, complexity, priority)

        result = PatternSelectionResult(
            pattern=selected_pattern,
            confidence=confidence,
            reasoning=reasoning,
            fallback_patterns=fallback_patterns
        )

        if HAS_STRUCTLOG:
            self.logger.info(
                "pattern_selected",
                pattern=selected_pattern.name,
                task_type=task_type.value,
                complexity=complexity.value,
                priority=priority.value,
                confidence=confidence
            )

        return result

    def _get_candidate_patterns(
        self,
        task_type: TaskType,
        complexity: PatternComplexity,
        priority: PatternPriority
    ) -> List[PromptPattern]:
        """Get candidate patterns based on task type, complexity, and priority"""
        candidates = []

        # Get patterns by task type from selection rules
        by_task_type = self.pattern_selection_rules.get('by_task_type', {})
        task_type_str = task_type.value

        if task_type_str in by_task_type:
            primary = by_task_type[task_type_str].get('primary')
            fallbacks = by_task_type[task_type_str].get('fallback', [])

            # Add primary pattern
            if primary and primary in self.patterns:
                candidates.append(self.patterns[primary])

            # Add fallback patterns
            for fallback in fallbacks:
                if fallback in self.patterns:
                    candidates.append(self.patterns[fallback])

        # Filter by complexity
        complexity_str = complexity.value
        by_complexity = self.pattern_selection_rules.get('by_complexity', {})
        if complexity_str in by_complexity:
            recommended = by_complexity[complexity_str].get('recommended_patterns', [])
            for pattern_id in recommended:
                if pattern_id in self.patterns and self.patterns[pattern_id] not in candidates:
                    candidates.append(self.patterns[pattern_id])

        # Add patterns by priority
        priority_str = priority.value
        by_priority = self.pattern_selection_rules.get('by_priority', {})
        if priority_str in by_priority:
            top_patterns = by_priority[priority_str].get('top_patterns', [])
            for pattern_id in top_patterns:
                if pattern_id in self.patterns and self.patterns[pattern_id] not in candidates:
                    candidates.append(self.patterns[pattern_id])

        return candidates

    def _get_fallback_patterns(self, complexity: PatternComplexity) -> List[PromptPattern]:
        """Get fallback patterns when no specific match found"""
        # Return patterns matching complexity level
        return [
            pattern for pattern in self.patterns.values()
            if pattern.complexity == complexity.value
        ]

    def _select_best_pattern(
        self,
        candidates: List[PromptPattern],
        priority: PatternPriority
    ) -> PromptPattern:
        """Select best pattern from candidates based on priority"""
        if not candidates:
            raise ValueError("No candidate patterns provided")

        # Get priority weights from rules
        priority_config = self.pattern_selection_rules.get('by_priority', {}).get(priority.value, {})
        quality_weight = priority_config.get('quality_weight', 0.4)
        cost_weight = priority_config.get('cost_weight', 0.4)
        speed_weight = priority_config.get('speed_weight', 0.2)

        # Calculate scores for each candidate
        scores = []
        for pattern in candidates:
            # Normalize metrics (0-1 scale)
            quality_score = pattern.metrics.quality_score / 10.0
            cost_score = 1.0 - min(pattern.metrics.avg_cost / 0.003, 1.0)  # Lower is better
            speed_score = 1.0 - min(pattern.metrics.avg_latency_ms / 4000, 1.0)  # Lower is better

            # Calculate weighted score
            weighted_score = (
                quality_weight * quality_score +
                cost_weight * cost_score +
                speed_weight * speed_score
            )

            scores.append((pattern, weighted_score))

        # Return pattern with highest score
        best_pattern = max(scores, key=lambda x: x[1])[0]
        return best_pattern

    def _calculate_confidence(
        self,
        pattern: PromptPattern,
        task_type: TaskType,
        complexity: PatternComplexity
    ) -> float:
        """Calculate confidence score for pattern selection"""
        confidence = 0.0

        # Factor 1: Pattern quality score (40%)
        confidence += (pattern.metrics.quality_score / 10.0) * 0.4

        # Factor 2: Success rate (30%)
        confidence += (pattern.metrics.success_rate / 100.0) * 0.3

        # Factor 3: Complexity match (20%)
        if pattern.complexity == complexity.value:
            confidence += 0.2
        else:
            confidence += 0.1

        # Factor 4: Task type match (10%)
        # Check if pattern name or category relates to task type
        task_type_str = task_type.value
        if task_type_str in pattern.name.lower() or task_type_str in pattern.category.lower():
            confidence += 0.1
        else:
            confidence += 0.05

        return min(confidence, 1.0)

    def _generate_reasoning(
        self,
        pattern: PromptPattern,
        task_type: TaskType,
        complexity: PatternComplexity,
        priority: PatternPriority
    ) -> str:
        """Generate human-readable reasoning for pattern selection"""
        reasons = []

        reasons.append(f"Task type: {task_type.value}")
        reasons.append(f"Complexity: {complexity.value}")
        reasons.append(f"Priority: {priority.value}")
        reasons.append(f"Selected pattern: {pattern.name} (quality score: {pattern.metrics.quality_score}/10)")
        reasons.append(f"Expected success rate: {pattern.metrics.success_rate}%")
        reasons.append(f"Estimated cost: ${pattern.metrics.avg_cost:.4f}")
        reasons.append(f"Estimated latency: {pattern.metrics.avg_latency_ms}ms")

        return " | ".join(reasons)

    def get_pattern_by_name(self, pattern_name: str) -> Optional[PromptPattern]:
        """Get pattern by name"""
        return self.patterns.get(pattern_name)

    def list_patterns(
        self,
        category: Optional[str] = None,
        complexity: Optional[PatternComplexity] = None,
        min_quality: float = 0.0
    ) -> List[PromptPattern]:
        """
        List patterns with optional filters

        Args:
            category: Filter by category (analysis, generation, review, optimization)
            complexity: Filter by complexity
            min_quality: Minimum quality score

        Returns:
            List of matching patterns
        """
        patterns = list(self.patterns.values())

        if category:
            patterns = [p for p in patterns if p.category == category]

        if complexity:
            patterns = [p for p in patterns if p.complexity == complexity.value]

        if min_quality > 0:
            patterns = [p for p in patterns if p.metrics.quality_score >= min_quality]

        # Sort by quality score descending
        patterns.sort(key=lambda p: p.metrics.quality_score, reverse=True)

        return patterns

    def format_prompt(
        self,
        pattern: PromptPattern,
        variables: Dict[str, Any]
    ) -> str:
        """
        Format pattern template with provided variables

        Args:
            pattern: PromptPattern to format
            variables: Dictionary of variable values

        Returns:
            Formatted prompt string
        """
        prompt = pattern.template

        # Replace variables in template
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(var_value))

        return prompt

    def predict_quality(
        self,
        pattern: PromptPattern,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict quality metrics for using pattern with task

        Args:
            pattern: Pattern to use
            task: Task to execute

        Returns:
            Dictionary with predicted quality metrics
        """
        complexity = self.analyze_complexity(task)

        # Base predictions from pattern metrics
        predicted_quality = pattern.metrics.quality_score
        predicted_cost = pattern.metrics.avg_cost
        predicted_latency = pattern.metrics.avg_latency_ms

        # Adjust based on complexity mismatch
        if pattern.complexity != complexity.value:
            if complexity == PatternComplexity.COMPLEX and pattern.complexity == 'simple':
                predicted_quality -= 2.0  # Quality degradation
                predicted_cost *= 1.5  # More iterations needed
            elif complexity == PatternComplexity.SIMPLE and pattern.complexity == 'complex':
                predicted_cost *= 0.8  # Overkill but still works

        return {
            'quality_score': max(1.0, min(10.0, predicted_quality)),
            'success_rate': pattern.metrics.success_rate,
            'estimated_cost': predicted_cost,
            'estimated_latency_ms': predicted_latency,
            'revision_rate': pattern.metrics.revision_rate,
            'confidence': self._calculate_confidence(
                pattern,
                self.detect_task_type(task),
                complexity
            )
        }

    def track_pattern_usage(
        self,
        pattern_name: str,
        actual_quality: float,
        actual_cost: float,
        actual_latency: int
    ):
        """
        Track actual pattern performance for learning

        Args:
            pattern_name: Name of pattern used
            actual_quality: Actual quality score achieved
            actual_cost: Actual cost incurred
            actual_latency: Actual latency in milliseconds
        """
        if pattern_name not in self.patterns:
            self.logger.warning(f"Unknown pattern: {pattern_name}")
            return

        pattern = self.patterns[pattern_name]
        pattern.metrics.use_count += 1

        # Update metrics with exponential moving average
        alpha = 0.2  # Learning rate
        pattern.metrics.quality_score = (
            alpha * actual_quality + (1 - alpha) * pattern.metrics.quality_score
        )
        pattern.metrics.avg_cost = (
            alpha * actual_cost + (1 - alpha) * pattern.metrics.avg_cost
        )
        pattern.metrics.avg_latency_ms = int(
            alpha * actual_latency + (1 - alpha) * pattern.metrics.avg_latency_ms
        )

        if HAS_STRUCTLOG:
            self.logger.info(
                "pattern_usage_tracked",
                pattern=pattern_name,
                use_count=pattern.metrics.use_count,
                updated_quality=pattern.metrics.quality_score
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of all patterns"""
        summary = {
            'total_patterns': len(self.patterns),
            'patterns_by_category': {},
            'patterns_by_complexity': {},
            'top_quality_patterns': [],
            'most_used_patterns': [],
            'average_metrics': {}
        }

        # Count by category
        for pattern in self.patterns.values():
            category = pattern.category
            summary['patterns_by_category'][category] = \
                summary['patterns_by_category'].get(category, 0) + 1

        # Count by complexity
        for pattern in self.patterns.values():
            complexity = pattern.complexity
            summary['patterns_by_complexity'][complexity] = \
                summary['patterns_by_complexity'].get(complexity, 0) + 1

        # Top quality patterns
        sorted_by_quality = sorted(
            self.patterns.values(),
            key=lambda p: p.metrics.quality_score,
            reverse=True
        )
        summary['top_quality_patterns'] = [
            {
                'name': p.name,
                'quality_score': p.metrics.quality_score,
                'success_rate': p.metrics.success_rate
            }
            for p in sorted_by_quality[:5]
        ]

        # Most used patterns
        sorted_by_usage = sorted(
            self.patterns.values(),
            key=lambda p: p.metrics.use_count,
            reverse=True
        )
        summary['most_used_patterns'] = [
            {
                'name': p.name,
                'use_count': p.metrics.use_count,
                'quality_score': p.metrics.quality_score
            }
            for p in sorted_by_usage[:5] if p.metrics.use_count > 0
        ]

        # Average metrics
        total_patterns = len(self.patterns)
        if total_patterns > 0:
            summary['average_metrics'] = {
                'quality_score': sum(p.metrics.quality_score for p in self.patterns.values()) / total_patterns,
                'success_rate': sum(p.metrics.success_rate for p in self.patterns.values()) / total_patterns,
                'avg_cost': sum(p.metrics.avg_cost for p in self.patterns.values()) / total_patterns,
                'avg_latency_ms': sum(p.metrics.avg_latency_ms for p in self.patterns.values()) / total_patterns
            }

        return summary
