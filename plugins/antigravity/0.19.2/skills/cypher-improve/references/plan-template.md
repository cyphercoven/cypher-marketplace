# Cypher implementation plan template

last_verified: 2026-11-16

Write into the existing factory run PLAN.md or assigned task brief. Do not create a parallel backlog. This is an executor handoff: include enough evidence for an agent with no prior chat context.

## Outcome and stage
- Goal and user/system outcome:
- Phases: POC | refinement | production; keep each phase's acceptance and deferred boundary separate
- Approved scope/spec reference:
- POC journey or production impact:
- Priority, effort, risk, confidence:
- Dependencies and execution order:
- Later-phase dispatch condition: refinement and production are not dispatchable until the working POC is shown and explicit owner approval is recorded against its acceptance, scope and demo; keep owner-chat provenance

## Evidence basis
- Repository and base commit:
- Planned-at commit:
- Changed/current head and delta to review:
- Plan path and digest:
- Relevant contracts, decisions and system-goal/principle trace:
- Environment/tool configuration and dependency state:
- Commands run and observed outcomes:
- Evidence reused, with reason still valid:
- Evidence invalidation conditions:

## Journey progress
- Owner-usable journey working now:
- Where/how to try it:
- Blockers:
- Explicitly deferred scope:
- Time/tokens to first usable POC (only if actually measured):

Measure progress by usable journeys, not internal task counts; tests and reviews are supporting evidence.

## Current state
For each relevant path/symbol, state its role and include short verified excerpts with file and line. Cite callers, contracts and a repo exemplar. Record approved tradeoffs and assumptions; mark unresolved facts explicitly.

## Scope
In scope (the only paths the executor may change):
- <explicit item>

Out of scope:
- <explicit item>

## Phase and owner acceptance

| Phase | Acceptance criteria (each clause labels `phase: poc`, `refinement` or `production`) | Dispatch condition |
|---|---|---|
| POC | Small working end-to-end journey; precise scope and deferred boundary | Build to a usable demo and record owner POC approval before any refinement/production dispatch |
| Refinement | Criteria address evidence-backed POC findings and feedback | Not dispatchable until recorded owner POC approval |
| Production | Full release outcome, safety, operations and recovery criteria | Not dispatchable until prior phase acceptance and applicable existing gates |

## Ordered steps
For every step include exact paths/symbols, intended change, dependencies and a verification command with its expected result.

1. <step, affected verification and expected outcome>

## Acceptance and checks
- Self-contained numbered job criteria per phase, with exact relevant S-ID/excerpt (or explicitly no S-ID), affected paths, invariants/interfaces, out-of-scope boundary, dependency/integration contract, exact verification command and expected output. Delta review receives this packet, actual delta, valid prior evidence and changed-input summary; it does not fetch the full epic spec by default. Missing/conflicting clauses are STOP conditions; only final release review checks the full approved spec:
- Machine-checkable outcome:
- Tests for changed behavior and affected callers:
- Contract/integration checks for changed adapters or boundaries:
- Risk-triggered security check or independent specialist review:
- Commands and expected output (from repo evidence, never guessed):
- Unavailable or skipped evidence and why:

## STOP conditions
Stop and report instead of improvising if:
- A later phase lacks an explicit owner POC approval bound to the shown acceptance, scope and demo; tests/reviews do not approve it.
- In-scope current code differs materially from the cited state or drift check.
- A critical assumption is false, impact cannot be bounded, or a security/data-safety issue is found.
- A required command/check fails and the cause is not a small in-scope fix, or fails again after one bounded correction.
- Completion would require an out-of-scope path, contract, permission or production operation.
- Any safety, spec, design or UAT gate applies but is not satisfied.

## Deferred edges
For each nonblocking deferred item: finding, category (security | journey | other), evidence, owner, revisit condition and why it is safe to defer. Security defects, unsafe exposure, current-journey blockers and production-readiness blockers cannot be deferred.

## Maintenance and review
- Future changes or contracts that interact:
- Reviewer focus and integrated behaviors not covered by prior evidence:
- After fixes: exact delta and relevant bug class to re-review; checks invalidated:

## Completion record
Executor records actual changed paths, each step's command/result, deviations, stopped conditions and any evidence not run. Reviewer independently verifies the diff and scope. Do not claim POC availability, feature review, or production readiness without its respective evidence.
