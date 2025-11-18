"""
Unit tests for the configuration module.

Author: Ruslan Magana
License: Apache 2.0
"""

import pytest
from pydantic import ValidationError

from holographic_chatbot.config import Settings


class TestSettings:
    """Test cases for the Settings class."""

    def test_settings_creation_with_minimal_required(self) -> None:
        """Test creating settings with minimal required fields."""
        settings = Settings(openai_api_key="sk-test-key-1234567890abcdefghijklmnop")

        assert settings.openai_api_key == "sk-test-key-1234567890abcdefghijklmnop"
        assert settings.openai_model == "gpt-4"
        assert settings.fan_frame_rate == 30

    def test_settings_validation_api_key_too_short(self) -> None:
        """Test that API key validation fails for short keys."""
        with pytest.raises(ValidationError):
            Settings(openai_api_key="short")

    def test_settings_log_level_validation(self) -> None:
        """Test log level validation."""
        # Valid log level
        settings = Settings(
            openai_api_key="sk-test-key-1234567890abcdefghijklmnop", log_level="DEBUG"
        )
        assert settings.log_level == "DEBUG"

        # Invalid log level should raise error
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test-key-1234567890abcdefghijklmnop",
                log_level="INVALID",
            )

    def test_get_fan_full_url(self) -> None:
        """Test fan URL construction."""
        settings = Settings(
            openai_api_key="sk-test-key-1234567890abcdefghijklmnop",
            fan_api_url="http://192.168.1.100",
            fan_upload_endpoint="/upload_frame",
        )

        expected_url = "http://192.168.1.100/upload_frame"
        assert settings.get_fan_full_url() == expected_url

    def test_model_dump_safe_masks_api_key(self) -> None:
        """Test that sensitive data is masked in dump."""
        settings = Settings(
            openai_api_key="sk-test-key-1234567890abcdefghijklmnop1234"
        )

        safe_dump = settings.model_dump_safe()
        assert "sk-test-" in safe_dump["openai_api_key"]
        assert "1234" in safe_dump["openai_api_key"]
        assert "..." in safe_dump["openai_api_key"]
        # Should not contain the full key
        assert safe_dump["openai_api_key"] != "sk-test-key-1234567890abcdefghijklmnop1234"
