
- **Reports and queue:** a 09:00 morning report is a progress snapshot. Keep AFK on and continue remaining authorized runnable work in this session. Record an early empty or owner-blocked-only queue as queue status without an early morning report. This may end the current turn but never AFK; distinguish it from all authorized work being complete. Reports never start a successor or create a scheduler/wake mechanism.

# cypher-afk on claude.ai (chat)

The rules are in `../SKILL.md`. Chat has no hooks and no way to keep a session alive on its own, so the thread rides on HANDOVER.md and the automatic summary.

- **Keep HANDOVER.md current after every task** (gateway `workspace_edit`, with `if_sha256` from your last read): tick the item, update "Next (exact first action)", add queue entries. When the conversation is summarised automatically, that file is what the summary can point to.
- **Owner return:** apply the main skill's next-local-morning response eligibility to daytime and overnight AFK. Before 05:00 turn-on uses that same-day morning; otherwise use the next day. Interim prompts preserve original `since`. Owning-session going-away instructions or literal "still AFK" preserve `since` before eligibility and renew it after eligibility; literal "still AFK" without an active owning period or from another session is inert. Only an actual eligible owner response or an opening explicit off ends AFK. Missing/invalid timestamps require explicit off. Missing/empty prompts and `Scheduled AFK morning report:` prompts preserve AFK and eligibility; an opening explicit off wins. Legacy `until` has no authority.
- **Waiting:** `job_poll` or `factory_events` inside a turn. For a job that outlasts the turn, set one `send_later` into this session at its expected finish, re-arm it if the job is still running, and remove it once it has fired. Never a polling loop, never a fresh session, never `fire_trigger`.
- **Check before ending a turn:** if `- [ ]` items remain, take the next one instead of ending.
- **Session:** if the gateway says the session is unknown or expired, call `session_begin` again and carry on. If the gateway goes down, assume another session is deploying it: wait 2 minutes and retry (`cypher-workflow` §2 standing rule 3).
- **Limit and cap:** chat has no compact command; the automatic summary is the compaction. At the AFK token cap or a long thread, keep HANDOVER.md current and carry on in this session. Never tell the owner to start a new or fresh session while AFK; `cypher-handover` waits until the owner is back.
