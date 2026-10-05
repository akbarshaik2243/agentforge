"""A tiny eval harness: define cases, run them, get a score.

An eval case is an input plus a check function. Checks receive the
agent's output and return True/False. The harness runs every case and
prints a report. Gate your deployments on ``passed == total``: if an
eval fails, the change does not ship.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class EvalCase:
    name: str
    input: str
    check: Callable[[str], bool]
    tags: list[str] = field(default_factory=list)


@dataclass
class EvalResult:
    name: str
    passed: bool
    output: str


def run_evals(
    cases: list[EvalCase], agent_fn: Callable[[str], str]
) -> list[EvalResult]:
    results: list[EvalResult] = []
    for case in cases:
        output = agent_fn(case.input)
        try:
            passed = bool(case.check(output))
        except Exception:
            passed = False
        results.append(EvalResult(case.name, passed, output))
    return results


def report(results: list[EvalResult]) -> bool:
    """Print a per-case report. Returns True only if every case passed."""
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"[{mark}] {r.name}")
        if not r.passed:
            print(f"       output was: {r.output!r}")
    print(f"\n{passed}/{total} evals passed")
    return passed == total
