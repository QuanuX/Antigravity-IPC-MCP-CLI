# Connection and Discovery

## Connection Summary (`symphony_connection`)

Call `symphony_connection` at the beginning of a session. It returns:

- `qxctl_sha256`: SHA-256 digest of the pinned `qxctl` binary.
- `registry_digest`: SHA-256 digest of the observed `symphony.qxctl.command-registry.v1` manifest.
- `registered_commands`: Total commands in the observed manifest (495 in current Symphony).
- `routable_commands`: Public, non-interactive, non-retired commands routable through the bridge (493 in current Symphony).
- `unsupported_commands`: Non-routable commands and their exact exclusion reason (`qxcmd:symphony:sov.target.invoke` requires stdin payload; `qxcmd:symphony:stav.append` is hidden/prohibited).
- `enabled_nonread_commands`: Exact `command_id` list enabled for preview/apply in the operator's `connection.json`.
- `service_health`: Always `"not_probed"`. Startup verifies executable and registry digests only; live authority/service checks require explicit `doctor` or `status` commands.

## Public Operation-Specific Catalogue Mode (`--tool-catalog`)

When `symphony-mcp` is started with `--tool-catalog catalog/tools.json` (the default for Antigravity, Antigravity IDE, and Antigravity CLI `agy`):

- `tools/list` exposes `symphony_connection` plus **697** operation-specific tools (698 total), paginated 50 tools per page via `nextCursor`.
- Read-only commands (`mutability: "read_only"`) map to `symphony_<route>` (289 tools).
- Non-read commands (`permission_backed_mutation`, `proposal_only`, `evidence_only`) map to `symphony_<route>_preview` and `symphony_<route>_apply` (204 pairs = 408 tools).
- Positional arguments `<name>` are passed as required string properties `arg_<name_with_underscores>`.
- Repeated flags `[--flag VALUE...]` require a JSON array of strings; scalar flags require a string; boolean switch flags require a JSON boolean.
- `--json` is requested automatically whenever the command contract supports `json_output: true`.

## Live Registry Discovery Mode (without `--tool-catalog`)

When `symphony-mcp` runs without `--tool-catalog`, it exposes 6 tools (`symphony_connection`, `symphony_discover`, `symphony_describe`, `symphony_read`, `symphony_prepare`, `symphony_apply`):

1. `symphony_discover`: Filter by substring `query` (matches `command_id` or `grammar`), `mutability`, `offset`, and `limit` (1..100).
2. `symphony_describe`: Inspect the exact `registry_record`, `flags`, `positionals`, and `enabled` state for one `command_id`.
3. Construct `flags` and `positionals` strictly from the described grammar.
