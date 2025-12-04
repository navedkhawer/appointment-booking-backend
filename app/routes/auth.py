from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from bson import ObjectId
from app.database import users_collection
from app.utils import (
    verify_hash, 
    get_hash, 
    create_access_token, 
    create_refresh_token, 
    decode_token
)

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

# ==============================================================================
# 1. LOGIN (Hash Token & Set Cookie)
# ==============================================================================
@router.post("/login")
async def login(creds: LoginRequest, response: Response):
    # 1. Validate User
    user = await users_collection.find_one({"email": creds.email})
    if not user or not verify_hash(creds.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])

    # 2. Generate Tokens
    access_token = create_access_token({"sub": user_id, "role": user.get("role", "doctor")})
    raw_refresh_token = create_refresh_token({"sub": user_id})

    # 3. HASH the Refresh Token before saving
    refresh_token_hash = get_hash(raw_refresh_token)

    # 4. Save Hash to DB
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"refresh_token_hash": refresh_token_hash}}
    )

    # 5. Set RAW Refresh Token in HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,       # JavaScript cannot access this
        secure=False,        # Set to True in Production (HTTPS)
        samesite="lax",      # Protects against CSRF
        path="/",            # Available for all paths
        max_age=7 * 24 * 60 * 60 
    )

    # 6. Return User Info & Access Token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"name": user["name"], "email": user["email"]}
    }

# ==============================================================================
# 2. REFRESH (Token Rotation)
# ==============================================================================
@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    # 1. Read Cookie
    old_refresh_token = request.cookies.get("refresh_token")
    
    if not old_refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    # 2. Decode & Verify JWT Structure
    payload = decode_token(old_refresh_token)
    if not payload or payload["type"] != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload["sub"]

    # 3. Get User from DB
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 4. SECURITY CHECK: Verify Incoming Token against Stored HASH
    # This prevents Token Reuse. If the DB hash doesn't match the cookie, it's invalid.
    stored_hash = user.get("refresh_token_hash")
    if not stored_hash or not verify_hash(old_refresh_token, stored_hash):
        # Possible reuse attack detected -> Clear cookie
        response.delete_cookie("refresh_token", path="/")
        raise HTTPException(status_code=401, detail="Invalid or reused token")

    # 5. TOKEN ROTATION: Generate NEW Tokens
    new_access_token = create_access_token({"sub": user_id, "role": user.get("role", "doctor")})
    new_refresh_token = create_refresh_token({"sub": user_id})
    
    # 6. Hash NEW Refresh Token
    new_refresh_hash = get_hash(new_refresh_token)

    # 7. Overwrite Old Hash in DB (Rotation)
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"refresh_token_hash": new_refresh_hash}}
    )

    # 8. Set NEW Cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False, 
        samesite="lax",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}

# ==============================================================================
# 3. LOGOUT (Invalidation)
# ==============================================================================
@router.post("/logout")
async def logout(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        payload = decode_token(refresh_token)
        if payload:
            # Invalidate in DB by removing the hash
            await users_collection.update_one(
                {"_id": ObjectId(payload["sub"])},
                {"$unset": {"refresh_token_hash": ""}}
            )
    
    # Remove Cookie
    response.delete_cookie("refresh_token", path="/")
    
    return {"message": "Logged out successfully"}