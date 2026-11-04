---
name: "cypher-afk"
user-invocable: false
description: "Load when the owner's message STARTS with a going-away phrase: \"going to bed\", \"going afk\", \"afk\", \"I'm away\", /cypher-admin afk. Turns away mode on: nothing waits on the owner, gates and ask-first actions go to a morning report queue, work carries on in the same session, and the run ends with one morning report. Do not load when afk is only a word inside a message (\"review the afk.py diff\", \"is afk still on?\")."
---

# Cypher AFK: working while the owner is away

This skill owns the away-mode rules AF-01..AF-06 (`rules/rules.yaml`). The lane, gates, ask-first list and the clean-check are `cypher-workflow`; the HANDOVER.md template is `cypher-handover`. Per-host steps are in `hosts/<host>.md`. Addresses, service names and the public-service list come from the gateway's `knowledge` tool at run time, never from this file.

## When to load this

Load it when the owner's message **starts** with a going-away phrase and they expect work to go on: "going to bed", "going afk", "afk", "I'm away" / "I am away", or `/cypher-admin afk`. A leading quote mark, `>` or filler word ("ok", "right", "so", "well") does not stop it counting, and "afk..." or "afk-ing now" is a trigger. The rest of the message can say anything ("going to bed so stay in this session until the task is complete").

Do not load it when "afk" or the phrase sits inside a message rather than opening it ("review the afk.py diff", "turn afk off please", "is afk still on?", "the afk hook", a game, a chat about someone else being away), when the owner wants a handover to a fresh session (`cypher-handover`), or when work is blocked on them and they are still here.

## 1. Turn it on (AF-01)

1. Find the run's HANDOVER.md (`~/scratch/<slug>/HANDOVER.md`; create it from the `cypher-handover` template if there is none).
2. Write these lines with Edit or Write, never a shell rewrite:

   ```markdown
   AFK: on since <UTC time, ISO>
   AFK token cap: <optional number; default 1500000 billable tokens per session>

   ## AFK queue
   - [ ] <task, one runnable step each, in order>
   - [?] <item that waits on the owner, and why>

   ## Morning report queue
   ```

   If an `AFK:` line is already there with a `session <id>` token, keep that token on the line when you rewrite it (`AFK: on since <time> session <id>`). On a first run the hook has no line to mark yet: write it without a session and the hook adds the owner at the next Stop or compaction. If the line still has no `session <id>` token by the end of your second turn, tell the owner the away-mode hooks are not active (the trigger was not seen) and carry on in plain AFK behaviour.

   `- [ ]` is runnable, `- [x]` done, `- [?]` waits on the owner. Put every task the owner named, plus the ones you can see coming from the plan, in the queue before you start.
3. Say it in one line ("AFK on since <time>, <n> tasks queued") and start the first task. Do not ask a question first.

**Any new message from the owner that does not start with a trigger phrase turns it off (AF-01).** On Claude Code a hook does it, and only for the session that owns the AFK (the hook writes `AFK: on since <time> session <id>` when a message opens with a trigger phrase in that session and the line exists; on a first run it remembers the session and the first Stop or compaction there adds the owner; a message in another session leaves it on, and a non-trigger message never turns an off line on); on every other host you do it yourself: the moment such a message arrives, change the line to `AFK: off since <time>` and answer them. A message that opens with "afk" again turns it back on through this section.

## 2. Nothing waits on the owner (AF-02)

While AFK, never stop to ask, and never do what needs a yes. Before each action, decide queue or do:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/afk.py" classify "<what you are about to do>"
```

(`CYPHER_PUBLIC_SERVICES` may carry the comma-separated public-service names from `knowledge`; the word "public" in the action also counts.) The answer is `queue` or `do`.

| Action | Result |
|---|---|
| A gate: spec, design, UAT, or anything that needs the owner's yes | `queue`, kind `gate` |
| Restarting a public-set service | `queue`, kind `restart` |
| Any kill, terminate, destroy or delete | `queue`, kind `destroy` |
| A downtime window | `queue`, kind `downtime` |
| Everything else in your lane (code, tests, PRs, merges after the review tier, deploys of non-public parts, docs) | `do` |

When it says `queue`:

1. Append `- <kind>: <what, with the exact command or link the owner would need>` under `## Morning report queue`. The same item twice is one item.
2. Mark the task `- [?]` in the AFK queue, with the reason.
3. **Do not do it, and do not ask.** Start the next independent task. If a later task depends on the queued one, mark it `- [?]` too and carry on with something that does not.

