from pydantic import EmailStr, Field
from typing import Literal, Optional, List
from .common import MongoBaseModel

class Patient(MongoBaseModel):
    name: str
    email: EmailStr
    phone: str
    dob: str
    gender: Literal['Male', 'Female', 'Other']
    
    # Optional fields
    emergency_contact: Optional[str] = None
    last_visit: Optional[str] = None
    ai_summary: Optional[str] = None
    personal_number: Optional[str] = None 

    # --- DYNAMIC FIELDS FOR ADMIN PROFILE ---
    # These must be declared here, otherwise FastAPI strips them out!
    latest_booking_id: Optional[str] = None
    latest_date: Optional[str] = None
    latest_time: Optional[str] = None
    
    # The missing fields causing your issue:
    latest_service_category: Optional[str] = None
    latest_specific_type: Optional[str] = None
    latest_file_urls: Optional[List[str]] = None
    latest_notes: Optional[str] = None