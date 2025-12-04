from typing import Literal, Optional, List
from .common import MongoBaseModel

# --- READ MODEL (Used when fetching appointments for Admin Panel) ---
class AppointmentBase(MongoBaseModel):
    id: Optional[str] = None
    custom_id: Optional[str] = None
    patient_id: str
    patient_name: str
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None
    
    # New Fields for Updated Workflow
    service_category: Optional[str] = None
    specific_type: Optional[str] = None
    file_urls: List[str] = []
    
    # Standard Fields
    service_type: Optional[str] = None # Combined string
    clinic: Optional[str] = None
    date: str
    time: str
    status: Literal['PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED'] = 'PENDING'
    notes: Optional[str] = None
    reason: Optional[str] = None

# --- WRITE MODEL (Used when booking a new appointment via Frontend) ---
class AppointmentCreate(MongoBaseModel):
    # Personal Information
    patient_name: str
    patient_email: str
    patient_phone: str
    patient_dob: str
    patient_gender: str
    emergency_contact: Optional[str] = None
    personal_number: Optional[str] = None # New Norwegian ID
    
    # Medical/Service Information
    service_category: str # e.g., "Digital Consultation"
    specific_type: Optional[str] = None # e.g., "Knee"
    description: Optional[str] = None # For "Other" descriptions
    
    # Legacy Medical Fields (Optional now)
    medications: Optional[str] = None
    allergies: Optional[str] = None
    conditions: Optional[str] = None
    symptoms: Optional[str] = None
    reason: Optional[str] = None
    
    # Files
    file_urls: List[str] = [] 
    
    # Booking Details
    date: str
    time: str
    slot_id: Optional[str] = None 
    service_type: str = "General Consultation" # Fallback/Combined
    clinic: str = "Central Clinic"
    notes: Optional[str] = None