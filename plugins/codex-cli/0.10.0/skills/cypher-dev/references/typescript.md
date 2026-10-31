# TypeScript rules for cypher* repos

Load when you touch `.ts` or `.tsx` (also Svelte and Lit sources). TypeScript is for UI: cypherui kit and app front-ends. Layers on top of `cypher-dev`. Rule ids D-23..D-31 in `rules/rules.yaml`.

## Strictness (D-23)

- `strict: true` in `tsconfig.json`.
- No `any`. Use proper types, or `unknown` plus a narrowing check.
- No `@ts-ignore` or `@ts-expect-error`. Fix the type, don't suppress it.
- No `as unknown as T` casts. Define a type guard or fix the signature.
- Type every function parameter and return. `noImplicitAny` is non-negotiable.

## Modules and imports (D-24)

- ESM only. No CommonJS in new code.
- Cross-package imports use the package alias (`@cypherflix/ui`, `@orqa/engine`), never relative paths into another package. Relative paths are fine within a package.
- One default export per file when it represents a single concept; named exports for utility modules.

## Async and errors (D-25)

- `async/await` over raw promise chains.
- Errors callers should handle are returned (or carried in a Result-shaped type), not thrown. Throw only for unrecoverable conditions and at the top boundary that catches them.
- No swallowed errors. `catch (e) { console.error(e) }` is a bug.

## Components (D-26)

Svelte 5 uses the runes API:

- `$state()` for reactive state, never `let x = value`.
- `$derived()` for computed values and `$effect()` for side effects, never `$:`.
- `$props()` for inputs, never `export let`.
- `{#snippet}` and `{@render}`, never `<slot>`.

Lit / web components (cypherflix's choice):

- Each cu-* primitive follows the five patterns in `.recon/02c-cf-primitive-architecture.md`: opt-in MutationObserver, signal-driven cross-cutting state, components own their visual concerns, host attributes as source of truth, lifecycle discipline.
- No inline fixture data inside a primitive; fixtures live in story files.
- No new `.cu-*` CSS class inside a primitive's `static css`. A new class is a sub-component fingerprint: extract it.
- Hard ceiling: 250 lines of primitive body (excluding the header docstring).
- A primitive's job description never contains "and". One word means one primitive.

Both frameworks:

- Components stay under 150 lines (Svelte) or 250 lines (Lit primitives); extract sub-components past that.
- Every component handles loading, empty and error states.
- No emoji in UI. Use Lucide icons (Svelte) or the project's icon set (Lit).
- Variant props, not inline Tailwind or utility-class overrides.
- Components take generic `data` props, not domain types. Domain-to-component mapping happens at the route or feature layer.

## UI is built from kit blocks only (D-27)

Every UI is composed from `@cyphercoven/cypherui` elements and nothing else (cypherui CUI-0057). If the blocks are complete, any layout can be built from them.

- Consumer code holds no raw HTML elements. Templates (lit `html```, JSX, Svelte markup, page-shell `<body>`) contain only `cu-*` kit elements and the app's own `<prefix>-*` elements, which are themselves built only from `cu-*`. Prefer an archetype (cypherui law 7) over assembling primitives by hand.
- It is a gate, not a guideline. Every repo that renders UI runs the kit's `cu-kit-only` in its `check` script and in CI; a finding fails the build.
- A missing block grows the kit. When a layout can't be built from the kit, don't work around it with a raw element: file `kit-requests/NNN-name.md` in the app, add the block to cypherui (a primitive or an archetype with stories, tests and docs), then use it.
- The kit's own primitive tier (`cypherui/src/primitives/**`) is the one place native elements are rendered, inside each primitive's shadow root.

## Styling (D-28)

- Utility CSS (Tailwind, UnoCSS) lives only at the UI component layer (`packages/ui/<component>/`). App routes use semantic CSS plus design tokens (`var(--cu-*)`).
- Overrides come through component props or theme tokens, not classes added from outside.
- Theme tokens flow top-down; components never reach up.

## Stores and state (D-29)

- Runes-based stores in `.svelte.ts` files (Svelte).
- Stores call the data layer; components read from stores.
- Expose reactive state and action methods. One store per domain concept.

## Testing (D-30)

- `vitest` for unit and integration; browser-mode vitest (`@vitest/browser-playwright`) for real Chromium where the DOM matters. Playwright for e2e against ephemeral fixture servers.
- Every UI primitive has a story in the component explorer.
- Coverage floors per `cypher-dev`: 80% line / 70% branch on touched files for app code; higher for shared primitives.
- Affected tests: `vitest related <changed files> --run`.

## Bundling (D-31)

- Vite for libraries (`packages/`) and Astro apps.
- No global polyfills shipped to the browser without a recon doc justifying them.
- A bundle-size budget gates CI.
