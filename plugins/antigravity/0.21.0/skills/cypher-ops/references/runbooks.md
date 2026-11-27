# Adding a runbook

PURPOSE: the shape every new operational runbook in cypherops follows, and when a
runbook is the right tool. Load it from the `cypher-ops` core when the task is
"write, change or index a runbook".

Rules:

- Name a runbook for the **situation** that sends an operator there, not the
  procedure: `restore-from-backup.md`, not `using-restic.md`.
- Every runbook opens with the repo's three-section file header
  (PURPOSE / CONVENTIONS / AGENT NOTES) plus a header block declaring Trigger,
  Estimated duration, Reversibility, Requires physical access and Last verified.
- Steps are numbered, with exact commands and expected outputs. Where judgement
  is needed the step says so.
- Destructive runbooks (data loss, force-pushes, key rotation with no rollback)
  are flagged in the header block **and** in the agent notes.
- When you hit an error a runbook covers, point the owner at the runbook; do not
  attempt the procedure autonomously. Some need physical access (a hardware key,
  a USB stick, a firewall console) that an agent cannot supply.
- A missing runbook for an operation the owner actually needs is a bug: stub the
  file and open an issue.

## When to write one

Write one when a symptom or scheduled event will recur, the response is
non-trivial and order-sensitive, and a missed step has a real cost (data loss,
downtime, a leaked secret). Do not write one for generic "how to use cypherops"
content (that is `CLAUDE.md` or `docs/agent/`), a one-off, or a decision (ADR).

## Naming and location

`docs/runbooks/<situation>.md`. The name should answer "what happened to send me
here" — a fresh session listing the directory should see the trigger at a glance.

## Template

```markdown
<!--
<name>.md — <one-line purpose>

PURPOSE
-------
What this runbook does and the situation that triggers it.

CONVENTIONS
-----------
- Numbered steps, exact commands, expected outputs.
- Destructive steps flagged inline with a callout.

AGENT NOTES
-----------
- What needs physical access vs. what a remote agent can do.
- Which incident this was written in response to.
-->

# <Title>

- **Trigger:** the symptom or scheduled event that sends an operator here
- **Estimated duration:** wall-clock, including "mostly waiting"
- **Reversibility:** Reversible | Partially reversible | Destructive
- **Requires physical access:** Yes (what) | No
- **Last verified:** YYYY-MM-DD

## Before you start
State to confirm first; the dashboards or commands that show the trigger is real.

## Procedure
1. **<Step>.** Exact command, then `Expected output: ...`.
2. ...

## Verification
Commands that confirm success, with specific expected outputs.

## Rollback
Exact undo commands. A destructive procedure says so explicitly and points at
the recovery runbook.

## Related
ADRs that authorise the design; other runbooks in the same incident chain.
```

Header values: **Reversibility** is Reversible (every step has a rollback),
Partially reversible (some steps destructive) or Destructive (run only if sure).
**Last verified** is the date of the last successful rehearsal; bump it on the
quarterly sweep.

## Index and commit

After landing a runbook add a row (name + trigger line) to
`docs/runbooks/README.md` — the index is what an operator under pressure reads
first. Commit as `docs(runbooks): add <name> runbook`, body giving the trigger,
what prompted it, the reversibility flag and the rehearsal date.
