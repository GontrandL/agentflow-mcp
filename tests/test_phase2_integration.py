"""
Phase 2 Integration Test

Tests the complete Phase 2 system including:
- Session history management
- Task tracking
- Knowledge base
- Session continuity with <30s recovery guarantee
"""

import pytest
import time
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Import Phase 2 components
from agentflow.phase2 import (
    SessionEvent,
    SessionHistoryManager,
    record_a2a_event,
    Task,
    TaskTracker,
    Pattern,
    KnowledgeBase,
    SessionCheckpoint,
    SessionContinuityProtocol,
    create_checkpoint,
    resume_session,
)


class TestSessionHistoryManager:
    """Test session history management"""

    def test_session_history_manager_init(self):
        """Test SessionHistoryManager initialization"""
        manager = SessionHistoryManager("session_123", "/tmp/test_history.json")
        assert manager.session_id == "session_123"
        assert manager.history_file_path == "/tmp/test_history.json"

    def test_load_save_history(self):
        """Test loading and saving history"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            manager = SessionHistoryManager("session_456", temp_file)

            # Save history
            test_data = {"events": ["event1", "event2"], "count": 2}
            manager.save_history(test_data)

            # Load history
            loaded_data = manager.load_history()
            assert loaded_data == test_data

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_record_a2a_event(self):
        """Test A2A event recording with <1ms overhead"""
        start_time = time.time()

        result = record_a2a_event(
            user_id="user_123",
            event_type="task_complete",
            timestamp=time.time(),
            metadata={"task_id": "task_001"}
        )

        elapsed = (time.time() - start_time) * 1000  # Convert to ms

        assert result is True
        assert elapsed < 1.0  # <1ms guarantee


class TestTaskTracker:
    """Test task tracking system"""

    def test_task_creation(self):
        """Test Task dataclass creation"""
        task = Task(
            id="task_001",
            description="Test task",
            dependencies=[],
            difficulty="medium",
            error_risk="low",
            estimated_tokens=1000
        )

        assert task.id == "task_001"
        assert task.difficulty == "medium"

    def test_task_validation(self):
        """Test Task validation in __post_init__"""
        with pytest.raises(ValueError, match="Difficulty must be"):
            Task(
                id="task_002",
                difficulty="invalid",  # Invalid difficulty
                error_risk="low",
                estimated_tokens=500
            )


class TestKnowledgeBase:
    """Test knowledge base functionality"""

    def test_knowledge_base_init(self):
        """Test KnowledgeBase initialization"""
        kb = KnowledgeBase()
        assert len(kb.patterns) == 0
        assert len(kb.insights) == 0

    def test_add_pattern(self):
        """Test adding patterns"""
        kb = KnowledgeBase()
        kb.add_pattern("singleton_pattern")
        kb.add_pattern("factory_pattern")

        assert len(kb.patterns) == 2
        assert "singleton_pattern" in kb.patterns

    def test_save_load_knowledge_base(self):
        """Test knowledge base persistence"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            kb = KnowledgeBase()
            kb.add_pattern("pattern1")
            kb.add_insight("insight1")
            kb.save(temp_file)

            kb2 = KnowledgeBase()
            kb2.load(temp_file)

            assert kb == kb2

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestSessionContinuityProtocol:
    """Test session continuity with <30s recovery guarantee"""

    def test_session_checkpoint_creation(self):
        """Test SessionCheckpoint dataclass"""
        checkpoint = SessionCheckpoint(
            session_id="session_789",
            timestamp=datetime.now(timezone.utc),
            data={"state": "active"},
            status="active",
            progress=0.5
        )

        assert checkpoint.session_id == "session_789"
        assert checkpoint.progress == 0.5

    def test_create_checkpoint(self):
        """Test checkpoint creation"""
        events = [
            {"event_type": "login", "timestamp": "2025-10-14T10:00:00Z", "data": {}},
            {"event_type": "task_start", "timestamp": "2025-10-14T10:05:00Z", "data": {}}
        ]
        state = {"user_id": "user_123", "tasks_completed": 5}

        checkpoint = create_checkpoint(events, state)

        assert "event_summary" in checkpoint
        assert "state_hash" in checkpoint
        assert "timestamp" in checkpoint

    def test_resume_session_recovery_time(self):
        """Test <30s recovery guarantee"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            json.dump({"session_id": "test", "status": "active"}, f)

        try:
            start_time = time.time()

            session_data = resume_session(temp_file)

            elapsed = time.time() - start_time

            assert session_data is not None
            assert elapsed < 30.0  # <30s guarantee

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestPhase2EndToEnd:
    """End-to-end integration test"""

    def test_complete_session_lifecycle(self):
        """Test complete session lifecycle with all Phase 2 components"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Initialize session history
            history_file = os.path.join(temp_dir, "session_history.json")
            session_manager = SessionHistoryManager("e2e_session", history_file)

            # 2. Initialize task tracker
            task_tracker_dir = os.path.join(temp_dir, "tasks")

            # 3. Initialize knowledge base
            kb = KnowledgeBase()
            kb.add_pattern("test_pattern")

            # 4. Create session checkpoint
            events = [{"event_type": "login", "timestamp": datetime.now().isoformat(), "data": {}}]
            state = {"session_id": "e2e_session", "kb_patterns": 1}
            checkpoint = create_checkpoint(events, state)

            # 5. Verify all components work together
            assert session_manager.session_id == "e2e_session"
            assert len(kb.patterns) == 1
            assert checkpoint["event_summary"] is not None

            # 6. Test session recovery
            checkpoint_file = os.path.join(temp_dir, "checkpoint.json")
            with open(checkpoint_file, 'w') as f:
                json.dump(state, f)

            recovered_session = resume_session(checkpoint_file)
            assert recovered_session["session_id"] == "e2e_session"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
