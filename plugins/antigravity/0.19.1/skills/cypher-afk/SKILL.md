---
name: "cypher-afk"
user-invocable: false
description: "Load when the owner's message STARTS with a going-away phrase: \"going to bed\", \"going afk\", \"afk\", \"I'm away\", /cypher-admin afk. Turns away mode on: nothing waits on the owner, gates and ask-first actions go to a morning report queue, work carries on in the same session, and morning reports show progress without ending AFK. Do not load when afk is only a word inside a message (\"review the afk.py diff\", \"is afk still on?\")."
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
   AFK: on since <UTC time>   (time format exactly YYYY-MM-DDTHH:MMZ, e.g. 2026-11-06T22:10Z)
   AFK token cap: <optional number; default 1500000 billable tokens per session>

   ## AFK queue
   - [ ] <task, one runnable step each, in order>
   - [?] <item that waits on the owner, and why>

   ## Morning report queue
   ```

   If an `AFK:` line is already there with a `session <id>` token, keep that token and the original `since` on interim updates (`AFK: on since <time> session <id>`); legacy `until` tokens have no authority. On a first run the hook has no line to mark yet: write it without a session and the hook adds the owner at the next Stop or compaction. If the line still has no `session <id>` token by the end of your second turn, tell the owner the away-mode hooks are not active (the trigger was not seen) and carry on in plain AFK behaviour.

   `- [ ]` is runnable, `- [x]` done, `- [?]` waits on the owner. Put every task the owner named, plus the ones you can see coming from the plan, in the queue before you start.
3. Say it in one line ("AFK on since <time>, <n> tasks queued") and start the first task. Do not ask a question first.

**Owner morning return (AF-01).** Every AFK period, including daytime turn-on, waits for the next local morning before a normal owner response can end it. Morning starts at 05:00 owner-local (host timezone; default Europe/London). Turn-on before 05:00 uses that upcoming same-day morning; turn-on at or after 05:00 uses the following day. This is response eligibility only: no clock time, including 07:00 or 09:00, expires AFK.

Before eligibility, answer interim status questions briefly, add quick instructions to the appropriate queue, and continue. Repeated going-away messages or literal "still AFK" in the same owning session preserve the original `since` before eligibility and renew `since` and next-morning eligibility after eligibility. Literal "still AFK" from another session or without an active owning period is inert. An opening explicit off ("afk off", "I'm back", "back", "stop afk", "turn afk off") ends AFK at any time. Otherwise an actual non-trigger owner response after eligibility turns it off. Invalid or missing timestamps conservatively require explicit off.

A prompt beginning with the reserved human-readable prefix `Scheduled AFK morning report:` is informational automation, never an owner return or a renewal. Preserve AFK, original `since`, eligibility and outstanding work. Missing or empty prompt events are also inert. An opening explicit off takes priority. Legacy `until` tokens may parse but never decide state or appear as active deadlines.

On Claude Code the prompt hook enforces these transitions for the owning session; a new trigger can claim the session, including a pending first-run claim, while other-session status/off/report messages leave it alone. On other hosts apply the same transitions manually in HANDOVER.md.

## 2. Nothing waits on the owner (AF-02)

While AFK, never stop to ask, and never do what needs a yes. The owner's standing pre-approval (owner, 2026-11-12; `cypher-workflow` §2 *Owner standing rules*) covers everything that can be rolled back and cannot take down the house internet: set it up, merge, apply or deploy it. That includes gateway/utils restarts, Ansible applies, new databases and migrations, live test data, test identities or invites sent to the owner's own catch-all domain, public-service restarts and downtime that can be rolled back. Before each action, decide queue or do:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/afk.py" classify "<what you are about to do>"
```

The answer is `queue` or `do`.

| Action | Result |
|---|---|
| A gate: spec, design or UAT | `queue`, kind `gate` |
| An irreversible delete (data, a guest, a backup, a repo, a vault item) | `queue`, kind `destroy` |
| Anything that could cut the house internet: the Flint router's WAN, DNS or DHCP (`flint_*`), the sw-core switch uplink (`switch_*`) | `queue`, kind `internet` |
| Everything else (code, tests, PRs, merges after the review tier, deploys, restarts incl. the gateway and public services, Ansible applies, databases and migrations, test data and test invites, killing a stuck job, docs) | `do` |

When it says `queue`:

1. Append `- <kind>: <what, with the exact command or link the owner would need>` under `## Morning report queue`. The same item twice is one item.
2. Mark the task `- [?]` in the AFK queue, with the reason.
3. **Do not do it, and do not ask.** Start the next independent task. If a later task depends on the queued one, mark it `- [?]` too and carry on with something that does not.

Anything else you were unsure about and cannot undo: treat it as ask-first and queue it.

**A refusal blocks one action only.** A safety-check, permission or classifier refusal blocks only that exact action. Take a safer equivalent route, or queue it as `ask first: <what was refused>` and carry on. Never turn one refusal into a question about other, unblocked work.

**Asking for something already covered is a rule break.** Before any ask or queue entry, check: is it a gate, an irreversible delete or a house-internet change? If none of these, do it.

