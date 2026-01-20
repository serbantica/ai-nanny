"""
Device Client - Handles API calls to the orchestrator for device interactions
"""

import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DeviceClient:
    """Client to communicate with AI Nanny orchestrator API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def generate_response(
        self,
        device_id: str,
        user_message: str,
        persona_id: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the orchestrator using the specified persona.
        
        Args:
            device_id: Device identifier
            user_message: User's input text
            persona_id: Persona to use (companion, activity, emergency, etc.)
            session_id: Optional session ID for context
        
        Returns:
            Dict with response text and metadata
        """
        try:
            # Call orchestrator's conversation endpoint
            response = requests.post(
                f"{self.api_base}/conversation/generate",
                json={
                    "device_id": device_id,
                    "user_message": user_message,
                    "persona_id": persona_id,
                    "session_id": session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.text
                logger.error(f"API error: {response.status_code} - {error_detail}")
                
                # Parse error message for better user feedback
                if "authentication_error" in error_detail or "invalid x-api-key" in error_detail:
                    return {
                        "response": "⚠️ LLM API key not configured. Using simulated response instead.",
                        "error": True,
                        "fallback": True,
                        "reason": "missing_api_key"
                    }
                elif response.status_code == 404:
                    return {
                        "response": f"API endpoint not found. Please check the API configuration.",
                        "error": True,
                        "fallback": True
                    }
                else:
                    return {
                        "response": f"Sorry, I encountered an error. Please try again.",
                        "error": True
                    }
        
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to orchestrator API")
            return {
                "response": "I can't connect to the AI service right now. Please check if the API is running.",
                "error": True,
                "fallback": True
            }
        
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return {
                "response": "The request took too long. Please try again.",
                "error": True
            }
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "response": f"An unexpected error occurred: {str(e)}",
                "error": True
            }
    
    def get_persona_info(self, persona_id: str) -> Dict[str, Any]:
        """Get persona information"""
        try:
            response = requests.get(
                f"{self.api_base}/personas/{persona_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"name": persona_id.title(), "error": True}
        
        except Exception as e:
            logger.error(f"Error fetching persona info: {e}")
            return {"name": persona_id.title(), "error": True}
    
    def check_health(self) -> bool:
        """Check if orchestrator API is available"""
        try:
            # Health endpoint is at /health, not /api/v1/health
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
