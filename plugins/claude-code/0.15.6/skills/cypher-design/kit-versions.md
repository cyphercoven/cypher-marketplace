# Kit versions, brands and lists

Read this with `SKILL.md` before choosing a kit version bump, and before putting a third-party mark or a list on a board.

## Kit version bumps (owner ruling, 2026-10-27)

**The kit's semver bump says how much a change matters to consumers.** Every kit change carries a changeset, and its bump level is the rule:

| Bump | What it covers |
|---|---|
| **patch** (0.0.x) | A new icon or glyph, a new component, variant or token nothing uses yet, a fix that doesn't move what a screen draws, docs |
| **minor** (0.x.0) | Anything that changes what screens draw: spacing, padding, positioning, sizing, type, colour, a component's default look |
| **major** (x.0.0) | Breaking: an element, attribute or slot retired or renamed, a changed API |

- **Pick the bump honestly.** Whether a screen draws differently decides patch versus minor, not the size of the diff. If unsure, preview one affected screen before and after and compare.
- The kit changelog (cypherui `CHANGELOG.md`, built from the changesets) is readable, so anyone can see what changed between versions.
- **The design-system mirror is retired (ADR: design-system mirror retired, 2026-11-06).** A kit bump no longer triggers any canvas render or sync. Previews are published as paths on the preview service (suite-tidy S-31/S-61; CypherMind `/mind` is the model); procedure: slice 2, pending. The last design-system publish stays as history: kit 1.13.0, Design System artifact version 101.

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
