# Administration and Mutability Classes

## Mutability Classes

Every routable `qxctl` command has an explicit `mutability` in `symphony.qxctl.command-registry.v1`:

- `read_only`:
  - Dispatched via `symphony_<route>` (public catalogue mode) or `symphony_read` (live discovery mode).
  - Does not require listing in `enabled_nonread_commands`.
- `permission_backed_mutation`:
  - Mutates protected local or target-host state under target-host permission, SSIAG authorization, and expected-state digests.
  - Must be listed in `enabled_nonread_commands` in the operator's `connection.json`.
  - Requires `symphony_<route>_preview` + `symphony_<route>_apply` (or `symphony_prepare` + `symphony_apply`).
- `proposal_only`:
  - Writes or evaluates unratified proposal artifacts or non-executing plans.
  - Treated as non-read by the bridge; requires `enabled_nonread_commands` and preview before apply.
- `evidence_only`:
  - Executes fresh verification or normalization that produces audit/reconciliation evidence.
  - Treated as non-read by the bridge; requires `enabled_nonread_commands` and preview before apply.
- `prohibited`:
  - Never exposed or dispatched (`qxcmd:symphony:stav.append`).

## What Transport Preview Does and Does Not Do

- **What it does**:
  - Validates the command contract and argument types against the observed registry.
  - Checks that the `command_id` is enabled in `enabled_nonread_commands`.
  - Verifies the pinned `qxctl` binary SHA-256 digest before creating the plan.
  - Computes SHA-256 digests (`direct_file_sha256`) for any existing regular file directly named by a `--flag=value` argument (up to 64 MiB).
  - Stores a single-use, session-bound `plan_id` valid for 300 seconds (up to 128 active previews per session).
- **What it does NOT do**:
  - It does **not** run `qxctl` or any native owner dry-run (`owner_plan_executed: false`).
  - It does **not** grant SSIAG or target-host permission (`authorization_granted: false`).
  - It does **not** inspect nested file references inside JSON payloads or positional arguments.

## Apply Consumption Rules

- Calling `symphony_<route>_apply` (or `symphony_apply`) **consumes the `plan_id` immediately before any check or process execution**.
- If a direct input file changed after preview, if the plan expired, or if `qxctl` binary verification fails, the plan is consumed and rejected without executing `qxctl`. Prepare a fresh preview after resolving the issue.
- A preview created in one MCP session cannot be applied in another MCP session, even over the same local Unix socket IPC daemon.
