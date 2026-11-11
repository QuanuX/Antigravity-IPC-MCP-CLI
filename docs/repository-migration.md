# Migration Guide: `QuanuX/quanux-gemini-cli-mcp` to QuanuX Symphony

This repository updates [`QuanuX/quanux-gemini-cli-mcp`](https://github.com/QuanuX/quanux-gemini-cli-mcp) from the legacy Python/FastAPI/NATS `QuanuX/quanux` prototype to the production **[QuanuX Symphony](https://github.com/QuanuX/Symphony)** platform (`C++26` / `Go` / `Rust`) and expands first-class support to **Antigravity 2.0**, **Antigravity IDE**, and **Antigravity CLI (`agy`)**.

## Summary of Changes

| Dimension | Legacy `quanux-gemini-cli-mcp` (`v0.1` Python) | Updated Symphony Antigravity & Gemini CLI MCP (`C++26`) |
| :--- | :--- | :--- |
| **Target Platform** | Deprecated `QuanuX/quanux` Python/FastAPI/NATS repo | **[QuanuX Symphony](https://github.com/QuanuX/Symphony)** governed execution & sovereign operations platform |
| **Runtime Implementation** | Python scripts calling local HTTP/NATS endpoints | Native **C++26** binary (`symphony-mcp`) calling `qxctl` via direct `fork`/`execve` |
| **Transport Modes** | Stdio only | Direct **MCP `2025-11-25` stdio** + same-user **Unix-socket IPC** (`--listen` / `--connect-socket`) |
| **Tool Surface** | Legacy static tools (`start_quanux`, `install_extension`, etc.) | **698** operation-specific public tools ([`catalog/tools.json`](../catalog/tools.json)) + **6** live discovery tools |
| **Supported Hosts** | Gemini CLI (`gemini-extension.json`, `GEMINI.md`) | **Antigravity 2.0**, **Antigravity IDE**, **Antigravity CLI (`agy`)**, **Gemini CLI**, **Codex**, **Claude Code** |
| **Governance Model** | Unchecked execution | VGAA caller-class neutrality, mandatory same-session `preview` -> `apply` SHA-256 plan binding, and semantic failure propagation |
