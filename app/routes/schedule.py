from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from datetime import datetime, date
from bson import ObjectId
import re

from app.database import slots_collection

router = APIRouter()

# --- Helpers ---
def validate_12h_format(t: str):
    pattern = r'^(0?[1-9]|1[0-2]):[0-5][0-9]\s(AM|PM)$'
    if not re.match(pattern, t):
        raise HTTPException(status_code=400, detail="Time must be in 'HH:MM AM/PM' format")

def serialize_slot(slot):
    return {
        "id": str(slot["_id"]),
        "date": slot["date"],
        "time": slot["time"],
        "is_booked": slot.get("is_booked", False),
        "appointment_id": slot.get("appointment_id")
    }

# --- Endpoints ---

@router.get("/overview")
async def get_schedule_overview():
    today = datetime.now().strftime("%Y-%m-%d")
    slots = await slots_collection.find({"date": {"$gte": today}}).sort([("date", 1), ("time", 1)]).to_list(5000)
    return [serialize_slot(s) for s in slots]

# UPDATED: Add a slot for a SPECIFIC date only
@router.post("/add")
async def add_single_slot(date: str = Body(...), time: str = Body(...)):
    """Adds a single slot for a specific date and time."""
    validate_12h_format(time)
    
    # Check duplicate for this specific date/time
    exists = await slots_collection.find_one({"date": date, "time": time})
    if exists:
        raise HTTPException(status_code=400, detail="Slot already exists for this time.")

    new_slot = {
        "date": date,
        "time": time,
        "is_booked": False,
        "appointment_id": None,
        "created_at": datetime.now()
    }
    
    await slots_collection.insert_one(new_slot)
    return {"message": "Slot added successfully"}

@router.delete("/{slot_id}")
async def delete_slot(slot_id: str):
    if not ObjectId.is_valid(slot_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    slot = await slots_collection.find_one({"_id": ObjectId(slot_id)})
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
        
    if slot.get("is_booked"):
        raise HTTPException(status_code=400, detail="Cannot delete a booked slot.")

    await slots_collection.delete_one({"_id": ObjectId(slot_id)})
    return {"message": "Slot deleted"}

@router.get("/available-slots/{date_str}")
async def get_public_slots(date_str: str):
    slots = await slots_collection.find({"date": date_str}).to_list(100)
    
    # Sort slots by time (AM/PM aware)
    serialized = [serialize_slot(s) for s in slots]
    serialized.sort(key=lambda x: datetime.strptime(x['time'], "%I:%M %p"))
    
    return serialized

@router.post("/book")
async def book_slot(slot_id: str = Body(...), patient_id: str = Body(...), notes: str = Body(None)):
    if not ObjectId.is_valid(slot_id):
        raise HTTPException(status_code=400, detail="Invalid Slot ID")

    result = await slots_collection.update_one(
        {"_id": ObjectId(slot_id), "is_booked": False},
        {"$set": {"is_booked": True, "booked_by": patient_id, "notes": notes}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Slot is already booked or unavailable")
        
    return {"success": True}