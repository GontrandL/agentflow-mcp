"""
Specialized Model Router - Intelligent Task-to-Model Routing

Automatically selects the best specialized model based on task type.
Prioritizes FREE models where possible for cost efficiency.

Based on research:
- Document parsing: Dolphin, MinerU, KOSMOS-2.5
- Code generation: CodeGen, DeepSeek Coder, Qwen Coder
- Agentic tasks: Llama-4 Maverick/Scout
- Vision-language: LLaVA, Idefics2
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class TaskType(Enum):
    """Task categories for model routing"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DOCUMENT_PARSING = "document_parsing"
    AGENTIC_COMPLEX = "agentic_complex"
    AGENTIC_SIMPLE = "agentic_simple"
    VISION_LANGUAGE = "vision_language"
    REASONING_DEEP = "reasoning_deep"
    GENERAL = "general"


@dataclass
class ModelSpec:
    """Specification for a specialized model"""
    model_id: str
    task_types: List[TaskType]
    is_free: bool
    input_price: float  # per 1M tokens
    output_price: float  # per 1M tokens
    max_tokens: int
    description: str
    priority: int  # Lower = higher priority (1 = best)


class SpecializedModelRouter:
    """
    Intelligent router that selects the best model for a given task.

    Routing Strategy:
    1. Detect task type from prompt keywords
    2. Filter models by task type
    3. Prioritize FREE models
    4. Fallback to paid if no free available
    5. Return best match with reasoning
    """

    # Specialized models catalog (based on OpenRouter availability + research)
    SPECIALIZED_MODELS: List[ModelSpec] = [
        # Agentic Tasks - Llama-4 (FREE)
        ModelSpec(
            model_id="meta-llama/llama-4-maverick:free",
            task_types=[TaskType.AGENTIC_COMPLEX, TaskType.REASONING_DEEP],
            is_free=True,
            input_price=0.0,
            output_price=0.0,
            max_tokens=8192,
            description="Llama-4 Maverick: Context-aware agent, extraction, real-time analysis",
            priority=1
        ),
        ModelSpec(
            model_id="meta-llama/llama-4-scout:free",
            task_types=[TaskType.AGENTIC_SIMPLE, TaskType.GENERAL],
            is_free=True,
            input_price=0.0,
            output_price=0.0,
            max_tokens=8192,
            description="Llama-4 Scout: Fast agentic tasks, contextual generation",
            priority=1
        ),

        # Document Parsing - Dolphin (FREE)
        ModelSpec(
            model_id="cognitivecomputations/dolphin3.0-mistral-24b:free",
            task_types=[TaskType.DOCUMENT_PARSING, TaskType.VISION_LANGUAGE],
            is_free=True,
            input_price=0.0,
            output_price=0.0,
            max_tokens=8192,
            description="Dolphin 3.0: Document parsing, analyze-then-parse approach",
            priority=1
        ),

        # Code Generation - DeepSeek (already in use, very cheap)
        ModelSpec(
            model_id="deepseek/deepseek-chat",
            task_types=[TaskType.CODE_GENERATION, TaskType.CODE_REVIEW, TaskType.REASONING_DEEP],
            is_free=False,
            input_price=0.14 / 1_000_000,
            output_price=0.28 / 1_000_000,
            max_tokens=8192,
            description="DeepSeek V3: Best price/performance for code generation",
            priority=2
        ),

        # Code Generation - Llama Coder (FREE fallback)
        ModelSpec(
            model_id="meta-llama/llama-3.3-70b-instruct:free",
            task_types=[TaskType.CODE_GENERATION, TaskType.CODE_REVIEW, TaskType.GENERAL],
            is_free=True,
            input_price=0.0,
            output_price=0.0,
            max_tokens=8192,
            description="Llama 3.3 70B: Solid code generation, FREE alternative",
            priority=3
        ),

        # Reasoning - DeepSeek R1 Distill (FREE)
        ModelSpec(
            model_id="deepseek/deepseek-r1-distill-llama-70b:free",
            task_types=[TaskType.REASONING_DEEP, TaskType.AGENTIC_COMPLEX],
            is_free=True,
            input_price=0.0,
            output_price=0.0,
            max_tokens=8192,
            description="DeepSeek R1 Distill: Deep reasoning, distilled from R1",
            priority=2
        ),

        # Vision-Language - Llama 3.2 Vision (standard models)
        ModelSpec(
            model_id="meta-llama/llama-3.2-90b-vision-instruct",
            task_types=[TaskType.VISION_LANGUAGE, TaskType.DOCUMENT_PARSING],
            is_free=False,
            input_price=0.00 / 1_000_000,  # Pricing varies
            output_price=0.00 / 1_000_000,
            max_tokens=8192,
            description="Llama 3.2 90B Vision: Multimodal, document understanding",
            priority=4
        ),

        # General Purpose - Llama 3.3 (FREE)
        ModelSpec(
            model_id="meta-llama/llama-3.3-8b-instruct:free",
            task_types=[TaskType.GENERAL, TaskType.AGENTIC_SIMPLE],
            is_free=True,
            input_price=0.0,
            output_price=0.0,
            max_tokens=8192,
            description="Llama 3.3 8B: Fast general purpose, FREE",
            priority=5
        )
    ]

    # Keyword patterns for task detection
    TASK_PATTERNS = {
        TaskType.CODE_GENERATION: [
            r'\b(implement|create|build|generate|write|code|function|class|api|endpoint)\b',
            r'\b(python|typescript|javascript|java|rust|go)\b',
            r'\b(algorithm|data structure|backend|frontend)\b'
        ],
        TaskType.CODE_REVIEW: [
            r'\b(review|analyze|audit|check|validate|test)\b.*\b(code|implementation)\b',
            r'\b(bug|error|issue|problem|fix)\b'
        ],
        TaskType.DOCUMENT_PARSING: [
            r'\b(parse|extract|read|convert|ocr)\b.*\b(document|pdf|markdown|image)\b',
            r'\b(table|formula|layout|structure)\b.*\b(document|pdf)\b'
        ],
        TaskType.AGENTIC_COMPLEX: [
            r'\b(orchestrate|coordinate|manage|workflow|multi-step|complex)\b',
            r'\b(agent|autonomous|automate)\b.*\b(complex|advanced|sophisticated)\b',
            r'\b(plan|strategy|architecture)\b.*\b(system|application)\b'
        ],
        TaskType.AGENTIC_SIMPLE: [
            r'\b(automate|script|task)\b',
            r'\b(agent|autonomous)\b.*\b(simple|basic|straightforward)\b'
        ],
        TaskType.VISION_LANGUAGE: [
            r'\b(image|visual|screenshot|diagram|chart)\b',
            r'\b(vision|multimodal|vl model)\b'
        ],
        TaskType.REASONING_DEEP: [
            r'\b(reason|analyze|deduce|infer|logic)\b',
            r'\b(complex|deep|advanced|sophisticated)\b.*\b(reasoning|analysis|thinking)\b',
            r'\b(mathematical|scientific|theoretical)\b'
        ]
    }

    def __init__(self):
        """Initialize the router"""
        self.models = self.SPECIALIZED_MODELS

    def detect_task_type(self, prompt: str) -> TaskType:
        """
        Detect task type from prompt keywords.

        Args:
            prompt: User's task description

        Returns:
            Detected TaskType (defaults to GENERAL if no match)
        """
        prompt_lower = prompt.lower()

        # Score each task type by pattern matches
        scores: Dict[TaskType, int] = {task_type: 0 for task_type in TaskType}

        for task_type, patterns in self.TASK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    scores[task_type] += 1

        # Return highest scoring task type (or GENERAL if all zero)
        max_score = max(scores.values())
        if max_score == 0:
            return TaskType.GENERAL

        return max(scores.items(), key=lambda x: x[1])[0]

    def route(self, prompt: str, prefer_free: bool = True) -> Tuple[ModelSpec, TaskType, str]:
        """
        Route a task to the best specialized model.

        Args:
            prompt: Task description
            prefer_free: Prioritize FREE models (default: True)

        Returns:
            Tuple of (selected_model, detected_task_type, reasoning)
        """
        # 1. Detect task type
        task_type = self.detect_task_type(prompt)

        # 2. Filter models by task type
        candidates = [
            model for model in self.models
            if task_type in model.task_types
        ]

        if not candidates:
            # Fallback to general purpose models
            candidates = [
                model for model in self.models
                if TaskType.GENERAL in model.task_types
            ]

        # 3. Prioritize FREE models if requested
        if prefer_free:
            free_candidates = [m for m in candidates if m.is_free]
            if free_candidates:
                candidates = free_candidates

        # 4. Sort by priority (lower = better)
        candidates.sort(key=lambda m: m.priority)

        # 5. Select best match
        best_model = candidates[0] if candidates else self.models[0]

        # 6. Generate reasoning
        reasoning = self._generate_reasoning(best_model, task_type, len(candidates))

        return best_model, task_type, reasoning

    def _generate_reasoning(self, model: ModelSpec, task_type: TaskType,
                          candidate_count: int) -> str:
        """Generate human-readable routing reasoning"""
        free_status = "FREE" if model.is_free else f"${model.input_price * 1_000_000:.2f}/M in"

        return (
            f"Selected {model.model_id} for {task_type.value} task\n"
            f"Reasoning: {model.description}\n"
            f"Cost: {free_status}\n"
            f"Priority: {model.priority}/5 (considered {candidate_count} models)"
        )

    def get_model_for_task_type(self, task_type: TaskType,
                                prefer_free: bool = True) -> ModelSpec:
        """
        Get best model for a specific task type.

        Args:
            task_type: TaskType enum value
            prefer_free: Prioritize FREE models

        Returns:
            Best ModelSpec for the task type
        """
        candidates = [
            model for model in self.models
            if task_type in model.task_types
        ]

        if prefer_free:
            free_candidates = [m for m in candidates if m.is_free]
            if free_candidates:
                candidates = free_candidates

        candidates.sort(key=lambda m: m.priority)
        return candidates[0] if candidates else self.models[0]

    def list_available_models(self, task_type: Optional[TaskType] = None,
                            free_only: bool = False) -> List[ModelSpec]:
        """
        List available models, optionally filtered.

        Args:
            task_type: Filter by task type (optional)
            free_only: Show only FREE models

        Returns:
            List of matching ModelSpec objects
        """
        models = self.models

        if task_type:
            models = [m for m in models if task_type in m.task_types]

        if free_only:
            models = [m for m in models if m.is_free]

        return sorted(models, key=lambda m: m.priority)


