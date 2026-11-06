# cypher-afk on claude.ai (chat)

The rules are in `../SKILL.md`. Chat has no hooks and no way to keep a session alive on its own, so the thread rides on HANDOVER.md and the automatic summary.

- **Keep HANDOVER.md current after every task** (gateway `workspace_edit`, with `if_sha256` from your last read): tick the item, update "Next (exact first action)", add queue entries. When the conversation is summarised automatically, that file is what the summary can point to.
- **Turn it off yourself:** when any message from the owner arrives, change the line to `AFK: off since <time>` and answer them.
- **Waiting:** `job_poll` or `factory_events` inside a turn. For a job that outlasts the turn, set one `send_later` into this session at its expected finish, re-arm it if the job is still running, and remove it once it has fired. Never a polling loop, never a fresh session, never `fire_trigger`.
- **Check before ending a turn:** if `- [ ]` items remain, take the next one instead of ending.
- **Session:** if the gateway says the session is unknown or expired, call `session_begin` again and carry on; a 502 during a gateway update: wait 30 seconds and retry.
- **Limit:** chat has no compact command. A thread that is too long to continue is handled by `cypher-handover` after the owner is back, not by a successor started overnight.
