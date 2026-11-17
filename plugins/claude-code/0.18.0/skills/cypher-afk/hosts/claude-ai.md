# cypher-afk on claude.ai (chat)

The rules are in `../SKILL.md`. Chat has no hooks and no way to keep a session alive on its own, so the thread rides on HANDOVER.md and the automatic summary.

- **Keep HANDOVER.md current after every task** (gateway `workspace_edit`, with `if_sha256` from your last read): tick the item, update "Next (exact first action)", add queue entries. When the conversation is summarised automatically, that file is what the summary can point to.
- **Turn it off yourself:** when a message from the owner arrives, change the line to `AFK: off since <time>` and answer them. Exception: an evening hold (`until <time>` on the line, time not yet passed) stays on for anything but an explicit off ("afk off", "I'm back", "back", "stop afk"); answer briefly and queue any quick instruction.
- **Waiting:** `job_poll` or `factory_events` inside a turn. For a job that outlasts the turn, set one `send_later` into this session at its expected finish, re-arm it if the job is still running, and remove it once it has fired. Never a polling loop, never a fresh session, never `fire_trigger`.
- **Check before ending a turn:** if `- [ ]` items remain, take the next one instead of ending.
- **Session:** if the gateway says the session is unknown or expired, call `session_begin` again and carry on. If the gateway goes down, assume another session is deploying it: wait 2 minutes and retry (`cypher-workflow` §2 standing rule 3).
- **Limit and cap:** chat has no compact command; the automatic summary is the compaction. At the AFK token cap or a long thread, keep HANDOVER.md current and carry on in this session. Never tell the owner to start a new or fresh session while AFK; `cypher-handover` waits until the owner is back.
