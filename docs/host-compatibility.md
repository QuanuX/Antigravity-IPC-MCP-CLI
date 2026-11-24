# Host Compatibility & Installation Guide

`symphony-mcp` supports **Antigravity 2.0**, **Antigravity IDE**, **Antigravity CLI (`agy`)**, **Gemini CLI**, **Codex**, **Claude Code**, and generic MCP `2025-11-25` stdio hosts in both **direct stdio mode** and **same-user Unix-socket IPC mode**.

---

## 1. Antigravity 2.0 & Antigravity IDE

Antigravity supports two installation paths for QuanuX Symphony:

For the beta.2.1 release, use the [public installer](https://quanux.org/downloads#antigravity). It writes the native plugin's absolute local command and argument paths to the installed plugin's own `mcp_config.json`. Antigravity loads the three skills, one rule and one MCP server from its standard plugin directories. Developer adapters and source builds are described below.

### A. Native Antigravity Plugin (`plugin.json` + `mcp_config.json`)

The root [`plugin.json`](../plugin.json) and [`mcp_config.json`](../mcp_config.json) register:
- **Always-on VGAA Rules:** [`rules/AGENTS.md`](../rules/AGENTS.md)
- **Skills:** [`skills/symphony-admin/`](../skills/symphony-admin/SKILL.md), [`skills/symphony-setup/`](../skills/symphony-setup/SKILL.md), [`skills/symphony-ipc/`](../skills/symphony-ipc/SKILL.md)
- **MCP Server (`symphony`):** Launched via [`packaging/antigravity/launcher.sh`](../packaging/antigravity/launcher.sh) using `${PLUGIN_DATA}/connection.json` and `${PLUGIN_ROOT}/catalog/tools.json`

To install as a local plugin inside `~/.gemini/config/plugins/symphony`:
1. Build and install `./bin/symphony-mcp`:
   ```bash
   cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
   cmake --build build -j 4
   cmake --install build --prefix "$PWD"
   ```
2. Place your mode-`0600` connection profile at `${PLUGIN_DATA}/connection.json` (or `~/.config/symphony-mcp/connection.json` and set `SYMPHONY_MCP_CONFIG` or update `mcp_config.json`).

### B. Direct Antigravity `mcp_config.json` Registration

Generate the `mcpServers.symphony` entry for `~/.gemini/antigravity/mcp_config.json`:

```bash
python3 scripts/configure_clients.py \
  --client antigravity \
  --binary /ABS/PATH/TO/bin/symphony-mcp \
  --config /ABS/PATH/TO/connection.json \
  --tool-catalog /ABS/PATH/TO/catalog/tools.json
```

See [`adapters/antigravity/mcp_config.json.example`](../adapters/antigravity/mcp_config.json.example) (direct stdio) and [`adapters/antigravity/mcp_config.ipc.json.example`](../adapters/antigravity/mcp_config.ipc.json.example) (`--connect-socket` IPC).

---

## 2. Antigravity CLI (`agy`) & Gemini CLI

Antigravity CLI (`agy`) and Gemini CLI read MCP server definitions from `~/.gemini/settings.json` (or workspace `.gemini/settings.json`) and load [`GEMINI.md`](../GEMINI.md) + [`gemini-extension.json`](../gemini-extension.json).

- **Import via `agy plugin import gemini`:** Point `agy` at this repository directory containing [`gemini-extension.json`](../gemini-extension.json) and [`GEMINI.md`](../GEMINI.md).
- **Generate `settings.json` snippet:**
  ```bash
  python3 scripts/configure_clients.py \
    --client antigravity-cli \
    --binary /ABS/PATH/TO/bin/symphony-mcp \
    --config /ABS/PATH/TO/connection.json \
    --tool-catalog /ABS/PATH/TO/catalog/tools.json
  ```

See [`adapters/antigravity-cli/settings.json.example`](../adapters/antigravity-cli/settings.json.example), [`adapters/antigravity-cli/settings.ipc.json.example`](../adapters/antigravity-cli/settings.ipc.json.example), and [`adapters/gemini-cli/settings.json.example`](../adapters/gemini-cli/settings.json.example).

---

## 3. Codex & Claude Code

- **Codex (`~/.codex/config.toml` or `.codex-plugin/plugin.json`):**
  ```bash
  python3 scripts/configure_clients.py \
    --client codex \
    --binary /ABS/PATH/TO/bin/symphony-mcp \
    --config /ABS/PATH/TO/connection.json \
    --tool-catalog /ABS/PATH/TO/catalog/tools.json
  ```
- **Claude Code (`.mcp.json` or `.claude-plugin/plugin.json`):**
  ```bash
  python3 scripts/configure_clients.py \
    --client claude \
    --binary /ABS/PATH/TO/bin/symphony-mcp \
    --config /ABS/PATH/TO/connection.json \
    --tool-catalog /ABS/PATH/TO/catalog/tools.json
  ```

---

## 4. Windows Hosts via WSL2

`symphony-mcp` uses POSIX `fork`/`execve`, process-group teardown, mode-`0600` file checks, and Unix-domain peer-credential verification. On Windows 11, compile and run `symphony-mcp` and `qxctl` inside **WSL2 Ubuntu** and invoke `wsl.exe` from the Windows host configuration. See [`adapters/generic/windows-wsl2.json.example`](../adapters/generic/windows-wsl2.json.example) and [`adapters/codex/windows-wsl2.toml.example`](../adapters/codex/windows-wsl2.toml.example).
