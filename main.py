import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Correct Imports
from app.routes import appointments, patients, stats, auth, ai, schedule, notifications
from app.database import client
from app.services.notification import watch_appointments

app = FastAPI(title="MediCare Connect API", version="1.0.0")

# --- CORS CONFIGURATION ---
# Must match the exact domains of your frontend/admin apps (No trailing slashes)
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://helse-admin.vercel.app",
    "https://helse-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Critical: Allows HttpOnly Cookies for Auth
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # 1. Check MongoDB Connection
    try:
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")

    # 2. Start Real-time Notification Service
    # This runs the MongoDB Change Stream listener in the background loop
    # It watches for new appointments and broadcasts them via WebSockets
    asyncio.create_task(watch_appointments())

# Register Routes
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(stats.router, prefix="/api/stats", tags=["Dashboard"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Services"])
app.include_router(schedule.router, prefix="/api/admin/schedule", tags=["Schedule"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

@app.get("/")
def root():
    return {"message": "MediCare Connect API is running"}