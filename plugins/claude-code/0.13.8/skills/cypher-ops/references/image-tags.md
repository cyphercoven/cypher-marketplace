# The `versions.yaml` image-tag manifest

PURPOSE: how every container image tag the suite runs is pinned in one manifest,
hydrated into per-stack `.env.template` files by `scripts/sync-versions.sh`, and
tracked by Renovate. Load it from the `cypher-ops` core when bumping, pinning or
hydrating an image tag, or triaging a Renovate PR.

Rules:

- Image tags never appear inline in a compose file. `image: foo:1.2.3` and
  `image: foo:latest` are both regressions; pin always.
- Compose files reference an env var: `image: foo:${FOO_TAG}`. The name is the
  manifest key uppercased with hyphens turned into underscores
  (`step-ca` → `STEP_CA_TAG`).
- `versions.yaml` is the single source of truth. `.env.template` is **generated**
  (never hand-edited — the next sync reverts it); `.env` is hydrated at deploy
  time from the template plus injected secrets and is never committed.
- Bumping a tag is a one-line edit to `versions.yaml` plus a re-run of
  `sync-versions.sh`. Never edit a compose `image:` to roll forward.

## Why a central manifest

Inline tags make drift invisible (three stacks, three versions), force a bump to
touch every compose file, give Renovate nothing clean to open a PR against, and
defeat reproducibility ("I can rebuild this exact state" needs one place to look).

## Anatomy

```yaml
<service>:
  tag: "<version>"
  registry: "<registry>/<image>"
  renovate:
    datasource: "docker"
    depName: "<registry>/<image>"
```

Each top-level key is a service or upstream component; `tag` is the value,
`registry` is where the image lives, `renovate` is what the bot uses to track
upstream releases. Which registry the first-party images use:
`knowledge {topic: "registry"}`.

## Hydration

`scripts/sync-versions.sh` walks the manifest and writes `<SERVICE>_TAG=<tag>`
lines into every stack's `.env.template`. `docker compose up` then reads `.env`
automatically. The split: `.env.template` is committed, version pins only; `.env`
is the full env including secrets, never committed.

## Renovate

Renovate runs on the infra guest, daily, watches `versions.yaml`, and opens a PR
per available upgrade: `chore(deps): bump <service> from X to Y`. Triage in the
cypherops repo:

1. CI runs the matrix (ansible-lint, opentofu plan, compose validate).
2. Green and non-breaking (patch/minor on a service the suite has run) → merge.
3. Major or breaking → leave it open until the owner has read the upstream
   changelog.

Schedule, per-package strategy and rebase behaviour live in `renovate.json` at
the repo root.

## Bumping manually

For a security advisory, a blocking bug or a planned upgrade:

```sh
# edit versions.yaml: change <service>.tag
scripts/sync-versions.sh
git commit -am "chore(deps): bump <service> from X to Y"
```

The commit body must say **why** (advisory id, upstream changelog entry). Then
deploy the stack that uses it (core §4); a bump that is merged but not run is
only half done.

## Anti-patterns

- Inline or `latest` tags (the rule the whole flow exists to enforce).
- Hand-editing `.env.template`.
- Bumping without running `sync-versions.sh` — the stack keeps its old template
  and the bump does not take effect. CI should catch it; do not rely on CI.
