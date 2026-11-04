# Python rules for cypher* repos

Load when you touch `.py`. Python is allowed only where no Rust option exists and the spec names why. Layers on top of `cypher-dev`. Rule ids D-32..D-42 in `rules/rules.yaml`. Source model: cypherdemon's `core / adapters / fetchers / inference / scheduler` split.

## Toolchain (D-32)

- `uv` for workspaces, lockfile and venvs. `uv.lock` is the source of truth.
- `ruff` for lint and format. Zero warnings.
- `mypy` in strict mode. No `# type: ignore` without a paired comment naming the upstream bug or library limitation.
- `pytest` for tests. `pytest --run-integration` runs the integration-marked tier, which is skipped by default.

## Functional Python (D-33)

- `core/` is pure. No I/O, no global state, no clock access. If you need the time, take a `Clock` parameter.
- `adapters/` are side-effect shells. Each is the thinnest wrapper around one I/O operation. It catches raw exceptions and returns `Result`.
- `fetchers/` (or service entry points) are composition only: load config, build request, call adapter, parse, return `Result`. No branching logic; branching belongs in `core/`.
- `daemon.py` / `main.py` is the loop driver. It is the only place that calls `time.sleep()` or runs an infinite loop.

## Error handling (D-34)

- Pure functions in `core/` never raise. They return `Result[T, E]` (the project's `Result` type, e.g. `cypherdemon.core.result`).
- Adapters may catch third-party exceptions but wrap them in `Result` before returning.
- Custom error types are dataclass-or-enum hierarchies. Every error has a `.fix_hint()` returning a short, actionable remediation string, surfaced in `/api/status` and in tray apps.
- `try: except Exception:` is allowed only at the outermost daemon loop driver and at the HTTP / IPC handler boundary. Never in `core/`: to swallow an exception there, define a new error variant.
- No silent `pass` in `except` blocks.

## Type design (D-35)

- Frozen dataclasses (`@dataclass(frozen=True)`) for domain types.
- `Final` for module-level constants.
- No `Any` unless interfacing with an untyped third-party library at the adapter boundary; cast and document it immediately.
- Prefer `Result[T, E]`, `Iterator[T]` and `Mapping[K, V]` over their mutable cousins.

## Module organisation (D-36)

- One module per domain concept.
- The logger namespace mirrors the module path: `cypherdemon.fetchers.calendar`.
- Environment variables follow the project's prefix convention (`CD_*` cypherdemon, `CM_*` cyphermind, `CB_*` the gateway). All caps, documented in the module that reads them.
- Docker volumes follow the project's kebab convention (`cd-*`, `cm-*`).

## File headers (D-37)

Every Python file opens with the project's header. If it is missing or wrong, fix it before touching anything else in the file. The three-section shape:

```python
"""<filename> — <one-line purpose>

PURPOSE
-------
What this file does and why it exists.

CONVENTIONS
-----------
Patterns to follow, anti-patterns to avoid, invariants this file relies on.

AGENT NOTES
-----------
Specific guidance for any LLM touching this file: what's load-bearing,
what changes require thinking, where edge cases hide.
"""
```

## State (D-38)

- No module-level mutable state. Exceptions: `__version__` strings and logger instances.
- Pass dependencies as parameters; don't reach for globals.

## Testing (D-39)

- TDD: write the failing test, watch it fail, then implement.
- Property tests with `hypothesis` for pure functions with structured input: at least one invariant per non-trivial `core/` function.
- Mock adapter behaviour in fetcher and service tests. Fetcher tests prove composition, not network behaviour.
- Integration tests are marked `@pytest.mark.integration`, skipped by default, gated behind `--run-integration`.
- Coverage gate: 80% global, 95% on `core/`. PRs below it don't merge.
- Affected tests: the test modules for changed modules and every module that imports them.

## Logging and secrets (D-40)

- Structured JSON logs to stderr via `structlog`. One log line per fetch and per scheduler tick (daemons).
- The structlog redactor blanks known secret keys. Never log secrets, full HTTP bodies or full PII.
- Secrets live in `secrets/`, gitignored and bind-mounted at runtime. Never baked into images.

## Docker (D-41)

- Multi-stage build: the builder installs deps, the runtime copies the venv and src.
- Run as non-root (UID 1000 by convention).
- Multi-arch via `TARGETARCH`.
- Entry point is a console script declared in `pyproject.toml` pointing at `<package>.daemon:main`.
- Status and control-plane ports bind to loopback only unless authentication is in place.

## Anti-patterns (D-42)

- Don't import inside functions to dodge circular imports; restructure the modules.
- Don't write to `core/` from `adapters/`.
- Don't put `try: except Exception:` anywhere but the boundaries above.
- Don't make a daemon depend on its desktop companion running. They are independent processes.
- Don't expose internal ports externally: loopback only, unless behind an auth layer with a recon doc justifying it.
