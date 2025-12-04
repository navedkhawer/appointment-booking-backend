import asyncio
from app.database import db, appointments_collection
from app.models.notification import Notification
from app.services.websocket import manager
from datetime import datetime

notifications_collection = db["notifications"]

class NotificationService:
    @staticmethod
    async def create_notification(data: dict):
        """Save notification to DB and broadcast via WebSocket"""
        new_notif = Notification(**data)
        
        # 1. Insert into DB
        result = await notifications_collection.insert_one(
            new_notif.model_dump(by_alias=True, exclude={"id"})
        )
        
        # 2. Prepare payload for WebSocket (serialize ID and Date)
        ws_payload = {
            "id": str(result.inserted_id),
            "title": new_notif.title,
            "message": new_notif.message,
            "type": new_notif.type,
            "related_id": new_notif.related_id,
            "is_read": False,
            "created_at": new_notif.created_at.isoformat()
        }
        
        # 3. Broadcast
        await manager.broadcast(ws_payload)

    @staticmethod
    async def get_recent(limit=20):
        """Get latest notifications for the REST API"""
        cursor = notifications_collection.find().sort("created_at", -1).limit(limit)
        notifs = await cursor.to_list(length=limit)
        
        # Serialize _id
        for n in notifs:
            n["id"] = str(n.pop("_id"))
        return notifs

    @staticmethod
    async def mark_all_read():
        await notifications_collection.update_many(
            {"is_read": False},
            {"$set": {"is_read": True}}
        )

# --- BACKGROUND TASK: WATCH MONGODB ---
async def watch_appointments():
    """
    Real-time listener for MongoDB 'appointments' collection.
    Requires MongoDB Atlas or Replica Set.
    """
    print("👀 Starting Change Stream Watcher on Appointments...")
    try:
        # Watch for Insert operations only
        async with appointments_collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
            async for change in stream:
                doc = change["fullDocument"]
                
                # Logic: When a new appointment is inserted, create a notification
                patient_name = doc.get("patient_name", "Unknown")
                time_slot = doc.get("time", "")
                date_str = doc.get("date", "")
                
                await NotificationService.create_notification({
                    "title": "New Appointment Booked",
                    "message": f"{patient_name} booked for {date_str} at {time_slot}",
                    "type": "appointment",
                    "related_id": str(doc["_id"]),
                    "is_read": False,
                    "created_at": datetime.now()
                })
    except Exception as e:
        print(f"❌ Change Stream Error: {e}")