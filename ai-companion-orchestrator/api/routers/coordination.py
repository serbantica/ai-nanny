from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List

from api.schemas.coordination import (
    GroupActivityCreate,
    GroupActivityResponse,
    HandoffRequest,
    SyncPlaybackRequest
)
from api.dependencies import get_group_coordinator, get_handoff_manager
from core.coordination.group_activity import GroupActivityCoordinator
from core.coordination.handoff import HandoffManager

router = APIRouter()

@router.post("/groups/start", response_model=GroupActivityResponse)
async def start_group_activity(
    request: GroupActivityCreate,
    coordinator: GroupActivityCoordinator = Depends(get_group_coordinator)
):
    try:
        activity = await coordinator.start_activity(
            activity_type=request.activity_type,
            device_ids=request.device_ids,
            persona_id=request.persona_id,
            config=request.config
        )
        return GroupActivityResponse(
            id=activity.id,
            activity_type=activity.activity_type,
            device_ids=activity.device_ids,
            persona_id=activity.persona_id,
            state=activity.state,
            current_step=activity.current_step,
            scores=activity.scores,
            started_at=activity.started_at.isoformat() if activity.started_at else None,
            ended_at=activity.ended_at.isoformat() if activity.ended_at else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/groups/{activity_id}/end")
async def end_group_activity(
    activity_id: str,
    coordinator: GroupActivityCoordinator = Depends(get_group_coordinator)
):
    await coordinator.end_activity(activity_id)
    return {"status": "success", "message": "Activity ended"}

@router.post("/handoff")
async def initiate_handoff(
    request: HandoffRequest,
    manager: HandoffManager = Depends(get_handoff_manager)
):
    success = await manager.initiate_handoff(
        session_id=request.session_id,
        from_device_id=request.from_device_id,
        to_device_id=request.to_device_id,
        notify_user=request.notify_user
    )
    if not success:
        raise HTTPException(status_code=400, detail="Handoff failed")
    return {"status": "success", "message": "Handoff initiated"}

@router.post("/sync/playback")
async def sync_playback(
    request: SyncPlaybackRequest,
    coordinator: GroupActivityCoordinator = Depends(get_group_coordinator)
):
    await coordinator.sync_playback(
        device_ids=request.device_ids,
        audio_url=request.audio_url,
        start_offset=request.start_offset
    )
    return {"status": "success", "message": "Sync playback command sent"}
