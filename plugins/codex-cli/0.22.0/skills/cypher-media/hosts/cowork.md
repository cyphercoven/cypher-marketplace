# cypher-media on Cowork

The rules are in `../SKILL.md`. This host has the gateway connector and a scheduled-task feature.

- **Start:** `session_begin {label: "Cypher: media: weekly maintenance", surface: "scheduled-task"}` when the scheduled task started you, `surface: "cowork"` when run by hand. The NAS watch uses the label "Cypher: ops: TV disk watch" with the same surface rule.
- **Recurring run:** the weekly maintenance is the "Media Maintenance" scheduled task (Sundays); the NAS watch is the "NAS Disk Watch" scheduled task. Each task's prompt is "load cypher-media and run it".
- **Finishing the NAS watch:** find the task with `list_triggers` by the name "NAS Disk Watch", then `update_trigger {enabled: false}`. Never delete it — a session cannot delete the task that started it.
- **Notify:** one push notification only under the conditions in SKILL.md step 9 and the NAS check; the `<routine_summary>` goes in the notification. Otherwise end with a one-line summary.
