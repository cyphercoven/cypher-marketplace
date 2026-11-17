# Optional Orca supervision inside the current workspace

last_verified: 2026-11-16

PURPOSE: prepare one orchestration entry point for multiple agents, learning Orca as a long-term CypherMind foundation through bounded workspace trials.
CONVENTIONS: resolve the current workspace, runtime, factory and plugin locations through gateway knowledge/configuration; never copy a machine path into a reusable brief.
AGENT NOTES: Orca's purpose is common orchestration, not token savings. ContextMode is the separate token-efficiency experiment. This optional execution path is not yet a default launcher or unattended guarantee; cost savings are not a condition of Orca's usefulness or qualification.

## Scope and evidence

A desktop chat orchestrator can use the gateway's existing workspace execution and background-job tools to drive the installed Orca CLI inside the current Coder workspace. An installed CLI and its authenticated provider login are separate from the desktop chat's tools, subscriptions and plugin adoption. Production deployment, credentials and authorization remain gateway responsibilities.

The isolated trial proved an Orca-launched native Codex worker changed the permitted fixture line, passed its immutable verifier and made a real ContextMode MCP call returning the requested value. Native read-only flags did not establish whole-worker confinement: shell bwrap failed, separately approved exact commands ran outside that shell boundary, and ContextMode ctx_execute ran with the server account's permissions. ContextMode output isolation is not a security boundary. The first attempt stopped before its completion receipt. A corrected attempt explicitly authorized the conditional verifier-plus-worker_done operation, started its240-second watchdog at actual readiness, received an accepted worker receipt, and settled successfully before cleanup. This proves that bounded coordinator-managed handoff, not unattended operation without an orchestrator or comprehensive isolation. Codex shell confinement failed on the host's namespace boundary; a subsequent no-model legacy-Landlock probe timed out. Do not disable confinement or widen permissions to make this path run. Use a supported native host fallback only when it preserves the required permissions and confinement; if none is available, stop the dependent work. Never downgrade a required safeguard automatically.

Use these trials to learn the shared orchestration contract and prepare CypherMind's long-term multi-agent foundation. Qualification concerns permissions, lifecycle, acceptance and recovery, not a token-savings target. Replacing Coder or deploying a separate Orca host is outside this path; it belongs in the future CypherMind specification with cross-repository impact checks.

## Before one worker starts

1. Confirm approved scope and select one complete, bounded job acceptance packet: current phase, allowed files, exact worktree/base, plan digest, criterion IDs, affected verification commands and expected results, deferred work and STOP conditions. Routine executors and delta reviewers receive this packet, not the full epic SPEC.
2. Resolve the installed CLI/runtime and supported provider/model choices on the execution host. Check runtime status and exact worktree identity. Choose an economical supported model and effort; record requested/effective values rather than assuming the requested route took effect. Use existing authenticated native subscription CLIs only; no API keys, SDK or substitute model harness.
3. Run the existing factory improve-transition.py for epic-planning and plan (or authorized refinement), binding --plan-file to this exact packet and --repo-path to the actual execution worktree. Set its context and reviewed policy root through the existing supported configuration. The shared policy owns plan/acceptance digests and freshness; all required checks must allow before launch. A loaded skill or resolve output is not admission.
4. Verify explicit Ask permissions on the actual execution profile and agent. In the pinned Orca contract, supported RPC settings.mutateAgentLaunch accepts {"type":"permission","choice":"ask","agent":"codex"}; settings.getAgentLaunch reports the result. Legacy manual means own/provider configuration, not enforced Ask. Ask for Codex projects explicit read-only/on-request/user approval constraints. Verify effective launch configuration and absence of bypass arguments; do not change a shared profile or another session's settings.
5. Establish a bounded external wallclock watchdog before launch, starting its execution deadline only at the actual ready receipt, with a separate startup limit and one owned-worker limit; prohibit helpers unless separately scoped and admitted. worker-start --timeout-ms is startup readiness/transport time, not an execution or token cap. Do not claim factory token caps automatically apply. Include the exact conditional affected verifier followed by the worker's own worker_done command in the packet; the worker must wait for its accepted CLI receipt before ending. On a required approval, the orchestrator promptly inspects and approves a single exact authorized operation through the supported permission mechanism; this is not an owner UAT gate. A missing mechanism or host refusal blocks that operation; never replace it with a standing allow, broad bypass or disabled confinement.

