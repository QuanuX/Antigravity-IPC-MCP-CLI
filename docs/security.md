# Security Boundary & IPC Invariants

`symphony-mcp` enforces strict OS-level and protocol-level boundaries between the MCP host (Antigravity, `agy`, Gemini CLI, Codex, Claude Code) and the local QuanuX Symphony `qxctl` installation.

## 1. Subprocess Execution Hardening (`src/transport.cpp`)

- **No Shell Execution:** `qxctl` is invoked exclusively through POSIX `fork()` and `execve()` with an explicit argument vector (`argv`) and sanitized environment (`envp`). Shell metacharacters in user arguments are never interpreted by a shell.
- **Executable Ownership & Permission Checks:** `qxctl` must be a regular executable file owned by the current effective UID or `root` (`0`), and must not be group-writable or world-writable.
- **Process Group Isolation & Bounded Timeouts:** Every child process is placed in its own process group (`setpgid(0, 0)`). On timeout (`timeout_ms`), `symphony-mcp` signals the entire process group with `SIGTERM`, waits up to a bounded grace window, and escalates to `SIGKILL`.
- **Bounded Output Capture:** Both `stdout` and `stderr` are capped at `max_output_bytes`. Truncation on a mutating command forces `outcome_state: "unknown_requires_reconciliation"` and MCP `isError: true`.

## 2. Same-User Unix-Domain Socket IPC (`--listen` / `--connect-socket`)

- **Parent Directory Verification:** The socket parent directory must be a real directory (not a symlink), owned by `geteuid()`, with permissions `0700`.
- **Socket Mode `0600`:** Created under a restrictive `umask(0177)` and explicitly `fchmod`/`chmod` to `0600`.
- **Kernel Peer-Credential Verification:** Both the listener (`accept`) and the client (`connect`) verify the peer process's effective UID via `getpeereid()` (macOS/BSD) or `SO_PEERCRED` (Linux) before reading or writing a single byte of JSON-RPC traffic.
- **Inode-Verified Cleanup:** On shutdown, the listener verifies the filesystem path's `st_dev` and `st_ino` match the bound socket before unlinking.
