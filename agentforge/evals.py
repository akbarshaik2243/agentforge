"""A tiny eval harness: define cases, run them, get a score.

An eval case is an input plus a check function. Checks receive the
agent's output and return True/False. The harness runs every case and
prints a report. Gate your deployments on the gate: if a case fails,
the change does not ship.

v0.2 additions for evals at scale:
- trials/quorum: run a case N times, pass on M successes. For flaky models.
- quarantine: known-flaky cases are reported but never block the gate.
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
    trials: int = 1
    quorum: int = 1
    quarantine: bool = False


@dataclass
class EvalResult:
    name: str
    passed: bool
    output: str
    passed_trials: int = 1
    trials: int = 1
    quarantined: bool = False


def run_evals(
    cases: list[EvalCase], agent_fn: Callable[[str], str]
) -> list[EvalResult]:
    results: list[EvalResult] = []
    for case in cases:
        passed_trials = 0
        last_output = ""
        for _ in range(max(1, case.trials)):
            try:
                last_output = agent_fn(case.input)
                if case.check(last_output):
                    passed_trials += 1
            except Exception:
                pass
        passed = passed_trials >= max(1, case.quorum)
        results.append(
            EvalResult(
                name=case.name,
                passed=passed,
                output=last_output,
                passed_trials=passed_trials,
                trials=max(1, case.trials),
                quarantined=case.quarantine,
            )
        )
    return results


def report(results: list[EvalResult]) -> bool:
    """Print a per-case report. Returns True only if every NON-QUARANTINED case passed."""
    blocking = [r for r in results if not r.quarantined]
    quarantined = [r for r in results if r.quarantined]
    for r in blocking:
        mark = "PASS" if r.passed else "FAIL"
        trial_note = f" ({r.passed_trials}/{r.trials})" if r.trials > 1 else ""
        print(f"[{mark}] {r.name}{trial_note}")
        if not r.passed:
            print(f"       output was: {r.output!r}")
    for r in quarantined:
        mark = "quarantined pass" if r.passed else "quarantined FAIL (not blocking)"
        print(f"[{mark}] {r.name}")
    passed = sum(1 for r in blocking if r.passed)
    total = len(blocking)
    note = f", {len(quarantined)} quarantined" if quarantined else ""
    print(f"\n{passed}/{total} evals passed{note}")
    return all(r.passed for r in blocking)
