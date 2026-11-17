# cypher-ops on Claude Code

The rules are in `../SKILL.md`. This host has a workspace shell and the gateway tools.

- **Where you work:** your own worktree of cypherops under the run's scratch directory, cut from `origin/main`. The shared checkout is read-only; never write into it.
- **Files:** Edit / Write / Read / Grep / Glob; never a shell rewrite of a tracked file.
- **Reaching guests:** the gateway `ct_exec` / `workspace_*` / `pve_*` / `utils_*` tools, per §3. Pass secrets through the `secrets:` list only.
- **Waiting for an idle service:** if a restart must wait for in-flight work, chain the check on the machine and read its result; a `/loop` or `ScheduleWakeup` is for the user to ask for, not a default.
- **Done:** run `clean-check.sh` from a current-main worktree and report its last line.
