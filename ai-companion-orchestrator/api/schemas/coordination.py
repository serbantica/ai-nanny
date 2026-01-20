from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from core.coordination.group_activity import ActivityType, ActivityState

class GroupActivityCreate(BaseModel):
    activity_type: ActivityType
    device_ids: List[str]
    persona_id: str
    config: Optional[Dict[str, Any]] = {}

class GroupActivityResponse(BaseModel):
    id: str
    activity_type: ActivityType
    device_ids: List[str]
    persona_id: str
    state: ActivityState
    current_step: int
    scores: Dict[str, int]
    started_at: Optional[str] = None
    ended_at: Optional[str] = None

class HandoffRequest(BaseModel):
    session_id: str
    from_device_id: str
    to_device_id: str
    notify_user: bool = True

class SyncPlaybackRequest(BaseModel):
    device_ids: List[str]
    audio_url: str
    start_offset: float = 0.0
