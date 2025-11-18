"""
Configuration management for the Holographic Chatbot application.

This module uses pydantic-settings to manage application configuration from
environment variables and .env files.

Author: Ruslan Magana
License: Apache 2.0
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        openai_api_key: OpenAI API key for ChatGPT integration
        openai_model: OpenAI model to use (default: gpt-4)
        openai_max_tokens: Maximum tokens for ChatGPT responses
        openai_temperature: Temperature for response generation (0.0-1.0)
        fan_api_url: Base URL for the holographic fan API
        fan_upload_endpoint: Endpoint path for frame uploads
        fan_frame_rate: Target frame rate for animations (fps)
        fan_resolution_width: Frame width in pixels
        fan_resolution_height: Frame height in pixels
        model_path: Path to the 3D model file (glTF/GLB/VRM)
        audio_output_dir: Directory for generated audio files
        frame_output_dir: Directory for generated animation frames
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_audio: Enable audio synthesis
        enable_lip_sync: Enable lip synchronization
        enable_fan_streaming: Enable streaming to holographic fan
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for ChatGPT",
        min_length=20,
    )
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use",
    )
    openai_max_tokens: int = Field(
        default=150,
        ge=10,
        le=4096,
        description="Maximum tokens for responses",
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for response generation",
    )

    # Fan Configuration
    fan_api_url: str = Field(
        default="http://192.168.1.100",
        description="Base URL for holographic fan API",
    )
    fan_upload_endpoint: str = Field(
        default="/upload_frame",
        description="Endpoint for frame uploads",
    )
    fan_frame_rate: int = Field(
        default=30,
        ge=1,
        le=60,
        description="Target frame rate (fps)",
    )
    fan_resolution_width: int = Field(
        default=256,
        ge=128,
        le=1024,
        description="Frame width in pixels",
    )
    fan_resolution_height: int = Field(
        default=256,
        ge=128,
        le=1024,
        description="Frame height in pixels",
    )

    # Model Configuration
    model_path: Optional[Path] = Field(
        default=None,
        description="Path to 3D model file",
    )

    # Directory Configuration
    audio_output_dir: Path = Field(
        default=Path("output/audio"),
        description="Directory for audio files",
    )
    frame_output_dir: Path = Field(
        default=Path("output/frames"),
        description="Directory for animation frames",
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    # Feature Flags
    enable_audio: bool = Field(
        default=True,
        description="Enable audio synthesis",
    )
    enable_lip_sync: bool = Field(
        default=True,
        description="Enable lip synchronization",
    )
    enable_fan_streaming: bool = Field(
        default=True,
        description="Enable streaming to fan",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v_upper

    @field_validator("model_path")
    @classmethod
    def validate_model_path(cls, v: Optional[Path]) -> Optional[Path]:
        """Validate model path exists if provided."""
        if v is not None and not v.exists():
            raise ValueError(f"Model file not found: {v}")
        return v

    def get_fan_full_url(self) -> str:
        """Get the complete URL for fan API uploads."""
        return f"{self.fan_api_url.rstrip('/')}{self.fan_upload_endpoint}"

    def ensure_directories(self) -> None:
        """Create output directories if they don't exist."""
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        self.frame_output_dir.mkdir(parents=True, exist_ok=True)

    def model_dump_safe(self) -> dict:
        """Dump configuration with sensitive data masked."""
        data = self.model_dump()
        if "openai_api_key" in data and data["openai_api_key"]:
            data["openai_api_key"] = f"{data['openai_api_key'][:8]}...{data['openai_api_key'][-4:]}"
        return data


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application configuration instance

    Example:
        >>> settings = get_settings()
        >>> print(settings.openai_model)
        'gpt-4'
    """
    return Settings()
