# cypher-afk on Claude Code

The rules are in `../SKILL.md`. This host runs the plugin's hooks (`hooks/hooks.json` → `${CLAUDE_PLUGIN_ROOT}/scripts/afk.py`), so the same session keeps going without a new session and without a scheduled task.

| Event | What `afk.py` does (all fail open, all silent when AFK is off) |
|---|---|
| PreCompact | rewrites HANDOVER "Next (exact first action)" from the first runnable `- [ ]` item, so the file is current before the summary is made |
| SessionStart, matcher `compact` | prints `hookSpecificOutput.additionalContext`: AFK since, HANDOVER Next, the runnable queue, how many items wait for the owner |
| Stop | prints `{"decision": "block", "reason": "<next task>"}` while runnable work remains; prints nothing (the stop is allowed) when the queue is empty, only `- [?]` items remain, the token cap is reached, or `stop_hook_active` is true and the queue has not moved since the last block |
| UserPromptSubmit | any message from the owner changes the line to `AFK: off since <time>` |

- **Which file:** `$CYPHER_AFK_HANDOVER`, else the newest `~/scratch/*/HANDOVER.md` whose last AFK line is `on`. Set the variable when two AFK sessions share a machine.
- **Cap:** `AFK token cap: <n>` in HANDOVER.md, else `$CYPHER_AFK_TOKEN_CAP`, else 1500000 billable tokens (input + output + cache creation, summed from the transcript; cache reads are not counted).
- **Loop guard:** Claude Code also stops continuing after 8 consecutive stop-hook continuations. A block with no progress between two stops is allowed by the hook itself.
- **Write HANDOVER.md** with Edit/Write only. The hooks write it too, one line at a time.
- **Headless seat:** a seat launched by the factory scripts follows its brief; AFK hooks only act when a HANDOVER.md says `AFK: on`.

Host notes, checked 2026-10-30 against https://code.claude.com/docs/en/hooks.md:
- PreCompact input carries `trigger` (`manual` or `auto`) and `custom_instructions`; exit 2 or `decision: "block"` would block compaction, which this hook never does.
- SessionStart takes `hookSpecificOutput.additionalContext`; its matcher `compact` fires after compaction.
- Stop input carries `stop_hook_active`, true when Claude Code is already continuing because of a stop hook; `decision: "block"` needs a `reason`.
