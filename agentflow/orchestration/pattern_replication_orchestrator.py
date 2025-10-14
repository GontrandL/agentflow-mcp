"""
Pattern Replication Orchestrator - Specialized for "Copy This Pattern" Tasks

This orchestrator is specifically designed to handle tasks where the goal is to
replicate an existing code pattern with modifications, such as:
- Creating MCP servers following existing patterns
- Implementing similar classes with different components
- Copy-paste-modify workflows

**Key Differences from SmartOrchestrator:**
1. Focuses on CODE EXTRACTION not tutorial generation
2. Uses explicit anti-pattern prompts to prevent explanatory content
3. Post-processes output to extract code from tutorial format if needed
4. Validates architectural correctness not just quality
5. Preserves reference patterns without compression

**When to Use:**
- Creating files following existing patterns
- "Make X like Y but change A to B" tasks
- MCP server creation (follow stdio pattern)
- Infrastructure code replication

**Status**: EXPERIMENTAL (2025-10-14)
Created to fix delegation failures in AgentFlow MCP server generation.
"""

import os
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
load_dotenv()

import structlog
from agentflow.orchestration.smart_orchestrator import SmartOrchestrator

logger = structlog.get_logger(__name__)


class PatternReplicationOrchestrator:
    """
    Specialized orchestrator for pattern replication tasks.

    This class wraps SmartOrchestrator with:
    1. Pattern-specific prompt engineering
    2. Code extraction post-processing
    3. Architectural validation
    4. Anti-tutorial safeguards
    """

    def __init__(
        self,
        provider: str = "deepseek",
        extract_code_from_markdown: bool = True
    ):
        """
        Initialize Pattern Replication Orchestrator.

        Args:
            provider: LLM provider (default: deepseek for cost savings)
            extract_code_from_markdown: If True, automatically extract code
                                       from markdown fences if LLM returns tutorial
        """
        self.smart_orchestrator = SmartOrchestrator(provider=provider)
        self.extract_code_from_markdown = extract_code_from_markdown
        self.provider = provider

        logger.info(
            "pattern_replication_orchestrator_initialized",
            provider=provider,
            extract_code=extract_code_from_markdown
        )

    def replicate_pattern(
        self,
        pattern_code: str,
        replacements: Dict[str, str],
        task_description: str,
        output_file: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Replicate a code pattern with specific replacements.

        This is the main entry point for pattern replication tasks.

        Args:
            pattern_code: The reference pattern code to follow
            replacements: Dict of OLD → NEW replacements
                         e.g. {"ContextGenerator": "SmartOrchestrator"}
            task_description: High-level description of what you're creating
            output_file: Where the generated code should be saved
            additional_context: Any additional context or requirements

        Returns:
            {
                'result': str,                    # Generated code
                'extracted': bool,                # Was code extracted from tutorial?
                'validation': dict,               # Validation results
                'output_file': str,              # Where it was saved
                'pattern_preserved': bool         # Was pattern followed?
            }
        """
        logger.info(
            "pattern_replication_started",
            pattern_length=len(pattern_code),
            replacements=replacements,
            output_file=output_file
        )

        # STEP 1: Build pattern-specific prompt
        enhanced_task = self._build_pattern_replication_prompt(
            pattern_code,
            replacements,
            task_description,
            additional_context
        )

        # STEP 2: Delegate DIRECTLY to LLM (bypass planning for pattern replication)
        # Pattern replication doesn't need analyze_and_plan - it's code generation
        logger.info("delegating_directly_to_llm", message="Bypassing planning for pattern task")

        # Call LLM directly without planning overhead
        import os
        from openai import OpenAI

        # Use DeepSeek V3 for cost-effective pattern replication
        client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a code replication expert. Output ONLY runnable Python code. NO markdown, NO explanations."
                },
                {
                    "role": "user",
                    "content": enhanced_task
                }
            ],
            max_tokens=16000,
            temperature=0.1  # Low temperature for consistency
        )

        result = response.choices[0].message.content

        # STEP 3: Extract code if LLM returned tutorial format
        extracted = False
        if self.extract_code_from_markdown and self._is_tutorial_format(result):
            logger.warning(
                "tutorial_format_detected",
                message="LLM returned tutorial - extracting code"
            )
            result = self._extract_code_from_tutorial(result)
            extracted = True

        # STEP 4: Validate pattern preservation
        validation = self._validate_pattern_replication(
            result,
            pattern_code,
            replacements
        )

        # STEP 5: Save to output file
        with open(output_file, 'w') as f:
            f.write(result)

        logger.info(
            "pattern_replication_complete",
            output_file=output_file,
            extracted=extracted,
            validation_score=validation['score'],
            pattern_preserved=validation['pattern_preserved']
        )

        return {
            'result': result,
            'extracted': extracted,
            'validation': validation,
            'output_file': output_file,
            'pattern_preserved': validation['pattern_preserved']
        }

    def _build_pattern_replication_prompt(
        self,
        pattern_code: str,
        replacements: Dict[str, str],
        task_description: str,
        additional_context: Optional[str]
    ) -> str:
        """
        Build specialized prompt for pattern replication.

        This prompt is designed to:
        1. Explicitly show the pattern to follow
        2. List exact replacements to make
        3. Use STRONG anti-tutorial language
        4. Demand ONLY runnable code output
        """
        # Truncate pattern if too long (keep critical parts)
        pattern_preview = pattern_code
        if len(pattern_code) > 30000:
            # Keep first 20K and last 10K (structure + completion)
            pattern_preview = pattern_code[:20000] + "\n\n# ... (middle omitted) ...\n\n" + pattern_code[-10000:]

        # Build replacements list
        replacements_str = "\n".join(
            f"   OLD: {old}\n   NEW: {new}"
            for old, new in replacements.items()
        )

        prompt = f"""
YOU ARE A CODE REPLICATOR. YOUR OUTPUT MUST BE 100% RUNNABLE PYTHON CODE.

{task_description}

## REFERENCE PATTERN (FOLLOW THIS EXACTLY)

<REFERENCE_CODE>
{pattern_preview}
</REFERENCE_CODE>

## YOUR TASK: COPY THE PATTERN AND MAKE THESE REPLACEMENTS

{replacements_str}

## ADDITIONAL REQUIREMENTS

{additional_context or "None"}

## CRITICAL OUTPUT REQUIREMENTS

⚠️ ABSOLUTELY NO TUTORIAL FORMAT ⚠️
⚠️ ABSOLUTELY NO MARKDOWN FENCES ⚠️
⚠️ ABSOLUTELY NO EXPLANATIONS ⚠️

YOU MUST OUTPUT:
1. ONLY runnable Python code
2. Start with: #!/usr/bin/env python3
3. NO markdown code fences (```)
4. NO section headers (###)
5. NO explanatory text
6. NO comments except inline code comments

YOUR OUTPUT WILL BE:
- Saved directly to a .py file
- Executed immediately
- If it has markdown/explanations, it will FAIL

EXAMPLE OF CORRECT OUTPUT FORMAT:

#!/usr/bin/env python3
import sys
import json
# ... rest of code ...

EXAMPLE OF WRONG OUTPUT FORMAT (DO NOT DO THIS):

### AgentFlow MCP Server Implementation

Here's the implementation:

```python
#!/usr/bin/env python3
```

The above uses markdown fences and explanations - THIS IS WRONG!

## BEGIN YOUR OUTPUT NOW (ONLY RUNNABLE CODE):
"""

        return prompt

    def _is_tutorial_format(self, output: str) -> bool:
        """
        Detect if output is tutorial format instead of raw code.

        Tutorial indicators:
        - Starts with ### (markdown headers)
        - Contains ```python fences
        - Has "Here's" or "The following" explanatory phrases
        - Multiple paragraphs of text
        """
        # Check first 200 chars for tutorial markers
        start = output[:200]

        tutorial_markers = [
            start.startswith('###'),
            start.startswith('# ') and '\n\n' in start[:100],  # Markdown title
            '```python' in output[:500],
            '```' in output[:500],
            'Here' in start and 'implementation' in start.lower(),
            'The following' in start,
            'This code' in start,
        ]

        return any(tutorial_markers)

    def _extract_code_from_tutorial(self, tutorial_output: str) -> str:
        """
        Extract code from tutorial format.

        Strategy:
        1. Find all ```python code blocks
        2. Concatenate them
        3. If no code blocks, try to extract lines starting with valid Python
        """
        # Strategy 1: Extract from markdown fences
        code_blocks = re.findall(r'```(?:python)?\n(.*?)```', tutorial_output, re.DOTALL)
        if code_blocks:
            extracted = '\n\n'.join(code_blocks)
            logger.info("extracted_from_markdown_fences", blocks=len(code_blocks))
            return extracted.strip()

        # Strategy 2: Extract lines that look like Python code
        lines = tutorial_output.split('\n')
        code_lines = []
        in_code_section = False

        for line in lines:
            # Skip markdown headers
            if line.startswith('###') or line.startswith('# ') and len(line) < 100:
                in_code_section = False
                continue

            # Detect code section start
            if line.startswith('#!/usr/bin/python') or line.startswith('import ') or line.startswith('from '):
                in_code_section = True

            # If in code section, keep line
            if in_code_section:
                # Skip empty explanatory paragraphs
                if line.strip() and not line.strip().startswith('This ') and not line.strip().startswith('The '):
                    code_lines.append(line)

        if code_lines:
            extracted = '\n'.join(code_lines)
            logger.info("extracted_python_lines", lines=len(code_lines))
            return extracted.strip()

        # Strategy 3: Return as-is (couldn't extract)
        logger.warning("could_not_extract_code", returning_original=True)
        return tutorial_output

    def _validate_pattern_replication(
        self,
        generated_code: str,
        pattern_code: str,
        replacements: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Validate that pattern was replicated correctly.

        Checks:
        1. Starts with shebang
        2. Has required imports
        3. Has replacements applied
        4. Follows structural pattern
        5. No markdown artifacts
        """
        checks = {}

        # Check 1: Shebang
        checks['has_shebang'] = generated_code.strip().startswith('#!/usr/bin/env python')

        # Check 2: No markdown fences
        checks['no_markdown'] = '```' not in generated_code

        # Check 3: Replacements applied
        checks['replacements_applied'] = {}
        for old, new in replacements.items():
            checks['replacements_applied'][f"{old} → {new}"] = new in generated_code

        # Check 4: Has imports
        checks['has_imports'] = 'import ' in generated_code[:500]

        # Check 5: Has class/function definitions
        checks['has_definitions'] = 'class ' in generated_code or 'def ' in generated_code or 'async def ' in generated_code

        # Check 6: Follows pattern structure (has similar structure)
        pattern_structure = self._extract_structure(pattern_code)
        generated_structure = self._extract_structure(generated_code)

        # Compare structures
        structure_similarity = len(set(generated_structure) & set(pattern_structure)) / len(set(pattern_structure)) if pattern_structure else 0
        checks['structure_similarity'] = f"{structure_similarity * 100:.0f}%"

        # Calculate score
        score = 0
        if checks['has_shebang']: score += 10
        if checks['no_markdown']: score += 20
        if checks['has_imports']: score += 10
        if checks['has_definitions']: score += 10
        if all(checks['replacements_applied'].values()): score += 30
        if structure_similarity > 0.5: score += 20

        checks['score'] = score
        checks['pattern_preserved'] = score >= 70

        return checks

    def _extract_structure(self, code: str) -> List[str]:
        """
        Extract structural elements from code.

        Returns list of:
        - Class names
        - Function names
        - Key patterns (async def, @dataclass, etc.)
        """
        structure = []

        # Extract class names
        classes = re.findall(r'class\s+(\w+)', code)
        structure.extend([f"class:{c}" for c in classes])

        # Extract function names
        functions = re.findall(r'(?:async\s+)?def\s+(\w+)', code)
        structure.extend([f"func:{f}" for f in functions])

        # Extract patterns
        if 'async def' in code: structure.append('pattern:async')
        if '@dataclass' in code: structure.append('pattern:dataclass')
        if 'if __name__ ==' in code: structure.append('pattern:main')

        return structure


# Convenience function for direct usage
def replicate_pattern(
    pattern_code: str,
    replacements: Dict[str, str],
    task_description: str,
    output_file: str,
    additional_context: Optional[str] = None,
    provider: str = "deepseek"
) -> Dict[str, Any]:
    """
    Convenience function to replicate a pattern without instantiating orchestrator.

    Args:
        pattern_code: Reference pattern to follow
        replacements: OLD → NEW mappings
        task_description: What you're creating
        output_file: Where to save result
        additional_context: Additional requirements
        provider: LLM provider (default: deepseek)

    Returns:
        Result dict with code, validation, etc.
    """
    orchestrator = PatternReplicationOrchestrator(provider=provider)
    return orchestrator.replicate_pattern(
        pattern_code,
        replacements,
        task_description,
        output_file,
        additional_context
    )
