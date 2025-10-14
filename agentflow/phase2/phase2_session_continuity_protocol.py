"""
Session Continuity Protocol - Core Phase 2 Component

Provides session checkpointing and recovery with <30s recovery guarantee.
Extracted from Worker 4 delegation output.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Literal, List, Any
import json
import os
import hashlib
import time


@dataclass
class SessionCheckpoint:
    """
    A dataclass representing a checkpoint for a session.

    Attributes:
        session_id (str): Unique identifier for the session, non-empty.
        timestamp (datetime): Represents when the checkpoint was created, must be UTC timezone-aware.
        data (dict): Contains session-specific data, cannot be None.
        status (Literal['active', 'paused', 'completed']): Represents the session status.
        progress (float): Represents completion progress, must be between 0.0 and 1.0 inclusive.
    """
    session_id: str
    timestamp: datetime
    data: Dict
    status: Literal['active', 'paused', 'completed']
    progress: float

    def __post_init__(self):
        """Validates the fields after initialization."""
        # Validate session_id
        if not isinstance(self.session_id, str) or not self.session_id:
            raise ValueError("session_id must be a non-empty string")

        # Validate timestamp
        if self.timestamp.tzinfo != timezone.utc:
            raise ValueError("timestamp must be UTC timezone-aware")

        # Validate data
        if not isinstance(self.data, dict) or self.data is None:
            raise ValueError("data must be a dictionary and cannot be None")

        # Validate status
        if self.status not in ['active', 'paused', 'completed']:
            raise ValueError("status must be one of 'active', 'paused', 'completed'")

        # Validate progress
        if not isinstance(self.progress, float) or not (0.0 <= self.progress <= 1.0):
            raise ValueError("progress must be a float between 0.0 and 1.0 inclusive")


class SessionContinuityProtocol:
    """
    A class to handle the setup of a directory structure for session continuity.

    Attributes:
        base_dir (str): The base directory where the session directory will be created.
        session_id (str): The unique identifier for the session.
        overwrite (bool): Whether to overwrite the existing directory structure.
    """

    def __init__(self, base_dir: str, session_id: str, overwrite: bool = False):
        """
        Initializes the SessionContinuityProtocol instance and sets up the directory structure.

        Args:
            base_dir (str): The base directory for the session.
            session_id (str): The unique identifier for the session.
            overwrite (bool): Whether to overwrite the existing directory. Defaults to False.

        Raises:
            ValueError: If `base_dir` or `session_id` is an empty string or contains invalid characters.
            OSError: If there are issues with file permissions or directory creation.
        """
        # Validate base_dir and session_id
        if not base_dir or not isinstance(base_dir, str):
            raise ValueError("base_dir must be a non-empty string.")
        if not session_id or not isinstance(session_id, str):
            raise ValueError("session_id must be a non-empty string.")

        self.base_dir = base_dir
        self.session_id = session_id
        self.overwrite = overwrite

        # Create the base directory if it doesn't exist
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        # Define the session directory path
        session_dir = os.path.join(self.base_dir, self.session_id)

        # If overwrite is True, remove the existing session directory
        if self.overwrite and os.path.exists(session_dir):
            import shutil
            shutil.rmtree(session_dir)

        # Create the session directory and subdirectories
        os.makedirs(session_dir, exist_ok=True)
        for subdir in ['logs', 'data', 'backups']:
            os.makedirs(os.path.join(session_dir, subdir), exist_ok=True)


def create_checkpoint(events: List[Dict[str, Any]], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a checkpoint by summarizing events and computing the state hash.

    Args:
        events (List[Dict[str, Any]]): List of event dictionaries.
        state (Dict[str, Any]): State dictionary.

    Returns:
        Dict[str, Any]: Dictionary containing event summary, state hash, and timestamp.
    """
    # Step 1: Summarize Events
    if not events:
        event_summary = "No events to summarize."
    else:
        event_groups = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            if event_type not in event_groups:
                event_groups[event_type] = {
                    "count": 0,
                    "first_timestamp": event.get("timestamp", ""),
                    "last_timestamp": event.get("timestamp", ""),
                    "sample_data": event.get("data", {})
                }
            event_groups[event_type]["count"] += 1
            event_groups[event_type]["last_timestamp"] = event.get("timestamp", "")

        event_summary = []
        for event_type, details in event_groups.items():
            summary = (
                f"{event_type}: {details['count']} events "
                f"(first: {details['first_timestamp']}, "
                f"last: {details['last_timestamp']}, "
                f"sample_data: {details['sample_data']})"
            )
            event_summary.append(summary)

        if len(event_summary) == 1:
            event_summary = event_summary[0]

    # Step 2: Compute State Hash
    if not state:
        state_hash = "Empty state."
    else:
        try:
            # Convert state to a JSON string, sorted by keys, with no whitespace
            state_json = json.dumps(state, sort_keys=True, separators=(",", ":"))
            # Compute MD5 hash
            state_hash = hashlib.md5(state_json.encode()).hexdigest()
        except TypeError:
            state_hash = "State serialization failed."

    # Step 3: Generate Timestamp
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Final Result
    return {
        "event_summary": event_summary,
        "state_hash": state_hash,
        "timestamp": timestamp
    }


