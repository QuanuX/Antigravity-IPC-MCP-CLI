---
name: symphony-setup
description: Build symphony-mcp, create a pinned mode-0600 connection.json profile, and configure Antigravity 2.0, Antigravity IDE, Antigravity CLI (agy), Gemini CLI, Codex, or Claude Code for direct stdio or local Unix-socket IPC.
---

# Symphony MCP & IPC Setup for Antigravity and Antigravity CLI (`agy`)

Configure the native C++26 `symphony-mcp` bridge for **Antigravity 2.0**, **Antigravity IDE**, and **Antigravity CLI (`agy`)** (as well as Gemini CLI, Codex, and Claude Code).

## 1. Prerequisites

- macOS (`arm64` or `x86_64`) or Linux (`x86_64` or `aarch64`), or Windows 11 launching the Linux bridge inside WSL2.
- CMake `>= 3.30`, a C++26-capable compiler (`clang++` or `g++`), and Python `>= 3.11` (for configuration and test scripts; Python is not in the runtime hot/cold MCP path).
- On Linux: OpenSSL 3 Crypto development headers (`libssl-dev`). On macOS: system `CommonCrypto` (included with Xcode Command Line Tools).
- An installed, trusted `qxctl` binary supporting `qxctl commands manifest --json`.

## 2. Build and Verify `symphony-mcp`

From the repository root:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
ctest --test-dir build --output-on-failure
cmake --install build --prefix "$PWD"
```

This installs `./bin/symphony-mcp`.

## 3. Create the Pinned Mode-0600 Connection Profile (`connection.json`)

Never store `connection.json` inside a tracked git tree. Create it in a private user directory:

- **For Antigravity Plugin installation (`${PLUGIN_DATA}`)**:
  Place `connection.json` at `${PLUGIN_DATA}/connection.json` (or `~/.config/symphony/connection.json`).
- **Command**:

```bash
python3 scripts/configure_connection.py \
  --qxctl /absolute/path/to/qxctl \
  --working-directory /absolute/path/to/symphony-workdir \
  --output ~/.config/symphony/connection.json
```

To enable specific non-read commands (`permission_backed_mutation`, `proposal_only`, `evidence_only`), pass `--enable-nonread qxcmd:symphony:<id>` (repeatable) and re-run with `--force`.

## 4. Configure Antigravity & Antigravity CLI (`agy`)

### Option A: Direct MCP Stdio Mode (Default)

Generate the `mcpServers.symphony` configuration for Antigravity (`~/.gemini/config/mcp_config.json` or workspace `.agents/mcp_config.json`) or Antigravity CLI (`~/.gemini/antigravity-cli/settings.json`):

```bash
# Antigravity 2.0 / Antigravity IDE (user or workspace mcp_config.json)
python3 scripts/configure_clients.py \
  --client antigravity \
  --binary "$PWD/bin/symphony-mcp" \
  --config "$HOME/.config/symphony/connection.json" \
  --tool-catalog "$PWD/catalog/tools.json" \
  --output "$HOME/.gemini/config/mcp_config.json"

# Antigravity CLI (agy)
python3 scripts/configure_clients.py \
  --client antigravity-cli \
  --binary "$PWD/bin/symphony-mcp" \
  --config "$HOME/.config/symphony/connection.json" \
  --tool-catalog "$PWD/catalog/tools.json"
```

### Option B: Same-User Local Unix-Socket IPC Mode (`--listen` / `--connect-socket`)

When running multiple Antigravity IDE windows, Antigravity 2.0 agents, and `agy` CLI sessions against the same `connection.json`, you can run a single local Unix-socket IPC daemon in a private mode-`0700` directory and connect each client via `--connect-socket`:

```bash
# 1. Start the local IPC listener in a mode-0700 directory
python3 scripts/manage_ipc_daemon.py start \
  --binary "$PWD/bin/symphony-mcp" \
  --config "$HOME/.config/symphony/connection.json" \
  --tool-catalog "$PWD/catalog/tools.json" \
  --socket "$HOME/.config/symphony/ipc/symphony.sock"

# 2. Generate the Antigravity / agy relay config (--connect-socket)
python3 scripts/configure_clients.py \
  --client antigravity \
  --binary "$PWD/bin/symphony-mcp" \
  --connect-socket "$HOME/.config/symphony/ipc/symphony.sock"
```

## 5. Verify Connection

In Antigravity or `agy`, invoke `symphony_connection` (or run `python3 scripts/manage_ipc_daemon.py status --socket "$HOME/.config/symphony/ipc/symphony.sock"` for IPC mode) and confirm that `qxctl_sha256` and `registry_digest` match your `connection.json`.
