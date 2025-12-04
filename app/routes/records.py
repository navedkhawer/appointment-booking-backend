from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def records_home():
    return {"records": []}
