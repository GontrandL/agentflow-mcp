def _build_enriched_prompt(base_prompt: str, context: list[str], task_description: str) -> str:
    """
    Constructs a context-enriched prompt by combining base prompt, context, and task description.
    
    Args:
        base_prompt: The initial prompt string (required)
        context: List of context strings to enrich the prompt
        task_description: Description of the task to append
    
    Returns:
        A single string representing the enriched prompt
    
    Raises:
        ValueError: If base_prompt is empty
        TypeError: If context contains non-string elements or task_description isn't a string
    """
    # Validate input types and values
    if not isinstance(base_prompt, str):
        raise TypeError("base_prompt must be a string")
    if not base_prompt.strip():
        raise ValueError("base_prompt cannot be empty")
    
    if not isinstance(context, list):
        raise TypeError("context must be a list")
    for item in context:
        if not isinstance(item, str):
            raise TypeError("All context items must be strings")
    
    if not isinstance(task_description, str):
        raise TypeError("task_description must be a string")
    
    # Remove duplicate context entries while preserving order
    unique_context = []
    seen_context = set()
    for item in context:
        normalized_item = item.strip()
        if normalized_item and normalized_item not in seen_context:
            seen_context.add(normalized_item)
            unique_context.append(item)
    
    # Start building the enriched prompt
    enriched_prompt = base_prompt
    
    # Add context if available
    if unique_context:
        # Join context items with newlines and add spacing
        context_str = '\n'.join(unique_context)
        enriched_prompt = f"{enriched_prompt}\n\n{context_str}"
    
    # Add task description if available
    if task_description.strip():
        enriched_prompt = f"{enriched_prompt}\n\nTask: {task_description}"
    
    # Check for size limit (8KB = 8192 bytes)
    MAX_SIZE = 8192
    if len(enriched_prompt.encode('utf-8')) > MAX_SIZE:
        # Calculate how much we need to truncate (with some buffer for the task description)
        current_size = len(enriched_prompt.encode('utf-8'))
        excess = current_size - MAX_SIZE
        
        # First try to truncate the context
        if unique_context:
            # Estimate average bytes per context line
            context_bytes = len(context_str.encode('utf-8'))
            avg_bytes_per_line = context_bytes / len(unique_context)
            
            # Calculate how many lines to remove (round up)
            lines_to_remove = min(len(unique_context), int(excess / avg_bytes_per_line) + 1)
            
            # Rebuild with fewer context lines
            truncated_context = unique_context[:-lines_to_remove]
            context_str = '\n'.join(truncated_context)
            
            # Reconstruct the prompt
            enriched_prompt = base_prompt
            if truncated_context:
                enriched_prompt = f"{enriched_prompt}\n\n{context_str}"
            if task_description.strip():
                enriched_prompt = f"{enriched_prompt}\n\nTask: {task_description}"
            
            # If still too large, fall back to just base prompt + task
            if len(enriched_prompt.encode('utf-8')) > MAX_SIZE:
                enriched_prompt = base_prompt
                if task_description.strip():
                    enriched_prompt = f"{enriched_prompt}\n\nTask: {task_description}"
        
        # Final fallback if still too large
        if len(enriched_prompt.encode('utf-8')) > MAX_SIZE:
            # Truncate the base prompt itself (preserve at least some content)
            max_base_length = MAX_SIZE - (len("Task: ") + len(task_description) if task_description.strip() else 0)
            enriched_prompt = base_prompt[:max_base_length]
            if task_description.strip():
                enriched_prompt = f"{enriched_prompt}\n\nTask: {task_description}"
    
    return enriched_prompt