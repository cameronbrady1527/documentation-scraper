# -------------------------------------------------------------------------------- #
# Completions Handler for AI Models
# -------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------- #
# Imports
# -------------------------------------------------------------------------------- #
# Built-in imports
from typing import Type, TypeVar, List, Dict, Any, Optional, Union

# Pydantic imports
from pydantic import BaseModel

# OpenAI imports
from openai.types.chat import ChatCompletion

# Module imports
from src.integrations.ai.openai_client import get_openai_client, get_async_openai_client

# TODO: can just replace with print if u want or I have a good copy / paste logger. just message me.
from src.common.logging.logger import logger

# -------------------------------------------------------------------------------- #
# Types and Constants
# -------------------------------------------------------------------------------- #

MessageContent = Union[str, List[Dict[str, Any]]]
Message = Dict[str, MessageContent]


# -------------------------------------------------------------------------------- #
# Completions Handler Functions
# -------------------------------------------------------------------------------- #

async def create_chat_completion(
    messages: List[Message],
    model: str = "gpt-4o",
    temperature: Optional[float] = None,
    response_format: Optional[Dict[str, str]] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs
) -> str:
    """
    Create a chat completion using the OpenAI API.

    Args:
        messages: List of messages in the conversation
        model: Model to use for completion
        temperature: Temperature for generation
        response_format: Optional format specification (e.g. {"type": "json_object"})
        max_tokens: Maximum tokens in the response
        stream: Whether to stream the response
        **kwargs: Additional parameters to pass to the API

    Returns:
        str: The completion response content
    """
    client = get_async_openai_client()

    try:
        completion_kwargs = {
            "model": model,
            "messages": messages,
        }

        # Add optional parameters if provided
        if temperature is not None:
            completion_kwargs["temperature"] = temperature
        if response_format is not None:
            completion_kwargs["response_format"] = response_format
        if max_tokens is not None:
            completion_kwargs["max_tokens"] = max_tokens
        if stream:
            completion_kwargs["stream"] = stream
            
        # Add any additional kwargs
        completion_kwargs.update(kwargs)

        response: ChatCompletion = await client.chat.completions.create(**completion_kwargs)
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error creating chat completion: {e}")
        raise


# -------------------------------------------------------------------------------- #
# Structured Completions Handler Functions
# -------------------------------------------------------------------------------- #

StructuredResponseType = TypeVar("StructuredResponseType", bound=BaseModel)


async def create_structured_completion(
    messages: List[Message],
    response_format: Type[StructuredResponseType],
    model: str = "gpt-4o",
    temperature: float = 0.0,
) -> StructuredResponseType:
    """
    Create a structured chat completion using the OpenAI API.

    Args:
        messages: List of messages in the conversation
        response_format: Structured response format
        model: Model to use for completion
        temperature: Temperature for generation

    Returns:
        StructuredResponseType: The parsed structured response matching the provided Pydantic model
    """

    client = get_async_openai_client()

    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "response_format": response_format,
        }

        response = await client.beta.chat.completions.parse(**kwargs)
        return response.choices[0].message.parsed

    except Exception as e:
        logger.error(f"Error creating chat completion: {e}")
        raise

