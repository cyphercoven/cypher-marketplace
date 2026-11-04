# cypher-workflow on Codex

The rules are in `../SKILL.md`. Codex has a workspace shell and no scheduling or artifact tools.

- **Files:** use the host's edit tool for tracked files; never `sed -i`, `perl -i`, a heredoc or a python rewrite.
- **Waiting:** chain the long job on the machine and read its result. Skip the scheduled check-in, Factory Watch and follow-up sweep lines of §3 and §5.
- **Handover (§4):** write HANDOVER.md and end with the paste line.
- **Session:** gateway `session_begin` with `surface` set to `codex`, when the gateway is connected.
