## Context

`run()` currently takes no parameters and `main.py` is a trivial passthrough. Adding an Artist Limit requires threading a user-supplied integer from the CLI down to the sync loop.

## Goals / Non-Goals

**Goals:**
- Expose `--limit N` as an optional CLI argument
- Reject invalid values (≤0) before any API calls

**Non-Goals:**
- Progress cursor / stateful batching across runs
- Limiting at the album or playlist level

## Decisions

**`main.py` owns argparse; `run()` accepts `limit` as a parameter.**
Putting argparse inside `run()` would make it hard to call from tests. `main.py` parses, `run()` accepts a plain `int | None`.

**Slice applied in `run()`, not inside `derive_artists`.**
`derive_artists` is a pure transformation. Slicing `artists[:limit]` in `run()` keeps policy at the orchestration layer and `derive_artists` side-effect-free.

**Validation via `argparse` custom type function.**
A `type=` callable raises `ArgumentTypeError` for ≤0 values, giving argparse a consistent exit path with a human-readable message before any I/O.

## Risks / Trade-offs

[Limit > number of artists] → Slice is a no-op; all artists processed. Correct behavior, no guard needed.
