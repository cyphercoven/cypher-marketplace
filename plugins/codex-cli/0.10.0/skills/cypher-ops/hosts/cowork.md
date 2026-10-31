# cypher-ops on Cowork

The rules are in `../SKILL.md`. This host has the gateway connector and a scheduled-task feature.

- **Where you work:** repo edits go through the workspace tools in a cypherops worktree, or are handed to a Claude Code session; Cowork does not hold a checkout itself.
- **Reaching guests:** the gateway tools named in §3; call `session_begin` first and again after an idle expiry.
- **Before a merge or restart:** show the `will_restart` plan and wait for the person's yes; anything public is a B-lane ask.
- **Waiting for an idle service:** create one scheduled task that re-checks the queue, health endpoint and journal, restarts only if idle, and then reports; cancel it when done. One check-in, not a polling loop.
- **Done:** have `clean-check.sh` run in the workspace and quote its last line.
