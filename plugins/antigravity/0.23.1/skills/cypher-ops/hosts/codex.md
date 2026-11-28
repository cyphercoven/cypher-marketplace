# cypher-ops on Codex

The rules are in `../SKILL.md`. This host has a shell and the gateway as an MCP server.

- **Where you work:** your own worktree of cypherops on a task branch from `origin/main`; the shared checkout is read-only.
- **Files:** use the patch/edit tool; never a shell rewrite of a tracked file.
- **Reaching guests:** the gateway tools named in §3, with secrets only through the `secrets:` list.
- **Waiting for an idle service:** no scheduler here. Finish the repo side, state exactly what is left to restart and the idle check to run, and hand that to the person.
- **Done:** run `clean-check.sh` from a current-main worktree and report its last line.
