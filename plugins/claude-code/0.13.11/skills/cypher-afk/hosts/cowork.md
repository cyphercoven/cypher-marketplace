# cypher-afk on Cowork

The rules are in `../SKILL.md`. Cowork has no plugin hooks, so, as in chat, the thread rides on HANDOVER.md and the automatic summary.

- **Keep HANDOVER.md current after every task** (gateway `workspace_edit` with `if_sha256`): tick the item, update "Next (exact first action)", add queue entries. Also keep the project doc `claude/<slug>-status.md` pointing at it.
- **Turn it off yourself:** the moment a message from the owner arrives, change the line to `AFK: off since <time>` and answer them.
- **Waiting:** `factory_events` or `job_poll` for a long job. **Never a scheduled task**, never `fire_trigger` or `delete_trigger` (the auto-mode check refuses them from a session), and never a successor session while AFK.
- **Check before ending a turn:** if `- [ ]` items remain, take the next one instead of ending.
- **Morning report:** send it as the last message, ask last; Cowork shows no other channel, so it is the only thing the owner reads first.
- **Context:** the automatic summary replaces early turns; the AFK lines and queue in HANDOVER.md are what survive, so never leave a decision only in the chat.
