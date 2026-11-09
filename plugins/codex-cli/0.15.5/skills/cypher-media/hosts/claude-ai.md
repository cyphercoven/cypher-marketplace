# cypher-media on claude.ai

The rules are in `../SKILL.md`. This host has the gateway connector but no workspace shell.

- **Start:** `session_begin {label: "Cypher: media: weekly maintenance", surface: "cowork"}`; the NAS watch uses the label "Cypher: ops: TV disk watch".
- **Commands on the guest and the workspace:** use `ct_exec` and `workspace_exec`; keep each call short and run long work detached.
- **Recurring run:** set the weekly run and the "NAS Disk Watch" scheduled task with the session's scheduling tools (`create_trigger`), or run this on demand.
- **Finishing the NAS watch:** find the "NAS Disk Watch" task with `list_triggers`, then disable it with `update_trigger {enabled: false}`.
- **Notify:** put the `<routine_summary>` in your final reply under the conditions in SKILL.md step 9.
