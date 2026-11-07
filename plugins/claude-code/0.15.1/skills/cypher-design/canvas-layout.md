# Canvas layout and sizing (cypher-design reference)

Loaded from `skills/cypher-design/SKILL.md` §1 and §2. Every rule here binds; `ds-measure --check` enforces most of them.

## Canvas layout: easy to navigate (owner ruling, 2026-10-24)

- **Lay the canvas out for the most accessible reading possible.** Someone opening it should find any screen in a couple of glances.
- **Keep pages small.** A page holds at most **12 boards in at most 4 rows**. When a page gets busier than that, split it into intuitively named category pages (for example Sign-in, Admin · People, Admin · Machines, App Store). Never put everything on one page.
- **Every board and note carries a page the canvas lists (owner ruling, 2026-10-26).** The host draws a pageless item on the first page, on top of its boards. `ds-measure --check` fails a pageless item and any overlap.
- **Page and row names are plain words:** "and", never "&"; "<title>, continued", never "X to Y" or "states: … to …".
- **Each row is a flow or a set of related screens**, read left to right in the order a person moves through them (e.g. sign-in → access → signed-in; list → detail → edit). Never mix unrelated screens in a row.
- **Use even spacing.** All boards in a row have the same gap, all rows on a page have the same gap, and each row is top-aligned. No staggered or ragged placement.
- **Size every board to fit its content exactly**, and never give it internal scroll. Screens keep the 1920 base width (see §2).
- **Treat dead space as a bug.** Empty space at the top or bottom of a board almost always means something is aligned wrong (a centred stack, a `fit` that doesn't fill, a wrong `min-height`). Fix the story or the kit; never pad or crop the board to hide it.
- **Judge a board by looking at it.** The canvas shot PNGs aren't 1920 wide, and `ds-measure` can't see a squeezed card. Take a real 1920-wide screenshot against the runner before calling a board right.
- **Titles and post-its are written for the product owner (owner ruling, 2026-10-25).**
  - Page, row and board titles are plain words ("Signing in", "Install finished"). Never use story paths ("Admin / Groups"), file stems ("session-session"), "Default", or "(1/3)".
  - A post-it is one or two plain sentences: what the person is doing and what to look at. It comes from the story's `parameters.ds.caption`.
  - A post-it never holds dev notes, file paths, ticket ids, element names, or a repeat of the title. No post-it beats a bad one.
  - Every story on an app canvas declares `parameters.ds.page`, `ds.row` and `ds.caption` (plus `ds.order` in a flow). Root repos (cypherinstall, cypherveil) carry the same fields in their own capture.
- **App canvases hold app screens only.** Component galleries, part strips and token pages go on CypherUI Components as card boards sized to their content.
- **Every board has a page.** Group pages by journey (a flow row, then its failure states), never by file.
- **Flows are clearly labelled and in order (owner ruling, 2026-10-25).** A row that is a flow says so in its title, naming the journey ("Sign-in flow: signed out → access → signed in"). Each board shows its step number ("1 · Signed out", "2 · Access"), and boards sit strictly in step order, left to right. Every story in a flow row declares `parameters.ds.order`, and the check fails on a missing, duplicate or out-of-order step. A row of related states or variants is not a flow and gets no step numbers.
- **One left edge per page (owner ruling, 2026-10-25).** Every row's title, its post-it and its first board start at exactly the same x, and that x is the same for every row on the page. No row is indented or offset.
- **Rows are equally spaced (owner ruling, 2026-10-25).** The gap from the bottom of one row (its tallest board) to the next row's title is exactly the same on every row and every page, whatever the row heights. The check measures it from the drawn boards and fails on any difference.
- **Nothing overlaps (owner ruling, 2026-10-25).** No board overlaps a board, and no label or post-it note overlaps a board or another note.
- **Labels sit in place.** Each row's title is left-aligned to the row's first board, directly above it, at the same offset on every row. A post-it subtitle sits directly under its title at the same x.
- **Leave plenty of room for titles.** The space between a row's title and its boards fits the title plus a two-line post-it, with generous margin, and it is the same on every row. `ds-measure --check` fails on any overlap or misplaced label.
- **How the generator does it** (`scripts/ds-page-layout.mjs`): every row gets the same title + caption band (NOTE_CLEAR 400, CAPTION_DY 128, NOTE_AIR 32, NAME_STRIP 40, GAP_Y 200). Change those numbers there, never per board.
- **A flow row has one board per `ds.order` step**, and the step count must equal the board count. A second story in a flow file needs its own row ("…: states"), or it inherits the flow row and fails the count.
- **A gallery or spec sheet declares `parameters.ds.board = 'card'`.** Otherwise it is a 1920 screen and `emptyScreen` fails it. `emptyScreen` also catches a body that never got projected (only chrome): look at the render before reaching for `board: 'card'`.
- **A story's `window` entry is its size only.** Resizable or not comes from the root card's window, which the story inherits.

## Canvas and screen sizing (owner ruling, 2026-10-24)

- **The base is 1920×1080.** A screen board is exactly 1920 px wide and at least 1080 px tall.
- **Expand, never overflow.** If the content is taller, the board grows taller so nothing is clipped and nothing scrolls inside the board. It never grows wider: no horizontal scroll, ever.
- **The navigation and the top bar are fixed height and never scroll.** The top bar is pinned at its kit height, and the side nav and app rail are pinned full-height. Only the main content region moves or grows, and the board's extra height goes to main.
  - The one exception is a web media view (`platform="web" purpose="media"`, e.g. CypherFlix in a browser). There, the nav strip keeps its slide-away-on-scroll-down behaviour. In the desktop app it is always pinned.
- A **window** board is a non-resizable window drawn at exactly its declared `tauri.conf.json` size (e.g. CypherInstall 640×480). Content must fit that window. A taller board means the screen is wrong, not the board.
- **No nav means no nav column.** A workspace with nothing in its nav slot draws no nav column, no collapse control and no gutter for it. An empty nav bar is a bug.
- A **card** board (a component strip) is sized to its content, up to a 3240 px cap. Split a taller story in the story itself.
- `ds-measure --check` must be clean: no clipping, screens 1920 × ≥1080, cards ≤ 3240.
- Older notes giving 1280×900 (CUI-0062 §5) are superseded.
