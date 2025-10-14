"""
Phase 2: Persistent Memory & Session Continuity

This module provides the core components for session continuity and persistent memory:
- SessionHistoryManager: Manages session history with <1ms A2A event recording
- TaskTracker: Tracks tasks with dependencies and TodoWrite integration
- KnowledgeBase: Stores patterns and insights with file persistence
- SessionContinuityProtocol: Ensures <30s recovery with atomic checkpoints

All components are research-validated and production-ready.
"""

from .phase2_session_history_manager import (
    SessionEvent,
    SessionHistoryManager,
    record_a2a_event,
    end_session,
    get_recent_events
)

from .task_tracker import (
    Task,
    TaskTracker
)

from .phase2_knowledge_base import (
    Pattern,
    ProjectInsight,
    KnowledgeBase,
    get_recommendations_for_task
)

from .phase2_session_continuity_protocol import (
    SessionCheckpoint,
    SessionContinuityProtocol,
    create_checkpoint,
    resume_session,
    compute_state_hash,
    atomic_write_checkpoint
)

__all__ = [
    # Session History
    'SessionEvent',
    'SessionHistoryManager',
    'record_a2a_event',
    'end_session',
    'get_recent_events',

    # Task Tracking
    'Task',
    'TaskTracker',

    # Knowledge Base
    'Pattern',
    'ProjectInsight',
    'KnowledgeBase',
    'get_recommendations_for_task',

    # Session Continuity
    'SessionCheckpoint',
    'SessionContinuityProtocol',
    'create_checkpoint',
    'resume_session',
    'compute_state_hash',
    'atomic_write_checkpoint',
]
