### Requirement: Status module provides a rewriting terminal status line
The system SHALL provide a `status` module at `spotify_playlist_creator/status.py` with a module-level callable (defaulting to a no-op lambda) that writes a rewriting status line to stdout. `status.write(msg)` SHALL emit `\r\033[2K{prefix} — {msg}` when a context prefix is set, or `\r\033[2K{msg}` when none is set, with no trailing newline, followed by `sys.stdout.flush()`.

#### Scenario: Write with no context set
- **WHEN** `status.write("fetching releases (1/3)...")` is called with no context set
- **THEN** `\r\033[2Kfetching releases (1/3)...` is written to stdout with no newline

#### Scenario: Default callable is no-op (no crash before configure is called)
- **WHEN** `status.write(...)` is called before `status.configure()` has ever been called
- **THEN** no exception is raised and nothing is written to stdout

#### Scenario: (no external I/O contract — output goes to stdout directly)

### Requirement: Status context prefix is prepended to all writes
`status.set_context(ctx)` SHALL store a prefix string. While a non-empty context is set, every call to `status.write(msg)` SHALL prepend `{ctx} — ` to the message.

#### Scenario: Write with context set
- **WHEN** `status.set_context("[3/10] Radiohead")` is called, then `status.write("fetching releases (2/4)...")`
- **THEN** `\r\033[2K[3/10] Radiohead — fetching releases (2/4)...` is written to stdout

#### Scenario: Empty context produces no prefix
- **WHEN** `status.set_context("")` is called, then `status.write("msg")`
- **THEN** `\r\033[2Kmsg` is written with no ` — ` separator

#### Scenario: (no external I/O contract)

### Requirement: clear() wipes the status line and resets context
`status.clear()` SHALL emit `\r\033[2K` to stdout (wiping the current line), flush, and reset the context to an empty string.

#### Scenario: clear() leaves the terminal on a clean empty line
- **WHEN** `status.clear()` is called after a previous `status.write(...)`
- **THEN** `\r\033[2K` is written and the context is reset to `""`

#### Scenario: clear() is safe to call with no prior writes
- **WHEN** `status.clear()` is called without any preceding `status.write()`
- **THEN** no exception is raised

#### Scenario: (no external I/O contract)

### Requirement: Status callable is replaceable via configure()
`status.configure(fn)` SHALL replace the module-level callable with `fn`. Subsequent calls to `status.write(msg)` SHALL invoke `fn` with the fully-assembled line string (including prefix and escape codes).

#### Scenario: Custom callable receives the assembled line
- **WHEN** `status.configure(fn)` is called with a recording function, then `status.write("hello")`
- **THEN** `fn` is called with `"\r\033[2Khello"`

#### Scenario: Replacing callable takes effect immediately
- **WHEN** `status.configure(fn1)` then `status.configure(fn2)` then `status.write("x")`
- **THEN** only `fn2` is called; `fn1` is not called

#### Scenario: (no external I/O contract)
