# cypher-ops on claude.ai

The rules are in `../SKILL.md`. This host has the gateway connector but no workspace shell.

- **Where you work:** you cannot hold a worktree. Do repo work through the workspace tools (`workspace_exec`, `workspace_edit`, `workspace_read`) in a worktree of cypherops, or hand the change to a Claude Code session with a short brief.
- **Reaching guests:** the gateway tools named in §3; call `session_begin` first and again after an idle expiry.
- **Before a merge or restart:** show the `will_restart` plan from `forgejo_pr_merge` (no `confirm`) to the person and wait for their yes. Anything public is a B-lane ask.
- **Waiting for an idle service:** you cannot wait. Ask the person to start a scheduled check-in (the host's scheduled-task feature) or return to it in a later turn.
- **Done:** have `clean-check.sh` run in the workspace and quote its last line.
