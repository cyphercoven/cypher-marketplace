---
name: "cypher-workflow"
user-invocable: false
description: "Load FIRST for any work on the Cypher Suite or any cypher* repo — picks the lane and gates, uses affected checks and lifecycle review checkpoints without duplicate passes, leaves every repo clean (clean-check before done), and suggests a fresh session with a handover."
---

# Cypher workflow — how any piece of work gets built

last_verified: 2026-11-28
Before non-trivial planning or task breakdown, load `cypher-systems-thinking`. Its goal trace and documented-principle map belong in the existing spec/plan; revisit them at slice boundaries and when evidence changes. Every proposed component and work item must show its contribution to the underlying system goals.

The product owner is the product manager. They braindump and approve at **spec · design where visual · demonstrated POC acceptance before refinement · production UAT where visual**. Do not ask twice for the same milestone. You do everything in between — branches, PRs, review, merge, deploy, credentials, cleanup — autonomously, and you spend the product owner's Max usage as if it were scarce, because it is.

Precedence when docs disagree: the running system > `STATUS.md` > ADRs > INTENT > SPEC > this skill > memory. A higher source being wrong is a bug: fix it in a PR on the spot (factual fixes need no gate). Single source: this plugin skill; the cypherops copy `docs/agent/cypher-workflow.md` is a generated pointer to it.

**On your host:** read `hosts/<your host>.md` beside this file (one file per host) for the steps only your host can do — scheduling, artifacts, project docs.
**Server routing:** all NEW SERVER implementation, testing and independent review agents default to common Orca entry `factory/bin/agent-dispatch.py` with healthy ContextMode; managed unavailability refuses dependent work and never silently falls back to raw/native server implementation. Desktop orchestration, planning, delegation and provider authentication remain native; gateway operator operations remain direct. Read `cypher-delegation` and its Orca reference for exact one-off Ask, admission, separate readiness/execution budgets, accepted receipts and owned cleanup. Existing gates, owner AFK/no clock cutoff and actual review independence remain mandatory.

**Golden rule — the most efficient path, same quality (W-31).**
- Before starting, and again whenever a step is about to repeat (a second build, re-review, re-run, another loop round), stop and ask: *is there a path that gives the same quality in less time or fewer tokens?* Use the tools already built for fast iteration first (live previews, HMR, affected-only tests, scoped review); keep the heavy path (full builds, pinned releases, full review, UAT) for once at the end (§3).
- Never cut a corner to get there: same evidence, same gates, same review tier.
- If a loop has gone round twice, write one line in the reply naming the cheaper path you considered and why you did or didn't take it.

## 0. Every session, before anything

1. Name the session `<App/Service>: <name>` — e.g. `CypherFlix: music import`, `CypherOps: cert renewer`. A cross-repo factory run is `Cypher: <slug>`.
2. Chat hosts (no workspace shell): first gateway call `session_begin {label, client_session, surface}`; pass `session` on every call; say the id in your first reply. If a later call says the session is unknown or expired, call `session_begin` again. If the gateway goes down (502, refused, timeout), follow standing rule 3 in §2: assume another session is deploying it, wait 2 minutes, retry.
3. Read `STATUS.md` in every repo the task names. Read, don't recall.
4. Pick the lane below. Say it in one line ("Lane C — POC-first factory run, staged owner gates").
5. Load the other skill the work needs: `cypher-ops` (any change in cypherops or on a running guest) · `cypher-spec` (a braindump or new factory run, gate 1) · `cypher-design` (any UI, screen, board, component, icon, avatar or brand, gate 2) · `cypher-secrets` (any key, token, password or credential).

**This skill is the project's rulebook.** Host project instructions only say "load cypher-workflow first"; every standing rule lives here or in the skills above, so a rule change is a change to this skill, never an edit to a host's instructions.

**Where to read — read, don't recall**

| Question | Read |
|---|---|
| What exists today | `STATUS.md` in every repo the task names |
| Where it's going | cypherwitch `docs/vision/<component>.md` (published on the docs site) |
| How to get into the workspace, and the dead ends | `cypherops/docs/agent/reaching-the-workspace.md` |
| How a run is described, dispatched and gated | `cypherops/factory/README.md` + ADR-0054 + ADR-0072 |
| Why a decision was taken | `cypherops/docs/adr/` |
| Who the product owner is and how they work | `knowledge` (the gateway tool), never memory |
| Working context left by earlier sessions | host project docs and memory — working context only, never system facts |