Anything else you were unsure about and cannot undo: treat it as ask-first and queue it.

## 3. Keep going on the same thread (AF-03)

- After every finished task: tick it `- [x]`, commit and push, and set HANDOVER "Next (exact first action)" to the next runnable task. A summary of this session must be enough to resume from that file alone.
- Never hand over to a fresh session, start a successor, or schedule anything while AFK. The thread stays in this session and survives compaction (section 6).
- When a long job runs (a build, a factory run), wait for it with the gateway's `factory_events` or `job_poll`, not with a polling loop, then carry on.
- Heavy steps (full review, mirror sync, UAT build) still run once at the end of the change set, as in `cypher-workflow`; a UAT build waits in the queue as a gate.

## 4. The end of the queue (AF-04)

Away mode ends when the runnable queue is empty or only `- [?]` items remain, or the token cap is reached. Then:

1. Make every repo clean: commit and push, merge or name the open PR, then
   ```bash
   cypherops/factory/bin/clean-check.sh --run <slug> <every repo you touched>
   ```
   It must exit 0; its last line goes in the report. The only FAILs allowed are open PRs the report names.
2. Leave `AFK: on` as it is: it ends when the owner writes, not when the queue empties. Put the report's ask on the `Waiting on the owner:` line in HANDOVER.md.
3. Send the morning report (section 5) as your one final message.

## 5. The morning report (AF-05)

One message, short, next action first. Fill every part from HANDOVER.md and the git history, not from memory:

```markdown
**Morning report — <App/Service>: <name>.** AFK <since> → <end>, <n> tasks done, <m> queued for you.

**Shipped**
- <merged PR or commit: what it does> (<link>)

**Restarted / deployed**
- <what restarted, or "nothing restarted">

**Not done: needs you** (queued, nothing was run)
- gate: <what, link>
- restart: <what, the exact command ready to run>
- destroy: <what, and what would be lost>
- downtime: <when, how long, what it takes down>

**Clean-check:** <last line of clean-check.sh>

**Gate <1 spec | 2 design | 3 UAT | ask first> — <what comes first>.**
<What the owner does, in one or two lines: where to look, what to answer.>

**YOUR INPUT NEEDED**
```

- The last paragraph is the ask, with nothing after it: no tool call, no sign-off (AF-05).
- If the queue is empty, there is no ask: end with `**Nothing needed from you** — <what is done>.` instead.
- One ask only. When several items are queued, list them all above and put the most blocking one last.
- Never put a secret value, a personal name or a pronoun in the report.

## 6. What carries the thread (AF-06)

The thread is HANDOVER.md plus the host's own compaction. Read `hosts/<host>.md` for yours. In short:

| Host | Carried by |
|---|---|
| Claude Code | hooks shipped with this plugin: PreCompact refreshes "Next", SessionStart(compact) re-injects it, Stop blocks while runnable work remains |
| Codex | the auto-compact limit and an AGENTS.md line pointing at HANDOVER.md |
| Chat hosts | HANDOVER.md kept current after every task so the automatic summary carries it |

## Edge cases

- **The owner says "afk" and a gate is next.** Queue it (section 2) and take the next independent task; do not ask "should I wait?".
- **Nothing runnable at the start.** Write the morning report straight away; do not invent work.
- **A task fails twice.** Mark it `- [?]` with the error (never a secret), add `ask first: <what failed>` to the morning queue and move on.
- **The clean-check fails on something that is not yours.** Copy it to `~/scratch/rescue-<date>/`, compare, and name it in the report; do not delete it unseen.
- **Two AFK sessions on one machine.** Set `CYPHER_AFK_HANDOVER` to this run's HANDOVER.md so the hooks read the right file.
