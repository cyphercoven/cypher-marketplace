# cypher-afk on claude.ai (chat)

The rules are in `../SKILL.md`. Chat has no hooks and no way to keep a session alive on its own, so the thread rides on HANDOVER.md and the automatic summary.

- **Keep HANDOVER.md current after every task** (gateway `workspace_edit`, with `if_sha256` from your last read): tick the item, update "Next (exact first action)", add queue entries. When the conversation is summarised automatically, that file is what the summary can point to.
- **Turn it off yourself:** when any message from the owner arrives, change the line to `AFK: off since <time>` and answer them.
- **Waiting:** use the gateway's `factory_events` or `job_poll` for a long job. Never a scheduled task, never a polling loop, and never a fresh session.
- **Check before ending a turn:** if `- [ ]` items remain, take the next one instead of ending.
- **Session:** if the gateway says the session is unknown or expired, call `session_begin` again and carry on; a 502 during a gateway update: wait 30 seconds and retry.
- **Limit:** chat has no compact command. A thread that is too long to continue is handled by `cypher-handover` after the owner is back, not by a successor started overnight.