## 3. Keep going on the same thread (AF-03)

- After every finished task: tick it `- [x]`, commit and push, and set HANDOVER "Next (exact first action)" to the next runnable task. A summary of this session must be enough to resume from that file alone.
- Never hand over to a fresh session or start a successor while AFK, and never tell the owner to start a new or fresh session. The `cypher-handover` "suggest a fresh session" signals do not apply while AFK is on. The thread stays in this session and survives compaction (section 6).
- **The token cap means compact and carry on, not stop.** At the cap, make HANDOVER.md current, let the host compact (Claude Code: the Stop hook says so and keeps going; Codex: auto-compact; chat: the automatic summary), and carry on with the next task in this same session.
- On a host without hooks, nothing wakes the session once a turn ends. For a job that outlasts the turn, set one check-in into this same session at the job's expected finish, re-arm it if the job is still running, and remove it once it has fired (your host file says how, and if the host has no scheduler the queue waits for the owner). On a host with hooks nothing is scheduled; the hooks keep the session going.
- When a long job runs (a build, a factory run), wait for it inside a turn with the gateway's `factory_events` or `job_poll`, not with a polling loop, then carry on.
- Heavy steps (full review, preview publish, UAT build) still run once at the end of the change set, as in `cypher-workflow`; a UAT build waits in the queue as a gate.

## 4. The end of the queue (AF-04)

An empty runnable queue or only `- [?]` items means the currently authorized work is exhausted or owner-blocked; AFK stays on. The token cap means compact and continue (section 3). When nothing runnable remains:

1. Make every repo clean: commit and push, merge or name the open PR, then
   ```bash
   cypherops/factory/bin/clean-check.sh --run <slug> <every repo you touched>
   ```
   It must exit 0; its last line goes in the report. The only FAILs allowed are open PRs the report names.
2. Leave `AFK: on` as it is: only an eligible actual owner response or explicit off ends it. Put the report's ask on the `Waiting on the owner:` line in HANDOVER.md.
3. Record the queue status without an early morning report. Do not invent work; retain AFK so newly authorized runnable work can continue in this session.

## 5. The morning report (AF-05)

A 09:00 report is a progress snapshot, never expiry, completion of outstanding work, a reason to block runnable work, or permission to start a successor. Report completed work, remaining runnable work and owner-blocked items separately, then continue authorized work in this session. No timer, scheduler or live wake mechanism is added by this skill. Fill the report from HANDOVER.md and git history:

```markdown
**Morning report — <App/Service>: <name>.** AFK on since <since>; snapshot at <time>: <usable owner journeys and where available>; <blockers>; <deferred scope>; <remaining runnable work and owner decisions>. Continue outstanding authorized work after this snapshot.

**Shipped**
- <merged PR or commit: what it does> (<link>)

**Restarted / deployed**
- <what restarted, or "nothing restarted">

**Still runnable**
- <next authorized task; work continues>

**Not done: needs you** (queued, nothing was run)
- gate: <what, link>
- destroy: <what, and what would be lost>
- internet: <what, and what it could cut>
- ask first: <what was refused or failed twice, and the exact next step>

**Clean-check:** <last line of clean-check.sh>

**Gate <1 spec | 2 design | 3 UAT | ask first> — <what comes first>.**
<What the owner does, in one or two lines: where to look, what to answer.>

**YOUR INPUT NEEDED**
```

The report never tells the owner to start a new or fresh session and never ends AFK. Send a morning snapshot when due through an existing host capability; an early empty queue is recorded as queue status, not an early final morning report.

- Put any owner ask last in the report message. A progress report does not prevent subsequent tool calls or continued runnable work (AF-05).
- If no owner input is needed, end the report with `**Nothing needed from you** — <what is running or the queue status>.` An empty queue does not turn AFK off.
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
- **A restart, migration, Ansible apply or test invite is next.** Do it: it is pre-approved (section 2). Note it under "Restarted / deployed".
- **The gateway goes down.** Assume another session is deploying it: wait 2 minutes from the failed call and retry. Still down: read the other active sessions' notes, then use the break-glass routes. If another session changed the gateway recently, leave the fix to it and carry on with work that does not need the gateway (`cypher-workflow` §2 standing rule 3).
- **A safety check or classifier refuses an action.** Only that action is blocked: take a safer equivalent route or queue it as `ask first`, and carry on with the rest.
- **The token cap is reached.** Compact and carry on in this session (section 3); never suggest a fresh session.
- **Nothing runnable at the start.** Record the empty or owner-blocked queue, retain AFK, and do not invent work or send an early final morning report.
- **A task fails twice.** Mark it `- [?]` with the error (never a secret), add `ask first: <what failed>` to the morning queue and move on.
- **The clean-check fails on something that is not yours.** Copy it to `~/scratch/rescue-<date>/`, compare, and name it in the report; do not delete it unseen.
- **Two AFK sessions on one machine.** Set `CYPHER_AFK_HANDOVER` to this run's HANDOVER.md so the hooks read the right file.
