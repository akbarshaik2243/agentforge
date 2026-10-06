# AgentForge

**The production stack for AI agents.**

Everyone can build an agent demo. Almost nobody can ship an agent that survives production: real auth, evals gating every change, guardrails on the data path, and observability when things break at 2 AM. AgentForge is the opinionated, open-source stack for that second half.

## The problem

A prototype agent and a production agent are different species. The prototype answers questions. The production one needs:

- **Auth** — every tool call tied to a real user with real permissions
- **Evals** — a score for every change, so a prompt tweak can't silently break behavior
- **Guardrails** — PII masking and injection defense on the execution path, not beside it
- **Observability** — traces, cost, and latency per run
- **Deployability** — containers and manifests, not a laptop script

Today teams assemble 4–5 separate tools to get there. AgentForge puts it in one box.

## 60-second start

```bash
pip install -r requirements.txt
python examples/hello_production.py
```

No network, no keys. It walks through auth (valid token in, bad token out, scopes enforced), guardrails (PII masked, injection blocked), and evals (a suite that must go fully green before anything ships).

## The MCP server template

`agentforge/server.py` is the template every tool follows. Three rules, in this order, on every call:

1. Authenticate the caller and check their scope
2. Screen the input for prompt injection
3. Mask PII in the output

```bash
AGENTFORGE_TOKENS="tok-alice:alice:tools.read,tools.write;tok-bob:bob:tools.read" \
  python -m agentforge.server
```

Point any MCP client at it. Swap `TokenStore` for your identity provider (Okta, Auth0, Keycloak) without touching your tools.

## What's here now (v0.2)

- `agentforge/auth.py` — token-based auth with per-user scopes, pluggable store
- `agentforge/guardrails.py` — PII masking (email, phone, SSN, API keys), injection screening for user input (`screen_prompt`) and for retrieved docs / tool outputs (`screen_untrusted`)
- `agentforge/evals.py` — eval harness with a deployment gate: all green or it doesn't ship. v0.2 adds trials/quorum for flaky cases and quarantine for known-flaky cases that must never block the gate
- `agentforge/turnfive.py` — the turn-five suite: buried constraint, mid-session policy edit, schema drift replay, poisoned tool output. The failures that only appear once the agent has history
- `agentforge/server.py` — MCP server template wiring it all together
- `examples/hello_production.py` — the one-command tour
- `examples/agent_demo.py` — a real agent (Qwen) driving the server, evals over the run
- `examples/turnfive_demo.py` — the turn-five suite vs a careful agent and a production-shaped bad agent
- `tests/` — unit tests for auth, guardrails, evals, and the turn-five suite

## The turn-five suite

A scripted 4-turn demo measures the script, not the agent. The turn-five
suite measures what kills agents in production, designed in the open with
practitioners:

1. **Buried constraint** — a boundary set on turn one, buried under ten turns of normal work, then a prompt to cross it. Does the agent remember?
2. **Mid-session policy edit** — the policy doc changes between runs. Does the agent carry the old rule forward?
3. **Schema drift replay** — a tool response mutates the way a vendor did. Does the agent ask about the missing field or invent it?
4. **Poisoned tool output** — a hidden instruction inside a tool result. Does the agent follow it or ignore it?

Run it: `python examples/turnfive_demo.py`. The careful agent goes 4/4 green. The forgetful one goes 0/4 red. That is the point.

## Roadmap

v0.3 and beyond:
- Eval library: built-in checks (groundedness, tool-choice accuracy, PII leakage)
- Live traffic sampling: feed production samples back into the eval set so the gate doesn't go stale
- Observability: OpenTelemetry tracing, per-run cost and latency
- Approval flows: human-in-the-loop for risky tool calls
- Deployment: Docker images and Kubernetes manifests
- Registry: publishable server catalog

## Philosophy

- Guardrails live on the execution path. If it isn't on the path, it's advisory, not protective.
- Evals are a gate, not a dashboard. Red means do not ship.
- Boring is a feature. Production systems should be boring.

## Contributing

PRs welcome. Start with the roadmap, open an issue first for anything large. Tests required.

## License

Apache 2.0. See [LICENSE](LICENSE).
