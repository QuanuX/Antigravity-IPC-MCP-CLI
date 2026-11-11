# Public Operation-Specific MCP Tools (`catalog/tools.json`)

When started with `--tool-catalog catalog/tools.json` (or `SYMPHONY_MCP_CATALOG`), `symphony-mcp` exposes **698** individually typed, annotated MCP tools derived from QuanuX Symphony's authoritative `tools/qxctl/COMMANDS.json` registry (`sha256:95c5c64d9aac9a341ecb74a333f4abcdf3641719f2475b2560077f84424d9ad0`) and enriched with Cobra flag descriptions from `tools/qxctl/cmd/qxctl/*.go`.

## Catalogue Breakdown

| Category | Count | Description |
| :--- | ---: | :--- |
| `symphony_connection` | 1 | Read-only probe of the local connection profile, `qxctl` binary executable status, and command registry digest |
| Read-only operation tools (`*_read`) | 289 | One read-only tool per `read_only: true` routable `qxctl` command (`readOnlyHint: true`, `destructiveHint: false`) |
| Preview operation tools (`*_preview`) | 204 | Same-session non-executing preview tool for each mutating/administrative `qxctl` command (`readOnlyHint: true`, `destructiveHint: false`) |
| Apply operation tools (`*_apply`) | 204 | Governed execution tool requiring `plan_id`, `plan_sha256`, `reason`, and exact `confirm_command_id` (`readOnlyHint: false`, `destructiveHint: true`) |
| **Total MCP Tools** | **698** | Paginated at 50 tools per `tools/list` page via `nextCursor` |

## Excluded Unroutable Commands

Two commands in `tools/qxctl/COMMANDS.json` have an empty `cli_path` (`[]`) and cannot be routed via `qxctl` argv:
- `qxcmd:symphony:sov.target.invoke` (`unroutable_without_cli_path`)
- `qxcmd:symphony:stav.append` (`unroutable_without_cli_path`)

Both are recorded explicitly in `excluded_commands` inside [`catalog/tools.json`](../catalog/tools.json).

## Rebuilding the Catalogue from a Symphony Checkout

```bash
python3 scripts/build_tool_catalog.py \
  --expected-registry /path/to/Symphony/tools/qxctl/COMMANDS.json \
  --symphony-source /path/to/Symphony \
  --output catalog/tools.json
```
