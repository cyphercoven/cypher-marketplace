<!-- templates/project-instructions.md
PURPOSE: the suite's project instructions with every personal fact as a {{variable}}.
CONVENTIONS: {{name}} substitutes; {{#if name}}...{{/if}} keeps a span when the answer is truthy.
  Variables are declared in variables.yaml; scripts/render_template.py renders (S-14).
AGENT NOTES: derived pronouns / pronoun_object / pronoun_possessive come from `pronoun_subject`. S-50: this file holds
  identity, working style and pointers to skills only. A rule goes in the skill that owns it (rules/rules.yaml),
  never here; `python3 tools/rules_audit.py --template` must report 0 rule lines. -->
You are working in the **Cypher Suite** — one project for every `cypher*` repo. They live as siblings in one Coder workspace, and most work crosses repos.

## Purpose

{{owner_name}} is the {{owner_role}}. {{owner_name}} braindumps, approves specs and designs, and tests builds in a preview; {{pronoun_possessive}} gates are **{{gates}}**. Everything else is yours to do.

## Working style

- {{owner_name}} uses {{pronouns}}.{{#if previous_name_rule}} Never call {{pronoun_object}} by a previous name or put one in anything an agent writes; stored historical records keep the name as it is.{{/if}}
- {{answer_style}}
- A cross-repo run session is named `{{session_name_prefix}}: <slug>`; the naming rule is in `cypher-workflow` §0.
- User preferences (claude.ai Settings › Profile): Clear step by step instructions; start with the best option, alternatives only if the first fails; {{pronouns}}{{#if previous_name_rule}}; never {{pronoun_possessive}} previous name{{/if}}. Session names prefixed with the project name.

## Load the skills — every session, before any work

| Skill | Load when |
|---|---|
| `cypher-workflow` | **First, always.** Any cypher* work: it picks the lane and the gates and owns the standing rules for how work runs |
| `cypher-spec` | A braindump, "spec this", or any new factory run (gate 1) |
| `cypher-design` | Any UI, screen, board, component, icon, avatar or brand work (gate 2) |
| `cypher-dev` | Editing code, tests, commits or PRs in any cypher* repo |
| `cypher-docs` | A doc changes or a decision is recorded: STATUS, ADRs, READMEs, docs/ |
| `cypher-mirror` | A merge whose plan says `will_mirror` — before closing the session |
| `cypher-secrets` | Any key, token, password or credential |

## How to navigate — read, don't recall

| Question | Read |
|---|---|
| What exists today | `STATUS.md` in every repo the task names |
| Where it's going | cypherwitch `docs/vision/<component>.md` (published on the docs site) |
| How to get into the workspace, and the dead ends | `cypherops/docs/agent/reaching-the-workspace.md` |
| How a run is described, dispatched and gated | `cypherops/factory/README.md` + ADR-0054 + ADR-0072 |
| Why a decision was taken | `cypherops/docs/adr/` |
| Who {{owner_name}} is and how to work with {{pronoun_object}} | cyphercore `sections/` |
| Working context left by earlier sessions | this project's memory — working context only, never system facts |
| Which source wins when docs disagree | `cypher-docs` §2 |
