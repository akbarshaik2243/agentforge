"""AgentForge: the production stack for AI agents.

MCP servers with real auth, guardrails on the data path, and evals
that gate every change. Built for teams shipping agents to production.
"""

from .auth import AuthError, TokenStore, User, require_scope
from .evals import EvalCase, EvalResult, report, run_evals
from .guardrails import BlockedContent, mask_pii, screen_prompt, screen_untrusted
from .turnfive import (
    buried_constraint,
    evaluate,
    mid_session_policy_edit,
    poisoned_tool_output,
    schema_drift_replay,
    suite,
)

__version__ = "0.2.0"
__all__ = [
    "AuthError",
    "TokenStore",
    "User",
    "require_scope",
    "EvalCase",
    "EvalResult",
    "report",
    "run_evals",
    "BlockedContent",
    "mask_pii",
    "screen_prompt",
    "screen_untrusted",
    "buried_constraint",
    "evaluate",
    "mid_session_policy_edit",
    "poisoned_tool_output",
    "schema_drift_replay",
    "suite",
]
