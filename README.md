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

## What's here now (v0.1)

- `agentforge/auth.py` — token-based auth with per-user scopes, pluggable store
- `agentforge/guardrails.py` — PII masking (email, phone, SSN, API keys) and injection screening
- `agentforge/evals.py` — tiny eval harness with a deployment gate: all green or it doesn't ship
- `agentforge/server.py` — MCP server template wiring all three together
- `examples/hello_production.py` — the one-command tour
- `tests/` — unit tests for auth and guardrails

## Roadmap

- Eval library: built-in checks (groundedness, tool-choice accuracy, PII leakage)
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
