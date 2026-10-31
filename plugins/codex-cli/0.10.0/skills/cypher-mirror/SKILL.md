---
name: "cypher-mirror"
description: "Run before closing any session whose forgejo_pr_merge plan said will_mirror (cypherui or cypherinstall merged to main): mirrors both repos' main into the CypherUI/CypherFlix/CypherInstall design artifacts."
---

# Cypher: design mirror sync (cypher-mirror)

Source of truth: `cypherops/docs/agent/design-mirror-sync-task.md` (edit there, then re-propose this skill to match). Publish rules restate `cypherui/docs/agent/design-artifacts.md`; that file wins on any disagreement.

You mirror cypherui's and cypherinstall's `main` into the product owner's Claude Design artifacts (CypherUI Design System, CypherUI Components, CypherFlix, CypherInstall canvases). Run inline in the session that merged — reuse its gateway `session`; do NOT call session_begin again. CypherBitch gateway tools plus your host's artifacts. Never print a secret value.

## Render by kit version — decide this first

Re-rendering costs the product owner's usage. The kit's semver bump for this change set decides what gets rendered. Read the bump from the changesets merged since the last publish: `pnpm ds:status` lists them by bump; else `.changeset/*.md` and `CHANGELOG.md`.

| Highest bump in the set | Do |
|---|---|
| **patch** (new icon, glyph or unused component; fixes that don't move what a board draws) | **No canvas render.** Build the bundle only (`pnpm ds:sync --only cypherui`, or the bundle step alone). Publish the Design System's changed kit files, then record the version. Canvases pick the bundle up when they are next published |
| **minor** (spacing, positioning, sizing, type, colour — boards draw differently) | Publish the Design System's kit. Render and publish **only the canvases this change set touched** (`ds:sync --only <them>`). Every other canvas waits until a session next opens it, runs `ds:status <canvas>` and asks the product owner whether to re-render |
| **major** (breaking: retired or renamed element, attribute or API) | The full run below (STEPS 1–7): every canvas, automatically, fixing what breaks |

**The CypherUI Components canvas is the exception: it is always kept current.** Patch: render and publish only its boards whose component or story changed in the set. Minor or major: re-render the whole Components canvas in this run. The table covers the app canvases.

Never run the full render because `will_mirror` fired, to publish a new icon, or to "keep canvases current". Every canvas you publish records the kit version it was rendered with.

## Rules that override everything below

1. Never publish from a branch or a dirty tree. If either repo isn't a clean `main`, stop and report it — never force, stash, or switch it yourself.
2. Every file path is under `project/` — read `publishPath`, never a bare `path`.
3. Per artifact: `added`/`changed` files first (≤255 per call), `removed` ones as `null`, then its `last` files (`project/canvas.json`) in their own final call. Every publish follows a `read` and a files `list` of that artifact (host file).
4. A null artifact id (`scripts/ds-targets.json`) means that canvas doesn't exist yet — skip it and say so; never create one yourself.
5. Snapshot differences notify; they never gate. Nothing here blocks a merge.

## STEP 1 — verify both repos

For the cypherui and cypherinstall workspace checkouts (paths: `knowledge {topic: "design-mirror"}`), via `workspace_exec` (absolute `cwd`): `git fetch -q origin main && git branch --show-current && git status --porcelain`. Both must show `main` and empty porcelain. Either fails → report which repo and why, and STOP.

## STEP 2 — anything to publish?

In cypherui read `ds-out/.published.json`: `commit` is the cypherui sha last published, `roots.cypherinstall.commit` the cypherinstall one. Compare each with `git rev-parse origin/main` in its repo. Both equal → report `main unchanged since <sha>; nothing to publish` per repo and END. A missing `.published.json` counts as changed.

## STEP 3 — pull and build

For each repo whose origin moved: `git pull --ff-only` (not fast-forward → stop and report) then `CI=true pnpm install --frozen-lockfile`. Then `pnpm ds:capture` in cypherinstall, then in cypherui `pnpm ds:sync --root cypherinstall=<cypherinstall checkout>/ds-out/stories.json` (15–25 min: run with `background: true` and `job_poll` every ~2 min; never a foreground call over 120 s). Exit ≠ 0 → report the log tail and STOP.

## STEP 4 — publish per the manifest

Read `ds-out/manifest.json` (`workspace_read`). Per `artifacts` key with a non-null `url` (skip + report null ones, rule 4), whose `files` entries with `status` `added`/`changed`/`removed` are non-empty, publish the artifact through your host's artifacts.

**On your host:** read `hosts/<your host>.md` beside this file — it has the exact publish calls (bring the files over, read → list → publish, `last` files, the "not read" retry). A host without artifacts (`claude-code`, `codex`) cannot run this step: stop here, say so, and leave the mirror owed for a session that can.

Whatever the host, these hold:

- Canvases (every key but `cypherui`) load the kit LIVE from the assets host named in `knowledge {topic: "design-mirror"}` — nothing of the kit is copied into them.
- Its `last` files (`project/canvas.json`) go in their own final call.
- A publish refused twice → note it and go on to the next artifact.

## STEP 5 — snapshots

`pnpm ds:diff --json` in cypherui — before STEP 6, which moves the baseline. Then `pnpm ds:report` with the Plane token injected as described in `knowledge {topic: "factory-run"}`: it creates one Plane item per project ("Screens changed: <n> (kit a → b)") and prints `{"items":[...]}`. For each item, tell the product owner in one line: `Design mirror: <n> screens changed in <project> — <id>` with the url. `{"items":[]}` → say nothing.

## STEP 6 — mark published

`pnpm ds:sync --mark-published` in cypherui. Only after every artifact in STEP 4 succeeded; otherwise skip it and say so, so the next run republishes.

## STEP 7 — the report

One short paragraph: which repos moved and to what sha; which artifacts published (added/changed/removed counts) or were skipped; whether `--mark-published`, `ds:diff` and `ds:report` ran; the Plane item links if any.

## IF STUCK

Never repeat a failing call more than twice — note it, move on. Any failed call: name the tool and its answer at the top of the report, then what did complete. Never guess a `publishPath`, an artifact id, or a `git` state — read it or stop.