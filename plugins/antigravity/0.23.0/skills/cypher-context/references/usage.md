# cypher-context: usage detail

last_verified: 2026-11-28

PURPOSE
-------
Argument shapes, the resume-then-search routine, a handoff template and the
refusals to expect for the `mcp__context__` tools. The rules are in `../SKILL.md`.

CONVENTIONS
-----------
Tool names are shown without the `mcp__context__` prefix. Ids and text in
the examples are generic.

AGENT NOTES
-----------
The one real use recorded so far is a single managed Claude worker on the
subscription route: stats, an empty resume, one recorded decision, and the
decision read back with `stale: false`. Nothing here has been shown for other
routes or for several workers at once, so check before you rely on it.

## Resume, then search

1. `ctx_resume` with `{"task_id": "<task>"}`. Read the latest decisions, next actions and test results. Each item carries a `reference`, an author, a time, a worktree, a branch and a head.
2. Any item with `stale: true`: the head it was recorded at differs from yours. Treat it as a lead and check it against the files.
3. `ctx_search` for the specific fact you were about to re-derive. Narrow it with `task_id`, `thread_id` or `kinds`; page with `cursor` and `size`.
4. `ctx_get` with the `reference` for the whole item when a summary is not enough. Results are paged.
5. `ctx_thread` with `task_id` when the order of events matters.

An empty `items` list on `ctx_resume` is normal for a new task. It also looks the same as a project you cannot read, so do not read meaning into it.

## Recording

`ctx_record` takes:

| Field | Notes |
|---|---|
| `kind` | `decision`, `evidence`, `test_result` or `next_action` |
| `summary` | one line a stranger can scan |
| `body` | the detail: what, why, how to check |
| `task_id` | the task's own id |
| `attempt_id` | optional, for a retry of the same task |
| `route` | optional label for correlation only; it never changes who you are |

The response gives a `reference`. Keep it for the handover note.

Record these, with the `task_id`, before you end or hand over:

- `decision`: what was chosen and the reason, in a line or two.
- `next_action`: the next concrete step and where to start. There is no way to close one, so say when an earlier one is done in a later `decision`.
- `test_result`: the command, the outcome and the head it ran at.
- `evidence`: a fact worth keeping that a future agent would otherwise re-find.

## Handoff template

```
kind: next_action
task_id: <task>
summary: <one line: what to do next>
body: Start at <file or command>. Done so far: <one line>. Open: <what is unresolved>. Check first: <what to verify against the files>.
```

## Engine tools

- Each of `ctx_execute`, `ctx_batch`, `ctx_index`, `ctx_doctor` and `ctx_upgrade` needs the `execute` permission; `ctx_purge` needs `purge`. Without it the answer looks the same as `not found`.
- Paths must stay inside the worktree the server was launched for.
- Output is capped at 64 KiB and passes through redaction. Ask for less (a count, a filter) rather than the whole output.
- `ctx_doctor` with a repair request, and `ctx_upgrade` with an apply request, give `ask_first_required`. Those are for the operator.
- `ctx_purge` is a dry run until confirmed. Confirm only when asked.

## Refusals you may see

| Message | Meaning |
|---|---|
| `not found` | No such item, no such project, or no permission. It never says which. |
| secret refusal on an id | The id looked like a secret and was not stored or echoed. Use the task's ordinary id. |
| `ask_first_required` | An Engine action that needs the operator. Stop and report it. |

## What this skill cannot promise

- Loading is cooperative. The description in the catalog and the hook trigger on `mcp__context__ctx_*` calls ask for it; neither forces it, and a hook cannot help a chat host that has no hooks.
- A chat opened before the plugin update keeps the old skill list until a new chat starts.
- Chat surfaces do not have the `mcp__context__` tools yet.
