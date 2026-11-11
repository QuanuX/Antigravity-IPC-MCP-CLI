---
name: symphony-ipc
description: Configure, start, inspect, and stop the local same-user Unix-socket IPC daemon (--listen) and stdio-to-socket relay (--connect-socket) for symphony-mcp across Antigravity and Antigravity CLI (agy).
---

# Symphony Local Unix-Socket IPC (`--listen` / `--connect-socket`)

`symphony-mcp` supports two native transport modes implemented in C++26 (`src/transport.cpp` and `src/main.cpp`):

1. **Direct MCP Stdio (`--config`)**: The MCP host spawns `symphony-mcp --config /abs/connection.json [--tool-catalog /abs/catalog/tools.json]` directly over `stdin`/`stdout`.
2. **Same-User Local Unix-Socket IPC (`--listen` + `--connect-socket`)**:
   - A local listener process runs `symphony-mcp --config /abs/connection.json [--tool-catalog /abs/catalog/tools.json] --listen /abs/private-0700-dir/symphony.sock`.
   - Antigravity 2.0, Antigravity IDE, and Antigravity CLI (`agy`) spawn lightweight stdio relays: `symphony-mcp --connect-socket /abs/private-0700-dir/symphony.sock`.

## Security & Isolation Guarantees of Unix-Socket IPC

- **Mode `0700` Non-Symlink Parent Directory**: `listen_local_socket` verifies via `lstat` that the parent directory of the socket path is a real directory (not a symlink), owned by `getuid()`, with zero group/other permission bits (`(st_mode & 0077) == 0`).
- **Mode `0600` Socket Endpoint**: Created under `umask(0177)` without unlinking or clobbering any existing file, socket, or symlink.
- **Kernel Peer UID Authentication**: Every both `accept_local_socket` and `connect_local_socket` verify that the remote peer's effective UID matches `getuid()` using `getpeereid()` on macOS or `SO_PEERCRED` on Linux.
- **Session-Bound Preview Isolation**: Each accepted socket connection constructs a fresh `Bridge` instance with its own isolated preview table (`plans_`), 60-second idle poll timeout (`poll`), and 1 MiB line limit. Previews created by one client can never be consumed by another client.
- **Inode-Verified Socket Cleanup**: On `SIGINT`/`SIGTERM` or listener exit, `remove_local_socket` verifies `st_dev` and `st_ino` before unlinking so it never deletes a replacement file.

## Operating the IPC Daemon with `scripts/manage_ipc_daemon.py`

### Start the Daemon

```bash
python3 scripts/manage_ipc_daemon.py start \
  --binary /absolute/path/to/bin/symphony-mcp \
  --config /absolute/path/to/connection.json \
  --tool-catalog /absolute/path/to/catalog/tools.json \
  --socket /absolute/path/to/private-0700-dir/symphony.sock
```

### Check Daemon & Relay Health

```bash
python3 scripts/manage_ipc_daemon.py status \
  --binary /absolute/path/to/bin/symphony-mcp \
  --socket /absolute/path/to/private-0700-dir/symphony.sock \
  --probe
```

When `--probe` is supplied alongside `--binary`, `manage_ipc_daemon.py` connects through `symphony-mcp --connect-socket`, performs an MCP `2025-11-25` `initialize` + `symphony_connection` check, and returns the live connection metadata.

### Stop the Daemon

```bash
python3 scripts/manage_ipc_daemon.py stop \
  --socket /absolute/path/to/private-0700-dir/symphony.sock
```

### Configure Antigravity and `agy` to Use the IPC Socket

```bash
python3 scripts/configure_clients.py \
  --client antigravity \
  --binary /absolute/path/to/bin/symphony-mcp \
  --connect-socket /absolute/path/to/private-0700-dir/symphony.sock \
  --output ~/.gemini/config/mcp_config.json
```

Note: When using `--connect-socket`, `--tool-catalog` is configured on the `--listen` daemon, **not** on the `--connect-socket` relay.
