---
name: "cypher-spec"
user-invocable: false
description: "Turn the product owner's unstructured braindump into a Cypher factory run: brainstorm, PRD, then INTENT.md + SPEC.md in the Coder workspace, rendered as a board for a one-question gate-1 approval. Use when they dump thoughts about something to build, says \"spec this\", \"turn this into a run\", or \"new factory run\"."
---

# Cypher spec: braindump → spec (the pre-gate-1 chain)

The product owner is the product manager. They braindump; this chain writes the spec. They read exactly two things at the end: a ≤40-line INTENT and a clause board. Never show them the PRD or raw SPEC.md. Load `cypher-workflow` first; this skill is its gate-1 step.

## 0. Capture

1. `session_begin` on the Cypher gateway first (label `<App/Service>: <name>`, or `Cypher: <slug>` for a cross-repo run; surface = your host's name); pass the session on every call. If a later call says `session_not_yours` (the MCP reconnected), call `session_begin` again and carry on with the new id.
2. Pick a kebab-case `<slug>` from the braindump's subject. Confirm it in one line only if ambiguous.
3. Save their words verbatim to `factory/work/<slug>/BRAINDUMP.md` in cypherops in the Coder workspace with `workspace_write` (the gateway route; vm_run.py/paramiko is break-glass only). Do not edit or tidy their words.

## 1. Ground, then brainstorm

1. **Ground first, in parallel with the questions.** Hand a read-only subagent the job of building a compact fact inventory (file:line cited, UNCONFIRMED marked) from STATUS.md, the relevant ADRs, ipam.yaml, inventory/guests.yaml and the tofu/uci sources. Always include STATUS.md's **Deferred** table and any ADR "SETTLED"/placement notes: decided-but-parked work (e.g. cortex/Suricata) is often what they'll pull into scope.
2. Invoke `product-management:brainstorm` on the braindump. Goal: the real problem, the assumptions, the non-goals.
   - Ask at most **five** questions, **one at a time**, each answerable in a sentence (AskUserQuestion), recommended option first. Do not skip questions because the braindump is thin — guesses here fail at UAT, the expensive gate.
   - Aim the questions at the forks the grounding turned up (what's public, login strength, automation tolerance, auto-response limits, scope edges).
   - Stop asking as soon as outcome, must-never and out-of-scope are clear.
3. They often add facts mid-turn (a network or device detail). Acknowledge each in one line and fold it into the next draft. These don't count toward the five.

## 2. PRD — `product-management:write-spec`

Produce the PRD from braindump + answers + grounding: problem, decisions from brainstorm, goals, non-goals, success metrics, phased scope, acceptance criteria. Save as `factory/work/<slug>/PRD.md`. This is an intermediate file; do not present it.

## 3. Reshape into the factory files

Read `factory/work/_template/INTENT.md` and `SPEC.md` first and follow their headers exactly. Also skim one recent approved SPEC (e.g. `persephone-error-triage`) for the clause shape.

**INTENT.md** (≤40 lines, `agents_may_edit: false`) has these sections:

- Outcome (one sentence)
- Why now (≤2 lines)
- Must never
- Done looks like (observable from outside)
- Out of scope

Write it in the product owner's own register, from their braindump where possible. <!-- {{owner-writing-register}}: personal working-style rule, supplied by the template (S-14) -->

**SPEC.md**: one clause `S-NN` per acceptance criterion. Each clause carries:

- `Epic:`
- `Scenario:` (Given/When/Then)
- `Repo:`
- `Verify:` (a runnable command, else `observation:` naming exactly what is looked at)
- `Depends:`

One testable statement per clause; split any "and". Set `approved: null` and `intent_sha` to the sha256 of INTENT.md. Add a one-line grounding note under the title listing what was read.

Rules:
- **No invented infrastructure** (cypherops CLAUDE.md §5.2). Any IP, hostname, service or path you cannot verify against STATUS.md or the running system becomes a clause tagged **needs the product owner**, never a fact.
- UI clauses must have a Scenario; runs with UI clauses will stop at gate 2 (design), which follows the `cypher-design` skill.
- Test/smoke clauses name their teardown (tear-down-test-leftovers rule).
- Verify lines run the affected tests only, never the full suite (ADR-0072 amendment 2026-10-25).
- Run `python3 factory/gates/spec-approved.py` on the result and fix what it refuses before going to the product owner. It must refuse only for the missing `approved:` date.
- Patch revisions with a small python read-modify-write in the workspace (assert the old text exists), never by re-typing the whole SPEC.

## 4. Gate 1 — one question

1. Render the clause board (how to render and republish it: `hosts/<your host>.md` beside this file; a host without artifacts writes it as one markdown page instead). It contains, in this order:
   - The INTENT verbatim at the top.
   - A **Tooling** strip: what each epic will use, in one line each. They will ask, so show it up front.
   - One card per clause, grouped by epic: title, scenario, verify, depends.
   - The repo list.
   - A rough size estimate (tasks × seats) in Max-window terms, not dollars.

   Keep the clause data in one list so revisions are small edits. **needs the product owner** cards are amber and show the question.
2. Ask one AskUserQuestion: **Approve** / **Something's wrong** (free text).
3. The product owner usually answers amber cards by quoting them back ("needs you: …"). Each answer resolves that card: update the clause, drop the tag, and do not re-ask. If they ask for suggestions, give **one** recommendation with a one-line reason and fold it in.
4. On "something's wrong" or a scope change: take their words, re-run from step 2 (PRD), not from the questions. Update INTENT, which recomputes `intent_sha`. Republish the same artifact path (it keeps the URL), mark it "rev N", and ask the one question again.
5. On approve:
   1. Set `approved: <today>` and re-run `spec-approved.py`. It must say dispatchable.
   2. The main cypherops checkout may sit on someone else's branch, so commit from a worktree: `git worktree add -b factory/<slug>-spec ~/scratch/<slug>/wt-spec origin/main` (never `/tmp`). Copy the run dir in, commit as the noreply identity with the session attribution lines, and push.
   3. **Track the run in Plane, not Forgejo milestones** (ADR-0056; factory/README "Specs are authored in Plane"). Use `factory/plane/seed.py --only runs`, with `PLANE_API_KEY` injected via the Plane token from `knowledge {topic: "factory-run"}`. seed.py has no slug filter, so run it from a scratch root holding only `factory/plane/` and `factory/work/<slug>/`. That way it doesn't create items for other runs. Dry-run first, then `--apply`, then re-run the dry run, which must print `changed: 0`. Delete the scratch root afterwards.
   4. Open the PR yourself (`forgejo_pr_open`) and merge it (`forgejo_pr_merge`, `delete_branch: true`). Say what restarts; for a spec-only PR that is nothing. Remove the worktree. Never hand them the PR link to act on.
   5. Tell them in two lines: approved, seeded to Plane as `run/<slug>`, ready to start — and, per `cypher-workflow` §4, offer a fresh session with a handover (a passed gate is the natural seam).
6. **Amendments after approval** (a change-log row marked "applied by the product owner"): commit the SPEC.md change, then run `factory/plane/seed.py --resync <slug>` with the same `secrets:` injection — dry-run, `--apply`, then dry-run again, which must print `changed: 0`. Never patch the Plane items by hand. A `REFUSED` line means someone edited that item in Plane after the commit: reconcile it, or pass `--force-item OPS-N` for that one item (ADR-0056, amendment 2026-10-23).

## Don'ts

- Don't ask them to write or edit clauses.
- Don't present more than five brainstorm questions in total across the chain. Gate questions and amber-card answers don't count.
- Don't show PRD.md or raw SPEC.md unless they ask.
- Don't use `--no-verify`, and don't commit as anything but the commit identity in `knowledge {topic: "factory-run"}`.
- Don't create Forgejo milestones or issues for a run; Plane owns run tracking.
- Don't print secret values; the vault and seed tokens go in only via `secrets:` injection.