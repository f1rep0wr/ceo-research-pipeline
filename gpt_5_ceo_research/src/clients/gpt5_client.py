"""
GPT-5 API Client

This module provides the GPT5ResponsesClient class for interacting with the OpenAI GPT-5 API
using async/await patterns. The client handles conversation state management and graceful
error handling for missing API keys.
"""

from typing import Dict, Any, Optional
import logging
from openai import AsyncOpenAI, OpenAIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class GPT5ResponsesClient:
    """
    Async client for GPT-5 API interactions with conversation state management.

    This client provides a simple interface for GPT-5 API calls while managing
    conversation states and handling configuration gracefully.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the GPT-5 client with settings and conversation state management.

        Args:
            settings: Application settings containing API configuration

        Note:
            If the API key is missing or invalid, the client will still initialize
            but API calls may fail. This allows for graceful degradation.
        """
        self.settings = settings
        self.conversation_states: Dict[str, Any] = {}

        # Initialize AsyncOpenAI client - handle missing API key gracefully
        try:
            api_key = getattr(settings, 'openai_api_key', None)
            if api_key:
                self._client = AsyncOpenAI(api_key=api_key)
                logger.info("GPT-5 client initialized successfully")
            else:
                self._client = None
                logger.warning("No OpenAI API key provided - client initialized without API access")
        except Exception as e:
            self._client = None
            logger.error(f"Failed to initialize OpenAI client: {e}")

    @property
    def is_ready(self) -> bool:
        """
        Check if the client is ready to make API calls.

        Returns:
            bool: True if client is properly initialized with API key, False otherwise
        """
        return self._client is not None

    def get_conversation_state(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation state for a given conversation ID.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            Conversation state dictionary or None if not found
        """
        return self.conversation_states.get(conversation_id)

    def set_conversation_state(self, conversation_id: str, state: Dict[str, Any]) -> None:
        """
        Set conversation state for a given conversation ID.

        Args:
            conversation_id: Unique identifier for the conversation
            state: State dictionary to store
        """
        self.conversation_states[conversation_id] = state
        logger.debug(f"Updated conversation state for {conversation_id}")

    def clear_conversation_state(self, conversation_id: str) -> bool:
        """
        Clear conversation state for a given conversation ID.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            bool: True if state was found and cleared, False otherwise
        """
        if conversation_id in self.conversation_states:
            del self.conversation_states[conversation_id]
            logger.debug(f"Cleared conversation state for {conversation_id}")
            return True
        return False

    def clear_all_conversation_states(self) -> int:
        """
        Clear all conversation states.

        Returns:
            int: Number of conversation states that were cleared
        """
        count = len(self.conversation_states)
        self.conversation_states.clear()
        logger.debug(f"Cleared {count} conversation states")
        return count

    async def test_connection(self) -> bool:
        """
        Test API connectivity with a minimal request.

        Sends a simple prompt to verify API key and connectivity.
        Uses minimal reasoning effort to reduce cost.

        Returns:
            bool: True if connection successful, False for any failure
        """
        try:
            if not self.is_ready:
                logger.warning("GPT-5 client not ready for connection test")
                return False

            # Send minimal test request using correct GPT-5 API format
            response = await self._client.responses.create(
                model="gpt-5",
                input="Return 'OK' if you can process this request.",
                reasoning={"effort": "minimal"},
                text={"verbosity": "low"}
            )

            # Check if we got a response
            success = response is not None
            logger.info(f"GPT-5 connection test {'successful' if success else 'failed'}")
            return success

        except Exception as e:
            logger.error(f"GPT-5 connection test failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OpenAIError, ConnectionError, TimeoutError)),
        reraise=True
    )
    async def create_response(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Create a response using GPT-5 Responses API with retry logic and conversation state management.

        Args:
            prompt: The input prompt for the API
            conversation_id: Optional conversation ID for state management
            reasoning_effort: Optional reasoning effort level (e.g., "high", "medium", "low")
            **kwargs: Additional parameters to pass to the API

        Returns:
            The API response object

        Raises:
            ValueError: If client is not ready (no API key)
            OpenAIError: If API call fails after retries
        """
        if not self.is_ready:
            raise ValueError("GPT-5 client is not ready - missing API key")

        # Get structured logger
        log = structlog.get_logger()

        # Build request parameters using correct GPT-5 API format
        request_params = {
            "model": "gpt-5",
            "input": prompt
        }

        # Add reasoning effort if provided
        if reasoning_effort:
            request_params["reasoning"] = {"effort": reasoning_effort}

        # Add text configuration (verbosity)
        verbosity = kwargs.get("verbosity", self.settings.default_verbosity)
        request_params["text"] = {"verbosity": verbosity}

        # Handle conversation state management
        if conversation_id and conversation_id in self.conversation_states:
            # Get previous response ID from conversation state
            conversation_state = self.conversation_states[conversation_id]
            if "response_id" in conversation_state:
                request_params["previous_response_id"] = conversation_state["response_id"]
                log.info(
                    "Adding previous response ID to request",
                    conversation_id=conversation_id,
                    previous_response_id=conversation_state["response_id"]
                )

        # Add any additional kwargs to request params
        for key, value in kwargs.items():
            if key not in request_params and key != "verbosity":
                request_params[key] = value

        # Log API call
        log.info(
            "Making GPT-5 API call",
            conversation_id=conversation_id,
            reasoning_effort=reasoning_effort,
            request_params=request_params
        )

        try:
            # Make API call using the responses endpoint
            response = await self._client.responses.create(**request_params)

            # Store response ID in conversation state if conversation_id provided
            if conversation_id:
                if conversation_id not in self.conversation_states:
                    self.conversation_states[conversation_id] = {}

                self.conversation_states[conversation_id]["response_id"] = response.id

                log.info(
                    "Updated conversation state with response ID",
                    conversation_id=conversation_id,
                    response_id=response.id
                )

            log.info(
                "GPT-5 API call successful",
                conversation_id=conversation_id,
                response_id=response.id
            )

            return response

        except OpenAIError as e:
            log.error(
                "GPT-5 API call failed",
                conversation_id=conversation_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
        except Exception as e:
            log.error(
                "Unexpected error in GPT-5 API call",
                conversation_id=conversation_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    async def close(self) -> None:
        """
        Close the underlying AsyncOpenAI client and release resources.

        This should be called when you're done using the client to properly
        clean up connections and resources.
        """
        if self._client is not None:
            await self._client.close()
            logger.info("GPT-5 client closed successfully")