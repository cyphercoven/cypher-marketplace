---
name: "cypher-dev"
user-invocable: false
description: "Load when editing, testing, committing or opening a PR for code in any cypher* repo. Owns the coding defaults: functional core, failing test first, affected tests only, commit and PR format, commit identity, never --no-verify, kit-only UI, and the file-header and shim rules."
---

# Cypher dev: how code gets written and shipped

This skill owns the dev rules D-01..D-14 (`rules/rules.yaml`). Lane, gates and heavy-step order live in `cypher-workflow`; documentation lives in `cypher-docs`. Facts about hosts or credentials come from the gateway's `knowledge` tool at run time, never from here.

## When to load this

Load it when code is about to change in any cypher* repo: a new function, a bug fix, a refactor, a test, a commit, a branch, a PR or a CI file. Do not load it for prose-only changes (use `cypher-docs`) or for a pure ops action on a running system.

## 1. Shape of the code

- **Functional core, side effects at the edge (D-01).** Pure functions hold the logic. Adapters at the boundary do the I/O.
  - Return a `Result` instead of raising; data is frozen.
  - No broad `try/except` inside the core.
- **Fix the cause, not the symptom (D-08).** Ship the proper fix, never the quick hack.
- **No aliases or compatibility shims (D-09).** Fix at source. Audit baselines only ratchet down.
- **Nothing is noise (D-10).** Every error is fixed. If it is genuinely harmless, re-tag or suppress it at source.
- **Every non-trivial file opens with a header (D-07):** `PURPOSE`, `CONVENTIONS`, `AGENT NOTES`. Match the file's existing comment style.
- **UI is kit-only.** Build screens from kit components and intent attributes, never raw colours, lengths or hand-written CSS. A gap is a kit request, not a local workaround. The full rules are in `cypher-design`.

## Language (D-15)

- **Backend is Rust.** Services, platforms, shared libraries and game or back-end logic are Rust crates, so shared libraries can be reused across every app.
- **TypeScript is for UI:** the cypherui kit and app front-ends.
- **Python only where no Rust option exists** (for example ML inference or training), and the spec names why.
- A spec that picks another language for backend work names the reason. A run never inherits a language from the code it is moving.
- Language rules live in references. Load the one that matches the files you touch:
  - `references/rust.md`: load when you touch `.rs`.
  - `references/typescript.md`: load when you touch `.ts` / `.tsx`.
  - `references/python.md`: load when you touch `.py`.

## 2. Tests

- **Write the failing test first (D-02).** Tests live alongside the code.
- **Coverage floor:** 80% global and 95% on pure core modules. CI measures it once on merge, not each round (owner ruling C-08, amended).
- **Run affected tests only.** That is the tests of every changed function, every caller that transitively imports a changed module, and the contract and integration tests of any changed adapter. Untouched pure functions are not re-tested. The per-language commands are in `cypher-workflow` §3.
- If a change cannot be traced (hidden global state, I/O inside a "pure" function), that is a boundary bug: fix the boundary, and test that module's whole dependent set meanwhile.
- **CI caches its dependencies (D-11).**

## 3. Git

- **Trunk-based (D-05).** Short-lived branches, one PR per slice, never force-push main.
- **Branch** `<type>/<KEY>-slug`. **PR title and commit subject** `<type>(<scope>): <subject>` (Conventional Commits), with the ticket key in the body (D-03, D-06; owner ruling C-06).
- **The commit body cites the doc or ADR that authorises a choice (D-03).**
- **A change ships with a version bump, a changelog line and its ticket key (D-12).**
- **Never `--no-verify` (D-04).** A hook error is fixed, not skipped.
- **Commit identity.** Commit with the identity the repo or the seat brief names. Never invent one. If a commit needs the owner addressed by name or pronoun, take them from the gateway's `knowledge` tool, and use `{{owner}}` / `{{pronouns}}` in anything written into a repo file.
- **Fetch and read against the remote before judging repo state (D-14).** A failing probe is investigated, not dismissed.
- **Edit repo files with the file tools (D-13),** not shell text round-trips that mangle UTF-8.

## Related skills

`cypher-workflow` (lane, gates, heavy steps) · `cypher-docs` (STATUS, ADRs, doc layout) · `cypher-design` (any UI) · `cypher-secrets` (any credential).
