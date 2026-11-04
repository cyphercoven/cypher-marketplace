# Component-first screen review
last_verified: 2026-11-03

Read before composing a new screen or revising owner feedback. This is the evidence
check for KIT-RULES 5, not another approval gate. It applies to every Cypher app.
App-specific workflow choices belong in that app's design brief.

## Look before composing

For each distinct screen shape, record a short source map in the run's design notes:
the task, the relevant manifest entries, the component's composed example, and an
existing app story using the same pattern. Read the actual attributes, slots, states
and events. A tag name or a screenshot alone is not an API reference.

Start with:
- `assets/manifest/cu-manifest.json` for registered APIs.
- `stories/molecules/Card.stories.ts` for headers, actions, footers and surfaces.
- `stories/archetypes/Workspace.stories.ts` and the navigation components for shell,
  tab and navigation ownership.
- `stories/organisms/Task.stories.ts` for task identity, state and assignment.
- Existing app stories for a comparable composition; inspect their source and native
  render. Check that the example obeys current rules before copying it.
- `docs/page-rhythm.md` and `docs/agent/building-screens.md` for hierarchy and gutters.

Choose by the information's role. Use cards for distinct records or sections, tables
for comparable records, rows for short lists of destinations, and charts for trends.
Do not wrap every item in a card or replace every shape with a list. A component's
documented composition wins over an improvised arrangement.

## Cards and hierarchy

Use `cu-card heading/eyebrow/icon`, `slot="actions"` and `slot="footer"` where they
express the content. Do not recreate its header with a page heading inside its body.
The actions slot centres status labels and controls against the title block.
Use semantic status variants; available, future, warning and unknown must remain
distinct without depending on colour alone.

An editor, diff, command record or transcript may belong in the documented sunken
surface. Reuse its radius, edge and spacing; do not draw a local approximation.
Page titles, section headings, card headings, body text and metadata must form a
clear hierarchy. Avoid a large heading or repeated title for every small region.

Follow the rhythm table: sections `3xl`, heading-to-content `m`, card header-to-body
`l`, rows `s`, inline items `xs`. Use the documented column/grid gap. A layout
split is not automatically a content gutter: check the visible distance between
columns and fix its owning kit composition if needed. Preserve normal content
padding on every side; flush navigation does not mean flush content.

## Navigation ownership

Navigation belongs to the context it changes. App navigation stays in the app
sidebar. Navigation that changes only a project tab belongs beneath that tab strip,
not beside the whole project. Use one hierarchical tree where it avoids parallel
columns. Keep independent regions scrollable within their allocated height.

Use documented primary/secondary tab sizes and the app-navigation surface for
navigation regions, distinct from the suite app rail. Do not reproduce either
background in consumer CSS. Tree roots and adjacent standalone navigation items
share icon and label alignment as well as height and type; measure their actual
left edges. Trees with character identities keep avatars in the kit's identity
lead slot. Group titles clearly belong to the items beneath them.

## Workspaces and interactions

Follow [Interactive design prototypes](design-stage.md): exercise complete flows with real
shared kit parts, keep local UI state in memory, and use one shared console helper for
future-backend action names, identifiers and payloads. Requests and explicitly selected
loading, success, failure, recovery and conflict examples are distinct; emitted records prove
neither persistence nor backend behavior. Refine candidate contracts during review.


- Editors: inspect the wrapper's model and feature APIs. Design open-file tabs,
  explorer, active-file state, minimap/completion and unsaved/error states when
  required by the brief. Preserve lazy loading of heavyweight runtimes. A code
  block is not an interactive editor.
- Graphs: investigate a maintained purpose-built graph library when the brief needs
  diagram layout, pan/zoom or rich nodes. Keep its adapter inside the kit, theme it
  through tokens/components, preserve keyboard navigation and disclose inferred
  relationships. A hand-positioned collection of boxes is not an equivalent.
- Boards: show task identity, assignment, progress and child counts required by the
  workflow. Dragging must be discoverable on hover and long press, keyboard
  accessible and visibly disabled when it cannot work. Do not imply persisted moves
  from a local fixture.
- Details: use named cards for description, properties, activity and related work.
  Research the requested product's actual workflow before claiming parity.
- Sessions: keep the message composer pinned below the scrollable history/output.
  Character identity belongs in the pane header when it identifies that pane.
  A draggable header exposes one accessible handle with a stable hit area; hover
  must not shift the avatar, label or layout.
- Design previews: if the brief asks for embedded interactive browsing and a separate
  window, design both states and the window boundary. A decorative preview tag
  does not fulfil that workflow.

A local context selector belongs in its section/header actions where that API
exists, not in an unrelated row above the content.

## Prove the composition

Run the relevant audits, but do not treat passing them as visual approval. Inspect
every changed screen in native Chromium at the required dimensions. Check header
and card roles, actual gaps and alignment, tab/nav ownership, clipped corners,
readable body content, overflow, and pinned composer behaviour with long content.

Exercise the real navigation and drill-downs, not only direct story URLs. Include
the requested detail, expanded, hovered/dragging and detached states in review
material. A static capture cannot prove interaction: pair it with browser evidence.
State clearly which controls are connected, local-only or disabled.

Apply shared failures at the kit boundary, document the reusable API, and use it
in the app. Never fix a screen with consumer CSS, undocumented attributes,
one-off spacing or part overrides. Record unresolved kit gaps explicitly.
