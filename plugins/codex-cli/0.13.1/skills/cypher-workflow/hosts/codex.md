# cypher-workflow on Codex

last_verified: 2026-11-04

The rules are in `../SKILL.md`. Codex has a workspace shell and no scheduling or artifact tools.

- **Immediate plugin adoption (CLI / desktop local runtime):** inspect `codex plugin marketplace upgrade --help` and `codex plugin add --help`; when supported, run `codex plugin marketplace upgrade cypher --json`, then `codex plugin add cypher@cypher --json`. Verify with `codex plugin list --marketplace cypher --json` and read the changed files from the reported installed version/cache, comparing them with the released source. Read the relevant installed SKILL.md files in this chat immediately; new chats discover the updated catalogue. Do not claim a separate cloud Chat/Work installation was updated by a local CLI command. If these commands are unavailable, use a supported plugin-management tool; otherwise report the exact manual refresh still needed. Never edit the cache or silently remove/reinstall a different plugin.
- **Files:** use the host's edit tool for tracked files; never `sed -i`, `perl -i`, a heredoc or a python rewrite.
- **Waiting:** chain the long job on the machine and read its result. Skip the scheduled check-in, Factory Watch and follow-up sweep lines of §3 and §5.
- **Handover (§4):** write HANDOVER.md and end with the paste line.
- **Session:** gateway `session_begin` with `surface` set to `codex`, when the gateway is connected.