**Standing rules about the product owner**
- Use the name and pronouns the product owner's profile gives (`knowledge`). Never use a previous name, even if found in old documents, memory or history; remove any trace without asking and say where it was.
- Short answers, the next action first, one option, a diagram where shape matters.
- Claude factory seats run on the Max subscription: never an API key, the Agent SDK, `claude --bare` or a third-party harness. Other hosts use supported native delegation; see `hosts/codex.md`. New managed server work uses the [bounded Orca path](../cypher-delegation/references/orca.md), preserving native subscription CLI permissions and existing gates.
- **One exception — API fallback mode (W-32):** only when subscription usage is exhausted AND the API credit ledger covers the whole task, switch on with `cypherops/factory/bin/api-mode.sh on` and follow the reduced workflow in [api-mode.md](api-mode.md): TDD and gates kept, heavy steps skipped and logged on the one OPS "API mode reconcile" ticket for backfill when usage resets. **Second exception, the `claude-console` route (S-05):** an owner-approved standing route that runs managed Orca workers on the Console API credit through `agent-dispatch.py --route claude-console` only. It is separate from W-32. Read its limits in [console-route.md](console-route.md) before use: credit only, and not usable until S-33 has passed and the S-06 isolation is in place.

**Standing design rules**
- One canonical Design board per product, created the first time we design for it and updated after that, never duplicated.
- All component work happens on the single "CypherUI Components" canvas, which the Design System links to (the Design System holds no component cards).
- Delete a gate board as soon as its ticket closes.

**Data lives in a database**
- People, profiles, roles, permissions, settings and every other piece of user or app data live in a database, so they change without a PR, build or deploy. Git holds code, schema, infrastructure and machine principals only — never user data, and no runtime data files standing in for a table.
- Every data operation writes an audit row in the same database, in the same transaction as the change (actor, time, reason, exact before and after), so any change can be reverted from it.

**Do it properly, first time — for all work**

```
problem ─► root cause, with evidence ─► how is this done properly? (real references, assets, known technique)
        ─► build THAT ─► verify ─► done
                 ✗ never: quick patch ─► see what breaks ─► patch the patch ─► … ─► "the proper fix"
```

- **The first fix is the proper fix.** Before any change, name the root cause and the established way to solve it, in one line each, then build that. A workaround, heuristic or "let's see if this works" tweak is never the opening move.
- **No guessing.** Build from real references, real assets and documented techniques (research first, cite them). If you don't know the proper way, find out *before* building, or ask the owner one question. Don't iterate towards it at their expense.
- **Two strikes, then stop.** If a second change to the same symptom hasn't fixed it, stop changing things. Diagnose with evidence (debug renders, logs, a minimal repro), write down the root cause, and only then continue, with the proper design.
- **Never announce "the proper fix" after the fact.** If you know a proper fix exists, that is the one you build. A cheaper or weaker option is allowed only when the owner chooses it, after you've told them plainly what it costs.

## 1. Pick the lane

```
                 ┌─ factual fix / one-liner ────────────► A  Quick fix      (no gate)
task ──► what? ──┼─ ops action on a running system ─────► B  Ops            (no gate*)
                 ├─ new feature / anything with clauses ► C  Factory run    (spec · design? · UAT?)
                 └─ look-and-feel of kit or a screen ───► D  Design loop    (design gate)
```

