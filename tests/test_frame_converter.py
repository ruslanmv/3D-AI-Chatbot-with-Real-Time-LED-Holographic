"""
Unit tests for the frame converter module.

Author: Ruslan Magana
License: Apache 2.0
"""

import numpy as np
import pytest

from holographic_chatbot.config import Settings
from holographic_chatbot.fan.frame_converter import FrameConverter


@pytest.fixture
def settings() -> Settings:
    """Create a settings fixture for tests."""
    return Settings(
        openai_api_key="sk-test-key-1234567890abcdefghijklmnop",
        fan_resolution_width=256,
        fan_resolution_height=256,
    )


@pytest.fixture
def converter(settings: Settings) -> FrameConverter:
    """Create a frame converter fixture."""
    return FrameConverter(settings)


@pytest.fixture
def test_frame() -> np.ndarray:
    """Create a test frame."""
    return np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)


class TestFrameConverter:
    """Test cases for the FrameConverter class."""

    def test_initialization(self, converter: FrameConverter) -> None:
        """Test converter initialization."""
        assert converter.target_size == (256, 256)
        assert converter.frames_processed == 0

    def test_resize_frame(self, converter: FrameConverter, test_frame: np.ndarray) -> None:
        """Test frame resizing."""
        resized = converter.resize_frame(test_frame, size=(256, 256))

        assert resized.shape[2] == 3  # RGB channels
        assert resized.dtype == np.uint8

    def test_enhance_brightness(
        self, converter: FrameConverter, test_frame: np.ndarray
    ) -> None:
        """Test brightness enhancement."""
        small_frame = test_frame[:100, :100, :]  # Use smaller frame for speed
        enhanced = converter.enhance_brightness(small_frame, factor=1.5)

        assert enhanced.shape == small_frame.shape
        assert enhanced.dtype == np.uint8

    def test_crop_to_square(
        self, converter: FrameConverter, test_frame: np.ndarray
    ) -> None:
        """Test square cropping."""
        # Create a non-square frame
        rect_frame = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
        cropped = converter.crop_to_square(rect_frame)

        height, width = cropped.shape[:2]
        assert height == width
        assert height == 400  # Should crop to smallest dimension

    def test_get_stats(self, converter: FrameConverter) -> None:
        """Test statistics retrieval."""
        stats = converter.get_stats()

        assert "frames_processed" in stats
        assert "target_size" in stats
        assert stats["target_size"] == (256, 256)
