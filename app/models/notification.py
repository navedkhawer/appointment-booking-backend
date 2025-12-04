from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from .common import MongoBaseModel

class Notification(MongoBaseModel):
    title: str
    message: str
    type: Literal['appointment', 'system'] = 'appointment'
    related_id: Optional[str] = None  # e.g., Appointment ID
    is_read: bool = False
    created_at: datetime = datetime.now()

class MarkReadRequest(BaseModel):
    ids: list[str] = [] # Optional: send specific IDs or empty for "all"