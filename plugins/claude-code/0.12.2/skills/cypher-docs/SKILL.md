---
name: "cypher-docs"
user-invocable: false
description: "Load when documentation changes or a decision is recorded in any cypher* repo: STATUS.md, an ADR, README, CLAUDE.md, docs/agent, runbooks, vision or intent docs. Owns the docs split, last_verified sweeps, the README logo, docs commits, and when a factual fix needs no gate."
---

# Cypher docs: where words live and how they change

This skill owns the documentation rules DOC-01..DOC-04 (`rules/rules.yaml`). Code rules live in `cypher-dev`; lane and gates in `cypher-workflow`.

## When to load this

Load it when a doc is about to change or a decision is about to be recorded: STATUS, an ADR, a README, a CLAUDE.md, anything under `docs/`, or a vision or intent document. Do not load it for code-only changes.

## 1. The docs split (DOC-01)

| Place | Holds |
|---|---|
| `CLAUDE.md` | short rules for people and agents working in the repo |
| `docs/agent/` | context an agent reads on demand |
| `docs/adr/` | decisions, one per file |
| `docs/runbooks/` | procedures, step by step |

Do not blur them: a rule in a runbook, or a procedure in CLAUDE.md, is a bug. Put it where it belongs and leave a pointer.

## 2. STATUS and vision docs

- **`STATUS.md`** says what is true now: what shipped, what is unit-green but not deployed, what is next. Update it in the same commit as the work. It outranks ADRs, INTENT and SPEC when they disagree.
- **Vision and intent docs** (INTENT, SPEC) say where the work is going. They do not claim a thing is done.
- **Precedence when docs disagree:** the running system, then `STATUS.md`, then ADRs, then INTENT, then SPEC, then skills, then memory.

## 3. A factual fix needs no gate

A wrong higher source is a bug: fix it in a PR on the spot. Correcting a fact, a path, a count or a stale command is not a decision, so it skips the spec, design and UAT gates. A change of rule or of direction is a decision: it goes through the spec gate, and an ADR records it.

## 4. ADRs (DOC-04)

- Every ADR keeps a `Status` line: Proposed, Accepted, Deprecated or Superseded.
- A superseding ADR names the one it replaces, and the old one is updated to say so.
- Record the decision, the context and the consequence. Not the diary.

## 5. Freshness and presentation

- **`last_verified` (DOC-02).** Every user and agent doc carries a `last_verified` date. A quarterly sweep re-checks them and bumps the date only when the content was actually checked.
- **READMEs lead with the brand's horizontal logo (DOC-03).**
- **Prose-only changes are `docs(scope):` commits (DOC-04).** Doc-only changes do not need a plugin version bump (see the repo's CLAUDE.md for which paths count).
- No real hosts, internal URLs or vault item names in docs. Say where to look up the fact at run time.

## Related skills

`cypher-workflow` (precedence, gates, closing) · `cypher-dev` (commit format) · `cypher-spec` (the spec gate).
