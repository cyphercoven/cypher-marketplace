# API fallback mode (W-32)

Owner rule, 2026-11-09. Max (and Codex) usage is the default and only normal
path. The Anthropic API key is a **fallback**, used only when all of this holds:

1. **Out of subscription usage.** Claude Max is exhausted (limit message or
   `/status`), and Codex is too or can't do the task.
2. **Enough credit to finish.** Read the ledger `~/.config/cypher-api/budget`
   (remaining USD). Estimate the task's cost (Sonnet; turns × ~30k tokens).
   Start only if the estimate is clearly under the remaining balance. If it
   isn't, stop and tell the owner. Never start a task the credit can't finish.
3. **Switched on explicitly.** Run `cypherops/factory/bin/api-mode.sh on` in the workspace. It
   exports `ANTHROPIC_API_KEY` for new shells from the API key item listed in
   `cypherops/secrets/README.md`. The owner topping up and saying so also
   counts as "on" for the current session.

```
usage left? ─yes─► normal workflow (Max)
     │no
credit ≥ estimate? ─no─► stop, tell owner
     │yes
cypherops/factory/bin/api-mode.sh on ─► reduced workflow ─► log skips on the reconcile ticket
```

## Reduced workflow — delivery at the lowest cost

**Kept, always:**
- TDD: a red → green test for every code change, plus affected tests only.
- Security fixes, and security checks on anything secret, auth or exposed.
- Owner gates (spec · design · UAT). A gate can't be skipped; work that needs
  one waits for it.
- Worktrees, clean-check, never printing secrets, and the commit identity.

**Skipped, then logged:**
- Full review and independent UX review. Self-verify instead: lint, types,
  red → green and affected tests.
- Subagents, seats and fan-out; Factory Watch.
- Preview publish, design-board updates, screenshots and renders.
- UAT / installer builds, unless the owner asked for that build now.
- Plugin client adoption beyond the client in use.
- Docs beyond one line in `STATUS.md` and the CHANGELOG.

**Model:** Sonnet only; Haiku for reading and searching. Never Opus.

## The reconcile ticket

Keep one Plane work item per API-mode period: **OPS — "API mode reconcile —
<start date>"**, labelled `api-mode`. Create it if none is open. For every
piece of work done in API mode, add one comment:

```
<repo> · PR #<n> · <what shipped>
skipped: <steps from the list above>
cost: ~$<amount>  (ledger now $<remaining>)
```

At the end of each session, subtract the session's `/cost` from the ledger.

## When usage resets

1. Run `cypherops/factory/bin/api-mode.sh off`.
2. Run one reconcile session on Max from the ticket. Do every skipped step in
   order: full review first, then UX review, previews, UAT builds, client
   adoption and docs.
3. Close the ticket with the last line of clean-check.
