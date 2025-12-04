from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def verify_access_token(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload