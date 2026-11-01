---
name: "cypher-handover"
user-invocable: false
description: "Load when a session should end and a fresh one take over: a gate just passed, context is long or has compacted, the run or repo set is switching, a debug tangle is over, or the next phase is a long unattended wait. Owns when to suggest a fresh session, the HANDOVER.md template, the clean-check before handover, the successor prompt and the paste line. No successor is ever scheduled."
---

# Cypher handover: ending a session so the next one starts lean

This skill owns the handover rules W-10 and H-02..H-06 (`rules/rules.yaml`). The lane, gates and the clean-check rule are `cypher-workflow`; this skill is the one place the handover steps live. Per-host extras (a pointer to the file, a cheaper alternative) are in `hosts/<host>.md`. Paths and addresses come from the gateway's `knowledge` tool at run time.

## When to load this

Load it when any signal in section 1 is true, or when the product owner asks for a handover or a status they can paste into a new session.

Do not load it for the end of a finished task (that is the closing checklist in `cypher-workflow`) or when the product owner is away and said so (`cypher-afk` applies and the session keeps going in the same thread).

## 1. The signals for a fresh session (W-10)

A session **suggests** a fresh session without being asked when any of these is true:

| Signal | Why |
|---|---|
| A gate just passed (spec approved, design approved, merged) | natural seam; the next phase needs none of this context |
| Context is past about 120k, or it compacted once already | past 150k it auto-compacts and loses early intent; every turn re-reads the whole window |
| Switching run, component or repo set | old context is pure per-turn cost |
| A long debug tangle ended with the fix found | the dead ends are noise now |
| Next phase is unattended seats or a long wait | the orchestrator should restart lean when the job lands |

**Do not hand over (H-02)** mid-task with uncommitted work, mid-gate conversation, or for a step that finishes in a few turns.

The suggestion is never a stop. If the product owner says to carry on in this session, carry on.

## 2. Before you hand over: make it clean (H-03)

1. Commit and push everything, run branch included. Run documents are written in a worktree on the run branch, never in the shared checkout.
2. Run the clean-check over every repo you touched:

   ```bash
   cypherops/factory/bin/clean-check.sh --run <slug> <every repo you touched>
   ```

3. It must exit 0. The only FAILs it may show are open PRs that HANDOVER.md names. Paste its last line into HANDOVER.md.

## 3. Write HANDOVER.md (H-04)

Write `~/scratch/<slug>/HANDOVER.md` from this template. It is scratch, never a repo.

```markdown
# Handover — <slug> — <date, UK time>
Session: <App/Service>: <name> · gateway session <id> (do not reuse; call session_begin)
Lane: <A|B|C|D> · Plane: <KEY-N> · Gates: spec ✓/✗ · design ✓/✗/n-a · UAT ✓/✗/n-a
Branches/PRs: <run branch>, <open PRs + state>
Done (with evidence): <clause → command/result>
Next (exact first action): <command or tool call>
Heavy steps still owed: <full review / ds:sync+cypher-mirror / UAT build>
Waiting on the product owner: <the one question, or none>
Gotchas found: <traps, wrong docs fixed or still wrong>
Leftovers to tear down: <guests, branches, vault items, test data>
Clean-check: <last line of `clean-check.sh --run <slug> <repos>`, and any open PR it flags>
```

- **Next is one exact action**, a command or a tool call, not a topic.
- **Done carries evidence**, the command and its result, not a claim.
- **Never put a secret value, a personal name or a pronoun in it.** Name the vault item to read, or say the knowledge tool holds it.
- Your host file may add a pointer to it (a project doc, a status note). It does not change the file.

## 4. The last message (H-05)

```
HANDOVER.md ─► last message: the suggestion + the paste line ─► the product owner opens a new session when they choose
```

Make this the **last message**, with nothing after it and no further tool calls:

> **Ready for a fresh session — <App/Service>: <name>.** Open a new session in this project and paste:
> `Continue <slug> — read ~/scratch/<slug>/HANDOVER.md and carry on.`

## 5. No successor is scheduled (H-06)

The session never starts its own successor, on any host. The old relay is retired: the host's auto-mode check refused it, and it added a hidden moving part.

- Do not create, update, fire or schedule anything to start a session.
- **Never delete a task that already fired a handover.** Deleting a task deletes every session it started. Leave it disabled.
- If a host has no way to open a new session in the right place, the paste line is the fallback and the only mechanism.

## 6. The successor prompt

For a session started outside the host's project (no project instructions, docs or memory) the prompt must stand alone:

```text
You are continuing "<App/Service>: <name>" for the product owner in the Cypher Suite.
Predecessor: <its link, if known>.
1. Load the cypher-workflow skill first, then any skill the work needs.
2. Gateway: session_begin {label: "<App/Service>: <name>", client_session: "<your session link>", surface: "<your host>"} — a new id, never the old one.
3. workspace_read ~/scratch/<slug>/HANDOVER.md and do its "Next" step.
Standing rules: repo work only in the Coder workspace via the gateway; Max subscription only (never an API key, the Agent SDK or --bare); short answers, next action first, one option.
```

## Edge cases

- **The clean-check shows a FAIL that is not an open PR you name.** Fix it, or copy the dirty file to `~/scratch/rescue-<date>/`, compare with main and the live system, then commit or drop it with the evidence. Do not hand over around it.
- **The gateway says the session is unknown or expired after a handover.** The successor calls `session_begin` again. A 502 during a gateway update: wait 30 seconds and retry.
- **Several repos, one run.** One HANDOVER.md for the run, listing every repo and branch; the clean-check takes all of them.
- **On your host.** Read `hosts/<your host>.md` in this skill for the extra steps.
