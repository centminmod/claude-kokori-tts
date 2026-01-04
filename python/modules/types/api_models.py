"""
Pydantic models for API request and response validation.

This module contains all Pydantic model definitions for API interactions with
the Kokoro-FastAPI server, providing runtime validation and IDE auto-completion.
Layer 1 - Foundation: No dependencies on other modules.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict


# Voice Discovery Models
class VoiceInfo(BaseModel):
    """Individual voice information from the models endpoint"""
    id: str = Field(..., description="Voice identifier (e.g., 'af_bella')")
    name: Optional[str] = Field(None, description="Human-readable voice name")
    language: Optional[str] = Field(None, description="Voice language code")
    gender: Optional[str] = Field(None, description="Voice gender (male/female)")
    description: Optional[str] = Field(None, description="Voice description")
    
    model_config = ConfigDict(extra='allow')  # Allow additional fields from API


class KokoroModel(BaseModel):
    """Kokoro model information containing available voices"""
    id: str = Field(..., description="Model identifier (should be 'kokoro')")
    voices: List[VoiceInfo] = Field(default_factory=list, description="Available voices")
    
    model_config = ConfigDict(extra='allow')


class ModelsResponse(BaseModel):
    """Response from /v1/models endpoint"""
    data: List[KokoroModel] = Field(default_factory=list, description="Available models")

    model_config = ConfigDict(extra='allow')


class VoicesListResponse(BaseModel):
    """Response from /v1/audio/voices endpoint"""
    voices: List[str] = Field(default_factory=list, description="List of available voice IDs")

    model_config = ConfigDict(extra='allow')


# Speech Generation Models
class SpeechGenerationRequest(BaseModel):
    """Request payload for /v1/audio/speech endpoint"""
    model: str = Field("kokoro", description="Model to use for generation")
    input: str = Field(..., description="Text to convert to speech")
    voice: str = Field("af_bella", description="Voice ID or blend specification")
    speed: float = Field(1.0, description="Speech speed (0.5-2.0)", ge=0.5, le=2.0)
    response_format: str = Field("wav", description="Output audio format")
    normalize: bool = Field(True, description="Apply text normalization")


# Phoneme Models
class WordTimestamp(BaseModel):
    """Individual word timing information"""
    word: str = Field(..., description="The word text")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    
    model_config = ConfigDict(extra='allow')


class PhonemeResponse(BaseModel):
    """Response from /v1/audio/phonemes endpoint"""
    phonemes: str = Field(..., description="Phoneme representation of text")
    tokens: List[int] = Field(default_factory=list, description="Token IDs")
    word_timestamps: Optional[List[WordTimestamp]] = Field(None, description="Word timing information")
    
    model_config = ConfigDict(extra='allow')


# Health and Monitoring Models
class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str = Field(..., description="Health status (e.g., 'healthy')")
    timestamp: Optional[float] = Field(None, description="Server timestamp")
    version: Optional[str] = Field(None, description="Server version")
    
    model_config = ConfigDict(extra='allow')


# Debug/Monitoring Models
class ThreadDebugInfo(BaseModel):
    """Thread information from debug endpoints"""
    threads: List[Dict[str, Any]] = Field(default_factory=list, description="Thread details")
    thread_count: int = Field(..., description="Total number of threads")
    
    model_config = ConfigDict(extra='allow')


class StorageDebugInfo(BaseModel):
    """Storage information from debug endpoints"""
    device: str = Field(..., description="Storage device path")
    mountpoint: str = Field(..., description="Mount point path")
    fstype: str = Field(..., description="Filesystem type")
    total: int = Field(..., description="Total space in bytes")
    used: int = Field(..., description="Used space in bytes")
    free: int = Field(..., description="Free space in bytes")
    percent: float = Field(..., description="Percentage used")
    
    model_config = ConfigDict(extra='allow')


class SystemDebugInfo(BaseModel):
    """System information from debug endpoints"""
    cpu: Dict[str, Any] = Field(default_factory=dict, description="CPU metrics")
    memory: Dict[str, Any] = Field(default_factory=dict, description="Memory metrics")
    process: Dict[str, Any] = Field(default_factory=dict, description="Process metrics")
    network: Dict[str, Any] = Field(default_factory=dict, description="Network metrics")
    
    model_config = ConfigDict(extra='allow')


class SessionPoolDebugInfo(BaseModel):
    """Session pool information from debug endpoints"""
    total_sessions: int = Field(0, description="Total number of sessions")
    active_sessions: int = Field(0, description="Number of active sessions")
    session_details: List[Dict[str, Any]] = Field(default_factory=list, description="Session details")
    
    model_config = ConfigDict(extra='allow')


# Voice Blend Models
class VoiceBlendRequest(BaseModel):
    """Request for creating voice blend files"""
    voices: List[Dict[str, Union[str, float]]] = Field(..., description="Voice blend components")
    target_voice: str = Field(..., description="Name for the blended voice")
    
    
class VoiceBlendResponse(BaseModel):
    """Response from voice blend creation"""
    success: bool = Field(..., description="Whether blend was created successfully")
    message: Optional[str] = Field(None, description="Status message")
    blend_file: Optional[str] = Field(None, description="Path to created blend file")
    
    model_config = ConfigDict(extra='allow')


# Error Response Models
class ErrorDetail(BaseModel):
    """Error detail information"""
    code: Optional[str] = Field(None, description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    
    model_config = ConfigDict(extra='allow')


class ErrorResponse(BaseModel):
    """Standard error response from API"""
    error: Union[str, ErrorDetail] = Field(..., description="Error information")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    detail: Optional[str] = Field(None, description="Additional error details")
    
    model_config = ConfigDict(extra='allow')


# Utility functions for response parsing
def parse_models_response(data: Dict[str, Any]) -> ModelsResponse:
    """Parse and validate models endpoint response"""
    return ModelsResponse(**data)


def parse_phoneme_response(data: Dict[str, Any]) -> PhonemeResponse:
    """Parse and validate phonemes endpoint response"""
    return PhonemeResponse(**data)


def parse_health_response(data: Dict[str, Any]) -> HealthResponse:
    """Parse and validate health endpoint response"""
    return HealthResponse(**data)


def parse_error_response(data: Dict[str, Any]) -> ErrorResponse:
    """Parse and validate error response"""
    return ErrorResponse(**data)


def parse_voices_list_response(data: Dict[str, Any]) -> VoicesListResponse:
    """Parse and validate voices list endpoint response"""
    return VoicesListResponse(**data)