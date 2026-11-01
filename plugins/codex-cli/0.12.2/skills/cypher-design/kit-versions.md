# Render by kit version, brands and lists

Read this with `SKILL.md` before any re-render, and before putting a third-party mark or a list on a board.

## Render by kit version (owner ruling, 2026-10-27)

Re-rendering canvases costs the product owner's usage. **The kit's semver bump decides whether a canvas is re-rendered, and when.** Every kit change carries a changeset, and its bump level is the rule:

| Bump | What it covers | What happens to canvases |
|---|---|---|
| **patch** (0.0.x) | A new icon or glyph, a new component, variant or token nothing on a board uses yet, a fix that doesn't move what a board draws, docs | **No re-render.** Publish the Design System's bundle. A canvas picks up the new bundle (a server-side copy) the next time it is published for another reason. The changelog records it |
| **minor** (0.x.0) | Anything that changes what boards draw: spacing, padding, positioning, sizing, type, colour, a component's default look | **Re-render only when that canvas is next touched.** Never re-render canvases nobody is working on |
| **major** (x.0.0) | Breaking: an element, attribute or slot retired or renamed, a changed API | **Full re-render of every canvas, automatically**, in the same change set, fixing whatever breaks |

- **The CypherUI Components canvas is always kept current.** It is the kit's own reference, so it never waits to be touched.
  - Patch: re-render and publish **only the boards whose component or story changed**, for example the new icon's board.
  - Minor or major: re-render the **whole** Components canvas in the same change set.
  - The table above governs the app canvases.
- **Pick the bump honestly.** Whether a board draws differently decides patch versus minor, not the size of the diff. If unsure, run `ds:sync --only` on one affected canvas and compare.
- **Each canvas records the kit version it was rendered with**, and the kit changelog (cypherui `CHANGELOG.md`, built from the changesets) is readable, so anyone can see what changed since a board was drawn.
- **On opening a canvas** (any session about to work on one), first check it: `pnpm ds:status <canvas>`. It lists the kit version on the canvas, the current version and the changelog entries in between, grouped by bump.
  - Only patches pending: carry on. The next publish of that canvas copies the bundle.
  - A minor pending: ask the product owner one question, "re-render <canvas> to kit <v> now?", with the minor changelog lines. Re-render only on their yes.
  - A major pending: it should already have been done. Re-render now and say so.
- **Never** run a full `ds:sync` or `cypher-mirror` re-render because a merge said `will_mirror`, to publish a new icon, or to "keep canvases current".

## Third-party brand marks (CUI-0026; owner ruling, 2026-10-27)

- Use `<cu-brand domain="…">`. It fetches the logo from Brandfetch; simple-icons is only its fallback. Never hand-pick a mark from simple-icons, and never call a brand "unsourceable" without checking Brandfetch.
- **Check the Brandfetch client ID is configured** wherever `cu-brand` renders: the app calls `setupCypherUi({ brandfetchClientId })` at boot, and the DS runner and canvas boards need it too. Without it `cu-brand` logs "No Brandfetch client ID configured" and paints only its fallback glyph, so a board full of fallback glyphs means the ID is missing. The ID is a public client-side value, but look it up and handle it under the `cypher-secrets` rules.
- On the dark UI prefer Brandfetch's light (white) theme variant; where a brand has none, `cu-brand` masks the colour logo to a single-colour (`currentColor`) silhouette.
- Third-party devices and services lead their list row with their brand mark (`cu-brand slot="lead"`). A missing brand logo is not a kit request.

## Descriptions, charts, rows and brand pages (owner rulings, 2026-10-26/27)

- **Descriptions are practical.** App Store and extension descriptions state what the app does and what you use it for. No marketing blurb. Sentence case.
- **Charts and stats.** A chart legend sits under the graph, never above it, and the chart fills the card's width and its row height: a card gets a `cu-chart`, never a sized one. A card whose last child is a `cu-table` has no bottom padding (the row padding is the gap). Cards in one grid row are the same height; only a `major-minor` split lets them differ. A stat's value, label and sparkline are centred, never pushed to the end. A glyph sits at the centre of its disc; fix a low icon at the glyph or the disc, never with an offset in a story.
- **Machines, rows, apps.** Machine names are lowercase, spelled as `knowledge {topic: "design-fixtures"}` gives them. Rows waiting on the viewer carry their real actions: a `cu-row` carries its item's buttons in the `actions` slot, not `end`. "Your apps" lists every app the viewer has. Control slots use control glyphs; illustrative art only leads a card-grid card or a state display. A card with no `heading` keeps its own titles' size. Art in a `cu-state-display` halo keeps an inset, never edge to edge. Another site's sign-in sets `brand` once on the shell, with the backdrop.
- **Brand pages and the profile hub.** A page for a specific brand uses that brand's branding throughout: `brand=` once on the shell tints frame, backdrop, auth container and logo. Button text is the label role, never its own face or tracking. The profile page is a hub of widgets from the apps the person uses; a person decides who sees each profile widget, and other viewers only see what was shared with them. A profile widget wears its app: the brand class is set once on the card, and a brand class must re-derive every accent variable resolved at `:root`. A tab strip's `value` may name a tab that has not arrived yet; `cu-tabs` leaves it alone.

## Lists and chat avatars

- **A list is a list (owner ruling, 2026-10-27).** Rows that form a list sit in `cu-rows`, which draws the shared list rhythm: striped rows, a hairline (`3xs`) gap, no per-row borders. Never stack bordered rows at a card's body gap. `cu-rows` also gives the list its loading, empty and error states.
- **Agents in chat are always character avatars** from the shared character set (`character-fixtures.ts`, `cu-character`). Never use initials or a generic bot icon.
