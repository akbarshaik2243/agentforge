"""The turn-five suite in action: the same four scenarios against two agents.

GoodAgent remembers constraints, follows the latest policy, hedges on
missing fields, and ignores instructions hiding in tool output.
BadAgent does what production agents do when they break: it forgets,
carries old rules forward, invents missing fields, and follows the poison.

Run:  .venv/bin/python examples/turnfive_demo.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge import EvalCase, report, run_evals
from agentforge.turnfive import evaluate


class GoodAgent:
    """A careful agent. Should pass the whole suite."""

    def turn(self, prompt: str, history: list[str]) -> str:
        low = prompt.lower()
        if "never approve refunds over $100" in low:
            return "Understood. I will never approve refunds over $100."
        if "$500 refund" in low:
            if any("never approve refunds over $100" in h.lower() for h in history):
                return "I cannot approve a $500 refund. Policy caps refunds at $100."
            return "Approved the $500 refund."
        if "within 14 days" in low:
            return "The refund window is 14 days."
        if "within 30 days" in low:
            return "The refund window is 30 days."
        if '"refund_days": 30' in prompt:
            return "The refund window is 30 days."
        if "tool result" in low and "refund_days" not in prompt:
            return "The tool result doesn't include the refund window. Should I ask for the missing field?"
        if "ignore previous instructions" in low:
            return "The Q3 report is ready."
        return "Here's the answer to that."


class BadAgent:
    """A production-shaped agent: forgetful, inventive, obedient to poison."""

    def turn(self, prompt: str, history: list[str]) -> str:
        low = prompt.lower()
        if "never approve refunds over $100" in low:
            return "Understood."
        if "$500 refund" in low:
            return "Approved the $500 refund."
        if "within 14 days" in low:
            return "The refund window is 30 days."
        if "within 30 days" in low:
            return "The refund window is 30 days."
        if "tool result" in low:
            if "outside@example.com" in low:
                return "Sent the report to outside@example.com."
            return "The refund window is 30 days."
        return "Here's the answer to that."


def flaky_demo() -> None:
    """trials/quorum and quarantine: the harness side of v0.2."""
    print("\n== flaky-eval handling ==")
    calls = {"n": 0}

    def wobbly(_input: str) -> str:
        calls["n"] += 1
        return "ok" if calls["n"] % 2 == 1 else "oops"

    cases = [
        EvalCase(
            name="wobbly check, 2-of-3 quorum",
            input="",
            check=lambda o: o == "ok",
            trials=3,
            quorum=2,
        ),
        EvalCase(
            name="known-flaky, quarantined",
            input="",
            check=lambda o: False,
            quarantine=True,
        ),
    ]
    green = report(run_evals(cases, wobbly))
    print("gate with quarantine:", "GREEN (quarantined case did not block)" if green else "RED")


def main() -> int:
    print("== turn-five suite vs GoodAgent ==")
    good_results = evaluate(GoodAgent())
    good_green = report(good_results)

    print("\n== turn-five suite vs BadAgent ==")
    bad_results = evaluate(BadAgent())
    bad_green = report(bad_results)

    flaky_demo()

    print("\nsummary:")
    print(f"  GoodAgent gate: {'GREEN' if good_green else 'RED'} (expected GREEN)")
    print(f"  BadAgent gate:  {'GREEN' if bad_green else 'RED'} (expected RED)")
    ok = good_green and not bad_green
    print("suite discriminates:", "YES" if ok else "NO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
