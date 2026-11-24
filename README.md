# QuanuX Symphony MCP, IPC, Rules, and Skills for Antigravity & Antigravity CLI

Native C++26 Model Context Protocol (`2025-11-25`) stdio server, same-user Unix-socket IPC bridge (`--listen` / `--connect-socket`), always-on VGAA architectural rules, and agent skills for **[QuanuX Symphony](https://github.com/QuanuX/Symphony)** across **Antigravity 2.0**, **Antigravity IDE**, **Antigravity CLI (`agy`)**, **Gemini CLI** (succeeding `QuanuX/quanux-gemini-cli-mcp`), **Codex**, and **Claude Code**.

- **Target Product:** [QuanuX Symphony (`github.com/QuanuX/Symphony`)](https://github.com/QuanuX/Symphony)
- **Websites:** [quanux.org](https://quanux.org) | [docs.quanux.org](https://docs.quanux.org) | [support.quanux.org](https://support.quanux.org)
- **Upstream Repository:** [`QuanuX/Antigravity-IPC-MCP-CLI`](https://github.com/QuanuX/Antigravity-IPC-MCP-CLI) (succeeding [`QuanuX/quanux-gemini-cli-mcp`](https://github.com/QuanuX/quanux-gemini-cli-mcp) and paired with [`QuanuX/symphony-codex-ipc-mcp-and-skills`](https://github.com/QuanuX/symphony-codex-ipc-mcp-and-skills))
- **License:** GNU Affero General Public License v3.0 (`AGPL-3.0-only`)

---

## Architectural Position (VGAA & Caller-Class Neutrality)

QuanuX Symphony is a **Vendor-Neutral Governed Execution & Sovereign Operations Platform** built in C++26 (`symphonyd`), Go (`qxctl`, `symphony-admin`), and Rust (`symphony-edge`, `symphony-Hot`).

This repository provides a **thin, caller-class-neutral local adapter** (`symphony-mcp`) that routes Model Context Protocol (`2025-11-25`) tool calls to an existing user-installed `qxctl` binary using direct POSIX `fork`/`execve` argument arrays (never `system()`, `popen()`, `/bin/sh -c`, or string interpolation):

1. **No Ambient Authority:** Calling through Antigravity, `agy`, Gemini CLI, Codex, or Claude Code grants zero additional authority. Every capability check, policy gate, confirmation token, and audit record is enforced by the native Symphony owner service behind `qxctl`.
2. **Strict Hot-Path Isolation:** Neither `symphony-mcp` nor any agent skill touches the Rust execution engine (`symphony-Hot`), live strategy state, or broker sockets directly. All interactions traverse the governed `qxctl` control plane.
3. **Process Exit `0` != Semantic Success:** `symphony-mcp` inspects the structured JSON payload returned by `qxctl` (`error`, `ok == false`, `status` in `failed` / `rejected` / `denied` / `error` / `blocked`) and sets MCP `isError: true` whenever the native owner reports a semantic rejection, even if the OS process exited `0`.
4. **Transport Preview != Owner Dry-Run:** Every non-read command requires a same-session preview step (`*_preview` or `symphony_prepare`) that computes a canonical `plan_id` and `plan_sha256` before execution (`*_apply` or `symphony_apply`). Transport preview verifies exact argument binding; it is not a native owner simulation or authorization grant.
5. **Reconcile Unknown Non-Read Outcomes:** If a mutating call returns `outcome_state: "unknown_requires_reconciliation"` (timeout, truncated output, signal termination, or non-JSON stdout), agents must reconcile owner state with a read-only `status`/`get`/`list` tool before retrying.

---

## Capabilities Overview

| Feature | Implementation |
| :--- | :--- |
| **Native C++26 MCP Server** | `symphony-mcp` implementing MCP `2025-11-25` over newline-delimited stdio JSON-RPC |
| **Reviewed Public Tool Catalogue** | [`catalog/tools.json`](catalog/tools.json) exposing **744 tools** (`symphony_connection` + **743** operation-specific tools covering all **523** routable `qxctl` commands: **303** `*_read` tools and **220** `*_preview` / `*_apply` pairs, paginated 50 per page via `nextCursor`) |
| **Live Registry Discovery Mode** | Omit `--tool-catalog` to expose the compact 6-tool live discovery surface (`symphony_connection`, `symphony_catalog`, `symphony_command_schema`, `symphony_read`, `symphony_prepare`, `symphony_apply`) backed by live `qxctl commands list --json` |
| **Same-User Unix-Socket IPC** | `--listen <socket>` runs a local mode-`0600` Unix-domain socket daemon inside a mode-`0700` non-symlink directory with kernel peer-UID verification (`getpeereid` / `SO_PEERCRED`); `--connect-socket <socket>` connects any stdio MCP host to the running daemon |
| **Always-On VGAA Rules** | [`rules/AGENTS.md`](rules/AGENTS.md) (Antigravity plugin rule) and [`GEMINI.md`](GEMINI.md) (Antigravity CLI / Gemini CLI context file) |
| **Agent Skills** | [`skills/symphony-admin/SKILL.md`](skills/symphony-admin/SKILL.md), [`skills/symphony-setup/SKILL.md`](skills/symphony-setup/SKILL.md), and [`skills/symphony-ipc/SKILL.md`](skills/symphony-ipc/SKILL.md) |
| **Host Manifests** | [`plugin.json`](plugin.json) + [`mcp_config.json`](mcp_config.json) (Antigravity & `agy`), [`gemini-extension.json`](gemini-extension.json) (Gemini CLI & `agy plugin import gemini`), [`mcp.json`](mcp.json), [`.mcp.json`](.mcp.json), [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json), [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json), and [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) |
| **Historical MCP Registry packaging templates** | [`server.json`](server.json) and [`packaging/mcpb/manifest.json`](packaging/mcpb/manifest.json) illustrate the alpha MCPB format. The zero digest is a placeholder. The beta installer and verified platform ZIPs are on the [official Antigravity release](https://github.com/QuanuX/Antigravity-IPC-MCP-CLI/releases/tag/v0.2.0-beta.2.1). |

---

## Install Symphony for Antigravity

Install [Symphony 0.2.0-beta.2.1](https://quanux.org/downloads) on the same machine that runs the local MCP server. Use the **Antigravity** install option on the [QuanuX downloads page](https://quanux.org/downloads#antigravity) to verify and run the Python installer. The [GitHub release](https://github.com/QuanuX/Antigravity-IPC-MCP-CLI/releases/tag/v0.2.0-beta.2.1) carries the installer, checksums and native plugin ZIPs.

The installer requires Python 3.11 or later and curl. It selects the current user's guided Symphony installation and installs the plugin in `~/.gemini/config/plugins/symphony`. It creates a private read-only connection, verifies a real MCP handshake against the selected qxctl, and loads the matching release catalog. Restart your Antigravity session and open `/mcp` to see the connection. The plugin includes three skills and the VGAA rule.

To install for just one project, run `python3 -I install-antigravity.py --workspace /path/to/project`. To select an alternate signed Symphony prefix, add `--qxctl /path/to/qxctl`. The helper preserves an existing plugin or different connection and reports its location. Repeating the install of the same release checks the existing binding.

Supported Symphony cohorts are macOS 15 Apple Silicon, Ubuntu 24.04 AMD64 or ARM64, and Ubuntu 26.04 AMD64. The component reports its own version as `0.2.0-beta.2.1`. Use the instructions below for a source build.

## Build from source

### 1. Build, Test, and Install `symphony-mcp`

Requires a C++26 compiler (Apple Clang 17+ or GCC 14+/Clang 19+), CMake 3.30+, and Python 3.11+ for test and configuration helpers:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
ctest --test-dir build --output-on-failure
cmake --install build --prefix "$PWD"
```

This installs the compiled binary at `./bin/symphony-mcp` (resolved automatically by [`packaging/antigravity/launcher.sh`](packaging/antigravity/launcher.sh)).

### 2. Create a Mode-`0600` Connection Profile

Create a private connection profile pointing to your local `qxctl` installation:

```bash
python3 scripts/configure_connection.py \
  --output "$HOME/.config/symphony-mcp/connection.json" \
  --qxctl /usr/local/bin/qxctl \
  --working-directory "$HOME" \
  --profile-name local-operator
```

### 3. Configure Antigravity, Antigravity CLI (`agy`), or Other Hosts

#### Option A: Direct Stdio Mode (Default — 744 Public Operation Tools)

Generate the host configuration for your client:

```bash
# Antigravity Desktop / IDE (~/.gemini/antigravity/mcp_config.json)
python3 scripts/configure_clients.py \
  --client antigravity \
  --binary "$PWD/bin/symphony-mcp" \
  --config "$HOME/.config/symphony-mcp/connection.json" \
  --tool-catalog "$PWD/catalog/tools.json"

# Antigravity CLI (agy) (~/.gemini/settings.json)
python3 scripts/configure_clients.py \
  --client antigravity-cli \
  --binary "$PWD/bin/symphony-mcp" \
  --config "$HOME/.config/symphony-mcp/connection.json" \
  --tool-catalog "$PWD/catalog/tools.json"
```

#### Option B: Local Unix-Socket IPC Daemon Mode (`--listen` / `--connect-socket`)

When running multiple Antigravity windows, `agy` sessions, or subagents simultaneously, start a single local Unix-socket IPC listener and connect each MCP host via `--connect-socket`:

```bash
# 1. Start the background same-user Unix-socket listener
python3 scripts/manage_ipc_daemon.py start \
  --binary "$PWD/bin/symphony-mcp" \
  --config "$HOME/.config/symphony-mcp/connection.json" \
  --socket "$HOME/.config/symphony-mcp/run/symphony-mcp.sock" \
  --tool-catalog "$PWD/catalog/tools.json"

# 2. Verify daemon health and run a live MCP initialize probe over the socket
python3 scripts/manage_ipc_daemon.py status \
  --socket "$HOME/.config/symphony-mcp/run/symphony-mcp.sock" \
  --binary "$PWD/bin/symphony-mcp" \
  --probe

# 3. Generate Antigravity / agy config pointing to --connect-socket
python3 scripts/configure_clients.py \
  --client antigravity \
  --binary "$PWD/bin/symphony-mcp" \
  --connect-socket "$HOME/.config/symphony-mcp/run/symphony-mcp.sock"
```

---

## Documentation Index

- [Host Compatibility & Installation (`docs/host-compatibility.md`)](docs/host-compatibility.md)
- [Connection Profile Schema (`docs/connection-profile.md`)](docs/connection-profile.md)
- [Public Operation-Specific Tools (`docs/public-operation-tools.md`)](docs/public-operation-tools.md)
- [Antigravity & Antigravity CLI Acceptance Guide (`docs/antigravity-acceptance.md`)](docs/antigravity-acceptance.md)
- [Codex & Multi-Host Acceptance Guide (`docs/codex-acceptance.md`)](docs/codex-acceptance.md)
- [Security Boundary & IPC Invariants (`docs/security.md`)](docs/security.md)
- [Migration from `QuanuX/quanux-gemini-cli-mcp` (`docs/repository-migration.md`)](docs/repository-migration.md)
- [Historical MCP Registry and MCPB packaging examples](docs/mcp-registry.md)
- [Verification & Qualification Suite (`docs/verification.md`)](docs/verification.md)
- [Directory Submission Guide (`docs/submission.md`)](docs/submission.md)
- [Supported Platforms (`docs/platforms.md`)](docs/platforms.md)
