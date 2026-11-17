# cypher-afk on Cowork

The rules are in `../SKILL.md`. Cowork has no plugin hooks, so, as in chat, the thread rides on HANDOVER.md and the automatic summary.

- **Keep HANDOVER.md current after every task** (gateway `workspace_edit` with `if_sha256`): tick the item, update "Next (exact first action)", add queue entries. Also keep the project doc `claude/<slug>-status.md` pointing at it.
- **Turn it off yourself:** when a message from the owner arrives, change the line to `AFK: off since <time>` and answer them. Exception: an evening hold (`until <time>` on the line, time not yet passed) stays on for anything but an explicit off ("afk off", "I'm back", "back", "stop afk"); answer briefly and queue any quick instruction.
- **Waiting:** `job_poll` or `factory_events` inside a turn. For a job that outlasts the turn, use the host's same-session check-in (`send_later`) at its expected finish, re-armed if the job is still running and disabled once it has fired (`update_trigger {enabled: false}`, logged as `cypher-scheduled-tasks` says). If the session has no same-session check-in, the queue waits for the owner. Never a polling loop, never `fire_trigger` or `delete_trigger` (the auto-mode check refuses them from a session), and never a successor session while AFK.
- **Check before ending a turn:** if `- [ ]` items remain, take the next one instead of ending.
- **Morning report:** send it as the last message, ask last; Cowork shows no other channel, so it is the only thing the owner reads first.
- **Context:** the automatic summary replaces early turns; the AFK lines and queue in HANDOVER.md are what survive, so never leave a decision only in the chat.
