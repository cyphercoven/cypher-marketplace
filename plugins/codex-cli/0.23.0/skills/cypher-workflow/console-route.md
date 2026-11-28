# The claude-console route (owner-approved exception)

last_verified: 2026-11-28

PURPOSE: the one standing exception, besides W-32 api-mode, to "factory workers never use an API key". Owner-approved in run cyphermind-orca-trial (S-05).
CONVENTIONS: limits only; how to launch is `cypher-delegation/references/orca.md`. No key value, vault title or host appears here.
AGENT NOTES: read before any `--route claude-console` dispatch. If a limit can't be shown to hold, STOP.

Once both conditions in the first limit below hold, any run may send managed Orca workers to OpenCode on the monthly Console API credit, so that credit is spent on real work instead of expiring. Use it only through `cypherops/factory/bin/agent-dispatch.py --route claude-console`, never a bare `opencode`, a shell export or the Orca server's environment. Limits:

- **Usable only when both hold:** S-33 has passed (cypherops !1260), and the S-06 isolation in `factory/work/cyphermind-orca-trial/reports/route-launch-spike.md` §3b is in place: a separate OS user, a network namespace, and a one-shot key per launch with none at rest. Until then the route is not usable.
- Its own route home and its own Console workspace key. Credit only: £0 cash, auto-reload off. Never the W-32 key, and it never switches api-mode on.
- Until S-25 lands, a run first reads the S-07 allowance, then STOPs on any cash spend, on credit below what the task needs, or on the key seen outside its route.
