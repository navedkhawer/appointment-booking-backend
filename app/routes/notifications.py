from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.services.notification import NotificationService
from app.services.websocket import manager

router = APIRouter()

# 1. REST API: Get Notifications
@router.get("/", response_model=List[dict])
async def get_notifications():
    return await NotificationService.get_recent()

# 2. REST API: Mark as Read
@router.post("/mark-read")
async def mark_read():
    await NotificationService.mark_all_read()
    return {"status": "success"}

# 3. WEBSOCKET ENDPOINT
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for messages (optional logic)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)