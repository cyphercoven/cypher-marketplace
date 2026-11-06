# Skill sources

Copied from the synced skill dir on 2026-10-25; sha256 of each source SKILL.md (before S-24 edits).

| skill | source path | sha256 | date |
|---|---|---|---|
| cypher-workflow | `<synced skills dir>/cypher-workflow/SKILL.md` | 41b5e5bd344028514571884cac3826963a6cb43bfe3f884caee6dfcf6dde45ba | 2026-10-25 |
| cypher-spec | `<synced skills dir>/cypher-spec/SKILL.md` | 528d9393614e504166c7d519130e791a4496d2f58ca4742c4a1d2c5c2ffef402 | 2026-10-25 |
| cypher-design | `<synced skills dir>/cypher-design/SKILL.md` | cc1f8651247981f369f68365e2d7b01a3099a54b3eb4ed48ea3282308d6e1664 | 2026-10-26 |
| cypher-mirror | `<synced skills dir>/cypher-mirror/SKILL.md` | 37fe1bb96da4083627782179425d5885976a5e7b0d5421c9afc2c79037c8d60b | 2026-10-25 |
| cypher-secrets | `<synced skills dir>/cypher-secrets/SKILL.md` | 40830d48cd52b62d755be4e0d4d35f7b6e1b2fcdc58f6ac9748839f557a521dc | 2026-10-25 |

## Re-diff 2026-10-25 (tI2a)

Each plugin skill was re-diffed against its live source before editing. All five live SKILL.md files still hash to the sha256
above, so no upstream change was carried over. The expected `cypher-workflow` instruction on which tools to use for writing
(the gateway's `workspace_edit` / `workspace_grep` / `workspace_glob`) has not landed upstream yet; carry it over when it does.
The plugin copies differ from the sources only by the S-24 edits and the tI2a ruling edits (secrets, workflow, design).


## Re-diff 2026-10-26 (tJ)

`cypher-design` live source changed (sha256 above, 363 lines). Ported every missing or older rule: canvas page/row layout, post-its, flow rows, icon tiers, avatars and first names, forms/tables/list leads, casing, extensions page, Servers on Today, render budget, checklist items. Personal facts stay out (portrait fixture and naming come from `knowledge {topic: "design-fixtures"}`). Canvas layout/sizing and rhythm/forms moved into `canvas-layout.md` and `spacing-and-forms.md` beside SKILL.md (S-45 300-line cap).

## Re-diff 2026-10-26 (orchestrator, cypherops main merge)

cypherops main changed its repo copy `docs/agent/cypher-workflow.md` (a8f3c50c, 6154ad49, 96d8e465) while this run turned it into a pointer. Ported into `cypher-workflow`: the "Changing a file" table and no-shell-rewrite rule (the instruction tI2a was waiting for), the contract/registry tests line under *Affected tests*, and the self-starting handover (`run_once_at`, never `fire_trigger`; handover tasks disabled, never deleted). Owner name replaced by "the product owner".

## Re-diff 2026-10-30 (tK1, S-59)

Compared against the live copies at cypherops `origin/main` a1d2fa19 and cypherui `origin/main` 8e504776 (the synced skill dir for spec, mirror and secrets, which have no repo copy).

| skill | live source | sha256 | result |
|---|---|---|---|
| cypher-workflow | cypherops `docs/agent/cypher-workflow.md` | bc3f79dd9f788e7bfb7a8a4c38c2b651e6a90f6b9a97c2b282cd5cad5efb4757 | ported: clean-check gate, YOUR INPUT NEEDED block and "ask goes last", semver-driven `ds:sync` (ADR-0075), 2026-10-30 handover (paste line, no self-start). Host steps moved to `hosts/` (S-60) |
| cypher-spec | synced skill dir | 528d9393614e504166c7d519130e791a4496d2f58ca4742c4a1d2c5c2ffef402 | unchanged; only S-60 host move |
| cypher-design | cypherui `docs/agent/cypher-design.md` | f58156701211b1fb96fc9e7a669e8ff8f54956de34de7a3c6cfd42b0fc587311 | ported into `kit-versions.md` (semver render rule, Brandfetch marks, `cu-rows`, character avatars, charts, rows, brand pages, descriptions); machine names via `knowledge` |
| cypher-mirror | synced skill dir | 5c7c9853ca1e50ddb0eee5626a219d2d436a7e8157eb15feefbe616175b27284 | ported: "Render by kit version" decision table; S-60 host move |
| cypher-secrets | synced skill dir | 40830d48cd52b62d755be4e0d4d35f7b6e1b2fcdc58f6ac9748839f557a521dc | unchanged |

The synced `cypher-design` skill (ae71f964e280…) and `cypher-workflow` (cce0c11c649d…) differ from the repo copies above; the repo copies were taken as the live source, as the brief names them.
