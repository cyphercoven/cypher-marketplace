
- **Owner return:** apply the main skill's next-local-morning response eligibility to daytime and overnight AFK. Before 05:00 turn-on uses that same-day morning; otherwise use the next day. Interim prompts preserve original `since`. Owning-session going-away instructions or literal "still AFK" preserve `since` before eligibility and renew it after eligibility; literal "still AFK" without an active owning period or from another session is inert. Only an actual eligible owner response or an opening explicit off ends AFK. Missing/invalid timestamps require explicit off. Missing/empty prompts and `Scheduled AFK morning report:` prompts preserve AFK and eligibility; an opening explicit off wins. Legacy `until` has no authority.
- **Reports and queue:** a 09:00 morning report is a progress snapshot. Keep AFK on and continue remaining authorized runnable work in this session. Record an early empty or owner-blocked-only queue as queue status without an early morning report. This may end the current turn but never AFK; distinguish it from all authorized work being complete. Reports never start a successor or create a scheduler/wake mechanism.

# cypher-afk on Codex

The rules are in `../SKILL.md`. The plugin ships no AFK hook for Codex, so the thread is carried by Codex's own compaction plus a pointer in AGENTS.md. You keep HANDOVER.md current by hand.

- **Auto-compact limit:** set `model_auto_compact_token_limit` (a number of tokens; unset uses the model default) in the Codex config file so compaction happens before the window is full, e.g. at about 80% of it. Compaction stays inside the same session.
- **AGENTS.md pointer:** add one line to the project's AGENTS.md so every turn after a compaction re-reads the file:
  `While HANDOVER.md says "AFK: on", read ~/scratch/<slug>/HANDOVER.md first and do its "Next" step; never ask the owner, queue gates and ask-first actions in its Morning report queue.`
  Codex reads at most `project_doc_max_bytes` of AGENTS.md; keep the line near the top.
- **After every task:** tick it in the AFK queue, commit and push, and rewrite "Next (exact first action)". Do this yourself; there is no PreCompact step to do it for you.
- **Stopping:** there is no Stop hook here. Before ending a turn with `- [ ]` items left, take the next one instead of ending.
- **Waiting:** `factory_events` or `job_poll` through the gateway inside a turn; no polling loops. Codex has no scheduler, so after a job that outlasts the turn the queue waits for the owner.
- **Surface:** pass `codex` as the `surface` when you call the gateway's `session_begin`.

Host notes, read 2026-10-30: https://learn.chatgpt.com/docs/config-file/config-reference (`model_auto_compact_token_limit`, `project_doc_max_bytes`). Codex does have hooks; shipping an AFK pair for it waits until its event names and block format are checked against the Codex docs.
