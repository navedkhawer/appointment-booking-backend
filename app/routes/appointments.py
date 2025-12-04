from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from typing import List
from bson import ObjectId
from pydantic import BaseModel

# Database Imports
from app.database import appointments_collection, patients_collection, slots_collection
# Model Imports
from app.models.appointment import AppointmentBase, AppointmentCreate
# Service Imports
from app.services.id_generator import generate_unique_id
from app.services.email import (
    send_cancellation_email, 
    send_confirmation_email, 
    send_admin_confirmation_email, # ADDED THIS IMPORT
    ADMIN_EMAIL
)
from app.services.s3 import generate_presigned_url

router = APIRouter()

# --- MODELS ---
class CancellationRequest(BaseModel):
    id: str
    reason: str

class FileUploadRequest(BaseModel):
    file_name: str
    file_type: str

# ==============================================================================
# 1. GET ALL APPOINTMENTS
# ==============================================================================
@router.get("/", response_model=List[AppointmentBase])
async def get_appointments():
    appointments = await appointments_collection.find().sort("date", -1).to_list(2000)
    
    results = []
    for appt in appointments:
        appt["id"] = str(appt["_id"])
        if "custom_id" not in appt:
            appt["custom_id"] = f"#{str(appt['_id'])[-6:].upper()}"
        results.append(appt)
        
    return results

# ==============================================================================
# 2. GENERATE S3 UPLOAD URL
# ==============================================================================
@router.post("/upload-url")
async def get_upload_url(data: FileUploadRequest):
    result = generate_presigned_url(data.file_name, data.file_type)
    if not result:
        raise HTTPException(status_code=500, detail="AWS S3 Configuration Error")
    return result

# ==============================================================================
# 3. CREATE APPOINTMENT (BOOKING)
# ==============================================================================
@router.post("/", status_code=201)
async def create_appointment(data: AppointmentCreate, background_tasks: BackgroundTasks):
    print(f"----- 📨 INCOMING BOOKING REQUEST: {data.patient_name} -----")
    
    # A. Validate Slot
    if data.slot_id:
        if not ObjectId.is_valid(data.slot_id):
            raise HTTPException(status_code=400, detail="Invalid Slot ID format")
        slot = await slots_collection.find_one({"_id": ObjectId(data.slot_id)})
        if not slot:
            raise HTTPException(status_code=404, detail="Selected time slot not found.")
        if slot.get("is_booked"):
            raise HTTPException(status_code=400, detail="This time slot has just been booked.")

    try:
        # B. Find or Create Patient (Strict Matching)
        existing_patient = await patients_collection.find_one({
            "email": data.patient_email,
            "name": {"$regex": f"^{data.patient_name}$", "$options": "i"}
        })

        if existing_patient:
            patient_id = str(existing_patient["_id"])
            await patients_collection.update_one(
                {"_id": existing_patient["_id"]},
                {"$set": {
                    "phone": data.patient_phone,
                    "dob": data.patient_dob,
                    "gender": data.patient_gender,
                    "emergency_contact": data.emergency_contact,
                    "personal_number": data.personal_number
                }}
            )
        else:
            new_patient = {
                "name": data.patient_name,
                "email": data.patient_email,
                "phone": data.patient_phone,
                "dob": data.patient_dob,
                "gender": data.patient_gender,
                "emergency_contact": data.emergency_contact,
                "personal_number": data.personal_number,
                "last_visit": None
            }
            result = await patients_collection.insert_one(new_patient)
            patient_id = str(result.inserted_id)

        # C. Generate Unique ID
        unique_id = await generate_unique_id()

        # D. Save Appointment
        appointment_doc = {
            "custom_id": unique_id,
            "patient_id": patient_id,
            "patient_name": data.patient_name,
            "patient_email": data.patient_email,
            "patient_phone": data.patient_phone,
            
            "service_category": data.service_category,
            "specific_type": data.specific_type,
            "file_urls": data.file_urls,
            
            "service_type": data.service_type,
            "clinic": data.clinic,
            "date": data.date,
            "time": data.time,
            "slot_id": data.slot_id,
            "status": "PENDING", 
            "notes": data.notes,
            "reason": data.reason,
            "symptoms": data.symptoms,
            "medications": data.medications,
            "allergies": data.allergies,
        }
        
        new_appt = await appointments_collection.insert_one(appointment_doc)
        new_appt_id = str(new_appt.inserted_id)
        
        # E. Lock Slot
        if data.slot_id:
            await slots_collection.update_one(
                {"_id": ObjectId(data.slot_id)},
                {"$set": {"is_booked": True, "appointment_id": new_appt_id}}
            )

        # F. Send Confirmation Emails (Background)
        
        # 1. To Patient (Using Patient Template)
        if data.patient_email:
            background_tasks.add_task(
                send_confirmation_email,
                to_email=data.patient_email,
                booking_id=unique_id,
                patient_name=data.patient_name,
                date=data.date,
                time=data.time,
                service=data.service_type
            )

        # 2. To Admin (Using Admin Template)
        background_tasks.add_task(
            send_admin_confirmation_email,
            booking_id=unique_id,
            patient_name=data.patient_name,
            patient_phone=data.patient_phone,
            patient_email=data.patient_email,
            date=data.date,
            time=data.time,
            service=data.service_type
        )

        print(f"✅ SUCCESS! Appointment ID: {new_appt_id}. Emails queued.")
        
        return {
            "id": new_appt_id, 
            "custom_id": unique_id,
            "message": "Appointment booked successfully"
        }
        
    except Exception as e:
        print(f"❌ ERROR during booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# 4. CANCEL APPOINTMENT
# ==============================================================================
@router.post("/cancel")
async def cancel_appointment(data: CancellationRequest, background_tasks: BackgroundTasks):
    if not ObjectId.is_valid(data.id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    appt = await appointments_collection.find_one({"_id": ObjectId(data.id)})
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    await appointments_collection.update_one(
        {"_id": ObjectId(data.id)},
        {"$set": {
            "status": "CANCELLED",
            "cancellation_reason": data.reason,
            "notes": f"{appt.get('notes', '')} [Cancelled: {data.reason}]"
        }}
    )

    if appt.get("slot_id"):
        await slots_collection.update_one(
            {"_id": ObjectId(appt["slot_id"])},
            {"$set": {"is_booked": False, "appointment_id": None}}
        )

    if appt.get("patient_email"):
        background_tasks.add_task(
            send_cancellation_email,
            to_email=appt["patient_email"],
            patient_name=appt["patient_name"],
            date=appt["date"],
            time=appt["time"],
            reason=data.reason
        )

    return {"message": "Cancelled and notified"}

# ==============================================================================
# 5. UPDATE STATUS
# ==============================================================================
@router.put("/{id}/status")
async def update_status(id: str, status: str = Body(..., embed=True)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    result = await appointments_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status}}
    )
    
    if result.modified_count == 1:
        if status == "CANCELLED":
            appt = await appointments_collection.find_one({"_id": ObjectId(id)})
            if appt and appt.get("slot_id"):
                await slots_collection.update_one(
                    {"_id": ObjectId(appt["slot_id"])},
                    {"$set": {"is_booked": False, "appointment_id": None}}
                )
        return {"message": "Updated"}
    
    raise HTTPException(status_code=404, detail="Not Found")