# Unknown-Outcome Recovery and Reconciliation

## Why Unknown Outcomes Happen

When `symphony-mcp` dispatches a non-read operation (`permission_backed_mutation`, `proposal_only`, or `evidence_only`), any of the following conditions produces `transport_outcome: "unknown_requires_owner_reconciliation"` with `isError: true` and `retry_automatically: false`:

1. **Process Timeout (`timed_out: true`)**: The child process exceeded `timeout_ms` and received `SIGTERM` (followed by `SIGKILL` if uncooperative after the grace window). The owner may have partially or fully committed state before termination.
2. **Output Limit Exceeded (`output_limited: true`)**: Combined `stdout` + `stderr` reached `max_output_bytes`. Because output was truncated, `parsed_stdout` is omitted and completion cannot be verified from stdout alone.
3. **Non-Zero Exit Code (`exit_code != 0`)**: The owner exited non-zero (for example, exit code `5` with partial/failed evidence).

## Mandatory Recovery Procedure

1. **Stop Automatic Retries**:
   - Do **not** call `*_preview` or `*_apply` again immediately.
   - The previous `plan_id` has already been consumed.
2. **Inspect the Returned Evidence**:
   - Check `exit_code`, `timed_out`, `output_limited`, `stdout`, `stderr`, `parsed_stdout` (if present), and `recovery_command_id`.
3. **Run the Declared Recovery or Status Command**:
   - If `recovery_command_id` is read-only (e.g., `qxcmd:symphony:sqv.rithmic.runtime.status`, `qxcmd:symphony:snv.state.status`, `qxcmd:symphony:knowledge.lifecycle.apply-status`), execute its read tool first to observe the owner's durable journal or attempt state.
   - If `recovery_command_id` is itself a permission-backed recovery command (e.g., `qxcmd:symphony:sov.transport.profile.recover`, `qxcmd:symphony:sov.cloudflare.cf.installation.reconcile`, `qxcmd:symphony:stav.accordare.reconcile`), first run the corresponding read-only `status` or `inspect` command when available, then prepare and apply the recovery command with the exact `operation_id` and expected state digests required by the owner.
4. **Preserve Compare-and-Swap & Operation IDs**:
   - Many Symphony owners (`knowledge reconcile`, `knowledge lifecycle`, `sav named-version`, `ssiag`, `stav`, `snv`, `sov`) require reusing the original `--operation-id` or supplying the current journal/attempt digest for safe idempotent recovery. Never delete or hand-edit owner journal slots to force a retry.
