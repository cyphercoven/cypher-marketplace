# cypher-media on Codex

The rules are in `../SKILL.md`. This host has a shell and the gateway as an MCP server.

- **Start:** `session_begin {label: "Cypher: media: weekly maintenance", surface: "cowork"}`; the NAS watch uses the label "Cypher: ops: TV disk watch".
- **Recurring run:** no scheduler here. Run on demand, or leave scheduling to a host that has it.
- **Finishing the NAS watch:** tell the person to disable the "NAS Disk Watch" scheduled task on the host that runs it.
- **Notify:** put the `<routine_summary>` in your final reply under the conditions in SKILL.md step 9.
- **Files:** write the run log with the patch/edit tool, never a shell rewrite of a tracked file.
