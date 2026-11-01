# cypher-workflow on claude.ai (chat)

What only this host can do. The rules are in `../SKILL.md`; this file adds the host steps it points to.

- **Check-in later:** one `send_later` at the expected finish of a long job (§3 "Waiting costs nothing"). No polling loops, no `Monitor` rounds for hour-long jobs. Delete it once it has run.
- **Factory Watch:** after `export FACTORY_RUN=<slug> FACTORY_SESSION=<id>` and the first seat, open it with the Artifact tool `open` (URL in the project doc `claude/factory-watch-status.md`).
- **Handover (§4):** write HANDOVER.md, then end with the paste line. Do not schedule a successor; never `fire_trigger`.
- **Closing (§5):** sweep follow-ups as `cypher-scheduled-tasks` says (`list_triggers` → `delete_trigger`; a refused delete → `update_trigger {enabled: false}` and log it). Fired handover tasks stay disabled, never deleted.
- **Context:** `/compact` is not available in chat; a long thread is the signal to suggest a fresh session.
