"""
Device Registry - Manages device registration and state.
"""
import json
from datetime import datetime
from typing import Optional, List, Dict
from uuid import uuid4

from redis import asyncio as aioredis

from core.device.models import Device, DeviceStatus, DeviceType, DeviceCapabilities
from core.exceptions import DeviceNotFoundError, DeviceRegistrationError
from core.local_store import LocalStore  # Use LocalStore

class DeviceRegistry:
    """
    Manages the lifecycle and state of devices.
    Uses LocalStore for persistence (replacing Redis).
    """
    
    DEVICE_PREFIX = "device:"
    HEARTBEAT_TTL = 300  # 5 minutes before marked offline
    
    def __init__(self, redis_client: aioredis.Redis = None):
        # We ignore the redis client but keep the signature for compatibility
        self.redis = redis_client

    async def register_device(
        self,
        name: str,
        device_type: DeviceType,
        capabilities: Optional[DeviceCapabilities] = None,
        group_id: Optional[str] = None,
        location: Optional[str] = None
    ) -> tuple[Device, str]:
        """
        Register a new device.
        Returns: (Device object, auth_token string)
        """
        device_id = f"dev_{uuid4().hex[:8]}"
        auth_token = f"tok_{uuid4().hex}" # In production, hash this!
        
        device = Device(
            id=device_id,
            name=name,
            type=device_type,
            group_id=group_id,
            location=location,
            capabilities=capabilities or DeviceCapabilities(),
            status=DeviceStatus.OFFLINE,
            registered_at=datetime.utcnow()
            # auth_token_hash would be set here
        )
        
        await self._save_device(device)
        return device, auth_token

    async def get_device(self, device_id: str) -> Device:
        """Get device by ID."""
        devices = LocalStore.list_devices()
        data = next((d for d in devices if d['id'] == device_id), None)
        
        if not data:
            raise DeviceNotFoundError(device_id)
        return Device(**data) # Using Pydantic unpacking

    async def update_status(self, device_id: str, status: DeviceStatus) -> Device:
        """Update device connection status."""
        device = await self.get_device(device_id)
        device.status = status
        device.last_heartbeat = datetime.utcnow()
        await self._save_device(device)
        return device

    async def heartbeat(self, device_id: str, health_metrics: Optional[Dict] = None) -> None:
        """Process a heartbeat from a device."""
        device = await self.get_device(device_id)
        device.status = DeviceStatus.ONLINE
        device.last_heartbeat = datetime.utcnow()
        if health_metrics:
            device.metadata["last_health"] = health_metrics
            
        await self._save_device(device, ttl=self.HEARTBEAT_TTL)

    async def list_devices(self, group_id: Optional[str] = None) -> List[Device]:
        """List registered devices, optionally filtered by group."""
        raw_devices = LocalStore.list_devices()
        devices = []
        for d_data in raw_devices:
            # Simple filtering
            if group_id is None or d_data.get('group_id') == group_id:
                try:
                    devices.append(Device(**d_data))
                except Exception as e:
                    # Skip invalid data
                    print(f"Skipping invalid device data: {e}")
                    pass
        return devices

    async def _save_device(self, device: Device, ttl: Optional[int] = None) -> None:
        """Save device state to LocalStore."""
        # We dump to dict, LocalStore handles JSON serialization
        LocalStore.save_device(device.model_dump())

