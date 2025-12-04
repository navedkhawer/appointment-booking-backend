from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from bson import ObjectId
from app.database import patients_collection, records_collection, appointments_collection
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.services.gemini import generate_patient_summary

router = APIRouter()

# ==============================================================================
# 1. GET ALL PATIENTS (Registry List View)
# ==============================================================================
@router.get("", response_model=List[Dict[str, Any]])
async def get_patients():
    try:
        patients = await patients_collection.find().to_list(1000)
        
        results = []
        for p in patients:
            # FIX: Manually handle ObjectId serialization
            p["id"] = str(p.pop("_id"))
            
            # Fetch the most recent appointment for Admin Panel Table display
            latest_appt = await appointments_collection.find_one(
                {"patient_id": p["id"]},
                sort=[("date", -1), ("time", -1)]
            )
            
            if latest_appt:
                custom_id = latest_appt.get("custom_id")
                if not custom_id:
                     custom_id = f"#{str(latest_appt['_id'])[-6:].upper()}"

                p["latest_booking_id"] = custom_id
                p["latest_date"] = latest_appt.get("date")
                p["latest_time"] = latest_appt.get("time")
            else:
                p["latest_booking_id"] = "New Patient"
                p["latest_date"] = None
                p["latest_time"] = None
                
            results.append(p)
            
        return results
    except Exception as e:
        print(f"❌ ERROR in get_patients: {e}") 
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# 2. GET SINGLE PATIENT PROFILE (Detailed View)
# ==============================================================================
@router.get("/{id}", response_model=Patient)
async def get_patient_details(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    patient = await patients_collection.find_one({"_id": ObjectId(id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # --- ENRICH WITH LATEST APPOINTMENT DATA ---
    # This fetches the specific details (Service, Notes, Files) for the Profile View
    latest_appt = await appointments_collection.find_one(
        {"patient_id": id},
        sort=[("date", -1), ("time", -1)]
    )
    
    if latest_appt:
        custom_id = latest_appt.get("custom_id") or f"#{str(latest_appt['_id'])[-6:].upper()}"
        
        # Basic Info
        patient["latest_booking_id"] = custom_id
        patient["latest_date"] = latest_appt.get("date")
        patient["latest_time"] = latest_appt.get("time")
        
        # Detailed Info (The missing fields you requested)
        patient["latest_service_category"] = latest_appt.get("service_category", "General")
        patient["latest_specific_type"] = latest_appt.get("specific_type", "Standard")
        patient["latest_file_urls"] = latest_appt.get("file_urls", [])
        patient["latest_notes"] = latest_appt.get("notes", "")
    
    return patient

# ==============================================================================
# 3. GET MEDICAL HISTORY
# ==============================================================================
@router.get("/{id}/history", response_model=List[MedicalRecord])
async def get_medical_history(id: str):
    # Strictly filter by the patient_id string to ensure unique history
    records = await records_collection.find({"patient_id": id}).sort("date", -1).to_list(1000)
    
    # Fix ObjectId serialization for Pydantic
    for r in records:
        r["id"] = str(r.pop("_id"))
        
    return records

# ==============================================================================
# 4. ADD PRESCRIPTION / MEDICAL RECORD
# ==============================================================================
@router.post("/{id}/records")
async def add_medical_record(id: str, record: MedicalRecord):
    # 1. Convert Pydantic model to dict
    record_dict = record.model_dump(by_alias=True, exclude={"id"})
    
    # 2. FORCE the patient_id to match the URL parameter.
    # This ensures the record is physically stored with the correct ID in MongoDB.
    record_dict["patient_id"] = id
    
    # 3. Insert
    await records_collection.insert_one(record_dict)
    
    # 4. Update Patient's "Last Visit"
    await patients_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"last_visit": record.date}}
    )
    return {"message": "Medical record added"}

# ==============================================================================
# 5. GENERATE AI SUMMARY
# ==============================================================================
@router.post("/{id}/generate-summary")
async def generate_and_save_summary(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    history = await records_collection.find({"patient_id": id}).sort("date", -1).to_list(100)
    
    if not history:
        return {"summary": "No medical history available to analyze."}

    text_parts = []
    for h in history:
        rx_text = ""
        if 'prescriptions' in h and isinstance(h['prescriptions'], list):
            rx_list = [f"{rx.get('name')} ({rx.get('dosage')})" for rx in h['prescriptions']]
            if rx_list:
                rx_text = f" | Meds: {', '.join(rx_list)}"
        
        entry = f"- Date: {h.get('date')} | Diagnosis: {h.get('diagnosis')} | Notes: {h.get('notes')}{rx_text}"
        text_parts.append(entry)

    full_text = "\n".join(text_parts)
    summary_text = await generate_patient_summary(full_text)

    await patients_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"ai_summary": summary_text}}
    )

    return {"summary": summary_text}