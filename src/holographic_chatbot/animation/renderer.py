"""
3D rendering module for generating holographic animation frames.

This module provides functionality to render 3D animations of text and models
using matplotlib, preparing them for display on holographic LED fans.

Author: Ruslan Magana
License: Apache 2.0
"""

from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

from holographic_chatbot.config import Settings
from holographic_chatbot.utils.logger import get_logger

logger = get_logger(__name__)


class RendererError(Exception):
    """Custom exception for rendering errors."""

    pass


class Renderer3D:
    """
    3D renderer for creating holographic animation frames.

    This class handles the creation of 3D visualizations using matplotlib,
    including text rendering and simple 3D objects for holographic display.

    Attributes:
        settings: Application settings instance
        fig: Matplotlib figure object
        ax: 3D axes object
        frame_count: Number of frames generated
    """

    def __init__(self, settings: Settings, figsize: Tuple[int, int] = (5, 5)) -> None:
        """
        Initialize the 3D renderer.

        Args:
            settings: Application settings
            figsize: Figure size as (width, height) in inches

        Raises:
            RendererError: If renderer initialization fails
        """
        self.settings = settings
        self.frame_count = 0

        try:
            # Initialize matplotlib figure
            self.fig = plt.figure(figsize=figsize)
            self.ax: Axes3D = self.fig.add_subplot(111, projection="3d")

            # Set background color
            self.fig.patch.set_facecolor("black")
            self.ax.set_facecolor("black")

            logger.info(f"3D renderer initialized with figsize: {figsize}")
        except Exception as e:
            logger.error(f"Failed to initialize renderer: {e}")
            raise RendererError(f"Renderer initialization failed: {e}") from e

    def clear(self) -> None:
        """Clear the current axes."""
        self.ax.clear()
        self.ax.set_facecolor("black")

    def set_limits(
        self,
        xlim: Tuple[float, float] = (-1, 1),
        ylim: Tuple[float, float] = (-1, 1),
        zlim: Tuple[float, float] = (-1, 1),
    ) -> None:
        """
        Set axis limits for the 3D plot.

        Args:
            xlim: X-axis limits as (min, max)
            ylim: Y-axis limits as (min, max)
            zlim: Z-axis limits as (min, max)
        """
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_zlim(zlim)

    def set_view(self, elev: float = 20.0, azim: float = 45.0) -> None:
        """
        Set the viewing angle for the 3D plot.

        Args:
            elev: Elevation angle in degrees
            azim: Azimuthal angle in degrees
        """
        self.ax.view_init(elev=elev, azim=azim)

    def hide_axes(self) -> None:
        """Hide axis lines and labels for cleaner rendering."""
        self.ax.set_axis_off()

    def render_text(
        self,
        text: str,
        position: Tuple[float, float, float] = (0, 0, 0),
        color: str = "cyan",
        fontsize: int = 15,
        rotation_angle: Optional[float] = None,
    ) -> None:
        """
        Render 3D text at the specified position.

        Args:
            text: Text content to render
            position: 3D position as (x, y, z)
            color: Text color
            fontsize: Font size in points
            rotation_angle: Optional azimuthal rotation angle

        Example:
            >>> renderer.render_text("Hello World", color="blue", fontsize=20)
        """
        try:
            x, y, z = position

            # Apply rotation if specified
            if rotation_angle is not None:
                self.set_view(elev=20, azim=rotation_angle)

            # Render text
            self.ax.text(
                x,
                y,
                z,
                text,
                color=color,
                fontsize=fontsize,
                ha="center",
                va="center",
                fontweight="bold",
            )

            logger.debug(f"Rendered text: '{text[:30]}...' at position {position}")
        except Exception as e:
            logger.error(f"Failed to render text: {e}")
            raise RendererError(f"Text rendering failed: {e}") from e

    def render_sphere(
        self,
        center: Tuple[float, float, float] = (0, 0, 0),
        radius: float = 0.5,
        color: str = "cyan",
        alpha: float = 0.6,
    ) -> None:
        """
        Render a 3D sphere.

        Args:
            center: Sphere center as (x, y, z)
            radius: Sphere radius
            color: Sphere color
            alpha: Transparency (0.0 to 1.0)
        """
        try:
            u = np.linspace(0, 2 * np.pi, 50)
            v = np.linspace(0, np.pi, 50)
            x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
            y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
            z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]

            self.ax.plot_surface(x, y, z, color=color, alpha=alpha)
            logger.debug(f"Rendered sphere at {center} with radius {radius}")
        except Exception as e:
            logger.error(f"Failed to render sphere: {e}")
            raise RendererError(f"Sphere rendering failed: {e}") from e

    def generate_frame(
        self,
        text: str,
        angle: float = 0.0,
        save_path: Optional[Path] = None,
    ) -> np.ndarray:
        """
        Generate a single animation frame.

        Args:
            text: Text to display in the frame
            angle: Rotation angle for the view
            save_path: Optional path to save the frame as an image

        Returns:
            np.ndarray: Frame as a numpy array (height, width, 3)

        Raises:
            RendererError: If frame generation fails
        """
        try:
            # Clear and set up the frame
            self.clear()
            self.set_limits()
            self.hide_axes()

            # Render text with rotation
            self.render_text(text, rotation_angle=angle)

            # Draw the canvas
            self.fig.canvas.draw()

            # Convert to numpy array
            frame = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
            frame = frame.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))

            self.frame_count += 1
            logger.debug(f"Generated frame #{self.frame_count}")

            # Save if path provided
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                self.save_frame(frame, save_path)

            return frame

        except Exception as e:
            logger.error(f"Failed to generate frame: {e}")
            raise RendererError(f"Frame generation failed: {e}") from e

    def save_frame(self, frame: np.ndarray, path: Path) -> None:
        """
        Save a frame to disk.

        Args:
            frame: Frame array to save
            path: Output file path

        Raises:
            RendererError: If save operation fails
        """
        try:
            from PIL import Image

            img = Image.fromarray(frame)
            img.save(path)
            logger.info(f"Frame saved to: {path}")
        except Exception as e:
            logger.error(f"Failed to save frame: {e}")
            raise RendererError(f"Frame save failed: {e}") from e

    def close(self) -> None:
        """Close the renderer and clean up resources."""
        plt.close(self.fig)
        logger.info("Renderer closed")

    def __enter__(self) -> "Renderer3D":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()
