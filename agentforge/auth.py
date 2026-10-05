"""Per-user authentication for AgentForge MCP servers.

The default implementation validates bearer tokens against a simple
token store. Point TokenStore at your own identity provider (Okta,
Auth0, Keycloak, ...) and your tools keep working unchanged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class User:
    id: str
    scopes: list[str] = field(default_factory=list)


class AuthError(Exception):
    """Raised when a request is unauthenticated or unauthorized."""


class TokenStore:
    """Maps bearer tokens to users.

    Configure via the AGENTFORGE_TOKENS environment variable:

        AGENTFORGE_TOKENS="tok-alice:alice:tools.read,tools.write;tok-bob:bob:tools.read"

    Each entry is ``token:user_id:comma,separated,scopes``.
    """

    def __init__(self, raw: str | None = None):
        self._users: dict[str, User] = {}
        raw = raw if raw is not None else os.environ.get("AGENTFORGE_TOKENS", "")
        for entry in raw.split(";"):
            entry = entry.strip()
            if not entry:
                continue
            token, user_id, scopes = entry.split(":")
            self._users[token.strip()] = User(
                id=user_id.strip(),
                scopes=[s.strip() for s in scopes.split(",") if s.strip()],
            )

    def authenticate(self, token: str | None) -> User:
        if not token or token not in self._users:
            raise AuthError("Invalid or missing bearer token.")
        return self._users[token]


def require_scope(user: User, scope: str) -> None:
    """Raise AuthError unless the user holds the given scope."""
    if scope not in user.scopes:
        raise AuthError(f"User '{user.id}' is missing required scope '{scope}'.")
