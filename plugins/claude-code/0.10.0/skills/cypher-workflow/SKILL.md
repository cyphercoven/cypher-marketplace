---
name: "cypher-workflow"
description: "Load FIRST for any work on the Cypher Suite or any cypher* repo — picks the lane and gates, runs heavy steps (design sync, full review, builds) once at the end, affected-only tests, leaves every repo clean (clean-check before done), and suggests a fresh session with a handover."
---

# Cypher workflow — how any piece of work gets built

The product owner is the product manager. They braindump, approve at **spec · design · UAT**, and nothing else. You do everything in between — branches, PRs, review, merge, deploy, credentials, cleanup — autonomously, and you spend the product owner's Max usage as if it were scarce, because it is.

Precedence when docs disagree: the running system > `STATUS.md` > ADRs > INTENT > SPEC > this skill > memory. A higher source being wrong is a bug: fix it in a PR on the spot (factual fixes need no gate). Single source: this plugin skill; the cypherops copy `docs/agent/cypher-workflow.md` is a generated pointer to it.

**On your host:** read `hosts/<your host>.md` beside this file (one file per host) for the steps only your host can do — scheduling, artifacts, project docs.

## 0. Every session, before anything

1. Name the session `<App/Service>: <name>` — e.g. `CypherFlix: music import`, `CypherOps: cert renewer`. A cross-repo factory run is `Cypher: <slug>`.
2. Chat hosts (no workspace shell): first gateway call `session_begin {label, client_session, surface}`; pass `session` on every call; say the id in your first reply. If a later call says the session is unknown or expired, call `session_begin` again; a 502 during a gateway update → wait 30 s and retry.
3. Read `STATUS.md` in every repo the task names. Read, don't recall.
4. Pick the lane below. Say it in one line ("Lane C — factory run, visual, 3 gates").
5. Load the other skill the work needs: `cypher-ops` (any change in cypherops or on a running guest) · `cypher-spec` (a braindump or new factory run, gate 1) · `cypher-design` (any UI, screen, board, component, icon, avatar or brand, gate 2) · `cypher-mirror` (a merge whose plan says `will_mirror`) · `cypher-secrets` (any key, token, password or credential).

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
- Everything runs on the Max subscription: never an API key, the Agent SDK, `claude --bare` or a third-party harness.

**Standing design rules**
- One canonical Design board per product, created the first time we design for it and updated after that, never duplicated.
- All component work happens on the single "CypherUI Components" canvas, which the Design System links to (the Design System holds no component cards).
- Delete a gate board as soon as its ticket closes.

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
| **B Ops** | gateway tools; hot-fix only if needed, then backfill IaC in the same session | none — except *ask first*: restarting public-set services (list: `knowledge {topic: "workflow-ops"}`), any kill/terminate/destroy/delete, a downtime window (quote when, how long, what) |
| **C Factory run** | `cypher-spec` → Plane epic Approved → `PLAN.md` (no gate) → `cypher-design` if visual → seats on one run branch → one final PR → merge → deploy → UAT or auto-close | **spec**; **design** only if there is a surface they will look at; **UAT** only if visual |
| **D Design loop** | `cypher-design`; `pnpm ds:review` → publish into the one **CypherUI Components** canvas; batch their comments | design |

Not sure between two lanes → take the heavier one. Not sure whether a run is visual → leave the epic open and ask.

## 2. Autonomy — what is yours, what is theirs

