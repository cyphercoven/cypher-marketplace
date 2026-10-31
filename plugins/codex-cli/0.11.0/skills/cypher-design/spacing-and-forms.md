# Rhythm, grids, tables and forms (cypher-design reference)

Loaded from `skills/cypher-design/SKILL.md` §8. Every rule here binds.

### Rhythm: spacing is hierarchical (owner ruling, 2026-10-24; `docs/page-rhythm.md`)

- **The gap shrinks as you go deeper into the structure.** Sections are further apart than a heading is from its content. A heading sits further from its rows than the rows sit from each other, and rows sit further apart than inline items. Space alone should show what belongs to what.
- **Every section must read as clearly separate.** Use the `3xl` section gap. Where space alone doesn't separate them clearly (dense pages, sections that look similar, long scrolling lists), put a `cu-divider` between them. Never use both a divider and extra margin; the divider sits within the section gap.
- Never give two levels the same gap. A heading-to-content gap equal to the row gap is a bug.

| Between (outer → inner) | Gap | Built with |
|---|---|---|
| Page title → sections | the header's own bottom padding | `cu-page-header` |
| Sections | `3xl` (+ `cu-divider` where space alone isn't clear) | `cu-stack gap="3xl"` |
| Heading → its content | `m` | `cu-stack gap="m"` around both (`cu-heading` has no margin) |
| Hero → first content | `l`, the same as a page title, never the section gap (owner ruling, 2026-10-25) | built into the page stack |
| Card header → card body | `l`, clearly bigger than the body rows (owner: "one of the main culprits") | built into `cu-card` |
| Rows | `s` | `cu-stack gap="s"` |
| Inline items | `xs` | `cu-cluster gap="xs"` |

- A child never has an outer margin. The parent stack owns every gap.
- **A divider sits exactly midway in its gap**, with equal space above and below.
- **A labelled divider** (`<cu-divider label="Or">`) draws its rules either side of the word, on one line, vertically centred. Never stack a divider with a separate "or".
- The space scale is closed: `3xs 2xs xs s m l xl 2xl 3xl 4xl 5xl`.
- Use container queries, not viewport queries.

### Grids (owner ruling, 2026-10-25)

- **One page grid.** Every row of cards on a page follows the same column grid. Never stack separate grids whose columns don't line up.
- **Spans are whole columns.** A 2-span card is exactly two columns plus the gap between them, so it matches the two cards above it. Split presets (major/minor) are built on that same column grid.
- **Gaps are even.** Row gap equals column gap.
- **Cards in a grid row are equal height**, and their actions (footer) line up at the bottom (kit default).

### Tables and lists (owner ruling, 2026-10-25)

- **Data tables sit in a card, and the card's heading names the table.** Don't use a section heading over a bare table.
- **A single-column table has no header row.** The heading already names it; action and icon columns don't count as columns.
- **Every list row leads with a graphic** (owner ruling, 2026-10-26): film or show art, the app icon, an avatar, or a control glyph in a two-tone lead disc (never an illustrative icon). This is the kit default, and `audit-row-lead` fails a row without one.

### Forms and controls (owner ruling, 2026-10-25)

- **Form fields fill their container** (kit default), and a button that pairs with them (`block`) matches their width.
- **A state never changes a control's size.** A loading button keeps its exact rest width: the spinner centres and the label hides.
- Profile text (name and role) is left aligned in every profile surface and variant.
- **A list of settings or access choices is a form** (owner ruling, 2026-10-26): `cu-field layout="row"`, with a fixed label column (title plus a one-line help text, the same gap on every row) and one aligned column of controls.
