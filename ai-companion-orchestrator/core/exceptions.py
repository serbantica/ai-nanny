"""
Custom exception classes for the AI Companion Orchestrator.
"""

from typing import Optional, Dict, Any


class AICompanionError(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


# =============================================================================
# Persona Errors
# =============================================================================

class PersonaError(AICompanionError):
    """Base exception for persona-related errors."""
    pass


class PersonaNotFoundError(PersonaError):
    """Raised when a persona cannot be found."""
    
    def __init__(self, persona_id: str):
        super().__init__(
            message=f"Persona not found: {persona_id}",
            error_code="PERSONA_NOT_FOUND",
            details={"persona_id": persona_id}
        )


class PersonaLoadError(PersonaError):
    """Raised when a persona fails to load."""
    
    def __init__(self, persona_id: str, reason: str):
        super().__init__(
            message=f"Failed to load persona {persona_id}: {reason}",
            error_code="PERSONA_LOAD_ERROR",
            details={"persona_id": persona_id, "reason": reason}
        )


class PersonaSwitchError(PersonaError):
    """Raised when persona switching fails."""
    
    def __init__(self, from_persona: str, to_persona: str, reason: str):
        super().__init__(
            message=f"Failed to switch from {from_persona} to {to_persona}: {reason}",
            error_code="PERSONA_SWITCH_ERROR",
            details={
                "from_persona": from_persona,
                "to_persona": to_persona,
                "reason": reason
            }
        )


# =============================================================================
# Device Errors
# =============================================================================

class DeviceError(AICompanionError):
    """Base exception for device-related errors."""
    pass


class DeviceNotFoundError(DeviceError):
    """Raised when a device cannot be found."""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"Device not found: {device_id}",
            error_code="DEVICE_NOT_FOUND",
            details={"device_id": device_id}
        )


class DeviceOfflineError(DeviceError):
    """Raised when attempting to communicate with an offline device."""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"Device is offline: {device_id}",
            error_code="DEVICE_OFFLINE",
            details={"device_id": device_id}
        )


class DeviceRegistrationError(DeviceError):
    """Raised when device registration fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Device registration failed: {reason}",
            error_code="DEVICE_REGISTRATION_ERROR",
            details={"reason": reason}
        )


# =============================================================================
# Session Errors
# =============================================================================

class SessionError(AICompanionError):
    """Base exception for session-related errors."""
    pass


class SessionNotFoundError(SessionError):
    """Raised when a session cannot be found."""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id}
        )


class SessionExpiredError(SessionError):
    """Raised when a session has expired."""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session has expired: {session_id}",
            error_code="SESSION_EXPIRED",
            details={"session_id": session_id}
        )


# =============================================================================
# Conversation Errors
# =============================================================================

class ConversationError(AICompanionError):
    """Base exception for conversation-related errors."""
    pass


class LLMAPIError(ConversationError):
    """Raised when LLM API call fails."""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"LLM API error ({provider}): {reason}",
            error_code="LLM_API_ERROR",
            details={"provider": provider, "reason": reason}
        )


class AudioProcessingError(ConversationError):
    """Raised when audio processing fails."""
    
    def __init__(self, stage: str, reason: str):
        super().__init__(
            message=f"Audio processing error at {stage}: {reason}",
            error_code="AUDIO_PROCESSING_ERROR",
            details={"stage": stage, "reason": reason}
        )


# =============================================================================
# Authentication Errors
# =============================================================================

class AuthError(AICompanionError):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            message="Invalid credentials",
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredError(AuthError):
    """Raised when a JWT token has expired."""
    
    def __init__(self):
        super().__init__(
            message="Token has expired",
            error_code="TOKEN_EXPIRED"
        )
