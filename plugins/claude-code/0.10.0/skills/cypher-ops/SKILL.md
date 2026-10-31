---
name: cypher-ops
description: Rules for changing the infrastructure-as-code repo (cypherops) and the guests it describes — where to work, how a change reaches a guest, hot-fix then backfill, secrets on guests, PR rules, leaving everything clean. Use when a task touches cypherops, a stack, an image tag, a runbook, ingress or Cloudflare config, a Pages deploy, or anything running on a guest.
---

# cypher-ops — working in cypherops and on the estate

cypherops is the suite's infrastructure-as-code: every guest, stack, record and
deploy is described there. Load **cypher-workflow** first (lanes, gates,
handover); this skill is the layer specific to that repo.

Precedence: the running system > `STATUS.md` > ADRs > the repo's `CLAUDE.md` >
this skill. When the live system and the repo disagree, the repo is the bug:
fix it on the spot. If a rule here disagrees with one of those, they win — say so.

Infra facts (guest list, addresses, hostnames, deploy lists, vault item names)
are never in this skill. Ask the gateway at run time: `knowledge {topic: <name>}`.
The topics this skill calls are listed at the end.

## When to use

Load this skill before you edit cypherops, before you change or restart anything
on a guest, and when someone asks how an image tag, an ingress route, a sidecar,
a capability bundle or a Pages site is wired. For a first-time stack, runbook or
Pages site, open the matching reference (table below). For "something is broken,
why", use **cypher-troubleshoot** instead.

**On your host:** read `hosts/<your host>.md` beside this file for the paths and
tools your host uses to reach the repo and the guests.

## 1. Where you work

- The shared checkout of cypherops is **read-only** and stays on `main`. You
  never edit, switch, check out or reset it, and never write into it — not even
  run documents. Allowed there: read, `fetch`, a clean `merge --ff-only origin/main`.
- Work in your own worktree on a task branch cut from `origin/main`
  (`git worktree add -b <branch> <path> origin/main`). Never `/tmp`, never a
  worktree inside a repo. Seat output (logs, streams, scratch) goes under the
  run's scratch directory and never enters a repo.
- Run the factory scripts (`seat`, `review`, `uat`) from a worktree of current
  `main`; they refuse a stale copy. `review` needs a Forgejo token supplied
  through the gateway `secrets:` list — which vault item: `knowledge {topic: "git-author"}`
  names the identity and the credential item to use.
- Run documents (`factory/work/<run>/*.md`, `briefs/`, `reports/`) are written on
  the run branch and committed as they are written.

The exact paths on your host: `hosts/<your host>.md`.

## 2. What lives where

| Thing | Where | Rule |
|---|---|---|
| Compose stack per guest | `stacks/<guest>/` | one per guest; shared sidecars via `stacks/shared/` (`extends:`) |
| Dockerfiles | `builds/<service>/` | never in a product repo |
| Image tags | `versions.yaml` → `scripts/sync-versions.sh` → `.env.template` | no inline `image: foo:1.2.3`, no `latest` |
| Guests (id, address, sizing) | `inventory/guests.yaml` | verify against the hypervisor before depending on it |
| LAN addresses | `hosts.yaml` | single source; `.tf` never restates an address |
| Cloudflare | `cloudflare/` (OpenTofu) | `cf_tofu` plan → apply; `cf_api` only as a planned one-off |
| Host provisioning | `ansible/` | idempotent roles; no hand `apt install` |
| Env names a guest reads | `stacks/<guest>/.env.template` | names only; why env-var (not file) is commented |
| Decisions · procedures · agent context | `docs/adr/` · `docs/runbooks/` · `docs/agent/` | rules in `CLAUDE.md`, context in `docs/agent` |
| Hot-fix record | `logs/hotfix-<date>.md` | the one thing committed under `logs/` |

Every non-trivial file opens with the `PURPOSE / CONVENTIONS / AGENT NOTES`
header; a missing or wrong header is fixed before anything else in the file.

## 3. The estate

The guest list (ids, names, roles, addresses) is `knowledge {topic: "estate"}`,
and it is a snapshot: re-read `inventory/guests.yaml` and confirm against the
hypervisor with `pve_guests` before you depend on a row.

Which tool reaches what: `ct_exec` reaches a container guest only if the
gateway's ACL admits you; the Coder workspace is `workspace_*`; the gateway's
own VM is `utils_*`; hypervisor-level work is `pve_*`.

## 4. How a change reaches a guest

1. **Merge = deploy for the ship-on-push stacks.** The workflow
   `.forgejo/workflows/ship-on-push.yaml` deploys on a merge touching one of the
   stacks it lists (which: `knowledge {topic: "deploy-paths"}`; the infra guest
   ships last). `forgejo_pr_merge` without `confirm` shows `will_restart`:
   **say what restarts before you merge.** Docs-only changes deploy nothing.
2. **Everything else is deployed by hand, and recorded.** A compose stack not in
   that list: dispatch `ship.yaml` with `stack: <name>`. A service that runs from
   a git checkout (the working directory is in the unit's `WorkingDirectory`;
   which services: `knowledge {topic: "deploy-paths"}`): `git fetch && git merge
   --ff-only origin/main` (+ `uv sync` if dependencies changed), then restart
   **only when idle** — check the queue, health endpoint and journal for
   in-flight work first; if busy, schedule one check-in and come back.
