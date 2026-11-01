# cypher-media on Claude Code

The rules are in `../SKILL.md`. This host has a shell and the gateway as an MCP server.

- **Start:** `session_begin {label: "Cypher: media: weekly maintenance", surface: "cowork"}` when run by hand (the NAS watch uses the label "Cypher: ops: TV disk watch"). Use `surface: "scheduled-task"` only when a scheduled run started you.
- **Recurring run:** the weekly maintenance is a Sunday scheduled task, and the NAS watch is a recurring scheduled task named "NAS Disk Watch". Create them with the host's scheduler (`CronCreate`) only when the person asks; the task's prompt is "load cypher-media and run it".
- **Finishing the NAS watch:** disable the "NAS Disk Watch" task (`CronList` to find it, then delete or pause it from a session other than the one it started). Never delete the task that started the current session.
- **Notify:** one push notification only under the conditions in SKILL.md step 9 and the NAS check; otherwise end with a one-line summary.
- **Files:** the run log goes in the workspace with the edit tools, never a shell rewrite of a tracked file.