| Lane | Path | Gates |
|---|---|---|
| **A Quick fix** | worktree → branch → red→green test (if code) → PR (`plane: none — <why>` or `refs KEY`) → self-verify → merge | none |
| **B Ops** | gateway tools; hot-fix only if needed, then backfill IaC in the same session | none — except *ask first* (§2 *Owner standing rules*): an irreversible delete; anything that could cut the house internet; and, when AFK is off, anything that causes downtime for a live user-facing service (a public-set restart — list: `knowledge {topic: "workflow-ops"}` — or a downtime window: quote when, how long, what). AFK on pre-approves that last one. |
| **C Factory run** | `cypher-spec` → Plane epic Approved → phase-labelled `PLAN.md` → `cypher-design` if visual → POC implementation → technical checks/independent review → POC merge/deploy/adopt usable demo → owner POC acceptance → refinement/production only when dispatched after that acceptance → integrated release review → merge/deploy → production UAT or auto-close | **spec**; **design** if visual; **POC acceptance** before refinement; **UAT** if visual |
| **D Design loop** | `cypher-design`; preview the kit on the preview service (path procedure: slice 2, pending); batch their comments | design |

Not sure between two lanes → take the heavier one. Not sure whether a run is visual → leave the epic open and ask.

## 2. Autonomy — what is yours, what is theirs

