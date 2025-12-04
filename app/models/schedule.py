from typing import List, Optional
from .common import MongoBaseModel
from pydantic import BaseModel

class SlotBase(MongoBaseModel):
    date: str  # YYYY-MM-DD
    start_time: str # HH:MM
    end_time: str   # HH:MM
    is_booked: bool = False
    appointment_id: Optional[str] = None

class SlotGenerateRequest(BaseModel):
    date: str
    start_time: str
    end_time: str
    duration: int # minutes
    break_time: int # minutes between slots

class BulkGenerateRequest(BaseModel):
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    duration: int
    break_time: int