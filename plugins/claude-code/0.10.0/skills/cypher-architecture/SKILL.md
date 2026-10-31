---
name: "cypher-architecture"
description: "Load when starting a new service, crate, package, public interface or public name in any cypher* repo, or when a change adds a cross-service dependency or alters an API, event or schema. Owns contract-first APIs, the architecture model as the dependency allowlist, ring layering and non-escapable gates, where packages and images are published, and brand versus token naming."
---

# Cypher architecture: contracts, dependency direction, distribution, names

This skill owns the architecture rules A-01..A-12 (`rules/rules.yaml`). How code is written inside a service is `cypher-dev`; lane and gates are `cypher-workflow`. Tool names, registry paths and addresses come from the gateway's `knowledge` tool at run time, never from here.

## When to load this

Load it when any of these is about to happen in a cypher* repo:

- a new service, crate, npm package, container image or public name
- a service starts to call another service, or an API, event or database schema is about to change
- an import crosses a service or layer boundary
- something is about to be published, or a build needs a package from another repo

Do not load it for a bug fix that touches no interface, a prose-only change (use `cypher-docs`) or an ops action on a running system.

## 1. API contracts

The contract is the agreement. For our own APIs there is no outside source of truth, so the contract is the source of truth, and it is settled before the code that implements it.

- **Contract first (A-01).** Changing an interface means changing the contract, a reviewed change, and only then the code. Never invent an internal interface in passing. If a task needs one that does not exist, stop and get the contract agreed.
- **Generated, not hand-written (A-02).** Types, clients and server stubs come from the contract, so they cannot drift. Hand-editing a generated type means the contract is wrong: fix the contract and regenerate.
- **Events are contracts too (A-03).** Anything streamed or published (transcripts, change notifications, job lifecycles, the hand-off of a fetched item to the next service) gets a message contract exactly as request and response APIs do.
- **Transport is a late, reversible choice (A-04).** Do not reach for a message broker because pub/sub sounds right. Use one only when a flow needs durable, multi-consumer fan-out that the datastore's live queries and the pieces already in the stack cannot give.
- **The brief names the contract (A-05).** A brief that builds or calls a service names the governing contract and where it lives. The contracts sit beside the architecture model in the ops repo and every service consumes them at build time.

## 2. Architecture conformance

The architecture is enforced, not requested. A boundary you can cross with an import is not a boundary unless something fails the build when you do.

- **The model is the allowlist (A-06).** The architecture model's relationships list which service may depend on which. No edge from A to B means A may not import B's client. A new cross-service dependency is a model change first.
- **Dependencies point inward only (A-07).** Inside a service the rings are:

  ```
  core (pure, ring 0) ◄ adapters (I/O at the edge, ring 1) ◄ composition (fetchers, rooms, api, scheduler) ◄ entrypoint
  ```

  A ring may depend only on rings inside it.
- **Purity is verified, not trusted (A-08).** `core` holds no I/O: no http, socket, filesystem or database imports, no clock or randomness, no module-level mutable state. Its functions return a `Result`. A side effect belongs in an adapter.
- **Schema has one source (A-09).** The schema is migrations plus a checked-in snapshot. The gate applies the migrations to a fresh database and fails on drift from the snapshot. Change the migration and the snapshot, never the live database.
- **Gates are non-escapable (A-10).** No inline `noqa`, `eslint-disable`, `#[allow]` or config carve-out may silence a conformance gate. A failing gate means the code is wrong, or the model must change first. It is never the gate being in the way.

Before you add a cross-service import, check the model has the edge. Before you put logic in `core`, check it is pure. Before you touch the schema, change the migration and snapshot.

## 3. Package and artifact distribution

- **One home (A-11).** The self-hosted forge is the single home for everything a cypher* repo produces for another to consume: git refs, CI, npm packages in the `@cyphercoven` scope, and built container images. GitHub is a push-mirror for backup and recovery only. It hosts no live package, serves no deploy artifact and runs no automation.
- **Two registries, two jobs.** The npm registry holds shared libraries, consumed at build time; a repo maps the scope to the forge in its `.npmrc`. The container registry holds built images, consumed at deploy time.
- **Build once, deploy from the ops repo.** A product repo builds its image, pushes a version-tagged copy, then dispatches the matching ops deploy workflow with the version. The ops repo pulls that exact tag. Nothing is rebuilt on the far side, and no deploy reaches into a producer's source tree.
- **No GitHub Actions, anywhere.** All CI and CD run as forge workflows on the home runners. A `.github/workflows` file is legacy to retire. New automation is authored as a forge workflow from the start.
- If a build or deploy depends on GitHub being reachable, that is a bug to migrate, not a pattern to copy. If a registry path or token scope is needed, ask the gateway's `knowledge` tool.

## 4. Naming

- **Brand names (A-12)** are CamelCase in prose, headings, UI copy and labels: `CypherFlix`, `CypherUI`. `CypherUI` and any other `CypherXXX` abbreviation stay upper case.
- **Technical tokens** are always lowercase: shell commands, paths, package names, repo names, hostnames and compose service names. `container_name` equals the compose service name, in lowercase-kebab.
- **An interim stack does not borrow the brand it stands in for.** A stopgap uses a plain descriptive name (`legacy-media`, not a `cypher*` name) until the real product replaces it.
- **Community and social brands** are not suite components. They keep their own casing and are never given the `Cypher` prefix.
- **Person-facing text** says `Cypher` or `cypherops-mcp`, never the retired internal name of the gateway.

Test for a new name: say where it appears. Prose and UI get the brand form; anything typed or parsed gets the lowercase token.

## 5. A new thing, in order

1. Name it (section 4) and check that no interim name is being reused.
2. Find or write its contract (section 1) and put it in the ops repo before any code.
3. Add its edges to the architecture model (section 2) before importing across a boundary.
4. Decide where it publishes (section 3). Never add a GitHub-hosted package or workflow.
5. Run the repo's conformance gates once with the change set, then hand the work to `cypher-review`.

## Edge cases

- **The spec and the model disagree.** Stop. The model is the allowlist, so ask for the spec or the model to be corrected; do not satisfy the spec with an unlisted import.
- **A gate fails on code you did not touch.** Report it with the gate's output and fix it at source in its own commit; do not suppress it.
- **A leftover GitHub package or workflow still exists.** Leave it alone unless the run covers its migration; name it in the report.
