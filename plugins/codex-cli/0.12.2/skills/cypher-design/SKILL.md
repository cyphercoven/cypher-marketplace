---
name: "cypher-design"
user-invocable: false
description: "Load before designing any new Cypher Suite or CypherUI UI, including screens, app views, Design canvas boards, mockups, kit components, icons, avatars or brand work. Applies the kit rules, story-first boards, kit requests, icons, spacing, padding, canvas sizing and the design gate."
---

# Designing for the Cypher Suite

**The core rule of this kit is composability and consistency (owner ruling, 2026-10-24).** Every repeated thing (a type role, a small part, a surface, a layout pattern, a motion) has exactly one implementation, built from root tokens. Components compose from it and never re-implement or override it. If you need a variation, add an intent variant to the shared part.

**All CSS values come from CSS variables (owner ruling, 2026-10-24).** Colour, space, size, radius, border, shadow, type, motion and z-index all read theme variables, so a new theme only redefines variables. No raw literals (`audit:css-vars`); a new raw length in primitive CSS needs a `--cu-*` token in `theme.css` (then `gen-design-md` and `tokens:map`).

You design by writing **stories** built only from `cu-*` kit components. Those stories become Design canvas boards through the design mirror. **Nothing is ever hand-drawn.** The product owner sees the result at the design gate.

Precedence: the running system, then `STATUS.md`, then ADRs, then this skill. When two docs disagree, the newer `Last verified` wins, and the product owner's rulings in this skill beat older docs.

## Before you design

- [ ] Read `STATUS.md` in every repo the task names, plus `cypherui/STATUS.md` for the current kit version.
- [ ] Read `cypherui/CLAUDE.md`. Its KIT-RULES block holds eight rules, and each one is checked by an automated gate.
- [ ] Read `cypherui/docs/DESIGN.md`, which is generated from `theme.css`: tokens, type, spacing, icons and the agent prompt guide.
- [ ] Look up components in `cypherui/assets/manifest/cu-manifest.json`: every `cu-*` element with its attributes, enums, slots, parts and events. Never guess an API.
- [ ] Read `cypherui/docs/agent/building-screens.md` (how to build a screen with the kit, step by step), `cypherui/docs/page-rhythm.md`, `docs/adr/CUI-0050-the-gutter-contract.md` and `docs/agent/design-artifacts.md`. Every rule in this skill is also written into those kit docs (owner ruling, 2026-10-25). If you find one that isn't, add it there too.
- [ ] Find the product's ONE canonical canvas (table below). If it has none yet, register it in `cypherui/scripts/ds-targets.json` with artifact `null` until the canvas exists.
- [ ] Copy the composed examples on each component's page (forms on the form pages, conversations on Chat). Do not invent compositions (KIT-RULES 5, CUI-0064).
- [ ] Name the ADR(s) that authorise the work before writing anything (`cypherui/CLAUDE.md`, "Session read order").

## 1. No hand-drawn boards, ever (owner ruling, 2026-10-24)

- **Designing means writing stories.** Every board is a capture of a rendered story: stories → DS runner → capture → `ds-out/` → publish (`docs/agent/design-artifacts.md`).
- Never write HTML on a canvas, never publish a hand-made `.dc.html`, and never keep a drawn board "just for now". If a canvas still holds one, port it to a story and delete the drawn file.
- Older docs that describe "hand-drawn boards — kit only" or `kitOnly` canvases are legacy. Port those boards.
- **Publishing belongs to the `cypher-mirror` skill.** It covers `ds:sync`, the publish contract, `--live-canvas` merges, `--mark-published` and the review loop. Do not repeat its steps here.
- Where stories live:
  - Kit components: `cypherui/stories/**`, titled `Components/<Page>/<Name>`.
  - App screens hosted in cypherui: `stories/Cypher/`, `stories/CypherFlix/`, `stories/CypherMuse/`, `stories/CypherLife/`, `stories/CypherHome/`, and so on.
  - Repos with their own story root (cypherinstall, CypherGhost in the cypherveil repo): they run `pnpm ds:capture` themselves, and the result is folded in with `ds:sync --root <name>=…`.
