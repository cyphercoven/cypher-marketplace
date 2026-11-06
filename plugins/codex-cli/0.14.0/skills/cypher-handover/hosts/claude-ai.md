# cypher-handover on claude.ai (chat)

The rules are in `../SKILL.md`; this file adds the host steps it points to.

- **No successor:** do not schedule one and never `fire_trigger`; the old relay is retired. The paste line is the only mechanism.
- **Fired handover tasks:** from older sessions they stay disabled and are never deleted.
- **Context:** `/compact` is not available in chat; a long thread is the signal to suggest a fresh session.
- **Last message:** the suggestion and the paste line, then stop.
