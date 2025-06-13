
from openai import APIConnectionError, Timeout, RateLimitError
import asyncio
from aio_pika.exceptions import AMQPConnectionError


class MalformedLLMResponseError(Exception):
    def __init__(self, raw_response: str):
        super().__init__("LLM returned malformed JSON response.")
        self.raw_response = raw_response


RETRYABLE_EXCEPTIONS = (
    Timeout,
    APIConnectionError,
    RateLimitError,
    AMQPConnectionError,
    asyncio.TimeoutError,
)
