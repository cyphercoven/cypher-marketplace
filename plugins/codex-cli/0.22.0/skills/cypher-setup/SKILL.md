---
name: cypher-setup
user-invocable: false
description: Sets up the person's Cypher project instructions — asks a few short questions with answers prefilled, saves them, renders the instructions and says exactly where to paste them (or writes the file for you on Claude Code, Codex and Antigravity). Use when someone says /cypher-admin setup, "set me up", "update my instructions", or is new to Cypher.
---

# cypher-setup

PURPOSE: turn a person's answers into their Cypher instructions and put those
instructions where their AI provider reads them. Typed as `/cypher-admin setup`
(the `/cypher-admin` command routes to this skill). The arithmetic is in
`${CLAUDE_PLUGIN_ROOT}/scripts/setup_render.py` at the plugin root — run it, don't redo it by hand.
Run it as `uv run --with pyyaml==6.0.2 "${CLAUDE_PLUGIN_ROOT}/scripts/setup_render.py" <command> …`.

## Rules

- One question at a time, best option first, the prefill shown so the person
  only confirms or changes it. Eight questions at most; never invent extra.
- Say nothing about hosts, tools or accounts from memory — locations come from
  `host`, answers from `settings_get`.
- Never write a file without showing the target path and diff and getting a yes.
- If the gateway or `settings_get` is unreachable, say so and offer the full
  setup without saved answers; do not guess saved answers.

## Steps

1. **Find the saved record.** Call `settings_get`. Write it to a scratch file
   (JSON). No record, or no `answers_version` in it → first run: go to step 3.
2. **Re-run (S-17).** Run `setup_render.py mode --record <file>`.
   - `ask-keep` or `ask-keep-stale`: ask exactly ONE question — "Keep your
     previous answers, or run the full setup?" — nothing else first. (For
     `ask-keep-stale` add: "the template has changed since you last ran it".)
   - **Keep** → turn the record into answers (the `work_style` fields plus
     `owner_name` ← `display_name`, `pronoun_subject` ← the part of `pronouns`
     before the `/`, `providers`), skip to step 4. No further questions.
   - **Full** → step 3.
3. **Ask (S-15, S-40).** Run `setup_render.py questions [--record <file>]
   [--host-details <file>]`. Put anything the host already knows about the
   person (profile name, saved preferences) in the host-details file as
   `{owner_name: …}` so it prefills. For each returned question in order, ask
   it in one short line with the prefill offered ("Call you Alex? — enter to
   confirm"). The `providers` question is which of claude, codex, antigravity,
   copilot, cursor they use; accept several.
4. **Find the host (S-18).** Run `setup_render.py host --client <the client
   you run in>` (the same client names `onboarding` uses). If it returns no
   host, ask once which one they use. Keep the host `id` for the next steps.
5. **Save (S-16).** Run `setup_render.py record --answers <file> --host <id>`
   and pass its JSON to `settings_set` (fields: display_name, pronouns,
   work_style, providers, hosts, answers_version). Confirm in one line.
6. **Render and place (S-18).** Run `setup_render.py render --answers <file>`
   and show the output, then say the host's `location` exactly as returned.
7. **Write for them (S-19).** Only when the host reports `can_write_file`
   (Claude Code, Codex, Antigravity): run `setup_render.py plan --answers
   <file> --host <id> --existing <target path>`; show the target path and the
   diff; ask "Write this?"; write on yes, leave the file alone on no. If the
   file already holds other content, the diff is the proof — don't replace
   unrelated text without saying so.
8. Finish in three lines: what was saved, where the instructions went, and
   that `/cypher-admin setup` can be run again any time.
