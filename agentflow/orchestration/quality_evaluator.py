import concurrent.futures
import logging
from typing import List, Dict, Callable, Optional

logging.basicConfig(level=logging.WARNING)

def orchestrate_with_evaluation(
    tasks: List[Dict],
    evaluation_func: Callable,
    timeout: Optional[float] = 10.0
) -> Dict:
    """
    Execute multiple AI model tasks in parallel, evaluate their outputs, and return the best result.

    Args:
        tasks: A list of task dictionaries with keys 'model_name', 'prompt', and 'params'.
        evaluation_func: A function that scores outputs (higher = better).
        timeout: Maximum seconds per task (default: 10.0).

    Returns:
        A dictionary with the best task's output, score, and task_id.

    Raises:
        ValueError: If the tasks list is empty.
        RuntimeError: If all tasks fail.
    """
    if not tasks:
        raise ValueError("No tasks provided")

    # Helper function to execute a single task
    def execute_task(task: Dict) -> Optional[str]:
        try:
            model_name = task["model_name"]
            prompt = task["prompt"]
            params = task.get("params", {})
            # Replace this with actual model execution logic
            if model_name not in ["gpt-4", "claude-2"]:
                logging.warning(f"Invalid model_name: {model_name}, skipping task")
                return None
            # Simulate model execution
            if model_name == "gpt-4":
                return "Hello there!"
            elif model_name == "claude-2":
                return "Hi!"
        except Exception as e:
            logging.warning(f"Task execution failed: {e}")
            return None

    # Execute tasks in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_task, task) for task in tasks]
        for i, future in enumerate(concurrent.futures.as_completed(futures, timeout=timeout)):
            try:
                output = future.result()
                if output is not None:
                    try:
                        score = evaluation_func(output)
                    except Exception as e:
                        logging.warning(f"Evaluation failed for task {i}: {e}")
                        score = float("-inf")
                    results.append({"output": output, "score": score, "task_id": i})
                else:
                    logging.warning(f"Task {i} returned None")
            except concurrent.futures.TimeoutError:
                logging.warning(f"Task {i} timed out")

    if not results:
        raise RuntimeError("All tasks failed")

    # Find the result with the highest score
    best_result = max(results, key=lambda x: x["score"])
    return best_result

# Example usage
if __name__ == "__main__":
    tasks = [
        {"model_name": "gpt-4", "prompt": "Say hello", "params": {}},
        {"model_name": "claude-2", "prompt": "Say hi", "params": {}}
    ]
    def eval_func(output: str) -> float:
        return float(len(output))  # Longer output = better
    try:
        result = orchestrate_with_evaluation(tasks, eval_func)
        print(result)
    except Exception as e:
        print(f"Error: {e}")