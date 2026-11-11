# Codex & Cross-Host Acceptance Guide

In addition to native Antigravity and Antigravity CLI (`agy`) manifests, this repository maintains full parity with [`QuanuX/symphony-codex-ipc-mcp-and-skills`](https://github.com/QuanuX/symphony-codex-ipc-mcp-and-skills) for Codex, Claude Code, and generic MCP `2025-11-25` stdio clients.

## Manifests Included

- **Antigravity & `agy`:** [`plugin.json`](../plugin.json), [`mcp_config.json`](../mcp_config.json), [`rules/AGENTS.md`](../rules/AGENTS.md)
- **Gemini CLI / `agy plugin import gemini`:** [`gemini-extension.json`](../gemini-extension.json), [`GEMINI.md`](../GEMINI.md)
- **Codex:** [`.codex-plugin/plugin.json`](../.codex-plugin/plugin.json), [`.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json), [`adapters/codex/config.toml.example`](../adapters/codex/config.toml.example)
- **Claude Code:** [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json), [`mcp.json`](../mcp.json), [`.mcp.json`](../.mcp.json)
- **MCP Bundle (`.mcpb`):** [`packaging/mcpb/manifest.json`](../packaging/mcpb/manifest.json), [`server.json`](../server.json)
