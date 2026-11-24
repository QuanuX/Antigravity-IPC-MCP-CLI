# Public Operation-Specific MCP Tools (`catalog/tools.json`)

The beta.2.1 profile package supplies 744 individually typed MCP tools. Each operating-system cohort has its own catalog digest and observed qxctl registry. The checked-in example is the Ubuntu 26.04 AMD64 catalog; prebuilt packages contain their cohort's exact catalog. The release pins are in [release-targets.json](../packaging/release-targets.json).

## Catalogue Breakdown

| Category | Count | Description |
| :--- | ---: | :--- |
| `symphony_connection` | 1 | Read-only probe of the local connection profile, `qxctl` binary executable status, and command registry digest |
| Read-only operation tools (`*_read`) | 303 | One read-only tool per `read_only: true` routable `qxctl` command (`readOnlyHint: true`, `destructiveHint: false`) |
| Preview operation tools (`*_preview`) | 220 | Same-session non-executing preview tool for each mutating/administrative `qxctl` command (`readOnlyHint: true`, `destructiveHint: false`) |
| Apply operation tools (`*_apply`) | 220 | Governed execution tool requiring the matching unconsumed `plan_id` (`readOnlyHint: false`, `destructiveHint: true`) |
| **Total MCP Tools** | **744** | Paginated at 50 tools per `tools/list` page via `nextCursor` |

## Excluded Unroutable Commands

The signed release catalog excludes two qxctl routes from the bridge interface:
- `qxcmd:symphony:sov.target.invoke` (`not_supported_by_bridge`)
- `qxcmd:symphony:stav.append` (`not_supported_by_bridge`)

Both are recorded explicitly in `excluded_commands` inside [`catalog/tools.json`](../catalog/tools.json).

## Rebuilding the Catalogue from a Symphony Checkout

```bash
python3 scripts/build_tool_catalog.py \
  --expected-registry /path/to/Symphony/tools/qxctl/COMMANDS.json \
  --symphony-source /path/to/Symphony \
  --output catalog/tools.json
```
