# Independent UX review
last_verified: 2026-11-04

This is the shared design-quality procedure. It is an internal acceptance check,
not owner UAT approval and not another owner gate. The approved app brief still
owns app-specific workflows; reusable component behavior belongs in the kit.

## Make the correct composition the easy one

When repeated feedback identifies the same mistake, investigate the owning
component before fixing each screen. Read its manifest API, composed examples,
usage documentation and a comparable native app view. Record the observed cause,
the owning boundary and the intended user outcome.

Put mechanically enforceable behavior in shared defaults, API constraints,
composed primitives and regression tests. Examples include one visible field
label with an accessible control name, correct card header/footer slots, semantic
zero/nonzero status, normal content gutters, consistent control sizing and safe
scroll allocations. Optional chrome follows actual renderable content, not merely
an attribute's presence. Closed modes are normalised before rendering; escaping
belongs at the rendering boundary. Context tied to an entity is cleared when its
identity changes, independently of editor/runtime disposal. Prefer a supported
intent variant to a consumer override.
Do not add consumer CSS, duplicate controls or undocumented attributes to satisfy
one screenshot. Demonstrate the shared fix in another relevant composition.

Keep judgement in guidance: which action is primary, useful grouping, information
priority, suitable density, concise wording and relationships worth exposing.
Do not hard-code one app's content or workflow into a generic primitive. Record
the useful rule and example in the owning component's usage documentation; add a
focused structural, interaction or visual check where the invariant is reliable.
A prose instruction alone does not resolve a repeatable component-default defect.

Exceptions to documented kit behavior need explicit owner approval. Record their
scope, reason, authority and follow-up; neither an audit waiver nor the word
"intentional" grants that approval.

## Review the experience as a whole

Use minimum useful copy: enough to understand state, consequences and the next
action. Remove screen narration, repeated labels, redundant format badges and
implementation commentary. Do not hide essential meaning behind unexplained icons.

Check these consistently across the whole changed flow:

- Actions: one clear primary action in each context; related secondary actions use
  the shared icon action group, consistent placement, tooltips and accessible
  names. Avoid duplicate close/hide controls and unrelated floating actions.
- Hierarchy: a leading page header is distinct from compact card/section headings.
  Show each title once. A subtitle describes the entity or task, not the screen type.
- Forms: use the documented Field Chrome/control composition; one visible label,
  aligned control columns, short help beside its label and appropriate validation.
  Use the documented bounded form measure to keep related labels and controls
  proximate on wide workspaces; checkbox groups retain intrinsic, compact widths.
  Check both broad and narrow allocations rather than fixing one viewport.
- Layout: shared row/column gaps, space between navigation and content, standard
  external content padding and intentional full-width/height allocations. Reading
  measure, zero payload padding and allocated workspace are different contracts:
  never infer semantics from an attribute name. Inspect its documented behavior
  and measure painted content against the actual allocation. Verify the finite
  fill chain through shadow roots and intermediate wrappers: zero padding alone
  does not allocate width or height, and scroll areas need a bounded ancestor.
  Flush tabs/editors keep their container's clipping and rounded corners.
- Panels: clearly separated sidebar surfaces and gaps; independently scrollable
  content, fixed identity/actions where needed, and pinned message entry.
  Compare docked, collapsed and detached states; use the intended sidebar
  surface rather than borrowing a navigation surface to suggest separation. An ordinary
  right column is not automatically docked; a true right dock mirrors left navigation,
  meets outer edges and retains density-aware inner padding.
- State: unknown, unavailable, zero, success and failure remain distinct. Counts
  determine semantic colour; zero failed is neutral. Status icons retain useful
  details through accessible tooltip/focus behavior.
- Identity: first-party branding and third-party brand marks use their actual
  shared components, including true brand-lead slots and detached-window chrome.
  Reuse established icons; do not invent lookalike assets. Measure visible brand ink,
  not just the asset box.
- Graphs: route around nodes, consider label placement separately, and inspect
  dense/zoomed/selected states. Keep canvas actions in a consistent shared group.
  Use concise labels and details on demand without losing relationship meaning.
- Documents/editors: one title, deliberate reading width and allocated editor
  height, clear view/edit modes and a consistent Save/Cancel hierarchy. Underlying
  documentation titles are Title Case even when the title component paints capitals.
  Inspect invalid mode attributes and identity changes after closing/reopening:
  stale source selections or attachments must not cross entity boundaries. Source edits
  preserve metadata byte-for-byte; preview hides complete frontmatter. Verify drafts
  per session across rerender and detached-window transitions. Visiting a wizard step
  is not completing it; wizard progress is not a relationship graph. Where a human has
  final decision authority, a roundtable cannot replace it with consensus or a vote.

A uniform screen is not automatically a usable screen. Verify task completion,
discoverability, feedback, recovery, keyboard use and accessibility as well as
appearance. A deliberate content-specific variation still needs a stated reason;
it does not excuse violating a documented invariant.

## Independent check before owner review

The reviewer is a fresh reviewer, not the implementer. Code review and independent
UX review are distinct evidence: neither passing tests nor the author's visual
pass substitutes for the latter. The reviewer receives the approved brief, complete
feedback checklist, component source map and current build/revision.

Use the supported Product Design audit capability when available and suitable.
It is not a mandatory dependency: a fresh reviewer using this procedure and native
browser evidence is an adequate documented path. Do not copy a third-party skill
or imply its tool was used when it was not. If a reviewer cannot inspect the actual
design or required interaction, record that check as incomplete, never passed.

Exercise actual navigation and complete flows, not only direct story URLs.
Inspect every affected page and applicable hover/focus, empty/long content,
loading/error/conflict, resized and detached states. Verify real pointer and
keyboard actions and their emitted intents. Capture the current source revision,
dimensions, route/state and evidence path so old screenshots cannot silently
stand in for the current design. Design fixture evidence remains separate from
backend integration and production evidence. Check each literal acceptance criterion.
When testing an editor, click the actual input and assert the typed value before
judging save; classify harness/focus failures separately from product defects.

Report each finding with severity, user impact, exact page/state, evidence,
owning shared/app boundary and a proposed correction:

- P0: catastrophic or unsafe outcome.
- P1: blocked core journey, lost work or inaccessible essential action.
- P2: material confusion, inconsistent interaction, overlap/clipping or a defect
  that prevents dependable understanding or use.
- P3: minor polish with no material effect on the task.

Prioritise findings by impact and shared cause. Fix the batch, then recheck the
changed and previously failing paths; do not repeat unrelated successful checks
by habit. No unresolved P0, P1 or P2 findings go to owner UAT or design review.
Do not downgrade a finding to avoid this requirement. Record P3 observations and
their disposition; exceptions still need explicit owner approval. If blocked on
a genuine owner decision, continue independent authorised fixes and queue that
decision under the active away-mode rules when applicable.

The final UX report names the independent reviewer, scope, current revision,
flows/states exercised, findings fixed, recheck evidence and material limitations.
Only then prepare the owner's existing design/UAT gate. Owner approval is never
inferred from an internal pass.
