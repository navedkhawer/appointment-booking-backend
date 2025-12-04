from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Convert ObjectId or Datetime to string if necessary before sending
        # But we assume the service layer handles serialization
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Remove dead connection
                self.disconnect(connection)

manager = ConnectionManager()