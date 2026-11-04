# cypher-workflow on Claude Code

The rules are in `../SKILL.md`. This host has a workspace shell, so most host-only steps do not apply.

- **Files:** Edit / Write / Grep / Glob / Read (the "Seat" row of *Changing a file*); never a shell rewrite.
- **Waiting:** chain the long job on the machine and read its result; no scheduled check-in tools here. A `/loop` or `ScheduleWakeup` is for the user to ask for, not a default.
- **Factory Watch, scheduled tasks, artifacts:** not available. Skip those lines of §3 and §5.
- **Handover (§4):** write HANDOVER.md and end with the paste line. `/compact` is the cheaper alternative only when the user prefers to stay in the thread.
- **Session:** a headless seat follows its brief; §3 and *Leave every repo clean* still apply.
