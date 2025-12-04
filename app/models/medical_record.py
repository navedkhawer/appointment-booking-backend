from typing import List, Optional
from pydantic import BaseModel
from .common import MongoBaseModel

class PrescriptionItem(BaseModel):
    name: str
    dosage: str
    duration: str
    frequency: str

class MedicalRecord(MongoBaseModel):
    # Make sure patient_id is present. 
    # We will overwrite it in the route to be safe, but it must exist in the schema.
    patient_id: str 
    date: str
    doctor_name: str
    diagnosis: str
    notes: str
    prescriptions: List[PrescriptionItem] = []
    advice: Optional[str] = None