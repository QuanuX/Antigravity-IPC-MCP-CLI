# MCP Registry & `.mcpb` Packaging

This repository includes reproducible `.mcpb` bundle creation and MCP Registry [`server.json`](../server.json) metadata generation via [`scripts/package_mcpb.py`](../scripts/package_mcpb.py) and [`packaging/mcpb/manifest.json`](../packaging/mcpb/manifest.json).

## Building a Deterministic Multi-Architecture `.mcpb` Bundle

Provide all four native `symphony-mcp` binaries (`darwin-arm64`, `darwin-x86_64`, `linux-x86_64`, `linux-aarch64`) to [`scripts/package_mcpb.py`](../scripts/package_mcpb.py):

```bash
python3 scripts/package_mcpb.py \
  --source-root . \
  --binary darwin-arm64=/path/to/darwin-arm64/symphony-mcp \
  --binary darwin-x86_64=/path/to/darwin-x86_64/symphony-mcp \
  --binary linux-x86_64=/path/to/linux-x86_64/symphony-mcp \
  --binary linux-aarch64=/path/to/linux-aarch64/symphony-mcp \
  --output dist/symphony.mcpb \
  --release-url https://github.com/QuanuX/Antigravity-IPC-MCP-CLI/releases/download/v0.1.0-alpha.1/symphony.mcpb
```

[`scripts/package_mcpb.py`](../scripts/package_mcpb.py) verifies:
- Every binary header matches its declared ELF or Mach-O architecture.
- Only tracked git files are included (untracked files, symlinks, connection profiles, and private key markers are rejected).
- Deterministic ZIP timestamps and permissions (`0755` for executables, `0644` for regular files) produce an identical SHA-256 across runs.
