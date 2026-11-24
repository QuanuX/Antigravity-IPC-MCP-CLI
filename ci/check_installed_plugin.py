#!/usr/bin/env python3
"""Read the installed Antigravity MCP configuration and verify the public surface."""
import json
from pathlib import Path
import subprocess
import sys


def check(plugin):
    config = json.loads((plugin / "mcp_config.json").read_text())["mcpServers"]["symphony"]
    receipt = json.loads((plugin / "release-profile.json").read_text())
    with subprocess.Popen([config["command"], *config["args"]], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, text=True) as server:
        seq = 0

        def request(method, params, notification=False):
            nonlocal seq
            message = {"jsonrpc": "2.0", "method": method, "params": params}
            if not notification:
                seq += 1
                message["id"] = seq
            server.stdin.write(json.dumps(message) + "\n")
            server.stdin.flush()
            if not notification:
                response = json.loads(server.stdout.readline())
                assert response["id"] == seq and "error" not in response, response
                return response["result"]

        try:
            result = request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                             "clientInfo": {"name": "antigravity-release-check", "version": "1"}})
            assert result["serverInfo"]["version"] == receipt["release"]
            request("notifications/initialized", {}, notification=True)
            expected = {x["tool"]["name"] for x in json.loads((plugin / "catalog/tools.json").read_text())["entries"]}
            expected.add("symphony_connection")
            names, cursor = set(), None
            while True:
                page = request("tools/list", {"cursor": cursor} if cursor else {})
                names.update(tool["name"] for tool in page["tools"])
                cursor = page.get("nextCursor")
                if not cursor:
                    break
            assert names == expected and len(names) == 744
            read = request("tools/call", {"name": "symphony_sov_remote_template", "arguments": {"operation": "target_configure"}})
            payload = read["structuredContent"]
            assert not read.get("isError") and payload["exit_code"] == 0
            assert payload["parsed_stdout"]["protocol"] == "symphony.sov.remote-template.v1"
            print(f"{receipt['profile']} verified {receipt['release']}, {len(names)} tools, and a native SOV template read.")
        finally:
            server.stdin.close()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


if __name__ == "__main__":
    check(Path(sys.argv[1]).resolve(strict=True))