- Story file names must be unique on their canvas. Two stories called `Main` collide as `Main.dc.html`. A story file that grows a second story needs an `.mdx` wrapper (copy a sibling's).
- Storybook is retired (UI-50). The renderer is `pnpm ds:runner:bg`, and reviews happen on the Claude Design canvases.
- Use the review loop for kit look-and-feel iteration: `pnpm ds:review` publishes the working tree's kit onto the CypherUI Components canvas (`docs/agent/ui-test-levels.md`).
- Each of the product owner's comments on a board is a change request to a story or to the kit. Fix it in a PR, then re-sync.
- **Fix the cause, not the board (owner ruling, 2026-10-25).** When a comment points at something a component should get right, fix it in the base component (or add an audit) so it can't recur, and add the rule to this skill. A story-only patch is for content that is only wrong in that story.
- **Batch board comments (owner ruling, 2026-10-24).** Collect comments as they arrive and acknowledge them, but don't start any work until one of two things happens:
  - no new comment has arrived for **5 minutes**, or
  - The product owner gives the go-ahead.
  - Then handle the whole batch as one change set, in small seats (one PR each) and one re-sync. A comment that arrives during the work starts the next batch.

### Canvases: one per product, for its whole life

| Canvas | Holds |
|---|---|
| CypherUI Design System | Kit files, foundations and README only. **No component cards.** |
| CypherUI Components | All component work, one page per group (CUI-0029) |
| Cypher, CypherFlix, CypherInstall, CypherGhost, CypherMuse, CypherLife, CypherHome, … | That product's screens, one board per story. The canvas title is the product name. |

- Never create a second board for a product.
- Delete a gate board as soon as its ticket closes.
- The canvas owns where a board sits, and the run owns what it shows. Always merge with `--live-canvas`. Placement then follows the layout rules below, and a live position is kept only when it already meets them.

### Canvas layout and screen sizing (owner ruling, 2026-10-24)

Read `canvas-layout.md` (next to this file) before laying out any canvas page. It holds the page, row and board rules: at most 12 boards in 4 rows per page, every board and note on a listed page, plain-word titles and post-its, flows labelled with numbered steps, one left edge, equal row gaps, no overlaps, boards sized to content (screens 1920 wide and at least 1080 high, cards up to 3240, windows at their declared size, no scroll, no dead space), and `ds-measure --check` clean. Judge a board by a real 1920-wide screenshot.

## 3. Backdrop: particles everywhere (owner ruling, 2026-10-24)

- **Every page uses the particle backdrop**: the brand-accented particle field over the accent bloom (`src/primitives/app-shell/_backdrop.ts`).
- **The plain bloom is only the reduced-motion fallback.** It is never the normal look of a page.
- The kit paints the backdrop. Apps write no markup or CSS for it. The only opt-out is `data-cu-backdrop="off"`, and only with the product owner's approval.
- A board showing only the bloom at full motion is a bug: raise it against the kit.

## 4. Use only kit components (KIT-RULES 1–3, 8; CUI-0057, CUI-0014, CUI-0064)

- Compose only `cu-*` elements. No `<div>`, `<span>`, `<section>`, `<button>`, `<p>` or `<h1>` in app code or stories.
  - The one exception: inline `<a>`, `<b>` and `<i>` inside prose, markdown and alert descriptions.
  - For a paragraph, use `cu-prose`.
- **Only registered elements.** A retired or unregistered `cu-*` (e.g. `cu-notice` → `cu-alert`, `cu-prose-doc` → `cu-prose`, `cu-section-heading` → `cu-heading`) renders as an empty box, and a card around it draws a stray line. `ds-measure --check` fails "unknown element cu-x".
- Lay out with `cu-stack`, `cu-cluster`, `cu-grid` and `cu-panel` (`measure` composes `cu-frame`). `cu-grid` child spans are 2, 3, 4 or full only, and `span-rows` is 2 or 3; any other value silently matches nothing (`audit:enum-usage`).
- **Write no CSS:**
  - no `<style>`, `style=`, app stylesheet or `::part()` override
  - no `class=` hook on a `cu-*` element
  - no `--cu-*` overrides unless the component documents them as API
- The look comes only from intent attributes: `variant`, `size`, `tone`, `appearance`, `brand` and `density`. Never pass a raw colour, length, font or z-index (CUI-0044 Laws 1–2).
- **Every app is one `cu-workspace`**, chosen by `platform` (`web` | `desktop`) and `purpose` (`media` | `pro`) (CUI-0062).
  - Desktop apps get window controls and no page footer.
  - Every desktop panel is a `cu-layout` panel.
- Choosing a container:
  - `cu-panel` is a layout region that owns the gutter.
  - `cu-card` is raised content.
  - `cu-surface` is only a mount for a foreign `<canvas>` or `<video>`.
- One layout is one component. Change behaviour with an attribute, never with a near-duplicate element (CUI-0065).
- **The gates:**
  - `audit:kit-only` and `audit:no-demo-styles` run on every commit, and their baselines only go down.
  - Never add an exception marker. An exception needs the product owner's approval by name.

## 5. Kit requests: a gap grows the kit (KIT-RULES 6; CUI-0057)

First check whether an archetype covers the shape, then whether a primitive composes into it. Only when neither does:

1. **File one file per gap** in the consuming repo: `kit-requests/NNN-short-name.md`, numbered in sequence (see `cypherhome/kit-requests/`). A kit-side gap goes in `cypherui/kit-requests/`.
2. **Use this format:**
   - Title: `# kit-request NNN — <name>`
   - `**Filed by:**` the session or ticket, the date and the kit version
   - `**Status:** open`
   - `## Gap`: what the kit can't express and where it's needed
   - `## Ask`: the intent-shaped API you want
   - Stand-in: the nearest kit part used until it lands
3. **Keep the consumer's `kit-requests/README.md` table** with the columns #, request, stand-in today, and Done (kit version and element).
4. **A separate session builds it in cypherui** under a Plane ticket in the UI project. Batch related requests (e.g. CypherHome's 15 → kit 0.32.0, UI-63).
5. **Close it with the kit change**, never with a local workaround. Fill in Done, then swap the stand-in for the real part.
6. Never build the missing piece locally, and never style a stand-in to fake it.
7. **A new pattern, abstraction or exception is a kit request, judged at the design gate (ruling C-10).** It is never introduced silently and never a separate approval step during the work; keep building with the stand-in.
8. A missing **illustration** is not a kit request: list it in `kit-requests/ILLUSTRATIONS.md` for the product owner to source. A missing **control glyph** is a kit request.

## 6. Iconography (KIT-RULES 7; CUI-0046, CUI-0047, CUI-0060)

- **Two icon tiers. NEVER use an illustrative icon as a control icon, and NEVER mix the two (owner ruling, 2026-10-26):**
  - `cu-icon` (control glyphs) is for anything clicked or scanned: buttons, menus, nav, tabs, tables, fields, list and row leads, keypads, media and remote keys, timelines, gauges, presence and inline text.
  - `cu-lottie-icon` (illustrative art) is used only at **48 px and up**, where the picture is the content: stat cards, empty and state displays, onboarding, feature cards and reactions.
  - Never put a Lottie or illustration in a control, menu, nav item, key, row or list. A name that exists in both tiers (e.g. `home`, `arrow-left`) always resolves to the control glyph inside any control host; a host that relays a name must pass itself so the tier resolves (the 2026-10-26 `cu-remote-pad` bug drew Lottie home/back keys).
  - Never mix tiers within one surface or set: every icon in a keypad, toolbar, row group, list, card or nav is the same tier at the same size. If one is missing, author the glyph; don't borrow the other tier.
  - Gates: `audit:icon-tier`, `audit:control-icons` (a control host can't resolve a Lottie).
- **One glyph language** (CUI-0046, checklist in `docs/agent/control-glyphs.md`):
  - 24×24 box with a 2-unit margin
  - stroke `var(--cu-glyph-stroke, 2)`, round caps and joins, no fill, `currentColor`
  - optical extent 0.70–0.85, perceived centre on the box centre
  - one gesture per glyph
  - accent part marked `part="… accent"`
- **If no glyph exists, author one.** Never use a Lottie, a raw `<svg>`, Lucide or a "close enough" glyph. An unknown name renders as a visible gap on purpose (CUI-0047).
- **Glyph motion:**
  - A state change is a reversible morph. An action is a one-shot that settles.
  - Hover shows about 40% of the motion, and press plays the full motion.
  - Durations and easings come only from tokens. Reduced motion reaches the same end state.
  - The whole surface triggers the motion, not the icon's own `:hover`.
- Never size a glyph yourself; the size ramp does it.
- Lottie packs are opt-in imports (`@cyphercoven/cypherui/icons/<set>`), and a pack that isn't imported shows a gap.
- Every nav item has an icon (`audit:nav-item-icons`). No native `title` tooltips.
- **Brand glyphs are brand art, not icons.** They appear only in app icons, favicons, `cu-app-rail` and `cu-app-switcher`, never in a control.
  - `house` is the dashboard glyph (three tiles). `witch` has no glyph.
  - They are generated by `scripts/brand/gen_app_glyphs.py` (`docs/adding-a-brand.md`).
- **No third-party logos or wordmarks as controls or app icons.** A provider (Claude, ChatGPT, Antigravity…) is named in plain text; the visual is our own app icon. The one exception: a third-party device or service in a list row leads with its brand mark via `cu-brand` (Brandfetch; see `kit-versions.md`).

## 7. Avatars (owner ruling, 2026-10-24)

- **The product owner is always their character portrait, everywhere** (owner ruling, 2026-10-25): shell profile, rail, people lists, chat, profile pages, CypherFlix and every fixture. Which fixture, and the naming rules for it, come from `knowledge {topic: "design-fixtures"}`.
  - Never use initials, a stock or placeholder avatar, someone else's photo or an inline `data:` image for them.
  - **Their portrait must be uploaded to every canvas that shows it** (see §1 and Render budget): a fixture missing from the canvas falls back to letters.
- **Other people get lettered avatars**, and the letters always match that person's displayed name. "Kaylee Frye" is "KF", never a random or mismatched pair. **Never invent a surname:** if only a first name is known, show one letter ("Wash" is "W").
- **Lettered avatars always draw the background pattern** (owner ruling, 2026-10-25), picker choices included; only the colour changes.
- **First names on display; the full name feeds the initials (owner ruling, 2026-10-25).**
  - Compact surfaces show the first name only: profile chips, the rail profile, people chips and tags, chat authors, and people-list rows.
  - The avatar still derives its initials from the full name, so "Kaylee Frye" shows "KF" next to the label "Kaylee".
  - Show the full name only where it is the point: a person's detail page, contact or emergency details, account forms.
  - Pass the full `name` and let the component pick (kit default). Give `cu-avatar` the name and let it derive the letters, rather than hard-coding them.
- Use the shared fixtures from `stories/_shared/`. Never invent an avatar asset in a story, and never point at image URLs that won't exist on the canvas (e.g. `/_blob/…`).
- **A missing or broken image falls back to letters.** A broken avatar is never shown (kit default).
- **Identity lead slot (owner ruling, 2026-10-25):** one fixed square, the size of an avatar. Avatars, characters, icons and initials are centred in it, and the square is centred on the title block, so agents and people line up.
- **Lead and identity slots default to square visuals.** A product is shown by its **app icon** (`cu-logo kind="app-icon"`), and the label carries the name.
  - **The exception is a column sized for the wordmark (owner ruling, 2026-10-25).** A full wordmark is good in a table or list of products when the lead column is set wide enough to fit it unclipped, with the same width on every row. Never squeeze a wordmark into a square slot.

## 8. Spacing, padding, typography and size

### Content padding: the gutter contract (CUI-0050)

- **Content is never flush to an edge.** Imagery and backgrounds may bleed edge to edge, but the content inside them keeps its padding (`bleed`).
- **One token, `--cu-page-gutter`**, is the padding of every panel body and of the shell's main, header and nav. It is equal on all four sides: the top distance equals the left one. Density (compact / base / comfortable) moves it.
- **A component owns the spacing inside itself** (a card's inner padding, a row's cell gap). It **never** owns its distance from the page edge; the panel owns that.
- **A shell body's bottom inset equals its top inset**, on every shell with a footer bar (owner ruling, 2026-10-25).
- **Heroes are either flush or within the container (owner ruling, 2026-10-24)**, never in between:
  - **Flush:** `bleed`, touching every edge of its container.
  - **Within:** inside the gutter, the same distance from every edge as other content, with the card treatment.
  - **A flush hero never draws card chrome** (surface, border, radius). Flush and boxed together is a bug.
  - **A hero is sized to its content (owner ruling, 2026-10-26).** No empty band; a too-tall hero is a bug.
- **Never double-pad.** Don't add padding to something that already sits inside a padded region.
- Never use a `vw`-based inset (`audit:page-inset`, baseline 0).
- `body` has no margin. The gutter comes from the shell.
- `cu-page-header` keeps its default padding on a page title, with no top padding (the gutter supplies it). `pad="none"` is only for a header embedded in a layout that already spaces it.

Read `spacing-and-forms.md` (next to this file) for the rest of this section: the hierarchical rhythm table, grids, tables and lists (every list row leads with a graphic), and forms and controls (fields fill their container, a state never changes a control's size, settings lists are form rows).

### Type and size

- **Type is set by role**, never inline (CUI-0003 R4, CUI-0015, `DESIGN.md`):
  - the heading face for all headings
  - the display face for logos and hero titles only
  - Inter for body text and anything 0.85rem or smaller
  - JetBrains Mono for code
  - long-form copy in `cu-prose`
- **The type stack is set once at `:root` and never ignored (owner ruling, 2026-10-24).** Every text style comes from the root tokens through its role. No hard-coded font, size, weight or line-height anywhere.
- **Body and prose content always comes from the global (root) body and prose styles (owner ruling, 2026-10-24).** Containers (card, hero, panel, state display) never restyle the text placed inside them. Only dedicated components carry their own type.
- **Eyebrows always look the same everywhere (owner ruling, 2026-10-24):** one root eyebrow style and the same gap to the title, in every component.
- **Components own their typography (owner ruling, 2026-10-24).** A button always uses the button component's fonts. A dedicated component (button, tab, chip, input, badge, nav item) never has its font, size, weight or case overwritten by a container or a story.
- **Headings are structure, not status.** A page-level status is a full-width `cu-alert` plus one `cu-button variant="brand"`.
- **One size scale**, `2xs xs s m l xl`, default `m`. `m` equals the form-control height, so buttons, icon buttons and inputs line up (CUI-0031).
- Optical centring is the kit's job (CUI-0019). Never nudge anything by hand.
- Hover means clickable. Surfaces you can't interact with never change on hover.

## 9. Brands (`src/primitives/_shared/brands.ts`; `docs/adding-a-brand.md`)

- **Ids:**
  - `house`: the core Cypher app, untinted
  - `flix`, `mind`, `life`, `ghost`, `home`, `muse`
  - `witch`: the parent brand, with no app
- **Retired ids**, which must never appear in new work: `veil`→ghost, `studio`→mind, `vault`→life, `ops`→house.
- Set the brand **once per app** on `cu-workspace` / `cu-app-shell`. Never colour a brand by hand.
- **One flat accent per brand**, generated (`pnpm gen:brand-theme`, `audit:brand-theme`). It must reach 4.5:1 on the card, base and canvas surfaces.
- **The mark:** the Tektur `c` with its broom. The `c` is always bone-white, and only the broom and the wordmark suffix take the accent. No gradient on marks, and no ring.
- A new brand needs the product owner's approval by name.
- `--brand` takes only these eight ids. There are no app-specific brand gradients (an installer or tool uses `house`). A root canvas takes its brand from `ds-targets.json`.

## 10. Other binding rules

- **Theme:** dark and low-stimulus, with one accent doing the emphasis.
  - Use semantic tokens.
  - Density classes are `cu-compact` and `cu-comfortable`; `cu-display` is for room-distance screens.
- **States:** design loading, empty, error and disabled alongside the rest state.
  - A skeleton matches the loaded layout, then content enters staggered (CUI-0005).
- **Motion:**
  - Every state change is transitioned, with no harsh hovers.
  - Nothing animates on mount if it is already settled.
  - Durations and easings come only from tokens, and reduced motion is honoured (CUI-0006).
  - The animated logo is only for loading spinners. Progress is `cu-progress`.
- **Accessibility:**
  - A control without a name is a build error.
  - Visible focus.
  - 4.5:1 contrast.
  - Nav items in Title Case.
- **Stories** (CUI-0007, CUI-0013, `docs/story-definition-of-done.md`):
  - Each declares `SHAPE: state` or `SHAPE: motion`.
  - A state story mounts its end state directly, with no `setTimeout` fakes.
  - Galleries, not controls: no `argTypes`.
  - Show every enum value, slot and event.
  - Fixtures come from `stories/_shared/`.
  - Leaf titles are CamelCase and match the file name.
- **Content:** no Rowling or Harry Potter content. No emoji in the UI.
  - No placeholder text ("[name]", "[amount]") and no developer labels (element names, attribute values) on a board. Use realistic fixtures.
  - A component that receives bad data never prints an error message on a board. A story that shows one is a failing story.
- **Casing (owner ruling, 2026-10-25):** all UI copy is sentence case: tags, badges, table cells, labels, buttons and headings. Nav items are Title Case. Product names keep their brand spelling (Cypher, Forgejo, Plane). Only code and ids keep their literal form (`audit:copy-case`). A heading that starts with a lowercase hostname gets an article in front ("The serenity NAS").
- **Spinners scale with their state.** A spinner in a large state display is large; never put a small spinner on a full-screen state.
- **The app rail and switcher show app brands only.** The parent `witch` brand and the base c mark never appear there.
- **No unpowered search (owner ruling, 2026-10-24):** no app top bar shows search until the search service exists. Set `no-search` on `cu-workspace`. The one exception is web CypherFlix, where Jellyfin powers search.
- **Layout by platform:** desktop apps have a collapsible left rail, and search goes in the top bar once a search service exists. Web apps put search centred in the header.
- **Extensions on the App Store (owner ruling, 2026-10-25/26)** sit under Apps in their own section and the same card grid (Apps · Extensions tabs only when a list outgrows a screen). **One extension per provider** (Cypher for Claude, ChatGPT, Antigravity, Cursor, VS Code). Each page shows "Your access", read from the viewer's role (`stories/_shared/permissions.ts`): "You can" rows with a check, "You can't" rows as `cu-row disabled` with a lock and reason.
- **Today for admins carries a Servers section (owner ruling, 2026-10-26)**, meant to replace Grafana for the everyday look: each machine's health and 24-hour sparklines, alerts and low storage first, a link to Machines and services. Non-admins don't see it.
- **Build handoff:** give the intent, the composition (by manifest name), the states, the motion tokens, the a11y behaviour and an API sketch. Every gap is one of three things: a new glyph, a part or an enum value.

## Render budget (owner ruling, 2026-10-24)

Render only the canvases you touch (`pnpm ds:sync --only <target>` plus `ds-measure --check`); a full `ds:sync` (about 800 boards) runs only for a **major** kit bump, and you publish straight from that `ds-out/`. The kit's semver bump decides what re-renders: read `kit-versions.md` (next to this file) before any re-render, and run `pnpm ds:status <canvas>` when you open a canvas. The rule is owned by `cypher-workflow` §3.

- **Small batches (owner ruling, 2026-10-25):** split work into small seats, but never duplicate heavy lifting. Each seat tests only changed and affected code. Tests and audits come first; a render is only for visual and layout checks.
- **One sync at a time per checkout.** Two `ds:sync` runs in the same `ds-out/` clobber each other's bundle and manifest. Check `ps` first; if another session's full sync is running, let it publish.
- **Every picture a board uses is uploaded to that canvas first** (its `/_blob/<id>` in `scripts/ds-assets-map/<canvas>.json`). `ds:sync` fails, naming `canvas: fixture`, when one is missing. Copy an asset another canvas already holds server-side (Artifact publish `asset: true` with `from_url` + `asset_ids`). A new canvas also needs its five `$fonts` copied in.
- Workers start their own DS runner on a free port (`--port 8043`, `DS_RUNNER_PORT` for the precommit hook), never 8018, and stop only that runner. Nobody kills a runner or `pkill`s while a sync is running.
- A new canvas (a new app) is wired in `scripts/ds-sync.mjs` like `cyphermuse` and gets its id and `brand` in `ds-targets.json` in the same change.

## Before the design gate

- [ ] Every board is a story capture. Nothing is hand-drawn, file names don't collide, and no second canvas exists for the product.
- [ ] Screens are 1920 × ≥1080, grown to fit with no overflow, and nav and top bar are fixed height.
- [ ] Every board fits its content exactly: no scroll and no dead space at the top or bottom; heroes sized to content.
- [ ] Each page has at most 12 boards in at most 4 rows. Each row is a flow, the spacing is even, and every page has a clear category name.
- [ ] Every board and note has a page; flow rows are labelled as flows, with numbered steps in the right order.
- [ ] No overlaps between boards, labels or post-its; every row title and post-it sits above its row's first board, with room to spare.
- [ ] Titles and post-its are plain words for the product owner; no story paths, file stems, "&" or dev notes.
- [ ] Particle backdrop on every page; bloom only under reduced motion.
- [ ] Avatars: the product owner's portrait everywhere (uploaded to the canvas), character avatars for agents, initials that match each name, first names on compact surfaces, lettered avatars with their pattern, no broken images.
- [ ] Every fixture a board uses is uploaded to its canvas (`ds:sync` passes the fixture gate); the canvas has its `$fonts`.
- [ ] Lead slots: fixed squares with app icons, or a column sized to fit the wordmark, never clipped; rail and switcher show app brands only; every list row leads with a graphic.
- [ ] Padding: the gutter on all four sides, equal top and bottom insets, no double padding; heroes flush or boxed, never both.
- [ ] Grids: one column grid per page, whole-column spans, even gaps, equal-height cards.
- [ ] Tables sit in a named card; single-column tables have no header row; settings and access lists are form rows.
- [ ] Fields fill their container; states never change a control's size.
- [ ] Copy is sentence case (`audit:copy-case`); spinners match their state's size.
- [ ] Spacing is hierarchical (sections > heading→content > rows > inline), hero→content is `l`, and each section is clearly separated by its gap or a midway `cu-divider`.
- [ ] Only registered `cu-*` elements (`ds-measure --check` reports no unknown element).
- [ ] `pnpm run audit`, `audit:kit-only` and `audit:no-demo-styles` pass, with zero new `style=`, `<style>` or `css\``.
- [ ] No illustrative icon in any control, key, row or list, and no surface mixes the two icon tiers.
- [ ] The icon gates pass: `audit:icon-tier`, `audit:control-icons`, `audit:icon-names`, `audit:glyph-conformance` and `audit:glyph-optics` (plus `audit:brand-theme` if a brand changed).
- [ ] `pnpm ds:runner:bg`, then `pnpm verify:stories <port>` and `audit:control-optics` pass.
- [ ] `ds:sync --only <touched targets>`, then `ds-measure --check` is clean, and the boards were looked at in a real 1920-wide screenshot. Publish that render. Any wider re-render follows the kit's semver bump (`kit-versions.md`): patch none, minor only touched canvases, major all.
- [ ] Lists are `cu-rows`; agents in chat are character avatars; third-party marks come from `cu-brand` (client ID set, no fallback glyphs on the boards).
- [ ] Published with the `cypher-mirror` skill, the canvas reopened and the `ds:diff` checked.
- [ ] An independent review against the Definition of Done has run; the author's own pass doesn't count.
- [ ] Open kit requests are filed and listed with their stand-ins.
- [ ] The product owner gets **one question** with the canvas link: "approve, or what's wrong?" Spec · design · UAT are the only human gates.
- [ ] After the gate ticket closes, delete any gate board.