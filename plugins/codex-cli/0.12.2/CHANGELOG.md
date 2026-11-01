# Changelog

All notable changes to this plugin are recorded here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); versions follow
semver, tracked in `plugin.src.yaml`.

## 0.12.2 — 2026-11-01

- A tested merge to source main automatically builds and publishes a version-bump PR to the public GitHub marketplace and merges its exact head. No manual tag, approval, Forgejo marketplace or sync-back is required. Published versions are immutable; verified retries and documentation-only merges do not replace them. Failed checks/builds stop publication. Claude ingestion will be verified by the owner after her usage resets (OPS-1690).

## 0.12.1 — 2026-11-01

- Marketplace releases use a merged GitHub version-bump PR, then return its exact merge to Forgejo. Releases serialize, validate published versions, and refuse divergent histories. Published through GitHub PR #1. Provider ingestion remains a separate verification (OPS-1690).

## 0.12.0 — 2026-11-01

- `cypher-animation` (new, model-invocable): headless Blender character work on 5.2 LTS. It covers rigging (UniRig, and Rigify including the cat), shape keys and GNM mouths, Rhubarb lip-sync with coarticulation, animation craft with cited realism numbers, mocap with licence checks, animals, rendering and verification. It also records the 4.2→5.x API facts probed on our builds. Material is adapted, with attribution, from four MIT skill repos.

## 0.11.1 — 2026-11-01

- `cypher-workflow` gains "Do it properly, first time — for all work": the first fix is the proper fix (root cause and the established technique named before any change), no guessing, two strikes then stop and diagnose, and never announcing "the proper fix" after the fact. Rules W-27 and W-28. Brings the owner's 2026-11-01 update to the account skill into the plugin, so a regenerated pointer does not drop it.

## 0.11.0 — 2026-10-31 (OPS-1012 p1)