**Yours, never asked:** opening and merging PRs (after the review tier below is clean), deploying, creating and updating vault items and credentials through the gateway (`cypher-secrets`; delete is ask-first), creating Plane items, managing your own scheduled follow-ups (standing approval — see your host file), fixing stale docs, rolling back something you broke, running UAT for agent-facing tooling (an independent tester seat that sees only the SPEC's "Done looks like"). Cost never needs their nod: the guard is the per-seat token cap (`cyphercore/sections/delegation-rules.md`).

**Merging never needs the product owner's approval** (owner, 2026-11-06). Once the review tier is clean, merge — kit and design-system PRs included. The only exception is a merge that is itself the step of a UAT gate the product owner has not already pre-approved in chat; that one waits for the UAT answer. Record the review evidence on the PR (tier, agents, red→green, checks) before merging. **Before every merge, bring the branch up to date (R-10):** fetch, run `cypherops/factory/bin/pr-fresh.sh <repo> <pr>`; if it is behind or conflicts, merge origin/main into the branch (never rebase plus force-push), resolve (STATUS.md: keep both entries, newest first), push, re-run only the affected checks (`cypher-review` §4). **Merges work from any session (OPS-2314, 2026-11-27).** The gateway's `forgejo_pr_merge` is the merge authority for every caller on every host: it runs the checkpoint `merge-check` in the Coder workspace, where the review seat wrote its evidence, and the local hook defers merges to it. If a merge is refused for missing evidence, take the automatic route: `review.sh --checkpoint` (`cypher-review` §4) — the review seat records epic-planning, plan and feature-review itself; never record a review yourself. If the process was followed (independent review done, checks green) and the refusal is a fault in the hooks, plugin or gateway tooling, override it yourself with the gateway's `forgejo_pr_override` (standing rule 5), which merges; file the tooling fault on the run's ticket. Never ask the owner to merge, and never ask them to open a session for you. Never post an APPROVE review from the account that opened the PR — Forgejo refuses it and the host blocks it as self-approval.

**Theirs, one question per gate:** spec (one board), design (canvas, if visual), demonstrated POC acceptance (one usable demo after the POC feature review), and production UAT (one installable build incl. Linux — never a CI zip — plus `UAT.md`, if visual). POC acceptance is a separate owner checkpoint; passing tests/review does not approve it. Do not ask again for the same milestone. Plus the B-lane "ask first" items. Never hand them a PR link, a script, or a step you could do. A new UI pattern is not a fourth gate: file it as a kit request and it is judged at the design gate (`cypher-design`).

### Owner standing rules (owner, 2026-11-12)

These are approved already. Every session follows them without asking; the owner should never have to repeat one.

1. **Standing pre-approval (W-22).**

   | Mode | Do it, no ask | Still ask first |
   |---|---|---|
   | AFK on (`cypher-afk`) | Set up, merge, apply or deploy anything that can be rolled back and cannot take down the house internet. Includes gateway/utils restarts, Ansible applies, new databases and migrations, live test data, test identities or invites sent to the owner's own catch-all domain, and public-service restarts. | An irreversible delete. Anything that could cut the house internet: the Flint router's WAN, DNS or DHCP (`flint_*`), the sw-core switch uplink (`switch_*`). |
   | AFK off | Deploy anything that does not create downtime for a live user-facing service. | The same two, plus anything that causes downtime for a live user-facing service. |

   "Irreversible" means it cannot be brought back: deleting data, a guest, a backup, a repo or a vault item. Killing a stuck job or restarting a container is reversible.
2. **AFK never ends in "start a fresh session".** While AFK is on, never tell the owner to start a new or fresh session. The AFK token cap means compact and carry on in this session, not stop. The `cypher-handover` suggestion does not apply while AFK is on (`cypher-afk` §3).
3. **The gateway goes down mid-session (W-33).** First assume another session is deploying it. Wait 2 minutes from the failed call, then retry (`session_begin` again if the session is unknown). Still down → investigate: first the notes of other active sessions (their `~/scratch/<run>/HANDOVER.md`, `session_list`), then the break-glass routes in `cypherops/docs/agent/reaching-the-workspace.md`. If another session deployed or changed the gateway recently, leave the fix to that session so there is no competing work; carry on with what does not need the gateway.
4. **A refusal blocks one action only (W-34).** A safety-check, permission or classifier refusal blocks only that exact action. Take a safer equivalent route (for a tooling fault: standing rule 5), or, only when it touches a gate, the public-facing media stack or the house internet, record it (AFK: the morning report queue) and carry on. Never turn one refusal into a question about other, unblocked work. **Asking for something these rules cover is itself a rule break (W-35).** Before any ask, check: is it a gate (spec, design, POC acceptance, UAT), an irreversible delete, a house-internet change, or (AFK off) downtime for the public-facing media stack? If none of these, do it.
5. **The owner is the authority; tooling faults are overridden, not escalated (W-44, owner 2026-11-27 22:01).** Work stops, and the owner is bothered, only at a gate, for something that affects the public-facing media stack, or for something that affects the house internet. When a check refuses and none of those apply, the process has been followed (independent review recorded, required checks green) and the refusal is a bug in the hooks, plugin, gateway or factory tooling, merge with the gateway's `forgejo_pr_override` (`kind: agent`, the exact repo/PR/head, the reason and the evidence) and carry on; open or update the fix ticket for the tooling bug in the same turn. Any other refused check: take the guarded route (rule 4) and ticket the fault. The owner can override a merge herself from any session: call `forgejo_pr_override` with `kind: owner` and she accepts the gateway's approval prompt. Overrides are kept by the gateway, one-shot, expiring and audited; open gates (spec, design, POC acceptance, UAT) are never overridden. **Away mode keeps going on every host (W-45, owner 2026-11-27 22:02):** on a host without hooks, a turn that ends with AFK on and runnable work left first arms a continuation into this same session (`cypher-afk` §3, your host file) — never end on "nothing needed tonight" while work remains.

### Continue through interim questions

An interim question, status request, correction or clarification does not end the active task. Answer briefly in commentary, incorporate the response, then ALWAYS continue any outstanding authorised work without waiting for another ‘go’. End the turn only when the requested outcome is complete, the user explicitly stops or replaces the task, or a genuine blocker requires user input. Continue independent work when one part is blocked. Never imply work continues after a final response unless an actual supported runner is active.

Existing approval, authorization and safety boundaries remain: a pending gate blocks dependent work, while independent authorised work continues.

### When you're waiting on them — the ask goes last

Any message that leaves the work blocked on the product owner (a gate, or a B-lane "ask first") ends with the ask as its **last paragraph**, so they never scroll up to find it. Nothing after it — no tool call, no sign-off.

```
**Gate <1 spec | 2 design | 3 UAT | ask first> — <what it's for>.**
<What they do, in one or two lines: where to look (link), what to answer.>

**YOUR INPUT NEEDED**
```

Example:

> **Gate 2 design — CypherFlix music import screens.**
> Open the [CypherFlix design board](<link>) and reply *approve*, or say what's wrong.
>
> **YOUR INPUT NEEDED**

Only when you are actually blocked on them — never on progress or merge reports.

When the turn ends with nothing waiting on them but work still going (seats, a factory run, a build, a background job, or a check-in still to fire), the last line says so instead:

```
**Nothing needed from you** — <what's running> · <when it should land, or what wakes this session>.
```

Every turn that ends on them therefore ends on one of the two lines. The handover message (§4) is the one exception: it ends exactly as written there. **Done says whether the session can be archived (W-43, owner 2026-11-27):** every *done* or closing report states, as its own line, either `**Session: can be archived**` (clean-check exits 0, nothing merged, scheduled or waiting needs this chat) or `**Session: keep open** — <what is still owed here>`. Never leave the owner to work it out.

**Migrations:** plan a quoted downtime window, not zero downtime. State when, how long and which services; when it takes a live user-facing service down and AFK is off, get explicit approval first (AFK on: pre-approved if it can be rolled back, standing rule 1); a migration with no user-facing downtime needs no ask. Prefer simple to clever. With IaC the default is stop → swap → start (announce, `down` the old, `apply`/`up -d` the new, verify). Use a crossover only when the service cannot tolerate the window.

Report progress by usable owner journey, not internal task counts: what works now, where/how to try it, blockers and explicitly deferred scope. Tests/reviews are supporting evidence. Record time/token cost to first usable POC only when measured. Report merges as: what shipped · what restarted (`will_restart`) · what's next.

### UX readiness is an internal check

For visual work, complete the design skill's [independent UX review](../cypher-design/ux-review.md)
before owner design review or UAT. Code review is separate. Fix shared causes and
recheck affected flows; no unresolved P0/P1/P2 findings are passed to the owner.
This adds no owner gate and never bypasses explicit exception approval.

### Changing a file

| Who | Change part of a file | New file / whole rewrite | Find · list · read |
|---|---|---|---|
| Chat host (through the gateway) | `workspace_edit` — pass `if_sha256` from your last `workspace_read`; `edits` for several changes at once | `workspace_write` | `workspace_grep` · `workspace_glob` · `workspace_read` with `offset`/`limit` |
| Seat (Claude Code in the workspace) | Edit | Write | Grep · Glob · Read |

Never `sed -i`, `perl -i`, a heredoc / `cat >` / `tee`, or a python read-modify-write on a tracked file — seats are blocked by a hook (`factory/hooks/no-shell-rewrite.py`), and a session has no excuse either. If a connector's tool list is stale and has no `workspace_edit` yet, `workspace_read` then `workspace_write` the whole file — never the shell.

## 3. Checks follow the lifecycle; reuse valid evidence

Run cheap affected checks during implementation. Run each required planning, integrated feature-review and production-readiness checkpoint at the transition it guards; do not duplicate the same review at task and final stages. Reuse passing evidence while its relevant inputs remain valid, and refresh only evidence invalidated by a code, dependency, environment, contract or risk change.

### Planned milestone order: POC first, then iterate

Follow the approved plan's milestone order; do not invent or silently reorder work. Specs split work from the outset into separately accepted POC, refinement and production phases, each with sharp acceptance and deferred boundaries. For new-app feature development, default the first milestone to the smallest working end-to-end POC that tests the key journey and its architectural assumptions. Build and demonstrate a usable POC, then wait for the owner's explicit POC acceptance before dispatching any refinement or production work; successful checks/reviews do not imply acceptance. Later phases may be outlined but remain undispatchable until that acceptance is recorded. Keep independent POCs moving and available for owner use/testing; do not force immediate refinement. A later authorized refinement run may batch work across multiple approved POCs, referencing their acceptance evidence. Use composable functional core and side-effect adapters, define contracts at real boundaries, and avoid speculative abstractions. Production fixes retain risk-aware triage; use a POC only when isolated and representative. A POC is a milestone, not production admission.

**SECURITY, REAL-DATA SAFETY, AND CURRENT-JOURNEY BLOCKERS ARE FIXED NOW.** POC acceptance is a separate owner gate after the usable POC is demonstrated, not a technical auto-pass or production UAT. Other nonblocking edges may be deferred with evidence, category, owner, and revisit condition in the existing backlog. Do not interrupt the POC journey for deferred edges. Never defer unsafe isolation, authentication/authorization, secret handling or real-data protection for actual exposure; never present unresolved production gaps as done.

Only undertake independent later-milestone work when the current milestone is genuinely blocked and that work cannot help unblock it. Record the blocker and exact return point, then return to the approved order as soon as it clears. The orchestrator owns this ordering and gives each delegated brief the current milestone, journey acceptance, exact scope, relevant plan/evidence and deferred-work boundary.

Contract-first work, existing product gates and required security/review checks before merge or live admission remain mandatory. Record milestone completion against its stated acceptance. Contain a demonstrated active incident or prevent an unsafe check with the minimum necessary exception, record why, then resume the planned order.

### Full journey first, then batch fixes

For multi-part implementation or integration, complete the current milestone's acceptance journey before local fix-and-verify loops. Keep one findings list, fix security and journey blockers immediately, and batch eligible deferred fixes by shared cause and dependency. A full journey pass is not a blanket run of unrelated test suites.

1. Exercise the current approved scenarios and real user journey; record failures, missing pieces, evidence and blocked checks. Continue through the remaining current-milestone scope. A blocked check is not a pass.
2. Keep findings in the existing run backlog. Do not recursively expand one component or reopen valid evidence without an acceptance failure, relevant drift or changed dependency.
3. At the planned fix stage, group findings by cause and dependency. Run affected checks after each change and a consolidated acceptance pass for the changed journey.
4. Report working scenarios, blockers and deferred items with owners, not module, commit or test counts.

Planning and evidence checks are automatic. The separately demonstrated, owner-approved POC is an explicit owner gate before refinement; it is never inferred from tests or review. Before the spec gate, record systems-thinking and risk assessment in the current spec/plan. Before production readiness or admission, independently assess whole-epic fit, integration, operations, recovery and risk. Reuse valid feature evidence; check uncovered interactions and invalidated inputs. See cypher-improve for the guarded checkpoint interface. Neither assessment replaces existing spec, design or UAT gates.

| Check or artifact | Avoid | Run or publish |
|---|---|---|
| Preview publish | from a worker seat, between comments, or to see whether something changed | after the last change of the set merges |
| Independent integrated feature review | per subtask and again in a duplicate full pass; by the implementer | once per complete POC feature before merge; use the risk-appropriate review scope and specialist input where needed |
| Tests | the full suite by habit | affected tests for each change and consolidated checks for the current journey; reuse unaffected passing evidence |
| UAT / installer build | per fix, as interim proof | once after known fixes are in and required checks pass |
| CI | on every push | PR open (tests) and merge (build), under current repo policy |
| Screenshots / renders / image batches | while changes are queued or known mistakes remain | after the last queued change |
| Test runs | partial or interim | the planned affected tests, with all their parts |

Order inside a run:

    epic-planning assessment -> existing spec gate -> plan -> design (if visual) -> existing design gate
    -> POC tasks on the feature/run branch + affected tests
    -> one independent integrated feature review -> POC merge/deploy/adopt usable demo -> explicit owner POC acceptance recorded
    -> later authorized targeted improve audits + refinement plans across approved apps -> affected implementation/checks
    -> final whole-epic production-readiness assessment -> deploy/admit -> existing UAT gate where visual -> close

Do not open a separate PR/review for each delegated task when tasks compose one feature. Record each task's scope and evidence, integrate on the feature/run branch, then review the complete feature once. After review fixes, independently assess the changed delta and relevant bug class; rerun only invalidated or required checks. This does not remove specialist security, architecture or UX evidence when risk or the visual gate requires it.

**Affected tests** (ADR-0072 amendment). The suite follows `cyphercore/sections/coding-defaults.md`: pure functions in the core, side effects in adapters at the edge. A pure function nobody changed behaves exactly as it did, so re-running its tests buys nothing. Per change, run:

```
changed functions ──► their tests
        │
        └─► reverse imports (transitive) ──► callers' tests
changed adapter / side-effect boundary ──► its contract + integration tests
```

- TypeScript: `vitest related <changed files> --run` (or `vitest --changed origin/main`).
- Python: the test modules for the changed modules and every module that imports them (`git diff --name-only origin/main` → import graph → `pytest <those modules>`).
- Rust: `cargo test -p <changed crate>` plus the crates that depend on it.
- Always add the contract / registry tests that enumerate every tool, error variant or hook (the gateway: `test_http_app`, `test_observability_errors`, `test_tools_vault_ns`, `test_profile`). Nothing imports a brand-new tool, so the import graph never reaches them — a build once failed on exactly these three.
- If a change can't be traced (global state, an I/O call inside a "pure" function, a shared helper with unknown callers), that is a functional-standards bug: fix the boundary, and test that module's whole dependent set meanwhile.

Other usage rules:
- **Claude factory seats only, outside managed server scope:** launch via `cypherops/factory/bin/{seat,review,uat}.sh` (sonnet, 120k autocompact, token cap). Never bare `claude -p`, `--bare`, an API key or the Agent SDK. One clause set ≈ 100 turns; bigger → split the brief. A tripped cap → re-dispatch smaller, don't raise it. On Codex desktop use supported native sub-agents for useful independent work; new server agents use the common entry above. Read `hosts/codex.md` and `cypher-delegation`. Factory incompatibility does not impose serial execution.
- `export FACTORY_RUN=<slug> FACTORY_SESSION=<id>` before the first seat; then open Factory Watch (your host file says how).
- Waiting costs nothing: chain long jobs on the machine; `factory_events` push, or one scheduled check-in at the expected finish (your host file). No polling loops for hour-long jobs.
- Board comments: see `cypher-design`.
- Delegate wide reads to a subagent and keep the conclusion, not the file dumps.
- Work under `~/scratch/<run>/`, never `/tmp`. Worktree always; never touch the shared checkout (see below). A repo's own tool output goes in that repo's gitignored `logs/`; the workspace block is in `cypherops/docs/agent/reaching-the-workspace.md`.
- Run `factory/bin/*` from a worktree of current origin/main; `seat.sh`/`review.sh`/`uat.sh` refuse a stale copy (`fresh_check`).

### Plugin and skill changes: immediate adoption

Every Cypher plugin change, including adding or editing a skill, includes client adoption in the same run. Publishing the source or marketplace alone is not completion.

1. Finish the source change, required checks/review and publication. Then refresh and update each in-scope consuming client that supports it, including supported Cypher assets used through Orca while retaining ChatGPT/Claude desktop plugins (see [Orca adoption](../cypher-delegation/references/orca.md)), using its documented management tool or CLI. Do this autonomously under the owner's requested change; do not stop at giving update instructions. Read the host file for the supported procedure.
2. Verify the installed/enabled version and read back the installed changed skill or relevant plugin files against the released source. Catalogue freshness, downloaded bytes and the version actually used are separate facts.
3. Use the updated guidance straight away: perform a supported capability reload where available and read the relevant installed skills into the current chat before continuing. A current chat's previously injected skill catalogue may remain stale; do not equate a disk update with automatic replacement of every active chat's context.
4. If a client needs an interactive reload, restart or new chat that cannot safely be done by the agent, finish every supported update first, name the remaining client and exact action, and carry it into the handover. Respect live-service restart safeguards and preserve other active chats.
5. Record released, installed and loaded versions separately, plus any unverified client behavior. Never claim adoption based only on publication. An unsupported client does not block adoption on supported clients.

Use supported installation/update mechanisms; never hand-edit plugin caches or bypass authentication, permissions or hook trust. If the host cannot update plugins, report that specific limitation instead of assuming every host has it.

### Leave every repo clean

Sessions never leave dirty repos. One shared cypherops checkout once sat 184 commits behind with 350+ uncommitted run files, five shared checkouts on old branches and 300+ dead worktrees, each left by a session that had called itself done; a review launched from the stale checkout ran 0 agents and said "no issues".

| Where | Rule |
|---|---|
| `~/workspace/<repo>` (the shared checkout) | **Read-only.** Never edit, never `git switch`/`checkout`/`reset`, never write seat output or run docs into it. Reading, `git fetch` and a clean `git merge --ff-only origin/main` are the only things allowed. |
| Run documents (`factory/work/<run>/*.md`: BRAINDUMP, INTENT, PRD, SPEC, PLAN, UAT, RESULT, `briefs/`, `reports/`) | Written in a **worktree on the run branch**, committed and pushed as they are written, landed with the run's PR. A brief a seat reads is committed before the seat starts. |
| Seat output (`*.jsonl`, `*.rc`, `*.done`, `*.err`, `*.log`, `*.out`, screenshots, glue `*.sh`) | `~/scratch/<run>/logs/`, never a repo. cypherops `.gitignore` drops them from `factory/work/` as a backstop only. |
| Worktrees | `~/scratch/<run>/<task>`, removed when merged. Never `/tmp`, never inside a repo. |
| Something dirty that is not yours | Never delete it unseen. Copy it to `~/scratch/rescue-<date>/`, compare it with main **and the live system**, then commit it or drop it with the evidence in a PR. |

**Done means clean.** Before you say *done*, close a ticket, or hand over:

```bash
cypherops/factory/bin/clean-check.sh --run <slug> <every repo you touched>
```

It must exit 0 (`clean-check: OK`): every touched shared checkout on main, clean, nothing unpushed; every worktree of this run merged and removed, or its open PR named in HANDOVER.md. Paste its last line into the closing note or HANDOVER.md.

**Build output on disk: the known latest working build and the active build, nothing else** (owner, 2026-11-14; the workspace disk hit 100% and stopped two seats).
- Build output is anything a build regenerates: cargo `target/`, `dist/`, bundles and installers, a finished worktree's `node_modules`, built images and caches a run created.
- A build is superseded when a newer build of the same thing passes, its branch merges, or its seat finishes with no seat queued in that worktree. Delete its output in that same step, not at the end of the run.
- Keep exactly two: the latest build known to work (the one you would ship or roll back to) and the build in progress. Seats building in parallel worktrees each count as active; if the disk cannot hold them, run them one after another.
- Before launching a seat or a build, check free space on the workspace disk. Under 15% free: delete this run's superseded output first. Still short: say which other runs hold the space; never delete another run's files unseen (the rescue rule above applies).

## 4. When to start a fresh session

Handover has its own skill: when a session should suggest a fresh one, the HANDOVER.md template, the clean-check and the paste line are all in `cypher-handover`. Load it when a gate passes, context runs long, or the run switches.

**While AFK is on, never suggest a fresh session** (standing rule 2). Keep HANDOVER.md current, compact when the host does, and carry on in this session; the AFK token cap means compact and carry on. Handover waits until the owner is back.

## 5. Closing anything

- [ ] **Clean:** `cypherops/factory/bin/clean-check.sh --run <slug> <every repo touched>` exits 0, and its last line is in the closing note. Nothing is done until it does (§3, *Leave every repo clean*). The note ends `Session: can be archived` or `Session: keep open — <why>` (W-43, §2).
- [ ] Merged with `delete_branch: true`; said what restarted.
- [ ] Plugin or skill change: supported in-scope clients updated and installed content verified; relevant skills read/reloaded for immediate use. Any client needing manual adoption is named (§3, *Plugin and skill changes*).
- [ ] Previews are published as paths on the preview service (suite-tidy S-31/S-61; CypherMind `/mind` is the model); procedure: slice 2, pending. The design-system mirror is retired (ADR: design-system mirror retired, 2026-11-06), so a merge no longer carries a mirror step.
- [ ] Every test leftover gone (guests + their PBS backups, branches, repos, vault items, DNS); listed in the closing note.
- [ ] `STATUS.md` updated in every repo touched.
- [ ] Plane: non-visual run → epic Done with evidence comment; visual → waiting on UAT. Gate board deleted when its ticket closes.
- [ ] `~/scratch/<run>/` and this run's worktrees removed (`factory/bin/prune-merged-worktrees.sh`; re-run `clean-check.sh` after).
- [ ] No build output of this run is left anywhere under `~/scratch/` (§3, *Build output on disk*).
- [ ] Measurements went to Grafana, not chat.
- [ ] Follow-ups this work scheduled are swept as your host file says: done ones removed, recurring, still-owed and hand-paused ones kept, fired handover tasks left disabled, never deleted.

## Related skills

`cypher-spec` (gate 1) · `cypher-improve` (evidence-backed plans and checkpoints) · `cypher-design` (any UI, gate 2) · `cypher-secrets` (any credential) · `cypher-ops` (any change in cypherops: stacks, IaC, factory, guests) · agent-skills inside seats (`/spec /plan /build /review /test /ship`). Source of truth for the factory: `cypherops/factory/README.md`, ADR-0054, ADR-0072, cypherui `docs/agent/ui-test-levels.md`.
