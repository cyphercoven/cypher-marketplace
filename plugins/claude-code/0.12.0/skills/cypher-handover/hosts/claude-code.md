# cypher-handover on Claude Code

The rules are in `../SKILL.md`. This host has a workspace shell and no way to start a session from another.

- **Write:** HANDOVER.md goes in `~/scratch/<slug>/` with the Write tool; never a shell rewrite.
- **Last message:** the suggestion and the paste line, then stop. Nothing is scheduled.
- **Staying in the thread:** `/compact` is the cheaper alternative only when the user prefers to stay in this session; the clean-check still runs first.
- **Headless seat:** a seat launched by the factory scripts follows its brief and ends with its report and the clean-check, not a handover message.
