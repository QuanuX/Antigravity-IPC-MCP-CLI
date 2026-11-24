# Verification & Platform Qualification Suite

## Running the CTest Suite

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
ctest --test-dir build --output-on-failure
```

## Named CTest Suites

| CTest Suite | Source | Coverage |
| :--- | :--- | :--- |
| `transport` | [`tests/transport_test.cpp`](../tests/transport_test.cpp) | Direct `fork`/`execve`, environment validation, process-group timeout cleanup, output bounds, mode-`0600` Unix socket creation, peer-UID verification, and inode-verified unlink |
| `bounded-hashing` | [`tests/hash_test.cpp`](../tests/hash_test.cpp) | NIST SHA-256 vectors and bounded file digest enforcement |
| `mcp-integration` | [`tests/test_mcp.py`](../tests/test_mcp.py) | MCP `2025-11-25` handshake, 6-tool live registry mode, same-session `prepare`/`apply` plan binding, semantic failure detection, unknown outcome reconciliation, and `--listen`/`--connect-socket` IPC relay |
| `public-operation-tools` | [`tests/test_public_tools.py`](../tests/test_public_tools.py) | 743 operation tools in [`catalog/tools.json`](../catalog/tools.json) covering 523 routable commands, 50-per-page pagination across 744 tools, read dispatch, preview/apply dispatch, and cross-tool plan rejection |
| `client-adapters` | [`tests/test_adapters.py`](../tests/test_adapters.py) | Antigravity, `agy`, Gemini CLI, Codex, and Claude Code manifest validation, `configure_connection.py`, `configure_clients.py` (stdio + IPC), `manage_ipc_daemon.py`, `prepare_reviewer_setup.py`, and `package_release.py` |
| `qualification-report` | [`tests/test_qualification.py`](../tests/test_qualification.py) | [`ci/qualify_local.py`](../ci/qualify_local.py) JUnit report validation, ELF architecture inspection, and source SHA-256 inventory |
| `mcpb-packaging` | [`tests/test_mcpb.py`](../tests/test_mcpb.py) | [`packaging/mcpb/launcher.sh`](../packaging/mcpb/launcher.sh) routing and [`scripts/package_mcpb.py`](../scripts/package_mcpb.py) deterministic archive verification |

## Native Host Qualification (`ci/qualify_local.py`)

To generate an auditable `RESULTS.json` and `source-sha256.json` qualification bundle on a native macOS or Ubuntu runner:

```bash
python3 ci/qualify_local.py \
  --source . \
  --out /tmp/symphony-qualify \
  --compiler /usr/bin/clang++ \
  --expected-os macos \
  --expected-arch x86_64 \
  --macos-deployment-target 15.0 \
  --host-kind physical
```
