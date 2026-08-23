import json
from functools import lru_cache

from openai import OpenAI

from app.config import get_settings


@lru_cache
def get_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)


def _create_response(input_messages: list[dict], text_format: dict | None = None):
    settings = get_settings()
    client = get_openai_client()
    kwargs: dict = {
        "model": settings.openai_chat_model,
        "reasoning": {"effort": settings.openai_reasoning_effort},
        "input": input_messages,
    }
    if text_format:
        kwargs["text"] = {"format": text_format}
    return client.responses.create(**kwargs)


def chat_text(system_prompt: str, user_prompt: str) -> str:
    """Plain text completion — used for resume parsing, question generation, evaluation."""
    response = _create_response(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return response.output_text


def chat_json(system_prompt: str, messages: list[dict], schema: dict, schema_name: str) -> dict:
    """Structured completion constrained to `schema` (JSON schema, `additionalProperties: false`)."""
    response = _create_response(
        [{"role": "system", "content": system_prompt}, *messages],
        text_format={
            "type": "json_schema",
            "name": schema_name,
            "schema": schema,
            "strict": True,
        },
    )
    return json.loads(response.output_text)
