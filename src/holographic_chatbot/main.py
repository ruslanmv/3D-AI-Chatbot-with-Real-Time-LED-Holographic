"""
Main entry point for the Holographic Chatbot application.

This module orchestrates all components: ChatGPT integration, 3D rendering,
audio synthesis, and holographic fan streaming.

Author: Ruslan Magana
License: Apache 2.0
"""

import sys
import time
from pathlib import Path
from typing import Optional

from holographic_chatbot.animation.renderer import Renderer3D
from holographic_chatbot.audio.phoneme_analyzer import PhonemeAnalyzer
from holographic_chatbot.audio.speech_synthesis import SpeechSynthesizer
from holographic_chatbot.chatbot.gpt_integration import ChatGPTClient
from holographic_chatbot.config import get_settings
from holographic_chatbot.fan.api_client import FanAPIClient
from holographic_chatbot.fan.frame_converter import FrameConverter
from holographic_chatbot.utils.logger import get_logger, setup_logging


class HolographicChatbot:
    """
    Main application class for the holographic chatbot.

    This class coordinates all components to create an interactive 3D chatbot
    experience with real-time holographic display.

    Attributes:
        settings: Application settings
        chatgpt: ChatGPT client
        renderer: 3D renderer
        synthesizer: Speech synthesizer
        phoneme_analyzer: Phoneme analyzer for lip sync
        fan_client: Fan API client
        frame_converter: Frame converter
        logger: Logger instance
    """

    def __init__(self) -> None:
        """Initialize the holographic chatbot application."""
        # Load settings
        self.settings = get_settings()

        # Setup logging
        setup_logging(level=self.settings.log_level)
        self.logger = get_logger(__name__)

        self.logger.info("Initializing Holographic Chatbot...")

        # Ensure directories exist
        self.settings.ensure_directories()

        # Initialize components
        try:
            self.chatgpt = ChatGPTClient(self.settings)
            self.renderer = Renderer3D(self.settings)
            self.synthesizer = SpeechSynthesizer(self.settings)
            self.phoneme_analyzer = PhonemeAnalyzer(self.settings)
            self.fan_client = FanAPIClient(self.settings)
            self.frame_converter = FrameConverter(self.settings)

            self.logger.info("All components initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

        # Set default system prompt
        self._setup_chatgpt()

    def _setup_chatgpt(self) -> None:
        """Configure ChatGPT with the default system prompt."""
        system_prompt = (
            "You are a friendly and helpful 3D holographic assistant. "
            "Your responses will be displayed on a holographic LED fan "
            "and spoken aloud. Keep responses concise (2-3 sentences) "
            "and engaging. Show personality and warmth in your responses."
        )
        self.chatgpt.set_system_prompt(system_prompt)
        self.logger.info("ChatGPT system prompt configured")

    def process_user_input(
        self,
        user_input: str,
        animate: bool = True,
        synthesize_audio: bool = True,
    ) -> str:
        """
        Process user input and generate a complete response.

        Args:
            user_input: User's question or message
            animate: Whether to generate and stream animations
            synthesize_audio: Whether to synthesize speech

        Returns:
            str: ChatGPT's response text

        Example:
            >>> bot = HolographicChatbot()
            >>> response = bot.process_user_input("Hello, how are you?")
        """
        self.logger.info(f"Processing input: '{user_input}'")

        # Get ChatGPT response
        try:
            response = self.chatgpt.get_response(user_input)
            self.logger.info(f"ChatGPT response: '{response}'")
        except Exception as e:
            self.logger.error(f"Failed to get ChatGPT response: {e}")
            response = "I'm sorry, I'm having trouble thinking right now."

        # Generate audio if enabled
        if synthesize_audio and self.settings.enable_audio:
            try:
                audio_path = self.synthesizer.synthesize(response)
                self.logger.info(f"Audio synthesized: {audio_path}")

                # Optionally play audio
                # self.synthesizer.play_audio(audio_path)
            except Exception as e:
                self.logger.error(f"Audio synthesis failed: {e}")

        # Generate and stream animation if enabled
        if animate and self.settings.enable_fan_streaming:
            try:
                self._animate_response(response)
            except Exception as e:
                self.logger.error(f"Animation failed: {e}")

        return response

    def _animate_response(self, text: str, duration: float = 3.0) -> None:
        """
        Generate and stream animated frames for the response.

        Args:
            text: Response text to display
            duration: Animation duration in seconds
        """
        num_frames = int(self.settings.fan_frame_rate * duration)
        frames = []

        self.logger.info(f"Generating {num_frames} animation frames...")

        # Generate rotating text animation
        for i in range(num_frames):
            angle = (360 / num_frames) * i
            frame = self.renderer.generate_frame(text, angle=angle)

            # Optimize frame for display
            frame = self.frame_converter.optimize_for_display(frame)
            frames.append(frame)

        # Stream frames to the fan
        if frames:
            self.logger.info("Streaming frames to holographic fan...")
            sent = self.fan_client.stream_frames(frames)
            self.logger.info(f"Streamed {sent}/{len(frames)} frames successfully")

    def interactive_mode(self) -> None:
        """
        Run the chatbot in interactive mode with user input from terminal.

        Example:
            >>> bot = HolographicChatbot()
            >>> bot.interactive_mode()
        """
        self.logger.info("Starting interactive mode...")

        print("\n" + "=" * 70)
        print("🌟 Holographic Chatbot - Interactive Mode 🌟")
        print("=" * 70)
        print("\nWelcome! Type your messages below (or 'quit' to exit)")
        print("Commands:")
        print("  - 'quit' or 'exit': Exit the application")
        print("  - 'clear': Clear conversation history")
        print("  - 'stats': Show statistics")
        print("=" * 70 + "\n")

        try:
            while True:
                try:
                    # Get user input
                    user_input = input("\n🎤 You: ").strip()

                    if not user_input:
                        continue

                    # Handle commands
                    if user_input.lower() in ["quit", "exit"]:
                        print("\n👋 Goodbye! Thanks for chatting!")
                        break

                    if user_input.lower() == "clear":
                        self.chatgpt.clear_history()
                        self._setup_chatgpt()
                        print("✅ Conversation history cleared")
                        continue

                    if user_input.lower() == "stats":
                        self._show_stats()
                        continue

                    # Process normal input
                    response = self.process_user_input(user_input)
                    print(f"\n🤖 Bot: {response}")

                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted. Goodbye!")
                    break

                except Exception as e:
                    self.logger.error(f"Error in interactive mode: {e}")
                    print(f"\n❌ Error: {e}")

        finally:
            self.cleanup()

    def _show_stats(self) -> None:
        """Display application statistics."""
        print("\n" + "=" * 70)
        print("📊 Application Statistics")
        print("=" * 70)

        # ChatGPT stats
        print(f"\n💬 ChatGPT:")
        print(f"  - Conversation length: {len(self.chatgpt.get_history())} messages")

        # Renderer stats
        print(f"\n🎬 Renderer:")
        print(f"  - Frames generated: {self.renderer.frame_count}")

        # Audio stats
        audio_stats = self.synthesizer.get_stats()
        print(f"\n🔊 Audio:")
        print(f"  - Files created: {audio_stats['audio_files_created']}")

        # Fan stats
        fan_stats = self.fan_client.get_stats()
        print(f"\n📡 Holographic Fan:")
        print(f"  - Frames sent: {fan_stats['frames_sent']}")
        print(f"  - API URL: {fan_stats['api_url']}")

        print("=" * 70 + "\n")

    def test_system(self) -> bool:
        """
        Test all system components.

        Returns:
            bool: True if all tests pass, False otherwise
        """
        self.logger.info("Running system tests...")

        tests_passed = True

        # Test ChatGPT
        try:
            print("🧪 Testing ChatGPT... ", end="")
            response = self.chatgpt.get_response("Say hello")
            print(f"✅ OK (response: '{response[:30]}...')")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            tests_passed = False

        # Test renderer
        try:
            print("🧪 Testing 3D Renderer... ", end="")
            frame = self.renderer.generate_frame("Test")
            print(f"✅ OK (frame shape: {frame.shape})")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            tests_passed = False

        # Test audio synthesis
        try:
            print("🧪 Testing Audio Synthesis... ", end="")
            audio_path = self.synthesizer.synthesize("Test audio")
            print(f"✅ OK (saved to: {audio_path})")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            tests_passed = False

        # Test fan connection
        if self.settings.enable_fan_streaming:
            try:
                print("🧪 Testing Fan Connection... ", end="")
                if self.fan_client.test_connection():
                    print("✅ OK")
                else:
                    print("⚠️  Connection failed (fan may be offline)")
            except Exception as e:
                print(f"❌ FAILED: {e}")
                tests_passed = False

        return tests_passed

    def cleanup(self) -> None:
        """Clean up resources and close connections."""
        self.logger.info("Cleaning up resources...")

        try:
            self.renderer.close()
            self.fan_client.close()
            self.logger.info("Cleanup complete")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Create and run the chatbot
        bot = HolographicChatbot()

        # Check for command-line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--test":
                # Run system tests
                success = bot.test_system()
                return 0 if success else 1

            elif sys.argv[1] == "--help":
                print("Holographic Chatbot - Usage:")
                print("  holographic-chatbot              Run in interactive mode")
                print("  holographic-chatbot --test       Run system tests")
                print("  holographic-chatbot --help       Show this help")
                return 0

        # Default: run interactive mode
        bot.interactive_mode()
        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 0

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
