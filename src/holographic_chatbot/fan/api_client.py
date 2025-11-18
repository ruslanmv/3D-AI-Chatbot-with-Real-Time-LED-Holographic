"""
Holographic LED fan API client module.

This module provides an HTTP client for communicating with holographic LED fans
(Missyou/GIWOX) to upload and display animation frames in real-time.

Author: Ruslan Magana
License: Apache 2.0
"""

import io
import time
from pathlib import Path
from typing import Optional, Union

import numpy as np
import requests
from PIL import Image

from holographic_chatbot.config import Settings
from holographic_chatbot.utils.logger import get_logger

logger = get_logger(__name__)


class FanAPIError(Exception):
    """Custom exception for fan API errors."""

    pass


class FanAPIClient:
    """
    Client for communicating with holographic LED fan APIs.

    This class handles frame uploads, connection testing, and error handling
    for holographic fan displays.

    Attributes:
        settings: Application settings instance
        api_url: Full URL for the fan API endpoint
        session: Requests session for persistent connections
        frames_sent: Counter for frames successfully sent
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the fan API client.

        Args:
            settings: Application settings with fan API configuration

        Example:
            >>> client = FanAPIClient(settings)
            >>> client.test_connection()
        """
        self.settings = settings
        self.api_url = settings.get_fan_full_url()
        self.session = requests.Session()
        self.frames_sent = 0

        # Set timeout defaults
        self.timeout = (5.0, 30.0)  # (connect timeout, read timeout)

        logger.info(f"Fan API client initialized: {self.api_url}")

    def test_connection(self, test_image_path: Optional[Path] = None) -> bool:
        """
        Test the connection to the fan API.

        Args:
            test_image_path: Optional path to a test image to upload

        Returns:
            bool: True if connection successful, False otherwise

        Example:
            >>> if client.test_connection():
            ...     print("Fan is connected!")
        """
        try:
            # Create a simple test frame if no image provided
            if test_image_path is None:
                test_frame = self._create_test_frame()
                response = self.send_frame(test_frame)
            else:
                response = self.send_frame_from_file(test_image_path)

            if response:
                logger.info("Fan API connection test successful")
                return True

            logger.warning("Fan API connection test failed")
            return False

        except FanAPIError as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def send_frame(self, frame: np.ndarray, retry_count: int = 3) -> bool:
        """
        Send a single frame to the holographic fan.

        Args:
            frame: Frame as numpy array (height, width, 3)
            retry_count: Number of retry attempts on failure

        Returns:
            bool: True if frame sent successfully, False otherwise

        Raises:
            FanAPIError: If all retry attempts fail

        Example:
            >>> frame = renderer.generate_frame("Hello World")
            >>> client.send_frame(frame)
        """
        for attempt in range(retry_count):
            try:
                # Convert numpy array to PNG bytes
                buffer = io.BytesIO()
                image = Image.fromarray(frame)
                image.save(buffer, format="PNG")
                buffer.seek(0)

                # Send to fan API
                files = {"frame": ("frame.png", buffer, "image/png")}
                response = self.session.post(
                    self.api_url,
                    files=files,
                    timeout=self.timeout,
                )

                # Check response
                if response.status_code == 200:
                    self.frames_sent += 1
                    logger.debug(f"Frame #{self.frames_sent} sent successfully")
                    return True

                logger.warning(
                    f"Frame upload failed (attempt {attempt + 1}/{retry_count}): "
                    f"Status {response.status_code}"
                )

            except requests.RequestException as e:
                logger.error(
                    f"Request error (attempt {attempt + 1}/{retry_count}): {e}"
                )

                if attempt < retry_count - 1:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue

            except Exception as e:
                logger.error(f"Unexpected error sending frame: {e}")
                break

        raise FanAPIError(f"Failed to send frame after {retry_count} attempts")

    def send_frame_from_file(self, file_path: Path) -> bool:
        """
        Send a frame from an image file to the fan.

        Args:
            file_path: Path to the image file

        Returns:
            bool: True if successful, False otherwise

        Raises:
            FanAPIError: If file doesn't exist or upload fails

        Example:
            >>> client.send_frame_from_file(Path("output/frame_001.png"))
        """
        if not file_path.exists():
            raise FanAPIError(f"Image file not found: {file_path}")

        try:
            with open(file_path, "rb") as img_file:
                files = {"frame": (file_path.name, img_file, "image/png")}
                response = self.session.post(
                    self.api_url,
                    files=files,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    self.frames_sent += 1
                    logger.info(f"Frame from file sent successfully: {file_path}")
                    return True

                logger.error(f"Failed to send frame: Status {response.status_code}")
                return False

        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            raise FanAPIError(f"Frame upload failed: {e}") from e

    def stream_frames(
        self,
        frames: list[np.ndarray],
        frame_rate: Optional[int] = None,
    ) -> int:
        """
        Stream multiple frames to the fan at the specified frame rate.

        Args:
            frames: List of frames as numpy arrays
            frame_rate: Target frame rate in fps (uses settings default if None)

        Returns:
            int: Number of frames successfully sent

        Example:
            >>> frames = [renderer.generate_frame(f"Frame {i}") for i in range(30)]
            >>> client.stream_frames(frames, frame_rate=30)
        """
        frame_rate = frame_rate or self.settings.fan_frame_rate
        frame_delay = 1.0 / frame_rate

        successful_frames = 0
        total_frames = len(frames)

        logger.info(f"Starting frame stream: {total_frames} frames at {frame_rate} fps")

        for i, frame in enumerate(frames):
            try:
                start_time = time.time()

                if self.send_frame(frame):
                    successful_frames += 1

                # Maintain frame rate timing
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_delay - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Progress logging
                if (i + 1) % 10 == 0:
                    logger.info(f"Streamed {i + 1}/{total_frames} frames")

            except FanAPIError as e:
                logger.error(f"Error streaming frame {i}: {e}")
                continue

        logger.info(
            f"Stream complete: {successful_frames}/{total_frames} frames sent successfully"
        )
        return successful_frames

    def get_stats(self) -> dict:
        """
        Get statistics about frames sent.

        Returns:
            dict: Statistics including total frames sent, API URL, etc.

        Example:
            >>> stats = client.get_stats()
            >>> print(f"Frames sent: {stats['frames_sent']}")
        """
        return {
            "frames_sent": self.frames_sent,
            "api_url": self.api_url,
            "fan_resolution": (
                self.settings.fan_resolution_width,
                self.settings.fan_resolution_height,
            ),
            "target_frame_rate": self.settings.fan_frame_rate,
        }

    def _create_test_frame(self) -> np.ndarray:
        """
        Create a simple test frame for connection testing.

        Returns:
            np.ndarray: Test frame array
        """
        # Create a simple gradient test pattern
        width = self.settings.fan_resolution_width
        height = self.settings.fan_resolution_height

        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Create gradient
        for i in range(height):
            frame[i, :, 0] = int(255 * i / height)  # Red gradient

        return frame

    def close(self) -> None:
        """Close the API client and clean up resources."""
        self.session.close()
        logger.info("Fan API client closed")

    def __enter__(self) -> "FanAPIClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()
