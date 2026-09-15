"""Helpers for validating and resolving AI provider credentials safely."""

from __future__ import annotations

import os
from typing import Mapping, Optional, Sequence

_PLACEHOLDER_MARKERS = (
    "your_",
    "your-",
    "placeholder",
    "changeme",
    "dummy",
    "example",
    "replace_me",
    "not_set",
    "none",
    "null",
    "undefined",
    "<token>",
)


def normalize_api_key(value: Optional[str]) -> Optional[str]:
    """Return a cleaned API key or None when the value is empty or placeholder-like."""
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    lowered = cleaned.lower()
    if lowered.startswith("sk-or-v1-your"):
        return None

    if any(marker in lowered for marker in _PLACEHOLDER_MARKERS):
        return None

    if lowered.startswith("sk-openclaw-placeholder"):
        return None

    return cleaned


def get_first_configured_api_key(
    names: Sequence[str],
    env: Optional[Mapping[str, str]] = None,
) -> Optional[str]:
    """Return the first non-placeholder API key from the provided environment variable names."""
    source = env if env is not None else os.environ
    for name in names:
        value = normalize_api_key(source.get(name))
        if value:
            return value
    return None
