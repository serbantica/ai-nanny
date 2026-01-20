from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List

from api.dependencies import get_persona_manager, get_device_registry
from api.schemas.persona import PersonaResponse
from core.persona.manager import PersonaManager
from core.device.registry import DeviceRegistry
from core.exceptions import PersonaNotFoundError

router = APIRouter()

@router.get("", response_model=List[PersonaResponse])
async def list_personas(
    manager: PersonaManager = Depends(get_persona_manager)
):
    persona_ids = await manager.list_personas()
    response = []
    
    for pid in persona_ids:
        try:
            p = await manager.load_persona(pid)
            response.append(PersonaResponse(
                id=p.id,
                name=p.config.name,
                description=p.config.description,
                version=p.config.version,
                tags=p.config.tags
            ))
        except Exception:
            continue
            
    return response

@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    manager: PersonaManager = Depends(get_persona_manager)
):
    try:
        p = await manager.load_persona(persona_id)
        return PersonaResponse(
            id=p.id,
            name=p.config.name,
            description=p.config.description,
            version=p.config.version,
            tags=p.config.tags
        )
    except PersonaNotFoundError:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")

@router.post("/{persona_id}/activate", response_model=PersonaResponse)
async def activate_persona(
    persona_id: str,
    device_id: str = Body(..., embed=True),
    manager: PersonaManager = Depends(get_persona_manager),
    device_registry: DeviceRegistry = Depends(get_device_registry)
):
    """
    Switch a device to use this persona.
    """
    try:
        # Check if device exists
        device = await device_registry.get_device(device_id)
        current_persona = device.active_persona_id
        
        # Perform switch
        new_persona = await manager.switch_persona(device_id, current_persona, persona_id)
        
        # Update device state in registry too
        device.active_persona_id = persona_id
        await device_registry._save_device(device)
        
        return PersonaResponse(
            id=new_persona.id,
            name=new_persona.config.name,
            description=new_persona.config.description,
            version=new_persona.config.version,
            tags=new_persona.config.tags
        )
    except PersonaNotFoundError:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
