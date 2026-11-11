# Connection Profile Specification (`symphony.agent.connection.v1`)

`symphony-mcp` loads an explicit connection profile JSON file via `--config <path>` (or `SYMPHONY_MCP_CONFIG` when launched through a plugin manifest without `--config`).

## Security Requirements

1. **Regular Mode-`0600` File:** The profile must be a regular file (not a symlink or FIFO) owned by the current effective UID with permissions `0600` (no group or world bits).
2. **Absolute `qxctl` Path:** `qxctl` must be an absolute path (`/...`), must not contain `..` traversal components, and must point to an executable regular file owned by either the current UID or `root` (`0`) without group/world write bits.
3. **Absolute `working_directory`:** Must be an absolute path without `..` segments pointing to an existing directory.
4. **No Secret Material in `environment`:** The profile `environment` object only accepts non-sensitive `QX_*`, `SYMPHONY_*`, and `SSL_CERT_*` variables. Any key containing `SECRET`, `TOKEN`, `PASSWORD`, `PRIVATE_KEY`, `API_KEY`, `ACCESS_KEY`, `CREDENTIAL`, `MNEMONIC`, `SEED`, `COOKIE`, `SESSION`, `BEARER`, or `AUTHORIZATION` is rejected at load time.

## Example Profile

```json
{
  "schema": "symphony.agent.connection.v1",
  "profile_name": "local-operator",
  "qxctl": "/usr/local/bin/qxctl",
  "working_directory": "/Users/operator",
  "config_path": "/Users/operator/.config/symphony/config.json",
  "timeout_ms": 15000,
  "max_output_bytes": 262144,
  "default_args": [],
  "environment": {
    "SYMPHONY_ENV": "local"
  }
}
```

## Generating a Profile Safely

Always use [`scripts/configure_connection.py`](../scripts/configure_connection.py) to create and validate the profile and its mode-`0700` parent directory:

```bash
python3 scripts/configure_connection.py \
  --output "$HOME/.config/symphony-mcp/connection.json" \
  --qxctl /usr/local/bin/qxctl \
  --working-directory "$HOME" \
  --profile-name local-operator
```
