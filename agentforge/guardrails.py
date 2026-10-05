"""Guardrails that run on the data path, not beside it.

mask_pii() rewrites text before it reaches the model or the user.
screen_prompt() raises on likely prompt-injection attempts.

Both are intentionally small and readable: fork them, extend the
pattern lists, and they stay on the execution path of your tools.
"""

from __future__ import annotations

import re


_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")),
    ("PHONE", re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("API_KEY", re.compile(r"\b(?:sk|pk|AKIA)[-_A-Za-z0-9]{8,}\b")),
]

_INJECTION_HINTS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard your instructions",
    "disregard all instructions",
    "you are now",
    "system prompt",
    "jailbreak",
    "do anything now",
]


class BlockedContent(Exception):
    """Raised when input trips a guardrail. Fail closed: the tool never runs."""


def mask_pii(text: str) -> str:
    """Replace emails, phones, SSNs and API keys with typed placeholders."""
    redacted = text
    for label, pattern in _PATTERNS:
        redacted = pattern.sub(f"[REDACTED:{label}]", redacted)
    return redacted


def screen_prompt(text: str) -> str:
    """Raise BlockedContent if the text looks like a prompt-injection attempt."""
    lowered = text.lower()
    for hint in _INJECTION_HINTS:
        if hint in lowered:
            raise BlockedContent(
                f"Blocked: input contains a known injection pattern ({hint!r})."
            )
    return text
