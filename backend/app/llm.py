import json
from functools import lru_cache

import anthropic

from app.config import get_settings

MAX_TOKENS = 16000  # non-streaming default per Claude API guidance; avoids truncating structured JSON mid-string


@lru_cache
def get_anthropic_client() -> anthropic.Anthropic:
    settings = get_settings()
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _create_message(messages: list[dict], system_prompt: str, output_format: dict | None = None):
    settings = get_settings()
    client = get_anthropic_client()
    output_config: dict = {"effort": settings.anthropic_effort}
    if output_format:
        output_config["format"] = output_format
    return client.messages.create(
        model=settings.anthropic_model,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=messages,
        output_config=output_config,
    )


def _text_of(response) -> str:
    return next(block.text for block in response.content if block.type == "text")


def chat_text(system_prompt: str, user_prompt: str) -> str:
    """Plain text completion — used for resume parsing, question generation, evaluation."""
    response = _create_message([{"role": "user", "content": user_prompt}], system_prompt)
    return _text_of(response)


def chat_json(system_prompt: str, messages: list[dict], schema: dict, schema_name: str) -> dict:
    """Structured completion constrained to `schema` (JSON schema, `additionalProperties: false`).

    `schema_name` is accepted for interface parity with callers but unused — Claude's
    output_config.format doesn't take a schema name, only the schema itself.
    """
    del schema_name
    response = _create_message(
        messages,
        system_prompt,
        output_format={"type": "json_schema", "schema": schema},
    )
    return json.loads(_text_of(response))
