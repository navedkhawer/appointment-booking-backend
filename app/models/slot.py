from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class Slot(BaseModel):
    id: Optional[str] = None
    date: date
    time: str  # 12-hour format like '9:00 AM'
    booked_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class SlotCreate(BaseModel):
    date: date
    time: str
