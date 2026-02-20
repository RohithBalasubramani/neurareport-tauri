"""
Collaboration Service Tests - Testing CollaborationService.
"""

import os
import threading
import time
import uuid

import pytest


from backend.app.services.documents.collaboration import (
    CollaborationService,
    CollaborationSession,
    CollaboratorPresence,
)


@pytest.fixture
def collab_service() -> CollaborationService:
    """Create a collaboration service."""
    return CollaborationService(websocket_base_url="ws://localhost:8000")


class TestStartSession:
    """Test session creation."""

    def test_start_session_creates_new(self, collab_service: CollaborationService):
        """Starting session creates new session."""
        session = collab_service.start_session("doc-123")
        assert session is not None
        assert session.document_id == "doc-123"
        assert session.is_active is True
        assert session.websocket_url == "ws://localhost:8000/ws/collab/doc-123"

    def test_start_session_with_user(self, collab_service: CollaborationService):
        """Starting session with user ID adds participant."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        assert "user-1" in session.participants

    def test_start_session_returns_existing(self, collab_service: CollaborationService):
        """Starting session for same document returns existing session."""
        session1 = collab_service.start_session("doc-123")
        session2 = collab_service.start_session("doc-123")
        assert session1.id == session2.id

    def test_start_session_different_documents(self, collab_service: CollaborationService):
        """Different documents get different sessions."""
        session1 = collab_service.start_session("doc-1")
        session2 = collab_service.start_session("doc-2")
        assert session1.id != session2.id

    def test_start_session_generates_unique_ids(self, collab_service: CollaborationService):
        """Each session should have unique ID."""
        sessions = [collab_service.start_session(f"doc-{i}") for i in range(5)]
        ids = [s.id for s in sessions]
        assert len(set(ids)) == 5

    def test_start_session_sets_timestamp(self, collab_service: CollaborationService):
        """Session should have created_at timestamp."""
        session = collab_service.start_session("doc-123")
        assert session.created_at is not None


class TestJoinSession:
    """Test joining sessions."""

    def test_join_session(self, collab_service: CollaborationService):
        """User can join existing session."""
        session = collab_service.start_session("doc-123")
        presence = collab_service.join_session(session.id, "user-1", "John")
        assert presence is not None
        assert presence.user_id == "user-1"
        assert presence.user_name == "John"

    def test_join_session_default_name(self, collab_service: CollaborationService):
        """Joining without name uses default."""
        session = collab_service.start_session("doc-123")
        presence = collab_service.join_session(session.id, "user-123")
        assert presence.user_name.startswith("User ")

    def test_join_session_adds_participant(self, collab_service: CollaborationService):
        """Joining adds user to participants list."""
        session = collab_service.start_session("doc-123")
        collab_service.join_session(session.id, "user-1")
        updated_session = collab_service.get_session(session.id)
        assert "user-1" in updated_session.participants

    def test_join_nonexistent_session(self, collab_service: CollaborationService):
        """Joining nonexistent session returns None."""
        result = collab_service.join_session("nonexistent", "user-1")
        assert result is None

    def test_join_assigns_color(self, collab_service: CollaborationService):
        """Joining assigns a color from palette."""
        session = collab_service.start_session("doc-123")
        presence = collab_service.join_session(session.id, "user-1")
        assert presence.color in CollaborationService.COLORS

    def test_join_assigns_different_colors(self, collab_service: CollaborationService):
        """Different users get different colors."""
        session = collab_service.start_session("doc-123")
        presence1 = collab_service.join_session(session.id, "user-1")
        presence2 = collab_service.join_session(session.id, "user-2")
        # Colors should be different (until palette cycles)
        assert presence1.color != presence2.color

    def test_join_sets_last_seen(self, collab_service: CollaborationService):
        """Joining sets last_seen timestamp."""
        session = collab_service.start_session("doc-123")
        presence = collab_service.join_session(session.id, "user-1")
        assert presence.last_seen is not None


class TestLeaveSession:
    """Test leaving sessions."""

    def test_leave_session(self, collab_service: CollaborationService):
        """User can leave session."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        result = collab_service.leave_session(session.id, "user-1")
        assert result is True

    def test_leave_removes_participant(self, collab_service: CollaborationService):
        """Leaving removes user from participants."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        collab_service.leave_session(session.id, "user-1")
        updated = collab_service.get_session(session.id)
        assert "user-1" not in updated.participants

    def test_leave_removes_presence(self, collab_service: CollaborationService):
        """Leaving removes user presence."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        collab_service.leave_session(session.id, "user-1")
        presence_list = collab_service.get_presence(session.id)
        assert all(p.user_id != "user-1" for p in presence_list)

    def test_leave_nonexistent_session(self, collab_service: CollaborationService):
        """Leaving nonexistent session returns False."""
        result = collab_service.leave_session("nonexistent", "user-1")
        assert result is False

    def test_leave_last_user_ends_session(self, collab_service: CollaborationService):
        """Leaving as last user ends session."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        collab_service.leave_session(session.id, "user-1")
        updated = collab_service.get_session(session.id)
        assert updated.is_active is False


class TestEndSession:
    """Test ending sessions."""

    def test_end_session(self, collab_service: CollaborationService):
        """Session can be ended."""
        session = collab_service.start_session("doc-123")
        result = collab_service.end_session(session.id)
        assert result is True

    def test_end_session_marks_inactive(self, collab_service: CollaborationService):
        """Ending session marks it as inactive."""
        session = collab_service.start_session("doc-123")
        collab_service.end_session(session.id)
        updated = collab_service.get_session(session.id)
        assert updated.is_active is False

    def test_end_nonexistent_session(self, collab_service: CollaborationService):
        """Ending nonexistent session returns False."""
        result = collab_service.end_session("nonexistent")
        assert result is False


class TestUpdatePresence:
    """Test presence updates."""

    def test_update_cursor_position(self, collab_service: CollaborationService):
        """Update cursor position."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        presence = collab_service.update_presence(session.id, "user-1", cursor_position=100)
        assert presence.cursor_position == 100

    def test_update_selection(self, collab_service: CollaborationService):
        """Update selection range."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        presence = collab_service.update_presence(
            session.id, "user-1",
            selection_start=50,
            selection_end=100,
        )
        assert presence.selection_start == 50
        assert presence.selection_end == 100

    def test_update_updates_last_seen(self, collab_service: CollaborationService):
        """Updating presence updates last_seen."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        presence1 = collab_service.get_presence(session.id)[0]
        original_last_seen = presence1.last_seen

        time.sleep(0.01)
        presence2 = collab_service.update_presence(session.id, "user-1", cursor_position=50)
        assert presence2.last_seen != original_last_seen

    def test_update_nonexistent_session(self, collab_service: CollaborationService):
        """Update in nonexistent session returns None."""
        result = collab_service.update_presence("nonexistent", "user-1", cursor_position=50)
        assert result is None

    def test_update_nonexistent_user(self, collab_service: CollaborationService):
        """Update for nonexistent user returns None."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        result = collab_service.update_presence(session.id, "nonexistent", cursor_position=50)
        assert result is None


class TestGetSession:
    """Test session retrieval."""

    def test_get_session_by_id(self, collab_service: CollaborationService):
        """Get session by ID."""
        created = collab_service.start_session("doc-123")
        retrieved = collab_service.get_session(created.id)
        assert retrieved.id == created.id

    def test_get_nonexistent_session(self, collab_service: CollaborationService):
        """Get nonexistent session returns None."""
        result = collab_service.get_session("nonexistent")
        assert result is None

    def test_get_session_by_document(self, collab_service: CollaborationService):
        """Get session by document ID."""
        created = collab_service.start_session("doc-123")
        retrieved = collab_service.get_session_by_document("doc-123")
        assert retrieved.id == created.id

    def test_get_session_by_document_nonexistent(self, collab_service: CollaborationService):
        """Get session for document without session returns None."""
        result = collab_service.get_session_by_document("nonexistent")
        assert result is None

    def test_get_session_by_document_inactive(self, collab_service: CollaborationService):
        """Get session for document with inactive session returns None."""
        session = collab_service.start_session("doc-123")
        collab_service.end_session(session.id)
        result = collab_service.get_session_by_document("doc-123")
        assert result is None


class TestGetPresence:
    """Test presence retrieval."""

    def test_get_presence_empty(self, collab_service: CollaborationService):
        """Get presence for empty session returns empty list."""
        session = collab_service.start_session("doc-123")
        presence = collab_service.get_presence(session.id)
        assert presence == []

    def test_get_presence_multiple_users(self, collab_service: CollaborationService):
        """Get presence for multiple users."""
        session = collab_service.start_session("doc-123")
        collab_service.join_session(session.id, "user-1", "John")
        collab_service.join_session(session.id, "user-2", "Jane")
        presence = collab_service.get_presence(session.id)
        assert len(presence) == 2

    def test_get_presence_nonexistent_session(self, collab_service: CollaborationService):
        """Get presence for nonexistent session returns empty list."""
        result = collab_service.get_presence("nonexistent")
        assert result == []


class TestWebSocketBaseUrl:
    """Test WebSocket URL configuration."""

    def test_set_websocket_base_url(self, collab_service: CollaborationService):
        """Set WebSocket base URL."""
        collab_service.set_websocket_base_url("ws://newhost:9000")
        session = collab_service.start_session("doc-123")
        assert "ws://newhost:9000" in session.websocket_url

    def test_set_websocket_url_updates_existing(self, collab_service: CollaborationService):
        """Setting URL updates existing active sessions."""
        session = collab_service.start_session("doc-123")
        collab_service.set_websocket_base_url("ws://newhost:9000")
        updated = collab_service.get_session(session.id)
        assert "ws://newhost:9000" in updated.websocket_url

    def test_set_empty_websocket_url_ignored(self, collab_service: CollaborationService):
        """Setting empty URL is ignored."""
        original_url = collab_service._websocket_base_url
        collab_service.set_websocket_base_url("")
        assert collab_service._websocket_base_url == original_url


class TestColorPalette:
    """Test color assignment."""

    def test_colors_cycle(self, collab_service: CollaborationService):
        """Colors should cycle through palette."""
        session = collab_service.start_session("doc-123")
        colors = []
        for i in range(len(CollaborationService.COLORS) + 2):
            presence = collab_service.join_session(session.id, f"user-{i}")
            colors.append(presence.color)

        # First 8 should be unique, then cycle repeats
        assert len(set(colors[:8])) == 8
        # 9th should match 1st
        assert colors[8] == colors[0]


class TestConcurrency:
    """Test thread safety."""

    def test_concurrent_session_starts(self, collab_service: CollaborationService):
        """Concurrent session starts should not cause issues."""
        results = []
        errors = []

        def start_session(doc_id):
            try:
                session = collab_service.start_session(doc_id)
                results.append(session.id)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=start_session, args=(f"doc-{i}",))
            for i in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

    def test_concurrent_joins(self, collab_service: CollaborationService):
        """Concurrent joins should not cause issues."""
        session = collab_service.start_session("doc-123")
        results = []
        errors = []

        def join_session(user_id):
            try:
                presence = collab_service.join_session(session.id, user_id)
                results.append(presence)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=join_session, args=(f"user-{i}",))
            for i in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

    def test_concurrent_presence_updates(self, collab_service: CollaborationService):
        """Concurrent presence updates should not cause issues."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        errors = []

        def update_presence(position):
            try:
                collab_service.update_presence(session.id, "user-1", cursor_position=position)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=update_presence, args=(i * 10,))
            for i in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
