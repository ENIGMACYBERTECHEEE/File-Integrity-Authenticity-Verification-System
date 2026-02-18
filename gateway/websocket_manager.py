"""
WebSocket Manager for Real-time Updates.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """
        Send message to a specific user's connections.
        
        Args:
            message: Message data
            user_id: Target user ID
        """
        if user_id in self.active_connections:
            message_json = json.dumps(message)
            disconnected = set()
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.active_connections[user_id].discard(ws)
    
    async def broadcast(self, message: dict, exclude_user: str = None):
        """
        Broadcast message to all connected users.
        
        Args:
            message: Message data
            exclude_user: Optional user ID to exclude from broadcast
        """
        message_json = json.dumps(message)
        
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
                
            for websocket in connections:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")
    
    async def notify_file_upload(self, user_id: str, file_data: dict):
        """
        Notify user about file upload.
        
        Args:
            user_id: User ID
            file_data: File information
        """
        message = {
            "type": "file_uploaded",
            "timestamp": datetime.utcnow().isoformat(),
            "data": file_data
        }
        await self.send_personal_message(message, user_id)
    
    async def notify_verification_complete(self, user_id: str, verification_data: dict):
        """
        Notify user about verification completion.
        
        Args:
            user_id: User ID
            verification_data: Verification results
        """
        message = {
            "type": "verification_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "data": verification_data
        }
        await self.send_personal_message(message, user_id)
    
    def get_active_users_count(self) -> int:
        """Get count of users with active connections."""
        return len(self.active_connections)
    
    def get_total_connections(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())


# Global connection manager instance
connection_manager = ConnectionManager()
