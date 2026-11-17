# Checkpoint context and result examples

Keep context, check logs and result JSON under the run's scratch directory, outside the Git repository. Point plan at the existing factory PLAN.md or assigned plan artifact. Context and results are runtime evidence, not another committed backlog.

## Context

Use schema_version 1 and policy poc-first-v1. Example shape; replace every placeholder with verified values:

    {
      "schema_version": 1,
      "policy": "poc-first-v1",
      "run": "approved-run-slug",
      "scope": "feature-or-job-scope",
      "repo": "/work/app",
      "base": "verified-base-commit",
      "plan": "/work/app/PLAN.md",
      "state_dir": "/work/state/run",
      "implementer": "actual executor identity",
      "paths": ["src/feature/**", "src/callers/**", "tests/feature/**", "tests/callers/**"],
      "acceptance": [
        {
          "id": "S-12",
          "phase": "poc",
          "criterion": "One self-contained, observable job acceptance statement",
          "paths": ["src/feature/**", "src/callers/**", "tests/feature/**", "tests/callers/**"]
        }
      ],
      "dependencies": {
        "src/feature/**": ["src/callers/**", "tests/callers/**"]
      },
      "leaf_paths": ["src/callers/**", "tests/feature/**", "tests/callers/**"],
      "checks": [
        {
          "id": "feature-tests",
          "paths": ["src/feature/**", "src/callers/**", "tests/feature/**", "tests/callers/**"],
          "argv": ["pytest", "tests/feature", "tests/callers"],
          "kind": "test",
          "phases": ["feature-review", "production-admission"]
        }
      ],
      "planning_inputs": ["/absolute/path/to/approved-intent-or-contract"],
      "config_paths": [],
      "external_state_paths": [],
      "security_triggers": [],
      "broadening": {"reason": "", "paths": []},
      "admission_required": false,
      "poc_prerequisites": []
    }

Use the exact approved job criteria, not invented summaries. Include the relevant S-ID and excerpt in acceptance. Add all changed code and contract paths to paths; map each source glob to its reverse dependants in dependencies. Use leaf_paths only when the path is known to have no dependants. If impact is unknown, resolve it before dispatch or record a bounded broadening reason and paths. Do not use a whole-suite check unless the context records why it is required.

Planning inputs, approved intent, contracts and relevant configuration must be named in the plan and represented in context inputs that should invalidate the assessment. Use paths/dependencies for tracked implementation and contract impact; use planning_inputs for approved intent, planning assumptions and contract files, config_paths for decision/config files whose content must be hashed, and external_state_paths for relevant external-state files. Never include secret values. Do not make expected implementation output invalidate the epic planning decision by itself; changes to approved intent, planning criteria, contracts, dependency assumptions or decision-critical configuration require a fresh planning assessment.

## Resolve and run measured checks

Bind the context to the active host session once when supported, then follow this order:

    python "${CLAUDE_PLUGIN_ROOT}/scripts/improve_checkpoint.py" bind --context <context.json> --session <session-id>
    python "${CLAUDE_PLUGIN_ROOT}/scripts/improve_checkpoint.py" resolve --context <context.json> --phase <phase>
    python "${CLAUDE_PLUGIN_ROOT}/scripts/improve_checkpoint.py" run-checks --context <context.json> --phase <phase>
    python "${CLAUDE_PLUGIN_ROOT}/scripts/improve_checkpoint.py" record --context <context.json> --phase <phase> --result <result.json>
    python "${CLAUDE_PLUGIN_ROOT}/scripts/improve_checkpoint.py" check --context <context.json> --phase <phase>

Supported phases: epic-planning, plan, refinement, feature-review, production-admission. Complete epic-planning before plan permits implementation dispatch. Unspecified check phases default to feature-review and production-admission; security checks also default to epic-planning. Planning does not require future implementation acceptance tests to pass. Inspect resolve's missing, impacted_paths, pending_checks, reused_checks and request_digest. Repair incomplete scope/context before continuing. run-checks executes only selected argv lists and stores measured logs in state_dir. Build the result from the latest request_digest, exact assessment and job criteria; save it outside the repo. Then record it and require check to report allowed before the dependent transition. Exit 1 means a valid checkpoint is missing/stale or a required check failed; exit 2 means invalid context or an error. Do not retry unchanged failures in a loop.

When a new commit changes no relevant in-scope content, preserve prior evidence with its ancestry/provenance; no new model review is needed just because HEAD moved. When relevant code, caller, contract, config, dependency or external-state content changes, resolve the affected delta, rerun invalidated checks and record why unaffected evidence remains valid.

## Result

Example for a feature review; each required acceptance ID must have a specific observed result:

    {
      "schema_version": 1,
      "outcome": "pass",
      "request_digest": "<latest resolve request_digest>",
      "summary": "Integrated feature satisfies the listed job criteria.",
      "assessment": {
        "risks": "Affected boundaries and remaining risk.",
        "security": "Risk-triggered check/review and limits.",
        "systems_fit": "Outcome, contracts and integration fit."
      },
      "reviewer": "independent reviewer, distinct from implementer",
      "reviewed_paths": ["src/feature/module.py", "tests/feature/test_module.py"],
      "criteria": [
        {"id": "S-12", "outcome": "pass", "evidence": "Observed response and test log reference."}
      ],
      "findings": []
    }

