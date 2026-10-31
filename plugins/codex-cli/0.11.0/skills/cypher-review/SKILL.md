---
name: "cypher-review"
user-invocable: false
description: "Load when a PR is opened, reviewed, re-reviewed or merged in any cypher* repo, or when a spec is checked before building. Owns the ADR-0072 review tiers (full, scoped, self-verify), the evidence each tier needs, independent review before approval, verifying on the real disk, and checking a spec's language against ADR-0078."
---

# Cypher review: which review a change gets, and what proves it

This skill owns the review rules R-01..R-09 (`rules/rules.yaml`). How code is written is `cypher-dev`; the order of heavy steps and the gates are `cypher-workflow`; launching a review seat is `cypher-delegation`. Script names, caps and addresses come from the gateway's `knowledge` tool at run time.

## When to load this

Load it when a PR is about to be opened, a PR or branch is to be reviewed, a review finding is to be fixed and re-checked, or a PR is about to merge. Also load it when a spec is read before a build starts, to check its language choice.

Do not load it for writing the code itself (`cypher-dev`) or for launching a worker seat (`cypher-delegation`).

## 1. Pick the tier (ADR-0072)

Review effort and test scope scale with the risk of the change. The tier is a ceiling on effort, never a floor.

| Change | Tier | Review | Tests |
|---|---|---|---|
| Trivial fix with a red-to-green test, not on a dispatch, security or untrusted-parser path | self-verify | the orchestrator's own verification is the gate; no review seat | the affected tests |
| Fix touching dispatch, security, a shared predicate or an untrusted parser | scoped | the diff and that one bug class, not a fresh-exploit sweep | the affected tests |
| A feature slice, or the first review of any PR | full | the full factory review | the affected tests |

- **When in doubt, review more (R-01).** Misclassifying down is the failure to guard against. If you cannot say which tier a change sits in, take the next one up.
- **Record the tier.** Every round report names the tier used and why.
- **Affected tests** (the amendment of 2026-10-25) replace the full suite as the pre-merge gate: the tests of every changed function, of every module that transitively imports one, and the contract and integration tests of any changed adapter. A change whose reach cannot be traced is a boundary bug to fix; test its whole dependent set meanwhile.

## 2. Evidence each tier needs

- **Self-verify (R-02).** All four, shown in the report, not asserted:
  1. the linter is clean
  2. the type checker is clean
  3. a test that fails before the fix and passes after (name it, paste both results)
  4. the targeted tests are green

  This removes a second agent re-deriving evidence; it does not remove the evidence. The attestation check still runs. The check output and the red-to-green result go in the PR itself (ruling C-09); a change outside the trivial tier gets a separate reviewer seat, whatever its size.
- **Scoped (R-03).** Name the bug class (for example "every caller of this predicate" or "every parser path that reads this field"), run the review with the scoped switch set, and show that the other instances of the class were checked too, not only the path where it was found. An invariant fixed in one path only is the recurring failure.
- **Full (R-04).** The full factory review needs at least four review subagents. If it cannot start them, the script reports a degraded run and that is a failure, never "no issues". Run it from a worktree of current main so the script does not refuse a stale copy. Run it once per feature slice or first PR review, not per fix round.
- **A review that found nothing says what it checked.** "No issues" with zero agents run is not a review.

## 3. Review is independent

- **The implementer is never the reviewer (R-05).** A review seat is a fresh session that did not write the change, and the orchestrator does not assess its own output. Self-verify is the only place the author's own evidence is the gate, and only for the trivial tier above.
- **Verify on the real disk (R-06).** Confirm a file's state with the Read tool, not with a grep across a mount or a remembered listing. A conflict that shows in only one of the two views is a stale view; trust the file.
- **Sweeps escalate (R-07).** A scoped, per-commit sweep of the affected stories or pages is allowed for small strokes. Any sweep that finds a problem outside its scope escalates automatically to the full sweep. Do not pay the full sweep for a one-line change, and do not skip the escalation when it is earned.
- **Independent review precedes approval.** Nothing is approved on the implementer's say-so, and the review result is attached to the PR before it merges.

## 4. Merging

- Seats open PRs; the orchestrator merges, once the tier is clean and the affected tests pass. Merging is not a gate and the product owner never opens a PR page.
- Merge with the branch deleted, and say what restarted.
- If a merge plan says it will mirror the design system, load `cypher-mirror` before closing.
- Fix a stale doc the review turns up in the same PR when the correction is factual.

## 5. Raise new patterns while the work happens (R-08)

When a review or a build shows a pattern that is not yet a rule (a new check, a naming habit, a recurring gap), raise it as a proposed rule while the work is happening, as one short note that quotes the evidence. Do not apply it silently, and do not block the work on it. The product owner approves rules at the next gate; until then the pattern is only a proposal. A new UI pattern is not a separate approval step (ruling C-10): it is filed as a kit request (`cypher-design` section 5) and judged at the design gate.

## 6. Check the spec's language before the build (R-09)

When a spec is read, check its language against ADR-0078:

| Part | Language |
|---|---|
| Back end: services, platforms, shared libraries, game logic | Rust |
| UI: the kit and app front-ends | TypeScript |
| Anything else | Python only by a named exception: no Rust option exists, and the spec says why |

- A spec that names another language for back-end work, without the named reason, is wrong: send it back with the rule quoted. Do not start the build and do not choose silently.
- A run never inherits a language from the code it is moving. A port to Rust is in scope when the spec says so.
- If the ADR file is not yet on main in the repo you can read, say so and use `cypher-dev`'s language rule (D-15), which carries the same text.

## Report format

```
Tier: <self-verify|scoped|full> — <why this tier>
Evidence: <lint, types, red→green test, affected tests, with results>
Reviewer: <fresh seat or orchestrator-verified>, agents run: <n>
Result: <findings fixed | none, and what was checked>
```

## Edge cases

- **Review script returns a degraded result.** Treat it as failed; re-run from a fresh worktree of current main. Never merge on it.
- **A finding arrives after merge.** Open a fix PR through the same tier choice; do not amend the merged change.
- **The tiers disagree with a repo's own CLAUDE.md.** The repo's rule wins in its repo; report the difference so it is ruled on.
