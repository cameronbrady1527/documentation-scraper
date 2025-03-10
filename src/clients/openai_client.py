# -------------------------------------------------------------------------------- #
# OpenAI Client Implementation
# -------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------- #
# Imports
# -------------------------------------------------------------------------------- #
# Built-in imports
import os
from typing import Optional
from functools import lru_cache

# openai imports
from openai import OpenAI, AsyncOpenAI

# -------------------------------------------------------------------------------- #
# Singleton Client Implementations
# -------------------------------------------------------------------------------- #


class OpenAIClientSingleton:
    """
    Singleton class for OpenAI Client.
    Ensures only one instance of the OpenAI client is created.
    """
    _instance: Optional[OpenAI] = None

    @classmethod
    def get_instance(cls, api_key: Optional[str] = None) -> OpenAI:
        """
        Get or create a singleton instance of the OpenAI client.

        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, loads from environment.

        Returns:
            OpenAI: Instance of the OpenAI client
        """
        if cls._instance is None:
            if api_key is None:
                api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it explicitly.")

            cls._instance = OpenAI(api_key=api_key)

        return cls._instance


class AsyncOpenAIClientSingleton:
    """
    Singleton class for AsyncOpenAI Client.
    Ensures only one instance of the AsyncOpenAI client is created.
    """
    _instance: Optional[AsyncOpenAI] = None

    @classmethod
    def get_instance(cls, api_key: Optional[str] = None) -> AsyncOpenAI:
        """
        Get or create a singleton instance of the AsyncOpenAI client.

        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, loads from environment.

        Returns:
            AsyncOpenAI: Instance of the AsyncOpenAI client
        """
        if cls._instance is None:
            if api_key is None:
                api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it explicitly.")

            cls._instance = AsyncOpenAI(api_key=api_key)

        return cls._instance


# -------------------------------------------------------------------------------- #
# Convenience functions
# -------------------------------------------------------------------------------- #

@lru_cache(maxsize=1)
def get_openai_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Get a singleton instance of the OpenAI client.

    Args:
        api_key (Optional[str]): OpenAI API key. If not provided, loads from environment.

    Returns:
        OpenAI: Instance of the OpenAI client
    """
    return OpenAIClientSingleton.get_instance(api_key=api_key)


@lru_cache(maxsize=1)
def get_async_openai_client(api_key: Optional[str] = None) -> AsyncOpenAI:
    """
    Get a singleton instance of the AsyncOpenAI client.

    Args:
        api_key (Optional[str]): OpenAI API key. If not provided, loads from environment.

    Returns:
        AsyncOpenAI: Instance of the AsyncOpenAI client
    """
    return AsyncOpenAIClientSingleton.get_instance(api_key=api_key)

