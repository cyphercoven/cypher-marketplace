---
name: cypher-admin
description: "The one Cypher command. Use when someone types /cypher-admin, with or without a sub-command, to set up, start, go away, spec, design, deploy, build an app, hand over, troubleshoot, mirror, run media upkeep, handle secrets, work on ops, review or pick a workflow. Routes the first word to the matching cypher skill."
disable-model-invocation: true
argument-hint: [sub-command] [args]
---

# Cypher admin: one command, many sub-commands

PURPOSE: the `/` menu shows one Cypher command, `/cypher-admin`, so every sub-command is namespaced under it. This skill only routes; the work lives in the skill each row names.
CONVENTIONS: every `cypher-*` skill keeps its own name and stays loadable by the model (triggers, the gateway gate and the seat hooks look skills up by name). They are hidden from the `/` menu, not removed.
AGENT NOTES: `${CLAUDE_PLUGIN_ROOT}/scripts/check_skills.py` fails if a row is missing or points at a skill that does not exist.

## When this runs

It runs only when a person types `/cypher-admin`. The model never loads it by itself.

## Routing

`$ARGUMENTS` is the sub-command and its arguments. Take the first word as the sub-command, lower-cased, and pass the rest on as that skill's arguments.

| Sub-command | Skill | What it does |
|---|---|---|
| `setup` | `cypher-setup` | Ask a few short questions and write your Cypher project instructions |
| `start` | `cypher-start` | Sign in and check what you got |
| `afk` | `cypher-afk` | Away mode: work carries on, one morning report |
| `spec` | `cypher-spec` | Turn a braindump into a factory run |
| `design` | `cypher-design` | Design a screen, board or kit component |
| `deploy` | `cypher-deploy` | Deploy or tear down an app |
| `build-app` | `cypher-build-app` | Build a small app from kit elements |
| `handover` | `cypher-handover` | End this session and hand over to a fresh one |
| `troubleshoot` | `cypher-troubleshoot` | Find out what is broken and what to do next |
| `mirror` | `cypher-mirror` | Mirror merged design repos into the design artifacts |
| `media` | `cypher-media` | Media library upkeep and the NAS space check |
| `secrets` | `cypher-secrets` | Read or register a secret in the vault |
| `ops` | `cypher-ops` | Rules for changing the ops repo and its guests |
| `review` | `cypher-review` | Review or re-review a PR |
| `workflow` | `cypher-workflow` | Lane, gates and closing rules for Cypher work |

## What to do

1. No argument, `help`, `?` or `--help`: print the table above (sub-command and one line each, no Skill column) and stop. End with: "Legal research is its own command: `/cypher-legal`."
2. The first word is a sub-command in the table: load that skill with the Skill tool (or read its `SKILL.md` where the host has no Skill tool), then follow it with the remaining words as the request. Do not summarise the skill; do its job.
3. The first word is not in the table: say so in one line, print the table, and do nothing else. Do not guess the nearest match.
4. `afk` with extra words ("afk back at 8") passes them on as part of the message that turned away mode on.

## Related skills

Every skill in the table. Legal questions go to `cypher-legal`.
