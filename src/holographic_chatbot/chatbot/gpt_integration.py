"""
ChatGPT integration module for conversational AI responses.

This module provides a client for interacting with OpenAI's ChatGPT API,
handling conversation history, and generating intelligent responses.

Author: Ruslan Magana
License: Apache 2.0
"""

from typing import Dict, List, Optional

from openai import OpenAI, OpenAIError

from holographic_chatbot.config import Settings
from holographic_chatbot.utils.logger import get_logger

logger = get_logger(__name__)


class ChatGPTError(Exception):
    """Custom exception for ChatGPT-related errors."""

    pass


class ChatGPTClient:
    """
    Client for interacting with OpenAI's ChatGPT API.

    This class manages conversation history, sends requests to the API,
    and handles responses with proper error handling.

    Attributes:
        settings: Application settings instance
        client: OpenAI client instance
        conversation_history: List of conversation messages
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize ChatGPT client.

        Args:
            settings: Application settings containing API key and model config

        Raises:
            ChatGPTError: If API key is invalid or client initialization fails
        """
        self.settings = settings
        self.conversation_history: List[Dict[str, str]] = []

        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info(f"ChatGPT client initialized with model: {settings.openai_model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ChatGPTError(f"Client initialization failed: {e}") from e

    def add_system_message(self, message: str) -> None:
        """
        Add a system message to the conversation history.

        System messages help set the behavior and context for the assistant.

        Args:
            message: System message content

        Example:
            >>> client.add_system_message("You are a helpful 3D holographic assistant.")
        """
        self.conversation_history.append({"role": "system", "content": message})
        logger.debug(f"Added system message: {message[:50]}...")

    def add_user_message(self, message: str) -> None:
        """
        Add a user message to the conversation history.

        Args:
            message: User message content
        """
        self.conversation_history.append({"role": "user", "content": message})
        logger.debug(f"Added user message: {message[:50]}...")

    def add_assistant_message(self, message: str) -> None:
        """
        Add an assistant message to the conversation history.

        Args:
            message: Assistant message content
        """
        self.conversation_history.append({"role": "assistant", "content": message})
        logger.debug(f"Added assistant message: {message[:50]}...")

    def get_response(
        self,
        user_input: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Get a response from ChatGPT for the given user input.

        Args:
            user_input: User's message/question
            max_tokens: Maximum tokens for the response (overrides settings)
            temperature: Temperature for response generation (overrides settings)

        Returns:
            str: ChatGPT's response text

        Raises:
            ChatGPTError: If API request fails or returns invalid response

        Example:
            >>> response = client.get_response("Hello, how are you?")
            >>> print(response)
            "I'm doing great! How can I help you today?"
        """
        # Add user message to history
        self.add_user_message(user_input)

        # Use provided values or fall back to settings
        max_tokens = max_tokens or self.settings.openai_max_tokens
        temperature = temperature or self.settings.openai_temperature

        try:
            logger.info(f"Sending request to ChatGPT (tokens: {max_tokens}, temp: {temperature})")

            # Create chat completion
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=self.conversation_history,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract response text
            if response.choices and len(response.choices) > 0:
                assistant_message = response.choices[0].message.content
                if assistant_message:
                    self.add_assistant_message(assistant_message)
                    logger.info(f"Received response: {assistant_message[:100]}...")
                    return assistant_message.strip()

            raise ChatGPTError("Empty response from ChatGPT")

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ChatGPTError(f"API request failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during ChatGPT request: {e}")
            raise ChatGPTError(f"Unexpected error: {e}") from e

    def clear_history(self) -> None:
        """
        Clear the conversation history.

        This is useful for starting a fresh conversation or managing memory usage.
        """
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.

        Returns:
            List[Dict[str, str]]: List of conversation messages
        """
        return self.conversation_history.copy()

    def set_system_prompt(self, prompt: str) -> None:
        """
        Set or update the system prompt for the conversation.

        This clears any existing history and sets a new system message.

        Args:
            prompt: System prompt to set

        Example:
            >>> client.set_system_prompt(
            ...     "You are a friendly 3D holographic assistant that responds "
            ...     "with emotions and gestures."
            ... )
        """
        self.clear_history()
        self.add_system_message(prompt)
        logger.info("System prompt set successfully")

    def get_conversation_context(self) -> str:
        """
        Get a formatted string representation of the conversation.

        Returns:
            str: Formatted conversation history

        Example:
            >>> print(client.get_conversation_context())
            System: You are a helpful assistant.
            User: Hello
            Assistant: Hi! How can I help?
        """
        context = []
        for msg in self.conversation_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            context.append(f"{role}: {content}")
        return "\n".join(context)
