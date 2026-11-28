# cypher-afk on Claude Code

The rules are in `../SKILL.md`. This host runs the plugin's hooks (`hooks/hooks.json` → `${CLAUDE_PLUGIN_ROOT}/scripts/afk.py`), so the same session keeps going without a new session and without a scheduled task.

| Event | What `afk.py` does (all fail open, all silent when AFK is off) |
|---|---|
| PreCompact | rewrites HANDOVER "Next (exact first action)" from the first runnable `- [ ]` item, so the file is current before the summary is made |
| SessionStart, matcher `compact` | prints `hookSpecificOutput.additionalContext`: AFK since, HANDOVER Next, the runnable queue, how many items wait for the owner |
| Stop | blocks while runnable work remains, including an unchanged repeated queue: diagnose lack of progress, wait for active work or compact and continue; at the token cap compaction takes priority. Allows a stop only when AFK is off, the queue is empty or only owner-blocked items remain |
| UserPromptSubmit | applies next-local-morning owner-response eligibility or explicit off; scheduled reports and missing/empty prompts are inert. Timezone: `$CYPHER_OWNER_TZ`, else non-UTC `$TZ`, else Europe/London |

- **Which file:** `$CYPHER_AFK_HANDOVER`, else the newest `~/scratch/*/HANDOVER.md` whose last AFK line is `on`. Set the variable when two AFK sessions share a machine.
- **Cap:** `AFK token cap: <n>` in HANDOVER.md, else `$CYPHER_AFK_TOKEN_CAP`, else 1500000 billable tokens (input + output + cache creation, summed from the transcript; cache reads are not counted). Reaching it means compact and carry on (`/compact` or auto-compact), never stop and never a fresh session (owner, 2026-11-12).
- **Loop guard:** unchanged runnable queues still block; diagnose or wait for active jobs, compact when needed, and never blindly repeat failed actions. Host continuation limits still apply; the plugin adds no scheduler or wake mechanism.
- **Owner return:** apply the main skill's next-local-morning response eligibility to daytime and overnight AFK. Before 05:00 turn-on uses that same-day morning; otherwise use the next day. Interim prompts preserve original `since`. Owning-session going-away instructions or literal "still AFK" preserve `since` before eligibility and renew it after eligibility; literal "still AFK" without an active owning period or from another session is inert. Only an actual eligible owner response or an opening explicit off ends AFK. Missing/invalid timestamps require explicit off. Missing/empty prompts and `Scheduled AFK morning report:` prompts preserve AFK and eligibility; an opening explicit off wins. Legacy `until` has no authority.
- **Reports and queue:** a 09:00 morning report is a progress snapshot. Keep AFK on and continue remaining authorized runnable work in this session. Record an early empty or owner-blocked-only queue as queue status without an early morning report. This may end the current turn but never AFK; distinguish it from all authorized work being complete. Reports never start a successor or create a scheduler/wake mechanism.
- **Write HANDOVER.md** with Edit/Write only. The hooks write it too, one line at a time.
- **Headless seat:** a seat launched by the factory scripts follows its brief; AFK hooks only act when a HANDOVER.md says `AFK: on`.

Host notes, checked 2026-10-30 against https://code.claude.com/docs/en/hooks.md:
- PreCompact input carries `trigger` (`manual` or `auto`) and `custom_instructions`; exit 2 or `decision: "block"` would block compaction, which this hook never does.
- SessionStart takes `hookSpecificOutput.additionalContext`; its matcher `compact` fires after compaction.
- Stop input carries `stop_hook_active`, true when Claude Code is already continuing because of a stop hook; `decision: "block"` needs a `reason`.
