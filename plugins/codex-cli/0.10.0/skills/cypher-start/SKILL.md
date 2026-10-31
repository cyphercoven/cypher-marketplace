---
name: cypher-start
description: Walks a person through signing in to the Cypher gateway and checking what they got, right after the plugin is installed. Use when someone has just installed the Cypher plugin and asks how to get started, how to sign in, or what to do first.
---

# cypher-start

PURPOSE: sign a freshly-installed person in and tell them, in a handful of
lines, who they are and what to do next — without stating a single infra
fact from memory. Every fact in the answer comes from a live gateway call.

## Steps

1. Call `onboarding` with `client` set to whichever client you are running
   in (`claude` or `codex`). It is read-only and safe to call with no
   other setup.
2. Read the result. It tells you: whether this person is signed in, what
   role (if any) they hold, what setup steps remain, and the next step
   for their specific client.
3. Answer in **10 lines or fewer**, covering only:
   - who they're signed in as (name/handle from `onboarding`)
   - their role, if any
   - what they can do today, in one line, drawn from what `onboarding`
     reports — not a guess
   - what they're waiting for: if `onboarding` reports no role, say
     exactly "ask a Cypher admin to give you a role in CypherOps" — do not
     speculate about what a role would unlock
   - the one next step `onboarding` names (e.g. finish a passkey step,
     or nothing further)

4. **First use (S-25).** Call `settings_get`. If there is no settings record,
   or it has no `answers_version`, finish with one extra line: "Want me to set
   up your Cypher instructions? Run `/cypher-setup` — it takes about eight
   short questions." If a record exists, say nothing about setup. If `settings_get` is unavailable, skip this.

5. **Changed instructions (S-21).** If a record with an `answers_version` exists,
   run `python3 scripts/update_prompt.py record --answers-version <that value>`
   (so the SessionStart hook, where the host has one, can compare without the
   gateway), then `python3 scripts/update_prompt.py check --answers-version <that
   value>`. If it prints a line, say it as your last line — it fires once per
   release. Say nothing otherwise.

## Rules

- Never state what a tool, host, or object is from memory. If
  `onboarding` doesn't mention it, you don't know it.
- If the gateway or `onboarding` is unreachable, say that plainly and
  stop — do not fall back to a guess about sign-in state or role.
- Keep the answer short. Ten lines is a ceiling, not a target — a person
  with no role needs three.
