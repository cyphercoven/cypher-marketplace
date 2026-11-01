# cypher-handover on Cowork

The rules are in `../SKILL.md`; this file adds the host steps it points to.

- **Pointer:** after writing HANDOVER.md, point the project doc `claude/<slug>-status.md` at it.
- **No successor:** do not schedule one. Cowork's auto-mode check refuses `fire_trigger` and `delete_trigger` from a session, and the old relay is retired.
- **Fired handover tasks:** from older sessions they stay disabled and are never deleted; deleting one deletes every session it started.
- **Last message:** the suggestion and the paste line, then stop.
- **Context:** a long thread, or a first `/compact`, is the signal to suggest a fresh session.