# Convenience function for quick routing
def route_task(prompt: str, prefer_free: bool = True) -> Tuple[str, TaskType, str]:
    """
    Quick routing function - returns (model_id, task_type, reasoning)

    Args:
        prompt: Task description
        prefer_free: Prioritize FREE models

    Returns:
        Tuple of (model_id, task_type, reasoning)
    """
    router = SpecializedModelRouter()
    model, task_type, reasoning = router.route(prompt, prefer_free)
    return model.model_id, task_type, reasoning


if __name__ == "__main__":
    # Test the router
    router = SpecializedModelRouter()

    test_prompts = [
        "Implement a REST API with authentication in Python",
        "Parse this PDF document and extract all tables",
        "Orchestrate a complex multi-agent workflow for code generation",
        "Analyze this image and describe what you see",
        "Write a quick script to automate file backups"
    ]

    print("=== SPECIALIZED MODEL ROUTER TEST ===\n")

    for prompt in test_prompts:
        model, task_type, reasoning = router.route(prompt)
        print(f"Prompt: {prompt[:60]}...")
        print(f"Task Type: {task_type.value}")
        print(f"Model: {model.model_id}")
        print(f"FREE: {model.is_free}")
        print(f"Reasoning: {reasoning}")
        print("-" * 80)
        print()
