# Directory & Marketplace Submission Guide

This repository is structured for submission and installation across:
1. **Google Antigravity Plugin System (`plugin.json` + `mcp_config.json`)**
2. **Antigravity CLI (`agy`) & Gemini CLI Extensions (`gemini-extension.json` + `GEMINI.md`)**
3. **OpenAI Codex Marketplace (`.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json`)**
4. **Anthropic Claude Code & MCP Bundle Registry (`.claude-plugin/plugin.json` + `packaging/mcpb/manifest.json` + `server.json`)**

## Reviewer Quick-Check

Reviewers without a live QuanuX Symphony deployment can verify all 698 MCP tools, preview/apply governance, and client configurations using the self-contained fixture setup:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
python3 scripts/prepare_reviewer_setup.py \
  --output-dir /tmp/symphony-reviewer \
  --binary "$PWD/build/symphony-mcp"
```
