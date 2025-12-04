from datetime import datetime
from app.database import db

# Collection to store the daily counters
counters_collection = db["counters"]

async def generate_unique_id() -> str:
    """
    Generates a unique daily ID in format: PN-YYYYMMDD-XXXX
    Example: PN-20251125-0001
    """
    # 1. Get today's date string for the sequence key
    today_str = datetime.now().strftime("%Y%m%d")
    
    # 2. Atomic Update: Find the counter for today, increment it by 1.
    # If it doesn't exist (new day), create it with seq: 1
    result = await counters_collection.find_one_and_update(
        {"_id": "appointment_seq_" + today_str},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    
    # 3. Get the sequence number
    sequence = result["seq"]
    
    # 4. Format with padding (0001, 0002, etc.)
    # PN stands for Patient/Prescription Number
    custom_id = f"PN-{today_str}-{sequence:04d}"
    
    return custom_id