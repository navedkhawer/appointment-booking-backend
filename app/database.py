import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env file")

# tlsAllowInvalidCertificates=True is often needed for local development with MongoDB Atlas
client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000, # Fail fast if connection fails (5 seconds)
    tlsAllowInvalidCertificates=True 
)
db = client[DB_NAME]

# Collections
patients_collection = db["patients"]
appointments_collection = db["appointments"]
records_collection = db["medical_records"]
slots_collection = db["slots"]  # <--- Added this line

users_collection = db["users"]