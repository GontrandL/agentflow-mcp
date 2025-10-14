import concurrent.futures
import time
from typing import Dict, Any

class TaskValidationError(Exception):
    """Raised when task validation fails."""
    pass

class TaskExecutionError(Exception):
    """Raised when task execution fails."""
    pass

class SmartOrchestrator:
    def __init__(self):
        # Initialize logger (assumed to be available)
        self.logger = None  # Replace with actual logger instance
    
    def _validate_task(self, task: Dict[str, Any]) -> None:
        """Validate the task dictionary structure and content.
        
        Args:
            task: The task dictionary to validate.
            
        Raises:
            ValueError: If task is None or not a dictionary.
            TaskValidationError: If task is missing required fields or has invalid values.
        """
        if task is None:
            raise ValueError("Task cannot be None")
        if not isinstance(task, dict):
            raise ValueError("Task must be a dictionary")
        
        required_keys = {'task_id', 'task_type'}
        missing_keys = required_keys - set(task.keys())
        if missing_keys:
            raise TaskValidationError(f"Task is missing required keys: {missing_keys}")
        
        # Set default timeout if not provided
        task.setdefault('timeout', 30)
        
        if not isinstance(task['timeout'], (int, float)) or task['timeout'] <= 0:
            raise TaskValidationError("Timeout must be a positive number")
    
    def _execute_single(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with timeout and error handling.
        
        Args:
            task: Dictionary containing task details.
            
        Returns:
            Dictionary with execution results containing:
            - status: 'success' or 'failure'
            - result: Task result if successful, None otherwise
            - error: Error message if failed, None otherwise
            - duration: Execution time in seconds
            
        Raises:
            ValueError: If task is None or not a dictionary.
            TaskValidationError: If task validation fails.
        """
        start_time = time.time()
        result = {
            'status': 'failure',
            'result': None,
            'error': None,
            'duration': 0.0
        }
        
        try:
            # Validate task structure
            self._validate_task(task)
            
            # Extract timeout and prepare for execution
            timeout = task.get('timeout', 30)
            task_id = task['task_id']
            
            self.logger.info(f"Executing task {task_id} with timeout {timeout}s")
            
            # Execute task with timeout handling
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.execute_task, task)
                try:
                    task_result = future.result(timeout=timeout)
                    result.update({
                        'status': 'success',
                        'result': task_result
                    })
                except concurrent.futures.TimeoutError:
                    future.cancel()
                    error_msg = f"Task {task_id} timed out after {timeout} seconds"
                    self.logger.error(error_msg)
                    raise TimeoutError(error_msg)
                except Exception as e:
                    error_msg = f"TaskExecutionError in task {task_id}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    raise TaskExecutionError(error_msg) from e
                
        except (ValueError, TaskValidationError) as e:
            error_msg = f"Task validation failed: {str(e)}"
            result['error'] = error_msg
            self.logger.error(error_msg, exc_info=True)
        except TimeoutError as e:
            result['error'] = str(e)
        except TaskExecutionError as e:
            result['error'] = str(e)
        except Exception as e:
            error_msg = f"Unexpected error executing task {task.get('task_id', 'unknown')}: {str(e)}"
            result['error'] = error_msg
            self.logger.error(error_msg, exc_info=True)
        finally:
            result['duration'] = time.time() - start_time
            return result
    
    def execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute the actual task (to be implemented or provided externally).
        
        Args:
            task: Dictionary containing task details.
            
        Returns:
            Result of the task execution.
            
        Raises:
            Exception: Any exception that might occur during task execution.
        """
        # This should be implemented or provided elsewhere
        raise NotImplementedError("execute_task method must be implemented")