The gateway execution call can invoke this existing preflight and the version-matched Orca commands sequentially; no additional wrapper framework or MCP service is required. This is explicit orchestration mediation only: raw Orca commands and native dispatch are not universally intercepted.

## Version-matched command contract

Use the installed CLI's --help and bundled orchestration skill; the verified reference is Orca v1.4.261. Resolve the executable instead of assuming its name or location. These examples use orca as a placeholder for that resolved executable:

    orca status --json
    orca orchestration worker-start --spec-file <packet> --worktree <exact-selector> --agent codex --model <supported-id> --effort low --timeout-ms <startup-ms> --json
    orca orchestration worker-show --dispatch <dispatch-id> --json
    orca orchestration worker-read --dispatch <dispatch-id> --source auto --limit 50 --json
    orca orchestration check --wait --types worker_done,escalation,question --timeout-ms <bounded-wait-ms> --json

Use explicit run/caller context when the installed CLI requires it. Existing worktrees reject creation flags. New child/top-level placement requires its appropriate repository selector; setup run/skip/inherit controls repository setup, not authorization. --effort requires --model; neither combines with reuse of an existing --terminal. Prefer --spec-file so packet text does not become shell code.

Capture the full start receipt, including run/task/dispatch, actual worktree, setup, mode, requested/effective launch and residual resources. Exit zero or a ready launch is not completed work. A missing observation or unknown outcome is not success. Process every delivered message; acknowledge deliveryId only when the returned deliveryAcknowledged contract requires it. Reacquire runtime-scoped handles after restart.

## Acceptance, failure and cleanup

- Independently inspect the exact diff and criterion outcomes, immutable checks and worker output/receipt. Preserve source/runtime revisions, base/head, packet/acceptance digests, actual commands/results, reviewed delta and applicable prior evidence. Follow the existing integrated review checkpoint; do not invent an extra full-spec task review.
- An accepted worker_done report and dispatch settlement are separate from controller-observed code passing tests. A stopped, abandoned, failed or unknown dispatch never becomes worker success. Record passing fixture observations alongside the actual failed/incomplete handoff, without sending worker_done on the worker's behalf. Do not claim owner POC acceptance or production readiness from either.
- On startup uncertainty, inspect worker-show and recovery actions before another start. --retry-of needs the task and explicit repeated placement/agent choices; it does not inherit them. No silent retry or deadline extension.
- For an authorized exact cancellation, worker-stop fences that dispatch and attempts its owned stop; stopping/stop_unknown is not proof of exit. worker-abandon fences an assignment while retaining possibly live resources, and is not cancellation.
- After actual settlement, worker-release releases only the proven owned resource. Respect release_pending/release_unknown and its recovery action; do not substitute broad terminal close. Save bounded worker-read evidence before cleanup and use its post-release archive when available.
- Stop only owned trial runtime/daemon processes. Check native-provider configuration and hook side effects; restore only exact Orca-owned changes, preserving ContextMode, concurrent hooks and user configuration. Keep uncertain artifacts and report them. Do not delete other sessions' worktrees or processes.

ContextMode requires actual worker tool-call/result evidence, not just installation, hooks or a prompt claim. A successful MCP call establishes that tool integration only; its executable code has the MCP server account's authority and does not inherit native shell confinement; it does not prove all-output interception, every hook working or token savings. Keep receipts private in the existing run evidence location; Orca artifacts share publishes a public link and is not a private worker evidence store.

## One maintained source, provider adapters

Maintain Cypher skills and checkpoint policy once, with thin provider discovery/configuration/hook adapters. Orca can be a common orchestration entry point; it does not currently replace every native plugin installation automatically.

| Boundary | Verified Orca support | Required limit |
|---|---|---|
| Skills | Canonical .agents/skills plus provider placements; Codex uses the canonical root, Claude its native skill directory. | Managed distribution still creates agent-discoverable placements; it is not universal prompt injection. |
| Launch and prompt guards | Orca plugin hooks can deny/rewrite its terminal launches and submitted prompts, including launches routed to SSH/WSL. | Resumes/restores and person-entered prompts bypass the relevant hooks. Error behavior defaults to pass; a guard must explicitly select onError deny and verify coverage. |
| Tool guards | Local Claude can wait for a tool deny/input decision. | Other agents report only; SSH/WSL tool hooks are absent. Retain native guards for blocking parity. |
| Result acceptance | The coordinator can require the shared checkpoint before accepting work or merging. | No completion/merge hook is present in the enumerated plugin-hook contract; controller mediation is not universal interception. |
| MCP | Native configurations, account/session-specific status and sign-in controls are exposed; Codex mirrors native configuration into its runtime home. | Configuration and authentication remain provider/execution-host concerns; do not assume one shared authenticated MCP session. |
| Plugin packaging | Orca has its own manifest and trusted-worker hook API. | Its skills and mcpServers contributions are reserved and must be empty in the pinned version; existing native plugin packages are not interchangeable. |

