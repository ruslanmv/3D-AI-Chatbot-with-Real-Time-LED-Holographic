"""
Holographic Chatbot - Interactive 3D AI Chatbot with Real-Time LED Holographic Display.

This package provides a complete solution for creating an interactive 3D chatbot
powered by OpenAI's ChatGPT and displayed on holographic LED fans (Missyou/GIWOX).

Author: Ruslan Magana
Website: https://ruslanmv.com
License: Apache 2.0
"""

__version__ = "1.0.0"
__author__ = "Ruslan Magana"
__email__ = "contact@ruslanmv.com"
__license__ = "Apache-2.0"

from holographic_chatbot.config import Settings, get_settings

__all__ = ["Settings", "get_settings", "__version__", "__author__"]
