---
name: cypher-build-app
user-invocable: false
description: Guides building a small web app using only cypherui kit elements, from scaffold to a working page. Use when someone wants to build, start, or scaffold a new app or page meant to run on the Cypher-managed stack.
---

# cypher-build-app

PURPOSE: scaffold a small web app that passes the cypherui kit-only audit
— every interactive element is a `cu-*` custom element, never raw HTML
outside prose/markdown and alert descriptions — using kit docs fetched
live from the gateway, never a remembered API.

## Kit-only rule

- Every interactive or structural UI element (buttons, inputs, layout,
  cards, nav, dialogs, tables, etc.) is a `cu-*` custom element from the
  cypherui kit.
- Raw HTML is allowed in exactly two places: inside prose/markdown
  content (e.g. body copy inside a `cu-card`), and inside an alert's
  `description` content. Nowhere else.
- No other component library, no hand-rolled `<button>`/`<input>`/
  `<div class="...">`-as-a-component. If the kit doesn't have the
  element you want, compose existing `cu-*` elements rather than
  reaching for raw HTML.

## Steps

1. Call `onboarding` if sign-in/role isn't already confirmed this
   session.
2. Call `knowledge` with `topic: "cypherui"`. This returns the kit's
   `llms.txt` (element-by-element usage guide) and `custom-elements.json`
   (the full element manifest: tags, attributes, slots, events) as
   served from the kit's own channel today, plus the channel address to
   load the kit from. Read both before writing any markup — they are the
   only source of truth for what elements exist and how they're used.
3. If `knowledge` doesn't have the `cypherui` topic yet (it can land
   after this skill does), fall back to `onboarding` to check whether
   the gateway names another way to reach the kit docs. If neither
   source has it, say so plainly and stop rather than guessing at tag
   names or a channel address from memory.
4. Build the page using `skills/cypher-build-app/template/` as the
   starting point: `index.html` loads the kit from the channel address
   `knowledge` just gave you (fill it in there — never hardcode one),
   and `main.js` wires up behavior using only `cu-*` elements and the
   events/attributes `custom-elements.json` documents for them.
5. Before calling the app done, re-read your markup against
   `custom-elements.json` once more: every tag should resolve to a real
   `cu-*` element, and every raw HTML tag should be inside prose or an
   alert description. That is the kit-only audit this skill must pass.

## Rules

- Never hardcode a kit channel address, element name, or attribute from
  memory — `knowledge`'s `cypherui` topic (or the `onboarding` fallback)
  is the only source, called fresh each time.
- This skill scaffolds and edits files only. It does not deploy or
  publish anything — that's `cypher-deploy`.
