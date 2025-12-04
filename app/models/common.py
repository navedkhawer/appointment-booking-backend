from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, Field

# Helper to map MongoDB _id to string
PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    id: PyObjectId | None = Field(default=None, alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {
            # This ensures ObjectId is serialized to str in JSON
            Any: str 
        }