**Yours, never asked:** opening and merging PRs (after the review tier below is clean), deploying, creating and updating vault items and credentials through the gateway (`cypher-secrets`; delete is ask-first), creating Plane items, managing your own scheduled follow-ups (standing approval — see your host file), fixing stale docs, rolling back something you broke, running UAT for agent-facing tooling (an independent tester seat that sees only the SPEC's "Done looks like"). Cost never needs their nod: the guard is the per-seat token cap (`cyphercore/sections/delegation-rules.md`).

**Theirs, one question each:** gate 1 spec (one board, one question), gate 2 design (canvas, one question), gate 3 UAT (a single installable build incl. Linux — never a CI zip — plus `UAT.md`, one question). Plus the B-lane "ask first" items. Never hand them a PR link, a script, or a step you could do. A new UI pattern is not a fourth gate: file it as a kit request and it is judged at the design gate (`cypher-design`).

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

Every turn that ends on them therefore ends on one of the two lines. The handover message (§4) is the one exception: it ends exactly as written there.

**Migrations:** plan a quoted downtime window, not zero downtime. State when, how long and which services; get explicit approval first; prefer simple to clever. With IaC the default is stop → swap → start (announce, `down` the old, `apply`/`up -d` the new, verify). Use a crossover only when the service cannot tolerate the window.

Report merges as: what shipped · what restarted (`will_restart`) · what's next.

### Changing a file

| Who | Change part of a file | New file / whole rewrite | Find · list · read |
|---|---|---|---|
| Chat host (through the gateway) | `workspace_edit` — pass `if_sha256` from your last `workspace_read`; `edits` for several changes at once | `workspace_write` | `workspace_grep` · `workspace_glob` · `workspace_read` with `offset`/`limit` |
| Seat (Claude Code in the workspace) | Edit | Write | Grep · Glob · Read |

Never `sed -i`, `perl -i`, a heredoc / `cat >` / `tee`, or a python read-modify-write on a tracked file — seats are blocked by a hook (`factory/hooks/no-shell-rewrite.py`), and a session has no excuse either. If a connector's tool list is stale and has no `workspace_edit` yet, `workspace_read` then `workspace_write` the whole file — never the shell.

## 3. Heavy work runs once, at the end

The rule: **cheap checks every round, heavy steps once per change set, last.** Queue changes, then pay for the expensive step one time.

| Heavy step | Never | Once, when |
|---|---|---|
| Full `ds:sync` / `cypher-mirror` (15–25 min) | from a worker seat, between comments, to "see if it changed" — or for a kit change that is only patch or minor | **decided by the kit's semver bump** (ADR-0075; run `pnpm ds:status`): patch → `ds:sync --bundle-only`, no canvas render; minor → only the canvases the set touched, after asking the product owner; major → the full sync, once, after the last change of the set merges. Publish straight from that `ds-out/`. Workers: `ds:sync --only <target>` + `ds-measure --check` on their canvas only |
| Full review (`review.sh` → `/factory-review`, 4+ agents, fresh PoCs) | to validate a 1–2 line fix | first review of a PR / feature slice. After: scoped review (dispatch, security, shared predicate, untrusted parser) or self-verify (ruff/mypy/lint + red→green + affected tests) — ADR-0072 |
| Tests | the full suite, ever, by habit | **affected tests only** — the tests of every changed function plus every caller that (transitively) imports a changed module, and the contract/integration tests of any changed adapter. Untouched pure functions are not re-tested. Every round, and as the pre-merge gate. See *Affected tests* below |
| UAT / installer build (Setup.exe) | per fix, as interim proof | once, after every known fix is in. Kit-only change → restart the UAT app, no rebuild |
| CI | on every push | PR open (tests) and merge (build) only |
| Screenshots / renders / image batches | while changes are still queued or known mistakes remain | after the last queued change; fix known causes first |
| Test runs | partial or interim | only the planned test, with all its parts |

Order inside a run:

```
spec ─► plan ─► design boards (touched canvases only) ─► [design gate]
     ─► seats build + affected tests ─► tiered review per task ─► merge tasks into run branch
     ─► affected tests + full review ONCE ─► final PR merge ─► deploy
     ─► full ds:sync / cypher-mirror ONCE ─► UAT build ONCE ─► [UAT gate] ─► close
```

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
- Seats only via `cypherops/factory/bin/{seat,review,uat}.sh` (sonnet, 120k autocompact, token cap). Never bare `claude -p`, never `--bare`, an API key or the Agent SDK. One clause set ≈ 100 turns; bigger → split the brief. A tripped cap → re-dispatch smaller, don't raise it.
- `export FACTORY_RUN=<slug> FACTORY_SESSION=<id>` before the first seat; then open Factory Watch (your host file says how).
- Waiting costs nothing: chain long jobs on the machine; `factory_events` push, or one scheduled check-in at the expected finish (your host file). No polling loops for hour-long jobs.
- Board comments: see `cypher-design`.
- Delegate wide reads to a subagent and keep the conclusion, not the file dumps.
- Work under `~/scratch/<run>/`, never `/tmp`. Worktree always; never touch the shared checkout (see below). A repo's own tool output goes in that repo's gitignored `logs/`; the workspace block is in `cypherops/docs/agent/reaching-the-workspace.md`.
- Run `factory/bin/*` from a worktree of current origin/main; `seat.sh`/`review.sh`/`uat.sh` refuse a stale copy (`fresh_check`).

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

## 4. When to start a fresh session

Handover has its own skill: when a session should suggest a fresh one, the HANDOVER.md template, the clean-check and the paste line are all in `cypher-handover`. Load it when a gate passes, context runs long, or the run switches.

## 5. Closing anything

- [ ] **Clean:** `cypherops/factory/bin/clean-check.sh --run <slug> <every repo touched>` exits 0, and its last line is in the closing note. Nothing is done until it does (§3, *Leave every repo clean*).
- [ ] Merged with `delete_branch: true`; said what restarted.
- [ ] `will_mirror` on the merge → run `cypher-mirror` in this session before closing. Its STEP 0b picks the size from the kit bump (`pnpm ds:status`): patch = bundle only, minor = touched canvases only, major = the one full render (ADR-0075).
- [ ] Every test leftover gone (guests + their PBS backups, branches, repos, vault items, DNS); listed in the closing note.
- [ ] `STATUS.md` updated in every repo touched.
- [ ] Plane: non-visual run → epic Done with evidence comment; visual → waiting on UAT. Gate board deleted when its ticket closes.
- [ ] `~/scratch/<run>/` and this run's worktrees removed (`factory/bin/prune-merged-worktrees.sh`; re-run `clean-check.sh` after).
- [ ] Measurements went to Grafana, not chat.
- [ ] Follow-ups this work scheduled are swept as your host file says: done ones removed, recurring, still-owed and hand-paused ones kept, fired handover tasks left disabled, never deleted.

## Related skills

`cypher-spec` (gate 1) · `cypher-design` (any UI, gate 2) · `cypher-mirror` (after a cypherui/cypherinstall merge) · `cypher-secrets` (any credential) · `cypher-ops` (any change in cypherops: stacks, IaC, factory, guests) · agent-skills inside seats (`/spec /plan /build /review /test /ship`). Source of truth for the factory: `cypherops/factory/README.md`, ADR-0054, ADR-0072, cypherui `docs/agent/ui-test-levels.md`.
