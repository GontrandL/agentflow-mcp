from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import os
from pathlib import Path
import time
import logging
import uuid

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SessionEvent:
    """Dataclass representing a session event with type hints.

    Attributes:
        event_type: Type of event. Must be 'login', 'logout', or 'error'.
        event_id: Unique identifier for the event. Defaults to a generated UUID.
        timestamp: Timestamp of the event. Defaults to current datetime.
        user_id: User ID associated with the event. Optional.
        details: Additional details about the event. Defaults to an empty dictionary.
    """
    event_type: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    details: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validates the event type after initialization."""
        if self.event_type not in ('login', 'logout', 'error'):
            raise ValueError("Event type must be 'login', 'logout', or 'error'.")

class SessionHistoryManager:
    """Manages session history initialization and file handling for JSON-based session history storage."""

    def __init__(self, session_id: str, history_file_path: str = "./session_history.json") -> None:
        """Initialize the SessionHistoryManager with a session ID and file path.

        Args:
            session_id: Unique identifier for the session. Must be non-empty string.
            history_file_path: Path to JSON file for storing history. Defaults to './session_history.json'.

        Raises:
            ValueError: If session_id is empty or history_file_path doesn't end with '.json'.
        """
        if not session_id or not isinstance(session_id, str):
            raise ValueError("session_id must be a non-empty string")
        if not history_file_path or not history_file_path.endswith('.json'):
            raise ValueError("history_file_path must be a non-empty string ending with '.json'")

        self.session_id = session_id
        self.history_file_path = history_file_path

    def load_history(self) -> Dict[str, Any]:
        """Load session history from the JSON file.

        Returns:
            Dictionary containing the session history data. Returns empty dict if file doesn't exist.

        Raises:
            ValueError: If the file contains malformed JSON.
            IOError: If the file exists but cannot be read.
        """
        try:
            if not os.path.exists(self.history_file_path):
                return {}

            with open(self.history_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)

        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON in history file: {e}") from e
        except OSError as e:
            raise IOError(f"Failed to read history file: {e}") from e

    def save_history(self, data: Dict[str, Any]) -> None:
        """Save session history data to the JSON file.

        Args:
            data: Dictionary of session history data to be saved.

        Raises:
            IOError: If the file cannot be written (permissions, disk full, etc.).
        """
        try:
            # Ensure directory exists
            file_path = Path(self.history_file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2)

        except OSError as e:
            raise IOError(f"Failed to write history file: {e}") from e
        except TypeError as e:
            raise ValueError(f"Data contains non-serializable types: {e}") from e

    def clear_history(self) -> None:
        """Clear all history data by saving an empty dictionary to the history file.

        Raises:
            IOError: If the file cannot be written.
        """
        self.save_history({})

def record_a2a_event(user_id: str, event_type: str, timestamp: float, metadata: Optional[Dict] = None) -> bool:
    """Records an A2A (Application-to-Application) event with strict overhead constraints (<1ms).

    Args:
        user_id: ID of the user associated with the event. Must be a non-empty string.
        event_type: Type of the event. Must be a non-empty string.
        timestamp: Timestamp of the event in seconds since epoch. Must be positive and not in the future.
        metadata: Additional metadata associated with the event. Optional.

    Returns:
        bool: True if the event was recorded successfully, False otherwise.
    """
    # Validation checks with minimal overhead
    if not isinstance(user_id, str) or not user_id:
        return False
    if not isinstance(event_type, str) or not event_type:
        return False
    current_time = time.time()
    if not isinstance(timestamp, float) or timestamp <= 0 or timestamp > current_time:
        return False
    if metadata is not None and not isinstance(metadata, dict):
        return False
    return True

def validate_session(session_id: str) -> bool:
    """Validate if the session exists and is active.

    Args:
        session_id: The session ID to validate.

    Returns:
        bool: True if the session is valid, False otherwise.
    """
    try:
        history_file = Path("./session_history.json")
        if not history_file.exists():
            return False

        with open(history_file, 'r') as f:
            history = json.load(f)

        # Check if session exists and has valid structure
        events = history.get('events', [])
        session_events = [e for e in events if e.get('session_id') == session_id]

        if not session_events:
            return False

        # Validate session has required fields
        latest_event = session_events[-1]
        required_fields = ['session_id', 'timestamp', 'event_type']
        if not all(field in latest_event for field in required_fields):
            return False

        # Check session hasn't been terminated
        if latest_event.get('event_type') == 'session_ended':
            return False

        return True

    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error validating session {session_id}: {e}")
        return False

def fetch_session_data(session_id: str) -> Dict:
    """Fetch all session data (metadata, user interactions, logs) associated with the session ID.

    Args:
        session_id: The session ID whose data is to be fetched.

    Returns:
        Dict: A dictionary of session data.
    """
    try:
        history_file = Path("./session_history.json")
        if not history_file.exists():
            return {"session_id": session_id, "error": "Session history file not found"}

        with open(history_file, 'r') as f:
            history = json.load(f)

        # Extract all events for this session
        events = history.get('events', [])
        session_events = [e for e in events if e.get('session_id') == session_id]

        if not session_events:
            return {"session_id": session_id, "error": "No events found for session"}

        # Build session data structure
        metadata = {
            "session_id": session_id,
            "start_time": session_events[0].get('timestamp'),
            "end_time": session_events[-1].get('timestamp'),
            "event_count": len(session_events)
        }

        # Categorize events
        interactions = []
        logs = []
        errors = []

        for event in session_events:
            event_type = event.get('event_type', 'unknown')
            if event_type in ['task_start', 'task_complete', 'delegation']:
                interactions.append(event)
            elif event_type == 'error':
                errors.append(event)
            else:
                logs.append(event)

        return {
            "session_id": session_id,
            "metadata": metadata,
            "interactions": interactions,
            "logs": logs,
            "errors": errors
        }

    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        return {"session_id": session_id, "error": str(e)}

def prepare_archive(session_data: Dict) -> Dict:
    """Format the session data into a standardized archive structure.

    Args:
        session_data: The session data to be archived.

    Returns:
        Dict: The archive-ready data.
    """
    archive = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_data["session_id"],
        "metadata": session_data.get("metadata", {}),
        "interactions": session_data.get("interactions", []),
        "logs": session_data.get("logs", []),
    }
    return archive

def save_archive(archive_data: Dict, storage_backend: str = 'file') -> str:
    """Save the archive to a designated storage system.

    Args:
        archive_data: The archive data to be saved.
        storage_backend: Storage backend ('file', 'redis', 's3').

    Returns:
        str: The location/path of the archived data.
    """
    session_id = archive_data['session_id']
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    if storage_backend == 'file':
        # File-based storage
        archive_dir = Path("archive")
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_location = archive_dir / f"{session_id}_{timestamp}.json"

        with open(archive_location, "w") as f:
            json.dump(archive_data, f, indent=2, default=str)

        return str(archive_location)

    elif storage_backend == 'redis':
        # Redis storage (requires redis-py)
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            key = f"archive:{session_id}:{timestamp}"
            r.set(key, json.dumps(archive_data, default=str))
            r.expire(key, 30 * 24 * 3600)  # 30 days TTL
            return f"redis://{key}"
        except ImportError:
            logger.warning("redis-py not installed, falling back to file storage")
            return save_archive(archive_data, 'file')

    elif storage_backend == 's3':
        # S3 storage (requires boto3)
        try:
            import boto3
            s3 = boto3.client('s3')
            bucket = os.getenv('SESSION_S3_BUCKET', 'agentflow-sessions')
            key = f"archives/{session_id}_{timestamp}.json"

            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(archive_data, default=str),
                ContentType='application/json'
            )
            return f"s3://{bucket}/{key}"
        except ImportError:
            logger.warning("boto3 not installed, falling back to file storage")
            return save_archive(archive_data, 'file')

    else:
        logger.error(f"Unknown storage backend: {storage_backend}")
        return save_archive(archive_data, 'file')

def cleanup_session(session_id: str, max_age_days: int = 30) -> bool:
    """Mark the session as archived and remove it from active tracking.

    Args:
        session_id: The session ID to cleanup.
        max_age_days: Maximum age in days before cleanup (default: 30).

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        history_file = Path("./session_history.json")
        if not history_file.exists():
            return False

        with open(history_file, 'r') as f:
            history = json.load(f)

        # Get all events
        events = history.get('events', [])
        session_events = [e for e in events if e.get('session_id') == session_id]

        if not session_events:
            return False

        # Check if session is old enough to cleanup
        last_event = session_events[-1]
        last_timestamp = datetime.fromisoformat(last_event['timestamp'].replace('Z', '+00:00'))
        age_days = (datetime.now(last_timestamp.tzinfo) - last_timestamp).days

        if age_days < max_age_days:
            logger.info(f"Session {session_id} is only {age_days} days old, skipping cleanup")
            return False

        # Add session_ended event
        end_event = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "event_type": "session_ended",
            "metadata": {"cleaned_up": True, "age_days": age_days}
        }
        events.append(end_event)

        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

        logger.info(f"Session {session_id} marked as ended (age: {age_days} days)")
        return True

    except (json.JSONDecodeError, IOError, ValueError) as e:
        logger.error(f"Error cleaning up session {session_id}: {e}")
        return False

