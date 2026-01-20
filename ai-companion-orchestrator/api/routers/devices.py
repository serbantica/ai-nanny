from fastapi import APIRouter, Depends, HTTPException
from typing import List

from api.dependencies import get_device_registry
from api.schemas.device import DeviceRegisterRequest, DeviceRegisterResponse, DeviceResponse
from core.device.registry import DeviceRegistry
from core.device.models import DeviceType, DeviceCapabilities

router = APIRouter()

@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    group_id: str = None, 
    registry: DeviceRegistry = Depends(get_device_registry)
):
    devices = await registry.list_devices(group_id)
    return [
        DeviceResponse(
            id=d.id,
            name=d.name,
            status=d.status,
            active_persona=d.active_persona_id,
            location=d.location,
            last_heartbeat=d.last_heartbeat.isoformat() if d.last_heartbeat else None
        ) for d in devices
    ]

@router.post("", response_model=DeviceRegisterResponse)
async def register_device(
    request: DeviceRegisterRequest,
    registry: DeviceRegistry = Depends(get_device_registry)
):
    # Map capability strings to model (simplified)
    caps = DeviceCapabilities() # Uses defaults for now
    
    device, token = await registry.register_device(
        name=request.name,
        device_type=request.device_type,
        capabilities=caps,
        group_id=request.group_id,
        location=request.location
    )
    
    return DeviceRegisterResponse(
        device_id=device.id,
        auth_token=token,
        websocket_url=f"/ws/{device.id}" # Simplified URL
    )