3. **Ask first** (cypher-workflow B lane) before restarting anything public
   (`knowledge {topic: "public-services"}` lists the zones, and what they route
   to is public too; when in doubt it is public), any kill/destroy/delete, or a
   downtime window (quote when, how long, what).
4. **Prove it live** after: the service's health endpoint, metrics and journal —
   not just "active".

Deploying a compose stack is the `deploy-stack` Ansible playbook, never
`docker compose up` by hand on the host: an imperative change outside the IaC
loop breaks reproducibility. Details: `references/stacks.md`.

## 5. Hot-fix → backfill, in the same session

A hot-fix on a guest is allowed only to stop harm, and is never the end state:

```
hot-fix on guest ─► same session: PR the IaC so git == guest ─► verify byte-for-byte
```

- Edit the repo copy, merge, then make the guest **byte-identical**: compare
  `sha256sum` of the guest file and the repo file. Drift in comments is still drift.
- Prefer a systemd **drop-in** (`<unit>.service.d/<name>.conf`, kept in the repo)
  over editing an installed unit you have not reconciled.
- `systemctl daemon-reload` resets runtime fields in `systemctl show ExecStart`
  (start time, pid); compare settings, not that line.
- Record it in `logs/hotfix-<date>.md` and the repo's `STATUS.md`.

## 6. Secrets on guests

Load **cypher-secrets** for any credential. On guests specifically:

- File-mount is the default; an env var needs a "why" comment in `.env.template`.
- Never print a value; pass secrets through the gateway `secrets:` list.
- **No secret-bearing backups left behind.** Don't `cp env env.bak-<x>` and walk
  away: old copies keep rotated tokens alive and invite a rollback to stale
  config. If a rollback copy is needed, put it in `/root/rescue-<date>/` (mode
  0600), name it in HANDOVER.md, and `shred -u` it when the change is proven.

## 7. PRs

- Branch, never `main`; the author identity is `knowledge {topic: "git-author"}`;
  never `--no-verify`.
- **A Plane key or an exemption, or it cannot merge:** `refs OPS-123` /
  `closes OPS-123` in the title or body, or one line `plane: none — <reason>`.
- Review tier follows the ADR on review tiers: one full `review` per change set;
  scoped review or self-verify for small fixes. Tests: affected only —
  `bash factory/tests/<x>.sh` for factory scripts, `pytest scripts/tests/<x>`
  for scripts, plus `shellcheck -S warning`.
- Open and merge it yourself (`forgejo_pr_open` → `forgejo_pr_merge` with
  `confirm: true, delete_branch: true`); report what shipped · what restarted ·
  what's next.

## 8. Done means clean

Run the factory `clean-check.sh --run <slug> cypherops <other repos touched>`
from the current-main worktree. It must print `clean-check: OK`. Then:
worktrees removed, `STATUS.md` updated, guest files byte-identical to git, no
stray backups on guests, no debris committed (`history.txt` from the database
CLI, downloaded wheels, logs at the repo root). Something dirty that isn't
yours: rescue it to a dated scratch directory, compare with `main` **and the
live system**, then commit or drop it with evidence in a PR.

## 9. Gotchas

- Gateway `session_not_yours` / idle expiry → call `session_begin` again; a 502
  during a gateway update → wait 30 s and retry.
- `ct_exec` runs without `/usr/local/bin` on PATH; call tools by full path.
- `pgrep -f <name>` through `ct_exec` matches its own `bash -lc` line — send the
  script on stdin (`cmd: "bash -s"`) and filter.
- Services bind the guest address, not loopback; probe the address the unit binds.
- In an LXC, `/proc/meminfo` is the guest's own limit (lxcfs) — and a co-tenant
  can grow after any check you make. Don't trust a one-time RAM check for
  anything that can be OOM-killed; give the expendable service `OOMScoreAdjust`.
- An untracked file **identical** to one on `main` still blocks `git pull`;
  compare with `git show origin/main:<p> | cmp - <p>` before removing it.
- `git worktree remove` without `--force`: if it refuses, there is uncommitted
  work — rescue it, don't force it.

## References — load on demand

Open one only when the task is that job; do not read them all.

| Task | File |
|---|---|
| Add or change a compose stack, pick its target, deploy it | `references/stacks.md` |
| Write or index an operational runbook | `references/runbooks.md` |
| Add a shared sidecar or consume one (`extends:`) | `references/sidecars.md` |
| Add or debug a capability bundle, a denied tool call, a sub-agent bundle | `references/capability-bundles.md` |
| Bump, pin or hydrate an image tag; Renovate PRs | `references/image-tags.md` |
| Hostnames, tunnel, Access, mTLS, step-ca, split-horizon DNS | `references/cloudflare-mtls.md` |
| Deploy a Cloudflare Pages site; add a Pages project | `references/pages-deploy.md` |

## Knowledge topics this skill calls

`estate` · `deploy-paths` · `public-services` · `git-author` · `ingress` ·
`identity` · `observability` · `registry` · `capability-bundles` · `pages-deploy`.
If one answers "no such topic", say so and stop short of guessing the value.
