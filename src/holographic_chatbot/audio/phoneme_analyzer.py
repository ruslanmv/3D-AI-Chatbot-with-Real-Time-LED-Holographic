"""
Phoneme analysis module for lip synchronization.

This module provides functionality to extract phonemes from text and map them
to mouth shapes for realistic lip sync animations.

Author: Ruslan Magana
License: Apache 2.0
"""

from typing import Dict, List, Tuple

from phonemizer import phonemize
from phonemizer.backend import EspeakBackend

from holographic_chatbot.config import Settings
from holographic_chatbot.utils.logger import get_logger

logger = get_logger(__name__)


class PhonemeAnalyzerError(Exception):
    """Custom exception for phoneme analysis errors."""

    pass


class PhonemeAnalyzer:
    """
    Analyzer for extracting phonemes and mapping to mouth shapes.

    This class converts text to phonemes and maps them to viseme (visual phoneme)
    categories for lip sync animation.

    Attributes:
        settings: Application settings instance
        backend: Phonemizer backend (espeak)
        viseme_map: Mapping of phonemes to viseme categories
    """

    # Viseme mapping for common English phonemes
    # Based on standard viseme categories (A, E, I, O, U, etc.)
    VISEME_MAP: Dict[str, str] = {
        # Silence
        "": "NEUTRAL",
        # Vowels
        "ɑ": "AA",  # father
        "æ": "AE",  # cat
        "ʌ": "AH",  # but
        "ə": "AH",  # about
        "ɛ": "EH",  # bed
        "eɪ": "EY",  # say
        "i": "IY",  # beet
        "ɪ": "IH",  # bit
        "oʊ": "OW",  # boat
        "ɔ": "AO",  # bought
        "u": "UW",  # boot
        "ʊ": "UH",  # book
        # Consonants
        "b": "B_P",  # lips together
        "p": "B_P",
        "m": "B_P",
        "f": "F_V",  # teeth on lip
        "v": "F_V",
        "θ": "TH",  # tongue between teeth
        "ð": "TH",
        "s": "S_Z",  # teeth close
        "z": "S_Z",
        "ʃ": "SH",  # lips rounded
        "ʒ": "SH",
        "tʃ": "CH",  # lips rounded + forward
        "dʒ": "CH",
        "t": "T_D",  # tongue on teeth ridge
        "d": "T_D",
        "n": "T_D",
        "l": "L",  # tongue up
        "r": "R",  # lips rounded
        "k": "K_G",  # mouth open
        "g": "K_G",
        "ŋ": "K_G",
        "w": "W",  # lips rounded
        "j": "Y",  # tongue up front
        "h": "H",  # mouth open
    }

    def __init__(self, settings: Settings, language: str = "en-us") -> None:
        """
        Initialize the phoneme analyzer.

        Args:
            settings: Application settings
            language: Language code for phonemization (default: 'en-us')

        Raises:
            PhonemeAnalyzerError: If backend initialization fails

        Example:
            >>> analyzer = PhonemeAnalyzer(settings)
            >>> phonemes = analyzer.text_to_phonemes("Hello world")
        """
        self.settings = settings
        self.language = language

        try:
            # Initialize espeak backend
            self.backend = EspeakBackend(language=language)
            logger.info(f"Phoneme analyzer initialized for language: {language}")
        except Exception as e:
            logger.error(f"Failed to initialize phoneme backend: {e}")
            raise PhonemeAnalyzerError(f"Backend initialization failed: {e}") from e

    def text_to_phonemes(
        self,
        text: str,
        strip: bool = True,
    ) -> str:
        """
        Convert text to phonemes.

        Args:
            text: Input text to convert
            strip: Whether to strip punctuation and whitespace

        Returns:
            str: Phoneme string

        Raises:
            PhonemeAnalyzerError: If phonemization fails

        Example:
            >>> phonemes = analyzer.text_to_phonemes("Hello world")
            >>> print(phonemes)
            'həˈloʊ wɝld'
        """
        if not text.strip():
            return ""

        try:
            phonemes = phonemize(
                text,
                language=self.language,
                backend="espeak",
                strip=strip,
            )

            logger.debug(f"Text '{text}' → Phonemes '{phonemes}'")
            return phonemes

        except Exception as e:
            logger.error(f"Failed to phonemize text: {e}")
            raise PhonemeAnalyzerError(f"Phonemization failed: {e}") from e

    def phonemes_to_visemes(self, phonemes: str) -> List[str]:
        """
        Convert phoneme string to list of visemes.

        Args:
            phonemes: Phoneme string (IPA format)

        Returns:
            List[str]: List of viseme categories

        Example:
            >>> visemes = analyzer.phonemes_to_visemes("həˈloʊ")
            >>> print(visemes)
            ['H', 'AH', 'L', 'OW']
        """
        visemes = []

        for char in phonemes:
            if char in " \n\t":
                continue

            viseme = self.VISEME_MAP.get(char, "NEUTRAL")
            visemes.append(viseme)

        logger.debug(f"Converted phonemes to {len(visemes)} visemes")
        return visemes

    def text_to_visemes(self, text: str) -> List[str]:
        """
        Convert text directly to visemes (convenience method).

        Args:
            text: Input text

        Returns:
            List[str]: List of viseme categories

        Example:
            >>> visemes = analyzer.text_to_visemes("Hello")
            >>> print(visemes)
            ['H', 'AH', 'L', 'OW']
        """
        phonemes = self.text_to_phonemes(text)
        return self.phonemes_to_visemes(phonemes)

    def get_mouth_shape_for_viseme(self, viseme: str) -> Dict[str, float]:
        """
        Get mouth shape parameters for a given viseme.

        This returns a dictionary of blend shape weights that can be applied
        to a 3D model for lip sync.

        Args:
            viseme: Viseme category (e.g., 'AA', 'B_P', 'NEUTRAL')

        Returns:
            Dict[str, float]: Blend shape weights (0.0 to 1.0)

        Example:
            >>> shapes = analyzer.get_mouth_shape_for_viseme('AA')
            >>> print(shapes)
            {'mouth_open': 0.8, 'jaw_open': 0.6}
        """
        # Simplified mouth shape mappings
        # In production, these would be calibrated to specific 3D models
        shape_map = {
            "NEUTRAL": {"mouth_open": 0.0, "jaw_open": 0.0},
            "AA": {"mouth_open": 0.8, "jaw_open": 0.6},  # father
            "AE": {"mouth_open": 0.5, "jaw_open": 0.4},  # cat
            "AH": {"mouth_open": 0.3, "jaw_open": 0.2},  # but
            "EH": {"mouth_open": 0.4, "jaw_open": 0.3},  # bed
            "EY": {"mouth_open": 0.3, "jaw_open": 0.2},  # say
            "IY": {"mouth_open": 0.2, "jaw_open": 0.1},  # beet
            "IH": {"mouth_open": 0.3, "jaw_open": 0.2},  # bit
            "OW": {"mouth_open": 0.6, "jaw_open": 0.4},  # boat
            "AO": {"mouth_open": 0.7, "jaw_open": 0.5},  # bought
            "UW": {"mouth_open": 0.4, "jaw_open": 0.2},  # boot
            "UH": {"mouth_open": 0.3, "jaw_open": 0.2},  # book
            "B_P": {"mouth_open": 0.0, "jaw_open": 0.0},  # lips together
            "F_V": {"mouth_open": 0.2, "jaw_open": 0.1},  # teeth on lip
            "TH": {"mouth_open": 0.3, "jaw_open": 0.2},  # tongue visible
            "S_Z": {"mouth_open": 0.2, "jaw_open": 0.1},  # teeth close
            "SH": {"mouth_open": 0.3, "jaw_open": 0.2},  # lips rounded
            "CH": {"mouth_open": 0.3, "jaw_open": 0.2},  # lips forward
            "T_D": {"mouth_open": 0.2, "jaw_open": 0.1},  # tongue up
            "L": {"mouth_open": 0.3, "jaw_open": 0.2},  # tongue up
            "R": {"mouth_open": 0.4, "jaw_open": 0.2},  # lips rounded
            "K_G": {"mouth_open": 0.5, "jaw_open": 0.3},  # mouth open
            "W": {"mouth_open": 0.3, "jaw_open": 0.1},  # lips rounded
            "Y": {"mouth_open": 0.2, "jaw_open": 0.1},  # tongue forward
            "H": {"mouth_open": 0.4, "jaw_open": 0.3},  # mouth open
        }

        return shape_map.get(viseme, {"mouth_open": 0.0, "jaw_open": 0.0})

    def analyze_text_for_animation(
        self,
        text: str,
        duration: float = 1.0,
    ) -> List[Tuple[float, Dict[str, float]]]:
        """
        Analyze text and generate timed mouth shape keyframes.

        Args:
            text: Text to analyze
            duration: Total duration in seconds for the animation

        Returns:
            List[Tuple[float, Dict[str, float]]]: List of (time, mouth_shapes) tuples

        Example:
            >>> keyframes = analyzer.analyze_text_for_animation("Hello", duration=2.0)
            >>> for time, shapes in keyframes:
            ...     print(f"{time:.2f}s: {shapes}")
        """
        visemes = self.text_to_visemes(text)

        if not visemes:
            return [(0.0, {"mouth_open": 0.0, "jaw_open": 0.0})]

        # Calculate time per viseme
        time_per_viseme = duration / len(visemes)

        keyframes = []
        for i, viseme in enumerate(visemes):
            time = i * time_per_viseme
            mouth_shape = self.get_mouth_shape_for_viseme(viseme)
            keyframes.append((time, mouth_shape))

        logger.debug(f"Generated {len(keyframes)} animation keyframes")
        return keyframes

    def get_viseme_categories(self) -> List[str]:
        """
        Get list of all available viseme categories.

        Returns:
            List[str]: List of viseme category names
        """
        return list(set(self.VISEME_MAP.values()))
