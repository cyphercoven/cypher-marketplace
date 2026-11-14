---
name: "cypher-systems-thinking"
user-invocable: false
description: "Use when designing Cypher architecture, specifying features, planning implementation or migrations, decomposing work, or reassessing a plan after new evidence. Connect every proposed change to system goals and documented architectural principles, and evaluate whole-system effects before local detail."
---

# Cypher systems thinking: purpose → system → intervention → evidence

last_verified: 2026-11-04

Every component and implementation step must contribute to the underlying goals of the system. A locally useful feature or an independently working service is insufficient justification. Start with the whole, choose the intervention that improves it, and keep the connection visible while building.

Load `cypher-workflow` first. This skill owns the reasoning approach; `cypher-architecture` owns architectural rules and conformance. It adds no product gate or authority to change scope, settled architecture or live systems.

## When to apply it

Use before non-trivial architecture, spec, design, implementation, operational-change or migration planning; when decomposing or delegating that work; and when evidence challenges the plan. Reuse an existing current system view. A bounded factual correction or mechanical edit needs only a brief goal-and-impact check, without creating a separate document. Contain an active incident safely first, then reassess before the lasting fix.

## 1. Establish purpose and governing architecture

Read the actual sources, following `cypher-workflow` precedence. Identify the relevant system goals, intended user outcomes, constraints, non-goals and observable success criteria before selecting components or technology.

**Required architecture grounding:**

- Read `cyphercore/sections/suite-vision.md`, `suite-end-state.md` and `suite-architecture.md` for the relevant goals, intended direction and cross-suite principles. Distinguish target state from current capability.
- Load `cypher-architecture`; read the relevant material it owns and references. Start at `cypherops/docs/adr/README.md`, then read applicable accepted ADRs and amendments, including contract-first ADR-0024, architecture-conformance ADR-0025 and language-choice ADR-0078 when relevant.
- Inspect `cypherops/architecture/workspace.dsl`, its included model/views and generated `workspace.json`, relevant component documentation/ADRs under `cypherops/architecture/`, governing contracts and conformance configuration. Use the canonical editable source; generated artifacts are evidence, not a second authority.
- Read affected repos' `STATUS.md`, local instructions, relevant ADRs and approved INTENT/SPEC. Follow links to the sources that actually govern the proposed change.

Record a compact **principle → source/section → implication for this decision → verification** map in the existing spec or plan. Include applicable ownership, dependency direction, functional-core boundaries, contract/schema authority, identity and trust, data/audit ownership, deployment responsibility, reuse/composability and language constraints. Mark a principle not applicable only with a reason. Do not treat this list as exhaustive or substitute it for the documented principles.

Do not invent missing goals or silently resolve contradictory sources. Mark assumptions and uncertainty; investigate decision-critical gaps. A running deviation is evidence to reconcile, not permission to abandon architectural intent. Route an actual change of goals or principles through the existing decision/spec process and record it in an ADR before conflicting implementation. Continue independent work within the approved scope.

## 2. Map the system before decomposing it

Make a small diagram where relationships matter, supported by concise notes:

- People and outcomes; system boundary and external dependencies.
- Existing capabilities, owners, sources of truth, contracts, data/control flows and trust boundaries.
- The complete journey from trigger through side effects to the user-visible result, including failure, recovery and operation.
- Relevant constraints, bottlenecks, shared resources, feedback loops and delays.

Distinguish observed facts from hypotheses. For each important causal claim, say why the intervention should improve the outcome and what evidence could disprove it. Consider reinforcing/balancing feedback, accumulation, queues or capacity only where they affect the decision. Avoid a catalogue of unrelated services.

## 3. Choose an intervention for the whole

Compare the meaningful options, including reusing or extending an existing capability and leaving the system unchanged. Present one recommendation with its rationale.

Assess total system effects: coupling, duplicated authority, operator effort, reliability, security/privacy, capacity, costs, downstream burden and transition risk. Consider delayed effects, failure propagation and who pays for a local improvement elsewhere. Prefer the smallest coherent intervention that advances the system goal and respects its principles; fewer components alone is not the objective.

For **each** proposed component and work item, record:

`system goal → required capability or constraint → proposed change → observable contribution`

Enabling work, tests and maintenance may contribute indirectly: name the dependency or risk they address and how that supports the goal. Do not manufacture metrics to justify an unrelated item. If the contribution is absent, challenge, remove or defer the item. A broader goal discovered during planning is a proposal, not automatic scope expansion.

## 4. Plan integrated outcomes

Write this into the existing SPEC/PLAN rather than creating a parallel planning bureaucracy:

- A short system view and source-backed principle map.
- The recommended intervention, tradeoffs, assumptions and unresolved decisions.
- Outcome-oriented slices with goal trace, owner, dependencies, affected boundaries and acceptance evidence.
- Necessary contract/model/schema changes before their consumers, integration points, operational readiness and safe transition/rollback where applicable.
- End-to-end success measures and failure/recovery checks that demonstrate system benefit, alongside the affected tests.

A technical prerequisite can be its own slice, but name the journey it enables and its integration acceptance. Components passing in isolation do not establish system completion. Do not measure success by files, tasks or services produced.

## 5. Zoom out while executing and reviewing

At slice boundaries, before integration/release, and when a new dependency, repeated failure, bottleneck or scope change appears, revisit the system view:

1. Does this work still contribute to the approved goal and respect its governing principles?
2. Has evidence changed the causal model, dependencies, constraint or best intervention?
3. Are we improving the whole journey or moving the problem to another component/person?
4. What remains necessary for the system outcome, and what detail can now be dropped?

Update the existing plan and findings list, then continue in dependency order. Use `cypher-workflow`'s full-scope passes and batched fixes; do not restart broad analysis for every edit. Reopen only decisions affected by evidence, and retain settled constraints.

Review checks goal traceability, principle conformance, cross-boundary effects and complete-journey evidence. Report the outcome achieved, remaining system blockers and assumptions still unverified. Preserve the distinction between unit/fixture evidence, integrated behavior, deployed behavior and owner UAT.
