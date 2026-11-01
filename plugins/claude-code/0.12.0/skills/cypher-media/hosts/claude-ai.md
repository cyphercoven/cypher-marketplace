# cypher-media on claude.ai

The rules are in `../SKILL.md`. This host has the gateway connector but no workspace shell.

- **Start:** `session_begin {label: "Cypher: media: weekly maintenance", surface: "cowork"}`; the NAS watch uses the label "Cypher: ops: TV disk watch".
- **Commands on the guest and the workspace:** use `ct_exec` and `workspace_exec`; keep each call short and run long work detached.
- **Recurring run:** you cannot hold a schedule. Ask the person to set up the weekly run and the "NAS Disk Watch" scheduled task on a host that has the feature, or run this on demand.
- **Finishing the NAS watch:** tell the person to disable the "NAS Disk Watch" scheduled task; you cannot do it from here.
- **Notify:** put the `<routine_summary>` in your final reply under the conditions in SKILL.md step 9.