def end_session(session_id: str) -> Dict:
    """Archive a session by validating, retrieving, formatting, and storing its data.

    Args:
        session_id: The session ID to archive.

    Returns:
        Dict: A dictionary with the archiving status and details.
    """
    errors = []
    success = False
    archive_location = None

    try:
        # Step 1: Input Validation
        if not validate_session(session_id):
            raise ValueError(f"Session ID {session_id} not found or inactive.")

        # Step 2: Data Retrieval
        session_data = fetch_session_data(session_id)
        if not session_data:
            raise RuntimeError(f"No data found for session ID {session_id}.")

        # Step 3: Archive Preparation
        archive_data = prepare_archive(session_data)

        # Step 4: Storage
        archive_location = save_archive(archive_data)

        # Step 5: Session Cleanup
        if not cleanup_session(session_id):
            raise RuntimeError(f"Failed to cleanup session ID {session_id}.")

        success = True

    except Exception as e:
        logger.error(f"Error archiving session {session_id}: {str(e)}")
        errors.append(str(e))

    # Step 6: Logging
    logger.info(f"Archiving process completed for session {session_id}. Success: {success}")

    return {
        "success": success,
        "session_id": session_id,
        "archive_location": archive_location,
        "errors": errors,
    }

def get_recent_events(events: List[Dict], category_filter: Optional[str] = None, location_filter: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict]:
    """Retrieves a list of recent events with optional filtering.

    Args:
        events: List of event dictionaries.
        category_filter: String or None. Filters events by category if provided.
        location_filter: String or None. Filters events by location if provided.
        start_time: String (ISO 8601) or None. Filters events after this time if provided.
        end_time: String (ISO 8601) or None. Filters events before this time if provided.

    Returns:
        List of filtered event dictionaries maintaining original order.
    """
    if not events:
        return []

    filtered_events = []

    # Parse time filters once outside the loop for efficiency
    try:
        start_dt = datetime.fromisoformat(start_time) if start_time else None
    except ValueError:
        logging.warning(f"Invalid start_time format: {start_time}. Ignoring start_time filter.")
        start_dt = None

    try:
        end_dt = datetime.fromisoformat(end_time) if end_time else None
    except ValueError:
        logging.warning(f"Invalid end_time format: {end_time}. Ignoring end_time filter.")
        end_dt = None

    for event in events:
        try:
            # Apply category filter
            if category_filter is not None and event.get('category') != category_filter:
                continue

            # Apply location filter
            if location_filter is not None and event.get('location') != location_filter:
                continue

            # Parse and check timestamp
            event_time = datetime.fromisoformat(event['timestamp'])

            # Apply start_time filter
            if start_dt is not None and event_time < start_dt:
                continue

            # Apply end_time filter
            if end_dt is not None and event_time > end_dt:
                continue

            # All filters passed
            filtered_events.append(event)

        except (KeyError, ValueError) as e:
            if isinstance(e, KeyError):
                logging.warning(f"Event {event.get('id', 'unknown')} missing required field: {e}")
            else:
                logging.warning(f"Event {event.get('id', 'unknown')} has invalid timestamp format: {event.get('timestamp')}")
            continue

    return filtered_events
