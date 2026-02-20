"""
Collaboration Service - Real-time document collaboration using Y.js.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("neura.collaboration")


def _utcnow() -> datetime:
    """Get current UTC time with timezone info."""
    return datetime.now(timezone.utc)


class CollaborationSession(BaseModel):
    """Collaboration session model."""

    id: str
    document_id: str
    created_at: str
    participants: list[str] = []
    websocket_url: Optional[str] = None
    is_active: bool = True


class CollaboratorPresence(BaseModel):
    """Collaborator presence information."""

    user_id: str
    user_name: str
    cursor_position: Optional[int] = None
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    color: str = "#3B82F6"  # Default blue
    last_seen: str


class CollaborationService:
    """Service for real-time collaboration."""

    # Color palette for collaborators
    COLORS = [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Violet
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
    ]

    def __init__(self, websocket_base_url: str = "ws://localhost:8000"):
        self._sessions: dict[str, CollaborationSession] = {}
        self._presence: dict[str, dict[str, CollaboratorPresence]] = {}
        self._websocket_base_url = websocket_base_url
        self._color_index = 0
        # Thread lock for protecting shared state
        self._lock = threading.Lock()

    def set_websocket_base_url(self, websocket_base_url: str) -> None:
        """Update the base URL used to build websocket session links."""
        if not websocket_base_url:
            return
        with self._lock:
            self._websocket_base_url = websocket_base_url
            for session in self._sessions.values():
                if session.is_active:
                    session.websocket_url = f"{self._websocket_base_url}/ws/collab/{session.document_id}"

    def start_session(
        self,
        document_id: str,
        user_id: Optional[str] = None,
    ) -> CollaborationSession:
        """Start a new collaboration session for a document."""
        with self._lock:
            # Check if session already exists
            for session in self._sessions.values():
                if session.document_id == document_id and session.is_active:
                    if user_id:
                        self._join_session_unlocked(session.id, user_id)
                    return session

            # Create new session
            session = CollaborationSession(
                id=str(uuid.uuid4()),
                document_id=document_id,
                created_at=_utcnow().isoformat(),
                websocket_url=f"{self._websocket_base_url}/ws/collab/{document_id}",
            )

            self._sessions[session.id] = session
            self._presence[session.id] = {}

            if user_id:
                self._join_session_unlocked(session.id, user_id)

            logger.info(f"Started collaboration session {session.id} for document {document_id}")
            return session

    def _join_session_unlocked(
        self,
        session_id: str,
        user_id: str,
        user_name: Optional[str] = None,
    ) -> Optional[CollaboratorPresence]:
        """Join session without acquiring lock (for internal use when lock is already held)."""
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]
        if user_id not in session.participants:
            session.participants.append(user_id)

        # Create presence
        presence = CollaboratorPresence(
            user_id=user_id,
            user_name=user_name or f"User {user_id[:8]}",
            color=self._get_next_color_unlocked(),
            last_seen=_utcnow().isoformat(),
        )

        self._presence[session_id][user_id] = presence
        logger.info(f"User {user_id} joined session {session_id}")
        return presence

    def join_session(
        self,
        session_id: str,
        user_id: str,
        user_name: Optional[str] = None,
    ) -> Optional[CollaboratorPresence]:
        """Join an existing collaboration session."""
        with self._lock:
            return self._join_session_unlocked(session_id, user_id, user_name)

    def leave_session(self, session_id: str, user_id: str) -> bool:
        """Leave a collaboration session."""
        with self._lock:
            if session_id not in self._sessions:
                return False

            session = self._sessions[session_id]
            if user_id in session.participants:
                session.participants.remove(user_id)

            if user_id in self._presence.get(session_id, {}):
                del self._presence[session_id][user_id]

            # End session if no participants
            if not session.participants:
                self._end_session_unlocked(session_id)

            logger.info(f"User {user_id} left session {session_id}")
            return True

    def _end_session_unlocked(self, session_id: str) -> bool:
        """End session without acquiring lock (for internal use)."""
        if session_id not in self._sessions:
            return False

        self._sessions[session_id].is_active = False
        logger.info(f"Ended collaboration session {session_id}")
        return True

    def end_session(self, session_id: str) -> bool:
        """End a collaboration session."""
        with self._lock:
            return self._end_session_unlocked(session_id)

    def update_presence(
        self,
        session_id: str,
        user_id: str,
        cursor_position: Optional[int] = None,
        selection_start: Optional[int] = None,
        selection_end: Optional[int] = None,
    ) -> Optional[CollaboratorPresence]:
        """Update a collaborator's presence."""
        with self._lock:
            if session_id not in self._presence:
                return None
            if user_id not in self._presence[session_id]:
                return None

            presence = self._presence[session_id][user_id]
            if cursor_position is not None:
                presence.cursor_position = cursor_position
            if selection_start is not None:
                presence.selection_start = selection_start
            if selection_end is not None:
                presence.selection_end = selection_end
            presence.last_seen = _utcnow().isoformat()

            return presence

    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get a collaboration session by ID."""
        with self._lock:
            return self._sessions.get(session_id)

    def get_session_by_document(self, document_id: str) -> Optional[CollaborationSession]:
        """Get active session for a document."""
        with self._lock:
            for session in self._sessions.values():
                if session.document_id == document_id and session.is_active:
                    return session
            return None

    def get_presence(self, session_id: str) -> list[CollaboratorPresence]:
        """Get all collaborator presence for a session."""
        with self._lock:
            if session_id not in self._presence:
                return []
            return list(self._presence[session_id].values())

    def _get_next_color_unlocked(self) -> str:
        """Get next color from palette (without lock)."""
        color = self.COLORS[self._color_index % len(self.COLORS)]
        self._color_index += 1
        return color

    def _get_next_color(self) -> str:
        """Get next color from palette."""
        with self._lock:
            return self._get_next_color_unlocked()


# WebSocket handler for Y.js synchronization
class YjsWebSocketHandler:
    """WebSocket handler for Y.js document synchronization."""

    def __init__(self, collaboration_service: CollaborationService):
        self._collab_service = collaboration_service
        self._connections: dict[str, set] = {}  # document_id -> set of websockets

    async def handle_connection(
        self,
        websocket: WebSocket,
        document_id: str,
        user_id: str,
    ):
        """Handle a new WebSocket connection for collaboration."""
        # Initialize connection set for document
        if document_id not in self._connections:
            self._connections[document_id] = set()

        await websocket.accept()
        self._connections[document_id].add(websocket)

        # Get or create session
        session = self._collab_service.start_session(document_id, user_id)

        try:
            async for message in websocket.iter_bytes():
                await self._handle_message(websocket, document_id, user_id, message)
        except WebSocketDisconnect:
            pass
        finally:
            self._connections[document_id].discard(websocket)
            self._collab_service.leave_session(session.id, user_id)

    async def _handle_message(
        self,
        websocket,
        document_id: str,
        user_id: str,
        message: bytes,
    ):
        """Handle incoming Y.js sync message."""
        # Broadcast to all other connections for this document
        if document_id in self._connections:
            for conn in self._connections[document_id]:
                if conn != websocket:
                    try:
                        if isinstance(message, bytes):
                            await conn.send_bytes(message)
                        else:
                            await conn.send_text(str(message))
                    except Exception as e:
                        logger.warning(f"Failed to send to connection: {e}")

    async def broadcast_presence(self, document_id: str, presence_data: dict):
        """Broadcast presence update to all connections."""
        if document_id not in self._connections:
            return

        message = json.dumps({"type": "presence", "data": presence_data})
        for conn in self._connections[document_id]:
            try:
                await conn.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast presence: {e}")
