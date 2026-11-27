---
name: "cypher-review"
user-invocable: false
description: "Load when a PR is opened, reviewed, re-reviewed or merged in any cypher* repo, when a spec is checked before building, or for independent UX readiness review of visual work. Owns risk-scoped verification, integrated feature review, evidence reuse, independent review before approval, and checking a spec's language against ADR-0078."
---

# Cypher review: which review a change gets, and what proves it

last_verified: 2026-11-27

For non-trivial plan, spec or implementation review, load `cypher-systems-thinking`. Check each proposed component and work item's goal trace, cited architectural principles, cross-boundary effects and complete-journey evidence; isolated component tests alone do not prove the system outcome.

This skill owns the review rules R-01..R-10 (`rules/rules.yaml`). How code is written is `cypher-dev`; the order of heavy steps and the gates are `cypher-workflow`; launching a review seat is `cypher-delegation`. Script names, caps and addresses come from the gateway's `knowledge` tool at run time.

## When to load this

Load it when a PR is about to be opened, a PR or branch is to be reviewed, a review finding is to be fixed and re-checked, or a PR is about to merge. Also load it when a spec is read before a build starts, to check its language choice.

Do not load it for writing the code itself (`cypher-dev`) or for launching a worker seat (`cypher-delegation`).

## 1. Pick the review scope and independence

Review effort and test scope scale with demonstrated risk. Scope is the affected change and boundary; do not equate a branch or PR with a reason for a fresh full-repository pass.

| Change | Review | Tests |
|---|---|---|
| Trivial fix with a red-to-green test, not on a dispatch, security or untrusted-parser path | author verification is sufficient | affected tests |
| Fix touching dispatch, identity/authorization, security, a shared predicate, untrusted parser, privileged write or sensitive-data flow | independent focused review of the diff and affected bug/threat class; specialist input when needed | affected tests plus callers/contracts in that class |
| Complete POC feature | one independent integrated pre-merge review of the complete feature against its approved journey, contracts, scope and evidence; no fixed reviewer count | affected tests and integration checks for changed boundaries |
| Epic production admission | independent whole-system assessment of intended outcome, integration, operations, recovery and risk, reusing valid feature evidence | uncovered interactions and evidence invalidated by integration/dependency/configuration changes |

- **When in doubt, broaden the affected boundary** (R-01). If impact cannot be bounded, record why and choose checks conservatively; do not automatically run every review category.
- Record review scope, reviewer, source/base/head, evidence reused and why, delta inspected, findings, and exact checks/outcomes.
- Affected tests are the tests of every changed function, every transitive caller, and contract/integration checks of changed adapters. If reach cannot be traced, fix the boundary or test the whole dependent set.
- A production fix is risk-triaged independently of the POC default for new-app feature development. Critical exposure and current-journey/security blockers are not deferred.

## 2. Evidence and delta review