A central Orca launch/prompt adapter calling the existing Cypher checkpoint policy is a prospective integration, not implemented by this candidate. Preserve current native guards, exact job packets and gateway authorization. Centralization must not discard per-tool enforcement or claim coverage for actions outside Orca.

These boundaries are defined by the pinned [manifest](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/docs/reference/plugin-manifest.md), [hook contracts](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/shared/plugins/events/plugin-hook-payloads.ts), [tool decision handling](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/main/agent-hooks/tool-events/agent-tool-plugin-hooks.ts), [skill placements](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/shared/skills/installation/skill-install-providers.ts) and [Codex configuration merge](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/main/codex/configuration/settings/codex-config-mirror-merge.ts). These contracts establish native placements and configuration, not a universal Cypher package.

## Refresh Cypher assets during release

The Cypher release/adoption procedure owns updates to its supported, in-scope Orca integration. This means Cypher assets used by workers, not upgrading the Orca binary. Keep both ChatGPT and Claude desktop plugins installed and updated through their existing host procedures. No session-start update hook is added.

1. Resolve the published Cypher version/source digest and the actual execution host. Inventory only Cypher-owned skill placements and any implemented hook bindings/MCP configuration. Record absent or unsupported integration as not configured; this candidate does not implement a central Orca hook adapter or MCP distributor, so neither can be reported refreshed.
2. Refresh supported, owned assets from that same verified release. The pinned Orca skills install/update command accepts only Orca's bundled skill names; do not use it to install Cypher. For a separately managed skill placement, the existing skills CLI supports a released local source directory, explicit skill names and explicit provider targets, for example:

       npx skills@<verified-cli-version> add <verified-release-directory> --skill <selected-skills> --agent claude-code codex --global --yes

   Inspect the installed CLI help and existing ownership/source registration first. Select the actual installed providers; do not use --all or overwrite modified/unowned placements. A canonical skill copy plus provider links can reduce duplicate content, but this is skill distribution only: it does not install native plugin hooks/MCP or scripts outside the selected skill folders. Check any plugin-root, script and reference dependencies against the complete release before adopting standalone placements. Preserve existing native plugin discovery and prevent duplicate/shadowing skills; where compatible managed placement is absent, retain native plugins and report that boundary.
3. Verify installed skill files/digests and provider discovery against the release; verify existing supported hook bindings and MCP configuration/status through the respective native host interfaces without copying authentication secrets or assuming a shared login. Preserve native blocking guards, active workers, their pinned release and concurrent configuration. Do not reload, restart or widen permissions merely to mark adoption complete.
4. Record version, source, owned targets, checks, skips and active-worker pins. Installed files are not proof that an existing chat/session loaded them. Load relevant updated guidance through the current host's supported mechanism; otherwise report that the next supported new session will discover it. Report desktop plugin adoption separately from worker skill/configuration adoption.

The supported source/target/symlink semantics are documented by the [skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md). Orca's pinned [bundled installer](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/cli/skills/bundled-skill-install-command.ts) resolves its own bundled names and retains modified placements. Do not substitute a generic latest-skills update for adoption of the exact Cypher release.

## Primary contract sources

Pinned upstream release: v1.4.261; links below bind its exact source revision.

- [Worker commands and receipt/recovery notes](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/cli/specs/orchestration-worker-specs.ts)
- [Explicit permission choices](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/shared/agent-launch/permissions/tui-agent-permission-choice.ts) and [Codex enforcement policies](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/shared/agent-launch/permissions/codex-permission-policy.ts)
- [Supported settings RPC](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/main/runtime/rpc/methods/client-state/client-ui.ts)
- [Startup-only deadline](https://github.com/stablyai/orca/blob/92d4266cc4ffa945dbc1fa52850e62448d2dfc1c/src/main/runtime/rpc/methods/orchestration/worker/start/launch/worker-start-budgets.ts)
