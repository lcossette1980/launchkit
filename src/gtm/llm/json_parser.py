"""Robust JSON extraction from LLM responses."""

from __future__ import annotations

import json
import logging
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def extract_json(text: str) -> dict:
    """Extract a JSON object from an LLM response string.

    Handles:
    - Raw JSON
    - ```json ... ``` code blocks
    - ```  ... ``` code blocks
    - JSON embedded in surrounding prose (regex fallback)

    Returns empty dict on failure.
    """
    if not text or not text.strip():
        return {}

    text = text.strip()

    # 1. Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Try stripping markdown code fences
    cleaned = text
    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Regex fallback — find outermost { ... }
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("Failed to extract JSON from LLM response (length=%d)", len(text))
    return {}


def parse_and_validate(text: str, schema: type[T]) -> T | None:
    """Extract JSON from text and validate against a Pydantic schema.

    Returns None if parsing or validation fails.
    """
    data = extract_json(text)
    if not data:
        return None
    try:
        return schema.model_validate(data)
    except ValidationError as exc:
        logger.warning("Schema validation failed for %s: %s", schema.__name__, exc)
        return None


def safe_parse(text: str, schema: type[T]) -> T:
    """Extract JSON and validate, returning schema defaults on failure."""
    result = parse_and_validate(text, schema)
    if result is not None:
        return result
    # Return a default-constructed instance
    return schema()
