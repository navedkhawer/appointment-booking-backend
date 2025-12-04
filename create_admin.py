import asyncio
import os
from dotenv import load_dotenv
from app.database import users_collection
from app.utils import get_hash

# Load environment variables from .env file
load_dotenv()

async def create_user():
    # --- CONFIGURATION FROM ENV ---
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    
    # Validation
    if not email or not password:
        print("❌ Error: ADMIN_EMAIL or ADMIN_PASSWORD is missing in .env file.")
        return
    # ---------------------
    
    print(f"🔄 Checking for existing user: {email}")
    existing = await users_collection.find_one({"email": email})
    
    if existing:
        print("⚠️ User already exists. Deleting to recreate with new hash...")
        await users_collection.delete_one({"email": email})

    # Hash the password using Argon2
    print("🔐 Hashing password...")
    hashed_password = get_hash(password)

    user = {
        "name": "Dr. Hassan Mehmood",
        "email": email,
        "password_hash": hashed_password,
        "role": "doctor",
        "created_at": "2025-12-04"
    }
    
    await users_collection.insert_one(user)
    print("------------------------------------------------")
    print(f"✅ User created successfully!")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password)} (Hidden for security)")
    print("------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(create_user())