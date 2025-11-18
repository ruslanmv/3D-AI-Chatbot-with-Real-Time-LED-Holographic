"""
Speech synthesis module for text-to-speech conversion.

This module provides functionality to convert chatbot text responses into
speech audio using Google Text-to-Speech (gTTS).

Author: Ruslan Magana
License: Apache 2.0
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from gtts import gTTS

from holographic_chatbot.config import Settings
from holographic_chatbot.utils.logger import get_logger

logger = get_logger(__name__)


class SpeechSynthesisError(Exception):
    """Custom exception for speech synthesis errors."""

    pass


class SpeechSynthesizer:
    """
    Text-to-speech synthesizer using Google TTS.

    This class handles converting text to speech audio files and optionally
    playing them back through the system audio.

    Attributes:
        settings: Application settings instance
        output_dir: Directory for saving audio files
        audio_files_created: Counter for audio files created
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the speech synthesizer.

        Args:
            settings: Application settings

        Example:
            >>> synthesizer = SpeechSynthesizer(settings)
            >>> synthesizer.synthesize("Hello, world!")
        """
        self.settings = settings
        self.output_dir = settings.audio_output_dir
        self.audio_files_created = 0

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Speech synthesizer initialized, output dir: {self.output_dir}")

    def synthesize(
        self,
        text: str,
        language: str = "en",
        slow: bool = False,
        output_filename: Optional[str] = None,
    ) -> Path:
        """
        Convert text to speech and save as an MP3 file.

        Args:
            text: Text content to synthesize
            language: Language code (default: 'en' for English)
            slow: Whether to speak slowly
            output_filename: Custom output filename (auto-generated if None)

        Returns:
            Path: Path to the generated audio file

        Raises:
            SpeechSynthesisError: If synthesis fails

        Example:
            >>> audio_path = synthesizer.synthesize("Hello, how are you?")
            >>> print(f"Audio saved to: {audio_path}")
        """
        if not text.strip():
            raise SpeechSynthesisError("Cannot synthesize empty text")

        try:
            # Generate filename if not provided
            if output_filename is None:
                self.audio_files_created += 1
                output_filename = f"speech_{self.audio_files_created:04d}.mp3"

            output_path = self.output_dir / output_filename

            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=slow)

            # Save to file
            tts.save(str(output_path))

            logger.info(f"Synthesized speech saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            raise SpeechSynthesisError(f"Speech synthesis failed: {e}") from e

    def synthesize_and_play(
        self,
        text: str,
        language: str = "en",
        slow: bool = False,
    ) -> Path:
        """
        Synthesize speech and play it immediately.

        Args:
            text: Text to synthesize and play
            language: Language code
            slow: Whether to speak slowly

        Returns:
            Path: Path to the generated audio file

        Raises:
            SpeechSynthesisError: If synthesis or playback fails

        Example:
            >>> synthesizer.synthesize_and_play("Welcome to the holographic chatbot!")
        """
        # Synthesize the audio
        audio_path = self.synthesize(text, language, slow)

        # Play the audio
        try:
            self.play_audio(audio_path)
        except SpeechSynthesisError as e:
            logger.warning(f"Synthesis succeeded but playback failed: {e}")

        return audio_path

    def play_audio(self, audio_path: Path) -> None:
        """
        Play an audio file through system audio.

        Args:
            audio_path: Path to the audio file to play

        Raises:
            SpeechSynthesisError: If playback fails

        Example:
            >>> synthesizer.play_audio(Path("output/speech_0001.mp3"))
        """
        if not audio_path.exists():
            raise SpeechSynthesisError(f"Audio file not found: {audio_path}")

        try:
            # Try different audio players depending on platform
            players = ["mpg123", "afplay", "ffplay", "play"]

            played = False
            for player in players:
                try:
                    # Check if player is available
                    result = subprocess.run(
                        ["which", player],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        # Player found, use it
                        subprocess.run(
                            [player, str(audio_path)],
                            check=True,
                            capture_output=True,
                        )
                        logger.info(f"Played audio using {player}")
                        played = True
                        break

                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            if not played:
                raise SpeechSynthesisError(
                    "No audio player found. Install mpg123, afplay, ffplay, or sox."
                )

        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            raise SpeechSynthesisError(f"Audio playback failed: {e}") from e

    def synthesize_batch(
        self,
        texts: list[str],
        language: str = "en",
        slow: bool = False,
    ) -> list[Path]:
        """
        Synthesize multiple text strings to audio files.

        Args:
            texts: List of text strings to synthesize
            language: Language code
            slow: Whether to speak slowly

        Returns:
            list[Path]: List of paths to generated audio files

        Example:
            >>> texts = ["Hello", "How are you?", "Goodbye"]
            >>> audio_files = synthesizer.synthesize_batch(texts)
        """
        audio_paths = []

        logger.info(f"Starting batch synthesis of {len(texts)} texts")

        for i, text in enumerate(texts):
            try:
                filename = f"batch_{i + 1:04d}.mp3"
                audio_path = self.synthesize(text, language, slow, filename)
                audio_paths.append(audio_path)
            except SpeechSynthesisError as e:
                logger.warning(f"Skipped text {i + 1}: {e}")

        logger.info(f"Batch synthesis complete: {len(audio_paths)} files created")
        return audio_paths

    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Get the duration of an audio file in seconds.

        Args:
            audio_path: Path to the audio file

        Returns:
            float: Duration in seconds

        Raises:
            SpeechSynthesisError: If duration cannot be determined

        Example:
            >>> duration = synthesizer.get_audio_duration(audio_path)
            >>> print(f"Audio is {duration:.2f} seconds long")
        """
        if not audio_path.exists():
            raise SpeechSynthesisError(f"Audio file not found: {audio_path}")

        try:
            # Use ffprobe to get duration
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(audio_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            duration = float(result.stdout.strip())
            return duration

        except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
            logger.warning(f"Could not determine audio duration: {e}")
            # Fallback: estimate based on text length (rough approximation)
            return 3.0  # Default fallback duration

    def clean_audio_directory(self, keep_latest: int = 0) -> int:
        """
        Clean up old audio files from the output directory.

        Args:
            keep_latest: Number of latest files to keep (0 = delete all)

        Returns:
            int: Number of files deleted

        Example:
            >>> deleted = synthesizer.clean_audio_directory(keep_latest=5)
            >>> print(f"Deleted {deleted} old audio files")
        """
        audio_files = sorted(
            self.output_dir.glob("*.mp3"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        files_to_delete = audio_files[keep_latest:] if keep_latest > 0 else audio_files

        deleted = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted += 1
                logger.debug(f"Deleted audio file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}: {e}")

        logger.info(f"Cleaned up {deleted} audio files")
        return deleted

    def get_stats(self) -> dict:
        """
        Get statistics about audio files created.

        Returns:
            dict: Statistics including files created, output directory, etc.
        """
        return {
            "audio_files_created": self.audio_files_created,
            "output_directory": str(self.output_dir),
        }