- Fix (incident 2026-10-31): 0.10.0 bundles did not contain `scripts/skill_gate.py` or `scripts/afk.py`, so the PreToolUse hook failed and blocked every Bash and MCP call. The release now derives the files a bundle ships from its hook and MCP config (every `${CLAUDE_PLUGIN_ROOT}/…` path, plus each script's local imports and data files); the release gate fails on any referenced path missing from a bundle or the Claude desktop zip; every hook command checks its script exists and exits 0 if not.
- Migration: the connector rename changes the tool prefix. A permission allowlist that names `mcp__cypherops-mcp__*` (formerly the connector's tool prefix) must be changed to `mcp__cypher-mcp__*`, or those calls ask for approval again.
- Fix (review p1b): scripts that skills run now ship. A script named in skill text (`scripts/<x>.py` or `${CLAUDE_PLUGIN_ROOT}/scripts/<x>.py`) is a release root, so `scripts/setup_render.py`, `scripts/render_template.py` and the `templates/` files they read are in every bundle and `/cypher-admin setup` works on an installed copy. Skills name those scripts as `${CLAUDE_PLUGIN_ROOT}/scripts/...`, not cwd-relative.
- Fix (review p1b): the release gate resolves a script's data-file dependencies against the repo, so a data file missing from a bundle (for example `CHANGELOG.md`, `skills/triggers.yaml`) is an error, and the planned copy set must be a subset of the bundle. A test fails if a shipped script builds a path the dependency scan cannot see (`os.path.join`, an f-string path, `importlib`).
- Fix (review p1b): hooks no longer use `sh -c`, which failed on Windows hosts without Git Bash (PowerShell). Every hook command is a python-only launcher that exits 0 when its script is missing, passes through the script's exit code (2 still blocks), stdout and arguments, and works when the plugin root contains a space.
- One `/cypher-admin <sub-command>` command replaces the per-skill commands (`setup`, `start`, `afk`, `spec`, `design`, `deploy`, `build-app`, `handover`, `troubleshoot`, `mirror`, `media`, `secrets`, `ops`, `review`, `workflow`, `help`). Every `cypher-*` skill keeps its name and stays model-invocable but is hidden from the `/` menu (`user-invocable: false`). `/cypher-afk` is not a command (the skill is hidden, and the host may never deliver it): away mode starts from "going afk", "afk", "going to bed", "I'm away" or `/cypher-admin afk`, and the trigger no longer accepts `/cypher-afk`.
- The connector is now `cypher-mcp` (formerly `cypherops-mcp`; OPS-1012 p2): the MCP server key in every bundle's config, every person-facing mention, the `make scan` rule (`cypher-mcp` required, `cypherops-mcp` and `cypherbitch` forbidden outside a "formerly" note here) and the trigger-glob proof (`mcp__cypher-mcp__vault_list`). Migration: anyone who signed in to `cypherops-mcp` signs in once more to `cypher-mcp`; on Codex that is `codex mcp login cypher-mcp --oauth-client-registration auto`. The gateway URL is unchanged.
- One `/cypher-legal [area] [question]` command and skill replaces the eleven `law-*` skills; each area (and the shared research method) is now a reference file under `skills/cypher-legal/references/`. `VERIFIED.md` and `verification.json` moved with it.
needs-setup: true
answers_version: 2

(The templates now name `/cypher-admin setup` instead of the old per-skill commands. The questions are unchanged, so `answers_version` stays at 2 and no install is asked to re-run setup; a re-run only refreshes the command names in the saved instructions.)

## 0.10.1 — 2026-10-31 (OPS-1404)

- `cypher-workflow` gains the standing rule *Data lives in a database* (rules W-25, W-26): user and app data (people, profiles, roles, permissions, settings) change without a PR, build or deploy, and every data operation writes a same-transaction audit row it can be reverted from.

## 0.10.0 — unreleased (cypher-plugin-providers epics J–N, OPS-1012)

needs-setup: true
answers_version: 2

(`templates/hosts.yaml` gains release-only `bundle:` / `catalogue:` fields; the setup answers are unchanged, so `answers_version` stays at 2 and no install is asked to re-run setup.)

- The plugin is the only source of every cypher skill: repo copies are generated pointers and `make check-skill-sources` fails on drift (S-58). `cypher-workflow` catches up with the live rules (clean-check, the ask goes last, file-edit table, suggest a fresh session) (S-59). Host-only steps live in `skills/<skill>/hosts/<host>.md` and `make check-skills` keeps them out of skill bodies (S-60). `cypher-troubleshoot` absorbs the error-triage routine (S-61).
- `cypher-dev` states the language choice (Rust back end, TypeScript UI, Python by exception — ADR-0078) and loads `references/{rust,typescript,python}.md` per language (S-69).
- New skills: `cypher-ops` (with seven references: stacks, runbooks, sidecars, capability bundles, image tags, Cloudflare/mTLS, pages deploy) and `cypher-media` (media-stack maintenance and the NAS check), with infra facts behind `knowledge` topics (S-62, S-63); `cypher-architecture`, `cypher-review`, `cypher-delegation` and `cypher-handover` (S-64..S-67). The rules audit now reads 69 sources: 159 rules, 0 unowned, 12 conflicts awaiting the owner's ruling (S-68).
- `make release VERSION=x` / `make release-dry` build one bundle per host into `dist/<version>/<host>/`; any failing validator or scan stops the release; `make rollback` plans the previous version for every catalogue (S-74, S-75, S-80).
- Skills load themselves: `skills/triggers.yaml` maps file types and tool calls to the skill they need; on Claude Code a PreToolUse hook refuses the call until that skill (and language reference) is loaded, and SessionStart (startup/resume/clear/compact) loads `cypher-workflow`. Every trigger row has a should-load and a should-not eval (S-52..S-54, S-57).
- `make publish` copies a built release into the private marketplace repo (Claude Code and Codex catalogues, a zip for Claude desktop); `.forgejo/workflows/release.yaml` publishes on a `v*` tag only; the monthly host check also watches each host's catalogue format (S-76, S-77, S-81).
- `cypher-afk` (away mode): "going to bed", "going afk", "afk", "I'm away" or `/cypher-afk` turn it on; gates and ask-first actions are queued for one morning report instead of asked; on Claude Code, PreCompact/SessionStart(compact) hooks carry HANDOVER.md across compaction and a Stop hook keeps the session working while runnable tasks remain, within a token cap; a new message from the owner turns it off (S-82..S-87).
- Rule conflicts C-09..C-12 ruled by the owner on 2026-10-30 (S-51).

## 0.9.1 — 2026-10-28

- Clarifies automatic loading of law-research for primary-authority and case-citation verification, including requests that need further details. Responds to two observed routing misses; evaluation prompts and graders are unchanged.

## 0.9.0 — 2026-10-28

- Adds eleven law skills for research, education, family, housing, benefits, employment, criminal law, substances, corporate law, small business and fraud/AML. Each requires primary sources, jurisdiction/event dates, commencement checks, explicit uncertainty and a free-advice signpost.
- Includes live locator provenance and 55 routing fixtures. Offline validation is distinct from the model evaluation; no 1.0 routing score or current-in-force guarantee is claimed.

## 0.8.1 — 2026-10-26

- `skills/cypher-scheduled-tasks` (new) — the product owner's standing approval to create, update, disable and delete
  scheduled tasks, the lifecycle (keep / disable / delete; handover tasks never deleted), a fallback for every refusal
  (refused delete → disable + sweep log; device-bound prompt; non-auto permission mode; repeating approval prompt) and
  an end-of-session sweep. Evals: 3 should-load, 2 should-not.
- `skills/cypher-workflow` — §2 lists scheduled tasks as never-asked, §5 sweep points at the new skill; typo fix.

## 0.8.0 — 2026-10-26

needs-setup: true
answers_version: 2

Update prompts and per-host README (cypher-plugin-providers tE, S-21, S-22):

- `scripts/update_prompt.py` (+ tests) — pure comparison of the saved `answers_version` with the newest `needs-setup`
  CHANGELOG entry that carries an `answers_version: N` line; says "Your Cypher instructions changed — run /cypher-setup"
  once per required version, remembered in a small local state file.
- `hooks/hooks.json` — SessionStart hook (Claude Code, Cowork, Codex) running it; `cypher-start` does the same check on
  every other host and records `answers_version` for the hook.
- README: Install / Update / First run for every host in `hosts.yaml`; `make check-readme` (in `make check`) enforces it.
- Releases flagged `needs-setup: true` now also carry `answers_version: N` (the template version that release needs).
- `skills/cypher-design` — ported the 2026-10-25/26 live-source drift (S-44, S-45): canvas page/row layout, post-its and flow rows, icon tiers, avatars and first names, forms/tables/list leads, casing, extensions page, Servers on Today, render budget, checklist items; canvas layout and spacing/forms rules moved to `canvas-layout.md` / `spacing-and-forms.md` to keep SKILL.md ≤300 lines.


Skills by job (cypher-plugin-providers tI2b, S-45..S-50):

- New `cypher-dev` (D-01..D-14: coding defaults, functional core, affected tests, commit identity, no `--no-verify`,
  kit-only UI) and `cypher-docs` (DOC-01..DOC-04: STATUS, ADRs, docs split, vision docs). Both in the skills list.
- `cypher-design` trimmed to 299 lines (render budget is a pointer to `cypher-workflow` §3).
- `make check-skills` (every skill <=300 lines, one trigger section) and `make check-evals` in `make check`;
  `evals/<skill>/*/case.yaml` (3 should-load, 2 should-not per skill); `make evals` runs `claude plugin eval` live,
  and the Forgejo `evals` job runs only when `CLAUDE_CODE_OAUTH_TOKEN` is set.
- `templates/hosts.yaml` — `autoload` line for Codex, Antigravity, Copilot and Cursor: load `cypher-workflow` first.
- `templates/project-instructions.md` — identity, working style and skill pointers only (the standing rules live in
  their skills); `rules_audit.py --template` reports 0 rule lines. Re-run `/cypher-setup` to refresh the project text.
- `rules/rules.yaml` — D-* and DOC-* owned; `--check` reports 0 unowned, 0 duplicates, 0 deferred.
- `make check-version` also requires `answers_version: N` when `templates/` changes.
- `make evals` fails on any miss locally; CI runs it at a 95% pass threshold, non-blocking until its first green run.
- The previous-name rule now reads: never call the owner by a previous name or write one; stored historical records keep it.
- Review fixes (PR !2): CI `check` job installs `nodejs npm` for `check-brand`; transcripts expect `answers_version: 2` and
  `test_transcripts` checks them against `templates/variables.yaml`; `cypher-setup` finds the host (step 4) before saving
  (step 5); no plugin text points an agent at a vault item or file for previous names (they live in the owner's people record).

## 0.6.1 — 2026-10-25

needs-setup: true
answers_version: 1

Owner rulings C-01..C-08 applied (cypher-plugin-providers tI2a, S-44, S-51):

- `cypher-secrets` — the agent creates and updates vault items itself (`vault_create`/`vault_update`/`vault_rotate`), never
  prints a value, and delete is ask-first; never ask the owner to run a command (C-01, C-07).
- `cypher-workflow` — scratch/worktree line points to the workspace block; Migrations paragraph (quoted downtime window);
  board comments point to `cypher-design`.
- `cypher-design` — comment logging, factory seats / `ds:watch`, image generation by construction (UI-02..UI-04).
- `rules/rules.yaml`, `tools/rules_audit.py` — rulings recorded as approved (C-08 amended), duplicates become pointers /
  out-of-git proposals, unowned rules awaiting `cypher-dev` / `cypher-docs` are `deferred`; `sources/PROPOSED-out-of-git.md`.
- `skills/SOURCES.md` — re-diffed against the live skills: no upstream change.

## 0.6.0 — 2026-10-25

needs-setup: true
answers_version: 1

`/cypher-setup` (cypher-plugin-providers tD2, S-15..S-19, S-25, S-40):

- `skills/cypher-setup` — up to eight short questions with prefills, saves to the settings record (`settings_set`,
  `answers_version`), renders the instructions, names the host's paste location, writes the file after a confirm on
  Claude Code / Codex / Antigravity. Re-run first asks "keep previous answers, or run the full setup?".
- `scripts/setup_render.py` — the pure core (questions + prefills, keep/full mode, record mapping, render, host lookup,
  write plan with diff); `tests/test_setup_render.py`.
- `templates/variables.yaml` gains `version: 1` and the `providers` question (8 questions now).
- `cypher-start` offers `/cypher-setup` when there is no settings record. Scripted transcripts in `tests/transcripts/`.

House brand from cypherui (cypher-plugin-providers tB, S-08/S-09):

- `make brand` installs the pinned `@cyphercoven/cypher-brand` 0.3.0 (`brand/`, lockfile committed) and
  copies the house app-icon + wordmark into `assets/house/` with its own `cypher-brand sync`; the 1024 px
  app-icon is also `.claude-plugin/icon.png` (square PNG for Claude's plugin directory).
- Every manifest now carries display name "Cypher" and the house icon; `plugin.src.yaml` gains a `brand:` block.
- `make check-brand` (in `make check`): icon sha vs the package, names, pin, PNG size rules, wordmark shipped.

## 0.5.0 — 2026-10-25

needs-setup: true
answers_version: 1

Project-instructions template and per-host paste locations (cypher-plugin-providers tD1, S-14/S-18/S-20):

- `templates/project-instructions.md` — the suite's project instructions with every personal fact
  as a `{{variable}}`; `templates/variables.yaml` declares each (question, type, default source).
- `make render-template FIXTURE=<name>` (or `FIXTURE_FILE=<path>` for a fixture outside the repo);
  non-personal `fixtures/example.yaml` + `fixtures/example-expected.md` drive the tests.
- `templates/hosts.yaml` — where to paste instructions on each of ten hosts, doc URL, check date,
  and file-write target for CLI hosts; `scripts/check_hosts.py --dry-run` compares stored doc-section hashes;
  `docs/hosts-check-task.md` holds the monthly task prompt.

- Rules audit (S-43): `tools/rules_audit.py`, `rules/rules.yaml` (65 rules, 8 conflicts) and the generated `RULES-AUDIT.md`; `scan` now covers them. `--check` is expected to fail until S-44.

## 0.4.1 — 2026-10-25

- Author is `cypherwitch` (all lowercase) on every host's manifest.

## 0.4.0 — 2026-10-25

The five Cypher workflow skills move in as the single source (cypher-plugin-providers tF, S-23/S-24):

- `cypher-workflow`, `cypher-spec`, `cypher-design`, `cypher-mirror` and
  `cypher-secrets` now ship from `skills/`, listed in `plugin.src.yaml`.
  `skills/SOURCES.md` records each source `SKILL.md` sha256.
- Every infra or personal fact the scan rejects is replaced by a
  `knowledge {topic}` call (`workflow-ops`, `factory-run`, `design-mirror`,
  `design-fixtures`, `credentials`); the pages live in the gateway repo.
- `make scan` accepts the sha256 column of `skills/SOURCES.md` only.

## 0.3.0 — 2026-10-25

Every host's manifest, stricter checks (cypher-plugin-providers tA, S-03..S-07):

- `make manifests` now also writes `.codex-plugin/plugin.json`,
  `.cursor-plugin/plugin.json` and `mcp_config.json` (Antigravity). Root
  `plugin.json` / `mcp.json` (Agent Plugins 1.0) stay separate from Claude's
  `.mcp.json`. The `$comment` markers and the Codex `extensions` block are
  gone — both Agent Plugins schemas and `claude plugin validate --strict`
  reject unknown keys.
- `make check-mcp` checks all three host MCP files per dialect, requires
  OAuth/DCR, forbids client credentials.
- New `make validate` (strict Claude validation + vendored Agent Plugins
  1.0.0 schemas) is part of `make check` and CI.
- `make scan` fails on personal names, pronoun phrases, a personal handle,
  and names on an externally supplied previous-name list.
- `make check-version` requires `needs-setup: true` when `templates/` changes.
- Plugin author is now "Cypher" (was a personal name).

## 0.2.1 — 2026-10-11

Fix `scripts/scan.py`'s hostname rule false-positiving on dotted JS property
access (`el.addEventListener`) (cypher-plugin tM, OPS-760):

- A dotted token is now only considered a hostname candidate when its last
  label is a real TLD (`com net org io dev work tv me app local internal
  lan home arpa`); `el.addEventListener`/`document.getElementById`-style
  property access never reaches the allow-list check.
- Dropped the suffix allow-list glob for subdomains of the one allowed app
  domain — only that exact domain is allowed now, so an arbitrary subdomain
  of it is correctly flagged.
  Dropped `ALLOWED_DOTTED_IDENTIFIERS` (`com.openai`) as dead code under the
  new TLD gate (`openai` is not a valid TLD, so it's filtered before the
  allow-list check regardless).
- Reverted `skills/cypher-build-app/template/main.js`'s bracket-notation
  workaround (`el["addEventListener"]`) back to normal dot-notation JS, now
  that the scanner doesn't need it.
- New fixtures/tests: dotted JS passes, a disallowed app-domain subdomain
  fails, an explicit private-range IPv4 literal fails.

## 0.2.0 — 2026-10-11

Real content for the four skills (S-32, S-33, S-34, S-35, S-18, S-37):

- `cypher-start` — calls `onboarding`, answers who the person is signed
  in as, their role, what they can do, and what they're waiting for
  (no role → "ask a Cypher admin to give you a role in CypherOps"), in ≤ 10 lines.
- `cypher-troubleshoot` — for "what's broken" questions, calls `status`
  then `obs_errors {since}` then whatever object tools this person
  holds, reports only what they can reach, never guesses a host, and
  gives one likely cause plus one next action.
- `cypher-build-app` — builds a small web app from `cypherui` kit `cu-*`
  elements only (raw HTML confined to prose/markdown and alert
  descriptions), fetching the kit's `llms.txt`/`custom-elements.json`
  and channel address from `knowledge {topic: "cypherui"}` at run time
  (falling back to `onboarding` while that topic is still landing), with
  a minimal `template/index.html` + `template/main.js` starting point
  that carries no hardcoded channel address.
- `cypher-deploy` — Builder/Owner only; plans a guest-in-own-pool deploy
  and a CypherAuth-fronted publish on a name the person owns, shows the
  plan, waits for confirmation, then acts via `pve_*`; includes a
  symmetric plan-first teardown.
- README gets a "What you get" section naming all four skills.
- `make scan` continues to cover `skills/**` (S-37); the new skill
  bodies and app template carry no real channel address, pool name, or
  host beyond the one gateway URL.

## 0.1.0 — 2026-10-11

Initial scaffold (S-24, S-25, S-26, S-30, S-37):

- `plugin.src.yaml` as the single source of truth, generating
  `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `.mcp.json`, root `plugin.json` + `mcp.json`, and
  `.agents/plugins/marketplace.json` via `make manifests`.
- One MCP server, `cypher-mcp` (formerly `cypherops-mcp`), streamable HTTP, OAuth via dynamic
  client registration — no headers, no bearer, no static token.
- `make check`: manifest-drift check, `check-mcp`, `scan`, `check-version`,
  each with a fixture under `tests/` proving it fails on bad input.
- Four placeholder skills (`cypher-start`, `cypher-troubleshoot`,
  `cypher-build-app`, `cypher-deploy`) — intent only, no infra facts; real
  content lands in a later task.
- Forgejo Actions workflow running `make check` on push and PR.
