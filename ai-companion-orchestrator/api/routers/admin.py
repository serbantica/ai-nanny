from fastapi import APIRouter
from typing import List, Dict
from core.local_store import LocalStore

router = APIRouter()

@router.get("", response_model=List[Dict])
async def get_activity_log():
    """Get persistent admin activity log."""
    return LocalStore.get_activities()

@router.post("")
async def log_activity(activity: Dict):
    """Log a new activity."""
    LocalStore.log_activity(activity)
    return {"status": "success"}
