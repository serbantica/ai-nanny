import httpx
from typing import Dict, Any, List, Optional

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.health_url = "http://localhost:8000/health"

    def get_health(self):
        try:
            return httpx.get(self.health_url)
        except httpx.RequestError:
            return None

    def start_group_activity(self, activity_type: str, device_ids: List[str], persona_id: str) -> Dict[str, Any]:
        """Start a group activity."""
        payload = {
            "activity_type": activity_type,
            "device_ids": device_ids,
            "persona_id": persona_id,
            "config": {}
        }
        response = httpx.post(f"{self.base_url}/coordination/groups/start", json=payload)
        response.raise_for_status()
        return response.json()

    def initiate_handoff(self, session_id: str, from_device: str, to_device: str) -> bool:
        """Initiate session handoff."""
        payload = {
            "session_id": session_id,
            "from_device_id": from_device,
            "to_device_id": to_device,
            "notify_user": True
        }
        try:
            response = httpx.post(f"{self.base_url}/coordination/handoff", json=payload)
            response.raise_for_status()
            return True
        except Exception:
            return False

    def activate_persona(self, device_id: str, persona_id: str) -> Dict[str, Any]:
        """Activate a persona on a device."""
        # Note: The API endpoint structure is /personas/{id}/activate with body {device_id}
        payload = {"device_id": device_id}
        response = httpx.post(f"{self.base_url}/personas/{persona_id}/activate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_personas(self) -> List[Dict[str, Any]]:
        """Get list of available personas."""
        try:
            response = httpx.get(f"{self.base_url}/personas")
            response.raise_for_status()
            return response.json()
        except:
            return []
