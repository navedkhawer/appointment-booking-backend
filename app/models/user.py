from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: Optional[str] = None
    role: str  # admin / doctor