For complex capabilities, use the [CypherUI](https://git.cypherwitch.com/cyphersuite/cypherui) guide at `docs/specialist-capabilities.md` to review the selection evidence and verify the complete user journey, including what loads on first use, visible loading and recovery, and resource cleanup.

- **Author verification:** show affected checks and red-to-green evidence where a test is added. This is not independent review for work above the trivial tier.
- **Focused review:** state the bug/threat class and demonstrate the other affected instances were checked. Include appropriate specialist security or architecture review when the changed boundary warrants it.
- **Integrated feature review:** reviewer did not implement the feature, checks the integrated diff against the approved plan and user journey, verifies scope and examines tests/evidence. Use specialists inside this review event when needed; no fixed agent count.
- **Fixes after review:** review the changed delta and relevant bug class, then rerun only invalidated/required tests or checks. Do not repeat the entire feature review or broad scan unless the fix changes the affected boundary or demonstrates a broader risk.
- **Epic admission:** assess the complete outcome and cross-feature integration using prior valid evidence. This is a systems-fit/readiness assessment, not a second line-by-line review of every feature.
- A finding-free report says what paths, behavior and risk class were examined. Failed, skipped, unavailable or uncertain checks are not passes.

## 3. Evidence remains independent

- **The implementer is not the independent reviewer.** Self-verification is allowed only for the trivial tier above.
- Verify source state from the actual worktree/disk and record commit context. A source excerpt, stale branch or model assertion is not evidence.
- Reuse evidence only while its relevant inputs remain unchanged: source/base/head, scope, environment/tool configuration, dependencies and external state. A new head records the delta and why earlier evidence still applies; never call ancestor evidence a new exact-head review.
- Unchanged passing tests/reviews stay valid. Changes to code, callers, contracts, dependency/configuration or relevant external state invalidate only the affected evidence. If impact is uncertain, expand with a recorded reason.
- Independent review precedes approval/merge when the tier requires it; attach its result to the existing PR/run record.

## Independent UX evidence for visual work

Visual changes also require the [independent UX review](../cypher-design/ux-review.md)
before owner design review or UAT. This is separate from code review and adds no
owner gate. A fresh reviewer exercises current complete flows and requested states,
reports severity and evidence, and rechecks fixes. No unresolved P0/P1/P2 findings
are handed to the owner; tests and the implementer's captures cannot substitute.
Use the supported Product Design audit capability where suitable, or the documented
native-browser review path when it is unavailable. Never claim unperformed checks.

## 4. Merging

- Seats open PRs; the orchestrator merges, once the tier is clean and the affected tests pass. Merging is not a gate and the product owner never opens a PR page.
- **Branch up to date before every merge (R-10).** Before any `forgejo_pr_merge`, fetch, then run `cypherops/factory/bin/pr-fresh.sh <repo> <pr>` (clean · behind · conflict):
  - **clean** → merge.
  - **behind or conflict** → in a worktree of the PR branch, `git merge origin/main`. Never rebase plus force-push: the safety check refuses force-push. Resolve any conflicts, push, re-run only the checks the merged-in change affects, then run `pr-fresh.sh` again.
  - **Conflict in STATUS.md** → keep both entries, newest first.
  - Evidence: on 2026-11-27 !1227 became unmergeable after another session prepended a STATUS.md entry.
- Merge with the branch deleted, and say what restarted.
- **Lane A/B merge path: `review.sh --checkpoint` (OPS-2314).** When the improve-checkpoint hook refuses a small Lane A/B cypherops PR (the reviewer brief lives in cypherops; other repos use the fallback below), get seat-recorded evidence; never write or record the review result yourself:
  1. Copy `cypherops/factory/templates/improve-context-ops.json` outside the repo; fill `lane: ops`, `applicability {reason, reference: <repo>!<pr>}` and `merge_target {repo, number, head}`; bind it to your session (`improve_checkpoint.py bind`).
  2. Run `review.sh <worktree> <pr> <log> --checkpoint <context.json>`. One review seat reviews the impacted paths, writes the result with its seat attestation and records it; `record` refuses a result from the bound session or the implementer.
  3. Merge from a session on the same host as the worktree and evidence (the hook reads them locally).
- Only if the seat cannot run, or the host still refuses the merge, follow the refusal paragraph in `cypher-workflow` §2 (one ask, "merge them"); never self-approve.
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
Scope: <author-check|focused-review|integrated-feature|epic-readiness> — <why this scope>
Evidence: <base/head, delta, reused evidence, affected checks and exact outcomes>
Reviewer: <independent reviewer when required; otherwise author verification>
Result: <findings fixed or explicitly deferred, and what was checked>
```

## Edge cases

- **Required evidence is missing, stale, unavailable or failed.** Treat the checkpoint as blocked; repair or rerun only affected evidence. Do not rerun a broad review solely because of reviewer count, and never merge or admit production on a failed checkpoint.
- **A finding arrives after merge.** Open a fix PR through the same tier choice; do not amend the merged change.
- **The tiers disagree with a repo's own CLAUDE.md.** The repo's rule wins in its repo; report the difference so it is ruled on.
