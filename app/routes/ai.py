from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.gemini import generate_patient_summary

router = APIRouter()

# Accept a list of generic dictionaries (handles _id, prescriptions, etc.)
@router.post("/summarize")
async def summarize_patient_history(history: List[Dict[str, Any]]):
    print("----- 🧠 AI SUMMARY REQUEST RECEIVED -----")
    
    if not history:
        return {"summary": "No medical history available to analyze."}

    # Format the data into a readable string for the AI
    # We safely use .get() to avoid errors if fields are missing
    text_parts = []
    for h in history:
        date = h.get('date', 'Unknown Date')
        diagnosis = h.get('diagnosis', 'No Diagnosis')
        notes = h.get('notes', '')
        
        # Format prescriptions if they exist
        rx_text = ""
        if 'prescriptions' in h and isinstance(h['prescriptions'], list):
            rx_list = [f"{rx.get('name')} ({rx.get('dosage')})" for rx in h['prescriptions']]
            if rx_list:
                rx_text = f" | Meds: {', '.join(rx_list)}"

        entry = f"- Date: {date} | Diagnosis: {diagnosis} | Notes: {notes}{rx_text}"
        text_parts.append(entry)

    full_text = "\n".join(text_parts)
    
    print(f"Sending {len(text_parts)} records to Gemini...")
    summary = await generate_patient_summary(full_text)
    
    print("✅ Summary Generated Successfully")
    return {"summary": summary}