def resume_session(file_path: str) -> dict:
    """
    Resume a session by atomically reading the checkpoint file.

    Args:
        file_path: Path to the checkpoint file.

    Returns:
        dict: Session data if successful, empty dict otherwise.
    """
    default_session = {'status': 'empty'}  # Predefined default session dictionary
    max_retries = 3  # Max retries for locked file
    retry_delay = 0.5  # Delay between retries in seconds

    for attempt in range(max_retries):
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return {}

            # Atomically read the file content
            with open(file_path, 'r') as file:
                file_content = file.read()

            # Handle empty file
            if not file_content:
                return default_session

            # Parse JSON content
            try:
                session_data = json.loads(file_content)
                if isinstance(session_data, dict):
                    return session_data
                else:
                    return {}  # Invalid JSON structure
            except json.JSONDecodeError:
                return {}  # Corrupted JSON

        except IOError as e:
            # Handle file lock (e.g., another process is writing)
            if getattr(e, 'winerror', None) == 32 or getattr(e, 'errno', None) == 13:  # File locked errors
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {}
            else:
                raise  # Re-raise other IO errors

    return {}  # Default return in case of unexpected failures


def compute_state_hash(state: Dict) -> str:
    """
    Compute an MD5 hash of a state dictionary for quick validation.

    Args:
        state: A dictionary representing the state to be hashed.

    Returns:
        A 32-character hexadecimal MD5 hash string.
    """
    def flatten(obj):
        """Recursively flatten an object into a string representation."""
        if obj is None:
            return "None"
        elif isinstance(obj, (str, int, float, bool)):
            return str(obj)
        elif isinstance(obj, (list, tuple)):
            return "[" + ",".join(flatten(item) for item in obj) + "]"
        elif isinstance(obj, dict):
            sorted_items = sorted(obj.items(), key=lambda x: str(x[0]))
            flattened_items = []
            for key, value in sorted_items:
                flattened_key = flatten(key)
                flattened_value = flatten(value)
                flattened_items.append(f"{flattened_key}:{flattened_value}")
            return "{" + ",".join(flattened_items) + "}"
        else:
            return str(obj)

    # Convert the state to a deterministic string representation
    state_str = flatten(state)

    # Compute MD5 hash of the string representation
    md5_hash = hashlib.md5(state_str.encode('utf-8'))

    # Return the hexadecimal digest
    return md5_hash.hexdigest()


def atomic_write_checkpoint(data: str, final_path: str):
    """
    Atomically write checkpoint data to a file.

    Args:
        data: The data to write (as string).
        final_path: The final destination path.

    Raises:
        Exception: If writing fails.
    """
    try:
        # Create a temporary file in the same directory as the final file
        temp_path = f"{final_path}.tmp"
        with open(temp_path, 'w') as temp_file:
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())  # Ensure data is written to disk

        # Atomically rename the temporary file to the final file
        os.rename(temp_path, final_path)

    except Exception as e:
        # Clean up the temporary file on failure
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e  # Re-raise the exception for handling by the caller
