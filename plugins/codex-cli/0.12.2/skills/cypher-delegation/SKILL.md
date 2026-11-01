---
name: "cypher-delegation"
user-invocable: false
description: "Load when work is delegated or a seat is launched in any cypher* repo: choosing a pathway, writing a seat brief, launching an implementer, review or UAT seat through the factory scripts, setting a token cap, picking a model, or deciding the team shape. Owns the seat launch rules, token caps, the four-layer brief, model routing and its one-line disclosure, and what is never dispatched."
---

# Cypher delegation: who does the work, how it is launched, what it costs

This skill owns the delegation rules DG-01..DG-12 (`rules/rules.yaml`). The lane and gates are `cypher-workflow`; which review a change gets and the evidence it needs are `cypher-review`; code rules are `cypher-dev`. Script paths, caps in force and addresses come from the gateway's `knowledge` tool at run time.

## When to load this

Load it when any of these is about to happen:

- work is handed to a sub-agent, a seat or a project's own AI endpoint
- a seat is launched (implementer, reviewer or independent tester)
- a brief is written, a token cap or model is chosen, or a seat's cost is questioned
- the shape of the team (who orchestrates, who builds, who reviews) is decided

Do not load it for doing the work yourself in your own session (`cypher-dev`), or for merging (`cypher-review`).

## 1. Two pathways

- **Coding work goes to a Claude Code sub-agent in the target repo (DG-01).** It runs inside the repo, makes the change, runs the affected tests, opens a PR with the brief in the body, and reports back.
- **Work about a project's own data goes to that project's AI endpoint** (an OpenAI-compatible endpoint the project exposes), when the project has tooling the orchestrator lacks. When in doubt, use a sub-agent: it is easier to observe and to roll back.
- Every dispatch is recorded with model, tokens, cost, latency and outcome.

## 2. Launch seats only through the factory scripts

| Seat | Script | Default cap | Env overrides |
|---|---|---|---|
| Implementer | `seat.sh <worktree> <brief.md> <log>` | 30 | `SEAT_MODEL` `SEAT_EFFORT` `SEAT_AUTOCOMPACT` `SEAT_TOKEN_CAP` |
| Reviewer | `review.sh <worktree> <branch-or-pr> <log>` | 15 | `REVIEW_*` |
| Independent tester | `uat.sh <workdir> <brief.md> <mcp.json> <log>` | 20 | `UAT_*` |

All three live in the ops repo under `factory/bin/`.

- **Only these scripts (DG-02).** Never a bare `claude -p`: that is the default large model with a huge window and no compaction, and it is how a weekly allowance disappears in days. Never an API key, the Agent SDK, `--bare` or a third-party harness. Everything runs on the subscription.
- **Defaults:** the Sonnet model, medium effort, compaction at 120000 tokens. `--model opus` is allowed only when the brief states the reason, and the seat's report names the model it used (ruling C-11).
- **Run them from a worktree of current main (DG-03).** Each script refuses a stale copy. A launch from an old checkout is the failure that once produced a review that ran zero agents and reported nothing.
- **Seat output is scratch (DG-04).** Logs, return codes and event streams go to `~/scratch/<run>/logs/`, never a repo. The script writes a done flag; poll that, not the process.
- **Export the run first:** the run slug and session id, so the watch view and the gateway events line up.
- **One clause set is about 100 turns.** A bigger brief is split before launch.

## 3. Token caps

- **The cap is the cost guard (DG-05).** It is a list-price token estimate used as a tripwire against a runaway seat, not money. Cost never needs the product owner's approval.
- **A tripped cap means re-dispatch smaller (DG-06).** Split the brief and relaunch. Never raise the cap to push the same brief through.
- Review: a degraded result (fewer than four review agents) is a failure and is re-run (see `cypher-review`).

## 4. The four-layer brief

Every sub-agent is launched with the same composed stack, in this order:

1. **Base:** the universal coding defaults (always, for coding work).
2. **Language:** the section for each language the task touches.
3. **Project:** the target repo's `CLAUDE.md`, plus the standing-rules files the task touches.
4. **Task brief (DG-07):** written from the discussion, with a goal in one sentence, context decided so far, cited sources, checkable acceptance criteria, the PR title pattern, and an **out of scope** list.

- **A brief that a seat reads is committed before the seat starts (DG-08).** The seat's report comes back into the run's reports, not the repo root.
- **The composer is named (DG-09):** the project lead when the work lives in one repo; the orchestrator when it crosses repos. The composition is shown on request.
- The brief names the contract that governs the work (`cypher-architecture`) and the files the seat may touch.

## 5. Team shape

```
product owner (the only human; spec, design, UAT)
   └─ orchestrator ("chair"): cross-project view, routes, composes, merges; does not code
        ├─ project lead, one per active project: deep context for that project
        ├─ role seats: architect, specialist coder per language, designer, researcher, reviewer
        └─ sub-agents / seats: implementers; contractors that deliver and report back
```

- **The orchestrator does not implement and does not self-review (DG-10).** Implementation is a seat's job. The reviewer is a separate seat from the implementer, except on the trivial self-verify tier whose evidence is in the PR (ruling C-09), and results flow back implementer to reviewer to project lead to orchestrator. See `cypher-review`.
- Project rooms are persistent, one per active project; an all-hands room is convened for cross-cutting decisions. Any seat can be called in by name; it reads the room's recent transcript, contributes, then leaves.
- Surface a decision and its cost at natural points: the end of a discussion, before a dispatch, after a result.

## 6. Model routing and disclosure

- **Default down (DG-11).** When unsure, take the cheaper model and let escalation handle the rest. Opus is never the default; routing to it needs an explicit reason such as a cross-system change or a genuinely hard problem.

| Tier | Use for |
|---|---|
| Haiku | single-file edits, formatting, lookups, short factual replies, log triage |
| Sonnet (default) | multi-file work in one project, reviews, planning, drafting |
| Opus | cross-system refactors, architecture decisions, hard reasoning over conflicting evidence |

- **Escalate** when the task touches more than one file or concept, is novel, shows real disagreement, or a wrong answer costs more than a re-prompt. **De-escalate** for narrow clarifications and mechanical work.
- **Announce the route in one line** at the top of the reply, for example `[Sonnet · multi-file edit]`. Mode routing is shown the same way.
- **Override is one word** (`/haiku`, `/sonnet`, `/opus`, `/auto` to clear), applied from the next response without argument.
- **Log cost.** Every dispatch records model, estimated tokens and estimated cost, and a turn about to cross a soft budget shows its cost inline. Cost is shown, never asked about (ruling C-12): the per-seat token cap is the guard, and the product owner may downgrade after the fact.
- **Never infer silently (DG-12):** sending, replying, accepting, deleting, paying or signing; spending that matters; or dropping a section from a seat's prompt. State what was composed.

## 7. What is never dispatched

- A destructive production action without explicit approval: deleting data, force-pushing a shared branch, killing or destroying a running service.
- A commit to main. Seats open PRs; the orchestrator merges after a clean review.
- Anything not agreed. If the discussion is still open, nothing is dispatched.

## Launch checklist

1. Worktree of current main under `~/scratch/<run>/<task>`; run slug exported.
2. Brief committed, within about 100 turns, naming the contract, scope and acceptance.
3. Right script, default model, cap set (or lowered); log path in scratch.
4. Wait on the done flag or a pushed event; do not poll.
5. Read the result, then route it to a separate reviewer seat.
