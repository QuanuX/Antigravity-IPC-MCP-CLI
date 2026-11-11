# Antigravity & Antigravity CLI (`agy`) Acceptance Guide

This document defines the acceptance checklist for verifying QuanuX Symphony inside **Antigravity 2.0**, **Antigravity IDE**, **Antigravity CLI (`agy`)**, and **Gemini CLI**.

## 1. Self-Contained Reviewer Sandbox Smoke Test

Run [`scripts/prepare_reviewer_setup.py`](../scripts/prepare_reviewer_setup.py) to create a local mode-`0700` reviewer environment with a fake `qxctl` fixture, a mode-`0600` connection profile, and ready-to-use configs for Antigravity, `agy`, Gemini CLI, Codex, and Claude Code:

```bash
python3 scripts/prepare_reviewer_setup.py \
  --output-dir /tmp/symphony-reviewer \
  --binary "$PWD/bin/symphony-mcp"
```

Expected JSON output:
- `"smoke_test": "passed"`
- `"public_tool_count": 698`
- Generated client configurations in `/tmp/symphony-reviewer/`:
  - `antigravity_mcp_config.json`
  - `antigravity_cli_settings.json`
  - `gemini_cli_settings.json`
  - `codex_config.toml`
  - `claude_mcp.json`

## 2. Native Antigravity Customizations Verification

Verify the Antigravity customization files in the repository root:
1. [`plugin.json`](../plugin.json): Declares `name: "symphony"`, `displayName: "QuanuX Symphony"`, `rules: "./rules/AGENTS.md"`, `skills: "./skills/"`, and `mcpServers: "./mcp_config.json"`.
2. [`mcp_config.json`](../mcp_config.json): Launches `${PLUGIN_ROOT}/packaging/antigravity/launcher.sh` with `--config ${PLUGIN_DATA}/connection.json --tool-catalog ${PLUGIN_ROOT}/catalog/tools.json`.
3. [`rules/AGENTS.md`](../rules/AGENTS.md) and [`GEMINI.md`](../GEMINI.md): Enforce QuanuX Symphony's VGAA invariants (caller-class neutrality, hot-path isolation, process exit `0` != semantic success, transport preview != owner dry-run, and mandatory reconciliation of unknown non-read outcomes).
4. [`skills/symphony-admin/SKILL.md`](../skills/symphony-admin/SKILL.md), [`skills/symphony-setup/SKILL.md`](../skills/symphony-setup/SKILL.md), and [`skills/symphony-ipc/SKILL.md`](../skills/symphony-ipc/SKILL.md): Provide specialized administrative, onboarding, and Unix-socket IPC workflows.

## 3. Unix-Socket IPC Acceptance Verification

Verify multi-session IPC relay over a mode-`0600` Unix-domain socket:

```bash
python3 scripts/manage_ipc_daemon.py start \
  --binary "$PWD/bin/symphony-mcp" \
  --config /tmp/symphony-reviewer/config/connection.json \
  --socket /tmp/symphony-reviewer/run/symphony-mcp.sock \
  --tool-catalog "$PWD/catalog/tools.json"

python3 scripts/manage_ipc_daemon.py status \
  --socket /tmp/symphony-reviewer/run/symphony-mcp.sock \
  --binary "$PWD/bin/symphony-mcp" \
  --probe

python3 scripts/manage_ipc_daemon.py stop \
  --socket /tmp/symphony-reviewer/run/symphony-mcp.sock
```