For feature-review and production-admission, reviewer must differ from implementer and reviewed_paths must cover resolved impacted_paths. Every requested criterion needs evidence. Report findings as resolved or deferred. Security/current-journey blockers cannot remain; other deferred findings need category, severity, owner and evidence. At production admission, P0–P2 findings cannot remain unresolved.

## Owner POC approval before refinement

The POC context above deliberately has no approval. POC review, demonstration and safe preview remain possible. Refinement and production admission refuse with required_phase owner-poc-approval until every listed prerequisite has a valid owner decision. A plan packet tagged refinement or production is guarded too. Spec approval, a passing model review and tests do not substitute for POC approval.

After the owner approves a shown POC, the later refinement context names the stable prerequisite:

    "poc_prerequisites": [
      {
        "id": "stable-app-poc-id",
        "milestone": "approved-poc-milestone",
        "scope": "Exact scope the owner approved",
        "acceptance": [
          {"id": "S-12", "phase": "poc", "criterion": "Exact shown POC acceptance"}
        ],
        "demo": {"reference": "shown-demo-or-artifact-reference", "revision": "shown-revision"},
        "approval": "/absolute/path/to/recorded-owner-decision.json"
      }
    ]

Approval artifact schema only; do not create this decision before actual owner approval:

    {
      "schema_version": 1,
      "decision": "approved",
      "poc_id": "stable-app-poc-id",
      "milestone": "approved-poc-milestone",
      "acceptance_digest": "<digest of prerequisite acceptance list>",
      "demo_digest": "<digest of prerequisite demo object>",
      "scope_digest": "<digest of prerequisite scope string>",
      "provenance": {
        "kind": "owner-chat",
        "reference": "<actual owner message reference>",
        "quote": "<actual owner approval wording>",
        "recorded_by": "<identity recording the decision>"
      }
    }

Compute these values with scripts.improve_checkpoint.digest using the exact prerequisite values. The function uses SHA256 of sorted compact JSON. This records manual owner-chat provenance; it does not claim cryptographic owner authentication. Never use synthetic fixture approval as a real decision.

Each prerequisite has its own id, milestone, acceptance, scope and shown demo. Approved POCs can wait and later be combined by listing them; approval never automatically starts refinement. Expected implementation edits do not alter the stable approval binding. Changed shown acceptance, scope or demo needs the corresponding owner decision. Acceptance phase values are poc, refinement or production; local jobs carry their current phase only.

## Review packet and production boundary

A delta review receives the self-contained numbered job acceptance packet (exact relevant S-IDs/excerpts, invariants/interfaces, out-of-scope paths, dependency/integration contract, exact verification and expected outputs), the actual changed delta, valid prior evidence and changed-input summary. It does not fetch the full epic SPEC by default. Planning may derive the packets from the approved full scope. If a criterion is missing or conflicts with approved intent, STOP and identify the exact unresolved clause; do not silently broaden to a full-spec scan. Only final release/admission checks full approved-spec traceability and records full_spec_fit.

### Final admission only

Load this section when performing final production admission; delta jobs do not load the full epic spec. Add:

    "full_spec": {
      "path": "/absolute/path/to/approved/SPEC.md",
      "criteria_path": "/absolute/path/to/complete-release-criteria.json"
    }

The criteria file is a JSON list, or an object containing criteria, using the same id/criterion schema. Its IDs must exactly match every unique canonical S-NN Markdown heading in SPEC.md; omitted IDs or unsupported formats refuse admission. The final request binds hashes of both files. Its result needs assessment.systems_fit, assessment.full_spec_fit and passing criteria observations for every requested release ID, alongside current independent feature evidence and owner POC prerequisites. This is later production readiness, not the initial POC gate.

Before an actual PR-merge call, bind the exact remote target in context and refresh the relevant checkpoint:

    "merge_target": {
      "repo": "exact-owner/exact-repository",
      "number": 123,
      "head": "<declared PR head commit>"
    }

The hook matches repo and number exactly, requires local HEAD to equal the declared head, and refuses dirty/untracked merge sources. It does not infer bare-name aliases or query the current remote PR head: record target metadata from a fresh PR inspection and do not claim the hook verified remote PR contents. This is local target binding, not a universal gateway authorization layer. Agent/Task assignment remains operator-managed; the factory adapter additionally pins its actual repository and brief. Native Codex arbitrary dispatch and commands are not intercepted.

The actual PR-merge guard requires production-admission evidence only when its context sets admission_required to true. Ordinary POC merges leave it false or omitted; POC preview remains possible before production readiness. Never invent a production MCP tool name or claim a transition is guarded unless the host actually mediates it.
