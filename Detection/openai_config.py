#!/usr/bin/env python3
"""Configuration helpers for the ADR detection model clients.

API credentials are read from the process environment at call time so importing
this module never requires secrets to be present. Do not log credential values.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from openai import OpenAI


def calculate_cost(
    cost_per_1m_input: float,
    cost_per_1m_output: float,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Return USD cost from per-million-token prices and token counts."""
    if cost_per_1m_input < 0 or cost_per_1m_output < 0:
        raise ValueError("Token prices must be non-negative")
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts must be non-negative")
    return (input_tokens * cost_per_1m_input + output_tokens * cost_per_1m_output) / 1_000_000


def _required_api_key(name: str) -> str:
    """Read and validate a required API key without exposing its value."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_openai_client() -> OpenAI:
    """Create an OpenAI client using OPENAI_API_KEY."""
    return OpenAI(api_key=_required_api_key("OPENAI_API_KEY"), timeout=60.0, max_retries=2)


def get_openai_config() -> Dict[str, Any]:
    """Return legacy OpenAI config shape for integrations that still require it.

    Prefer :func:`get_openai_client` so callers do not need to handle secret
    material directly. Never log or persist the returned mapping.
    """
    return {"api_key": _required_api_key("OPENAI_API_KEY")}


def create_chat_completion(
    model: str = "gpt-4o",
    messages: Optional[list] = None,
    **kwargs: Any,
) -> Any:
    """Create an OpenAI chat completion with bounded client timeouts/retries."""
    if not model or not model.strip():
        raise ValueError("model is required")
    if not messages:
        raise ValueError("messages is required and must not be empty")

    return get_openai_client().chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )


def create_reasoning_completion(
    model: str = "claude-sonnet-4-6",
    messages: Optional[list] = None,
    max_tokens: int = 4000,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Create an Anthropic Messages API completion.

    The previous implementation sent a Claude model name to the OpenAI API,
    which is not a valid or reliable provider routing strategy. This function
    now uses the Anthropic SDK and returns the established normalized response
    shape consumed by the detector.
    """
    if not model or not model.strip():
        raise ValueError("model is required")
    if not messages:
        raise ValueError("messages is required and must not be empty")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero")

    system_parts: List[str] = []
    anthropic_messages: List[Dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Each message must be a mapping")
        role = message.get("role")
        content = message.get("content")
        if role == "system":
            if content:
                system_parts.append(str(content))
            continue
        if role not in ("user", "assistant"):
            raise ValueError("Anthropic messages must use user, assistant, or system roles")
        if content is None:
            raise ValueError("Message content must not be null")
        anthropic_messages.append({"role": role, "content": content})

    if not anthropic_messages:
        raise ValueError("At least one user or assistant message is required")

    client = Anthropic(
        api_key=_required_api_key("ANTHROPIC_API_KEY"),
        timeout=300.0,
        max_retries=2,
    )
    response = client.messages.create(
        model=model,
        messages=anthropic_messages,
        max_tokens=max_tokens,
        **({"system": "\n\n".join(system_parts)} if system_parts else {}),
        **kwargs,
    )

    text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    usage = getattr(response, "usage", None)
    return {
        "content": [{"text": text, "type": "text"}],
        "model": response.model,
        "usage": {
            "input_tokens": getattr(usage, "input_tokens", 0) if usage else 0,
            "output_tokens": getattr(usage, "output_tokens", 0) if usage else 0,
        },
    }


if __name__ == "__main__":
    # Explicit smoke test; requires an intentionally configured API key.
    print("Testing OpenAI configuration...")
    response = create_chat_completion(
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        max_tokens=10,
    )
    message = response.choices[0].message
    print("Completion succeeded")
    print(f"Response: {(message.content or '')[:50]}...")
