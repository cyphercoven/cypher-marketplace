# Rust rules for cypher* repos

Load when you touch `.rs`. Layers on top of `cypher-dev` (functional core, failing test first). Rule ids D-16..D-22 in `rules/rules.yaml`.

## Formatting and linting (D-16)

- `rustfmt` formats all code. Run `cargo fmt --check` before commits.
- `clippy` with the pedantic and nursery groups enabled. Zero warnings: `cargo clippy --all-targets -- -D warnings`.

## Error handling (D-17)

- `thiserror` for all custom error types.
- Every function that can fail returns `Result<T, E>`. No `unwrap()`, `expect()`, `panic!()` or `unreachable!()` in production code. Tests may use them.
- Error types are enums with descriptive variants. Each variant carries enough context to fix the problem without a re-run.
- IPC commands (Tauri) return `Result<T, String>` for serialisation; the `String` is built from the `thiserror` `Display`.
- `?` is the default. Use `match` only when you branch on the variant.

## Type design (D-18)

- IPC types derive `Serialize`, `Deserialize`, `Debug`, `Clone`.
- Domain types are immutable by default. Mutation goes through a constructor or a builder, never direct field writes.
- Newtypes for every domain identifier: `SessionId(String)`, `ArtifactId(String)`, `EpicId(String)`. No raw `String` IDs in function signatures.
- Prefer `&str` over `String` for parameters that do not need ownership.

## Module organisation (D-19)

- One module per domain concept.
- Public API through `mod.rs` or `lib.rs`. Internal items stay `pub(crate)` or unmarked.
- `main.rs` is minimal: it wires things together and starts the runtime. Logic lives in modules.
- Conventional layout: `commands/` for IPC entry points, `domain/` for pure logic, `repo/` for data access, `adapters/` for side-effect wrappers.

## Function size (D-20)

- Domain functions 20-30 lines, command handlers 30-50, utilities 10-20.
- Hard ceiling: 50 lines of function body. Past it, extract helpers.

## Dependencies (D-21)

- Prefer well-maintained crates with a release in the last 12 months (soft bar).
- No duplicate functionality between crates: pick one and use it consistently.
- Pin versions in `Cargo.toml`. No `*` or `^x` ranges in production.
- Justify every new dependency in the commit message.

## Testing (D-22)

- Unit tests sit alongside code in `#[cfg(test)] mod tests` blocks. Integration tests go in `tests/`.
- Property tests with `proptest` or `quickcheck` for pure functions with structured input.
- Async tests use `tokio::test` (or the runtime's macro). No bare blocking in async tests.
- Affected tests: `cargo test -p <changed crate>` plus the crates that depend on it.
