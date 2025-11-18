"""
Frame conversion and image processing module.

This module provides functionality to convert and optimize animation frames
for holographic LED fan compatibility, including resizing, format conversion,
and enhancement operations.

Author: Ruslan Magana
License: Apache 2.0
"""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from holographic_chatbot.config import Settings
from holographic_chatbot.utils.logger import get_logger

logger = get_logger(__name__)


class FrameConverterError(Exception):
    """Custom exception for frame conversion errors."""

    pass


class FrameConverter:
    """
    Converter for processing and optimizing frames for holographic display.

    This class handles image resizing, format conversion, and various
    enhancement operations to prepare frames for LED fan display.

    Attributes:
        settings: Application settings instance
        target_size: Target resolution as (width, height)
        frames_processed: Counter for processed frames
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the frame converter.

        Args:
            settings: Application settings with fan resolution configuration

        Example:
            >>> converter = FrameConverter(settings)
            >>> frame = converter.resize_frame(input_frame, (256, 256))
        """
        self.settings = settings
        self.target_size = (
            settings.fan_resolution_width,
            settings.fan_resolution_height,
        )
        self.frames_processed = 0

        logger.info(f"Frame converter initialized with target size: {self.target_size}")

    def resize_frame(
        self,
        frame: np.ndarray,
        size: Optional[Tuple[int, int]] = None,
        maintain_aspect: bool = True,
    ) -> np.ndarray:
        """
        Resize a frame to the specified dimensions.

        Args:
            frame: Input frame as numpy array
            size: Target size as (width, height), uses settings default if None
            maintain_aspect: Whether to maintain aspect ratio

        Returns:
            np.ndarray: Resized frame

        Raises:
            FrameConverterError: If resizing fails

        Example:
            >>> resized = converter.resize_frame(frame, (256, 256))
        """
        try:
            size = size or self.target_size
            image = Image.fromarray(frame)

            if maintain_aspect:
                image.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                image = image.resize(size, Image.Resampling.LANCZOS)

            result = np.array(image)
            logger.debug(f"Frame resized to {size}")
            return result

        except Exception as e:
            logger.error(f"Failed to resize frame: {e}")
            raise FrameConverterError(f"Frame resize failed: {e}") from e

    def convert_to_fan_format(
        self,
        input_path: Path,
        output_path: Path,
        size: Optional[Tuple[int, int]] = None,
    ) -> None:
        """
        Convert an image file to fan-compatible format.

        Args:
            input_path: Path to input image
            output_path: Path for output image
            size: Target size (uses settings default if None)

        Raises:
            FrameConverterError: If conversion fails

        Example:
            >>> converter.convert_to_fan_format(
            ...     Path("input.jpg"),
            ...     Path("output.png")
            ... )
        """
        if not input_path.exists():
            raise FrameConverterError(f"Input file not found: {input_path}")

        try:
            size = size or self.target_size

            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize
                img = img.resize(size, Image.Resampling.LANCZOS)

                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Save as PNG
                img.save(output_path, format="PNG")

            self.frames_processed += 1
            logger.info(f"Converted {input_path} to {output_path}")

        except Exception as e:
            logger.error(f"Failed to convert image: {e}")
            raise FrameConverterError(f"Image conversion failed: {e}") from e

    def enhance_brightness(
        self,
        frame: np.ndarray,
        factor: float = 1.2,
    ) -> np.ndarray:
        """
        Enhance the brightness of a frame.

        Args:
            frame: Input frame
            factor: Brightness enhancement factor (1.0 = no change)

        Returns:
            np.ndarray: Enhanced frame

        Example:
            >>> bright_frame = converter.enhance_brightness(frame, factor=1.5)
        """
        try:
            image = Image.fromarray(frame)
            enhancer = ImageEnhance.Brightness(image)
            enhanced = enhancer.enhance(factor)
            return np.array(enhanced)

        except Exception as e:
            logger.error(f"Failed to enhance brightness: {e}")
            raise FrameConverterError(f"Brightness enhancement failed: {e}") from e

    def enhance_contrast(
        self,
        frame: np.ndarray,
        factor: float = 1.2,
    ) -> np.ndarray:
        """
        Enhance the contrast of a frame.

        Args:
            frame: Input frame
            factor: Contrast enhancement factor (1.0 = no change)

        Returns:
            np.ndarray: Enhanced frame

        Example:
            >>> high_contrast = converter.enhance_contrast(frame, factor=1.3)
        """
        try:
            image = Image.fromarray(frame)
            enhancer = ImageEnhance.Contrast(image)
            enhanced = enhancer.enhance(factor)
            return np.array(enhanced)

        except Exception as e:
            logger.error(f"Failed to enhance contrast: {e}")
            raise FrameConverterError(f"Contrast enhancement failed: {e}") from e

    def apply_gaussian_blur(
        self,
        frame: np.ndarray,
        radius: float = 2.0,
    ) -> np.ndarray:
        """
        Apply Gaussian blur to a frame.

        Args:
            frame: Input frame
            radius: Blur radius

        Returns:
            np.ndarray: Blurred frame

        Example:
            >>> blurred = converter.apply_gaussian_blur(frame, radius=3.0)
        """
        try:
            image = Image.fromarray(frame)
            blurred = image.filter(ImageFilter.GaussianBlur(radius))
            return np.array(blurred)

        except Exception as e:
            logger.error(f"Failed to apply blur: {e}")
            raise FrameConverterError(f"Blur application failed: {e}") from e

    def apply_sharpen(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply sharpening filter to a frame.

        Args:
            frame: Input frame

        Returns:
            np.ndarray: Sharpened frame

        Example:
            >>> sharp_frame = converter.apply_sharpen(frame)
        """
        try:
            image = Image.fromarray(frame)
            sharpened = image.filter(ImageFilter.SHARPEN)
            return np.array(sharpened)

        except Exception as e:
            logger.error(f"Failed to apply sharpen: {e}")
            raise FrameConverterError(f"Sharpen application failed: {e}") from e

    def crop_to_square(self, frame: np.ndarray) -> np.ndarray:
        """
        Crop frame to a square aspect ratio (center crop).

        Args:
            frame: Input frame

        Returns:
            np.ndarray: Cropped square frame

        Example:
            >>> square_frame = converter.crop_to_square(frame)
        """
        try:
            height, width = frame.shape[:2]
            min_dim = min(height, width)

            # Calculate crop coordinates
            y_start = (height - min_dim) // 2
            x_start = (width - min_dim) // 2

            cropped = frame[y_start : y_start + min_dim, x_start : x_start + min_dim]

            logger.debug(f"Cropped frame from {width}x{height} to {min_dim}x{min_dim}")
            return cropped

        except Exception as e:
            logger.error(f"Failed to crop frame: {e}")
            raise FrameConverterError(f"Frame crop failed: {e}") from e

    def optimize_for_display(
        self,
        frame: np.ndarray,
        brightness_factor: float = 1.2,
        contrast_factor: float = 1.1,
        sharpen: bool = True,
    ) -> np.ndarray:
        """
        Apply a series of optimizations for holographic display.

        Args:
            frame: Input frame
            brightness_factor: Brightness enhancement factor
            contrast_factor: Contrast enhancement factor
            sharpen: Whether to apply sharpening

        Returns:
            np.ndarray: Optimized frame

        Example:
            >>> optimized = converter.optimize_for_display(frame)
        """
        try:
            # Resize to target size
            optimized = self.resize_frame(frame)

            # Enhance brightness and contrast
            optimized = self.enhance_brightness(optimized, brightness_factor)
            optimized = self.enhance_contrast(optimized, contrast_factor)

            # Apply sharpening if requested
            if sharpen:
                optimized = self.apply_sharpen(optimized)

            logger.debug("Frame optimized for display")
            return optimized

        except Exception as e:
            logger.error(f"Failed to optimize frame: {e}")
            raise FrameConverterError(f"Frame optimization failed: {e}") from e

    def batch_convert_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        pattern: str = "*.png",
    ) -> int:
        """
        Batch convert all images in a directory.

        Args:
            input_dir: Input directory containing images
            output_dir: Output directory for converted images
            pattern: File pattern to match (default: *.png)

        Returns:
            int: Number of images converted

        Example:
            >>> count = converter.batch_convert_directory(
            ...     Path("input_frames"),
            ...     Path("output_frames")
            ... )
        """
        if not input_dir.exists():
            raise FrameConverterError(f"Input directory not found: {input_dir}")

        converted = 0
        for input_path in input_dir.glob(pattern):
            try:
                output_path = output_dir / input_path.name
                self.convert_to_fan_format(input_path, output_path)
                converted += 1
            except FrameConverterError as e:
                logger.warning(f"Skipped {input_path}: {e}")

        logger.info(f"Batch conversion complete: {converted} files")
        return converted

    def get_stats(self) -> dict:
        """
        Get statistics about frames processed.

        Returns:
            dict: Statistics including frames processed, target size, etc.
        """
        return {
            "frames_processed": self.frames_processed,
            "target_size": self.target_size,
        }
