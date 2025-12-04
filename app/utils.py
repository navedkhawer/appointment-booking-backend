from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_this_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security Context (Argon2)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- PASSWORD & TOKEN HASHING ---
def verify_hash(plain_secret: str, hashed_secret: str) -> bool:
    """Verifies a password OR a refresh token against its hash."""
    return pwd_context.verify(plain_secret, hashed_secret)

def get_hash(secret: str) -> str:
    """Hashes a password OR a refresh token."""
    return pwd_context.hash(secret)

# --- JWT GENERATION ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None