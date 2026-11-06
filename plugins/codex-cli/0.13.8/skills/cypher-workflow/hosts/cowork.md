# cypher-workflow on Cowork

What only this host can do. The rules are in `../SKILL.md`; this file adds the host steps it points to.

- **Session:** first gateway call is `session_begin {label, client_session, surface: "cowork"}`; say the id in your first reply.
- **Check-in later:** one `send_later` at the expected finish of a long job. No polling loops, no `Monitor` rounds for hour-long jobs. Delete it once it has run.
- **Factory Watch:** after `export FACTORY_RUN=<slug> FACTORY_SESSION=<id>` and the first seat, open it with the Artifact tool `open` (URL in the project doc `claude/factory-watch-status.md`).
- **Handover (§4):** write HANDOVER.md and point the project doc `claude/<slug>-status.md` at it, then end with the paste line. Do not schedule a successor: Cowork's auto-mode check refuses `fire_trigger` and `delete_trigger` from a session.
- **Closing (§5):** sweep follow-ups as `cypher-scheduled-tasks` says. Fired handover tasks stay disabled, never deleted.
- **Context:** a long thread, or a first `/compact`, is the signal to suggest a fresh session.
