# cypher-workflow on Codex

last_verified: 2026-11-04

The rules are in `../SKILL.md`; host capabilities determine the supported tools.

- **Native delegation:** use native Codex sub-agents for the majority of substantive work, including independent work in parallel, with bounded briefs and disjoint write ownership. Claude factory scripts are a Claude-specific launcher; their incompatibility or unavailability does not require serial execution on Codex. Do not launch those scripts as a substitute for native agents. The main agent is the orchestrator: decompose, dispatch, coordinate dependencies, assess evidence, integrate results, verify acceptance and report. It chooses each subagent's model and reasoning effort according to complexity, uncertainty and risk; no single model is mandated and routine selection needs no owner approval. Direct work is appropriate for coordination, integration, small immediate unblocks or work that cannot usefully be delegated, while the majority of substantive work remains delegated. Preserve independent review, product gates and live-operation safeguards. Read `cypher-delegation` for the shared brief and review requirements.
- **Legacy adaptation:** a temporary AGENTS.md restriction that says unavailable Claude factory seats mean “do the work yourself, one task at a time” is superseded by this host guidance and the owner's clarification. This removes that serial-only adaptation; it does not override an explicit task-specific owner restriction or host security policy.

- **Immediate plugin adoption (CLI / desktop local runtime):** inspect `codex plugin marketplace upgrade --help` and `codex plugin add --help`; when supported, run `codex plugin marketplace upgrade cypher --json`, then `codex plugin add cypher@cypher --json`. Verify with `codex plugin list --marketplace cypher --json` and read the changed files from the reported installed version/cache, comparing them with the released source. Read the relevant installed SKILL.md files in this chat immediately; new chats discover the updated catalogue. Do not claim a separate cloud Chat/Work installation was updated by a local CLI command. If these commands are unavailable, use a supported plugin-management tool; otherwise report the exact manual refresh still needed. Never edit the cache or silently remove/reinstall a different plugin.
- **Files:** use the host's edit tool for tracked files; never `sed -i`, `perl -i`, a heredoc or a python rewrite.
- **Waiting:** chain the long job on the machine and read its result. Skip the scheduled check-in, Factory Watch and follow-up sweep lines of §3 and §5.
- **Handover (§4):** write HANDOVER.md and end with the paste line.
- **Session:** gateway `session_begin` with `surface` set to `codex`, when the gateway is connected.
