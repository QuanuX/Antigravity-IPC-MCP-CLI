#!/bin/sh
# Antigravity & Antigravity CLI (agy) native plugin launcher for symphony-mcp.
# Resolves the compiled native binary from bin/symphony-mcp, bin/<target>/symphony-mcp,
# or build/symphony-mcp, and forwards arguments without shell evaluation.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
PLUGIN_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)

SYSTEM=$(uname -s 2>/dev/null || printf unknown)
MACHINE=$(uname -m 2>/dev/null || printf unknown)

case "$SYSTEM:$MACHINE" in
  Darwin:x86_64) TARGET="darwin-x86_64" ;;
  Darwin:arm64) TARGET="darwin-arm64" ;;
  Linux:x86_64) TARGET="linux-x86_64" ;;
  Linux:aarch64|Linux:arm64) TARGET="linux-aarch64" ;;
  *)
    printf '%s\n' "symphony-mcp: unsupported platform $SYSTEM/$MACHINE; supported targets are darwin-x86_64, darwin-arm64, linux-x86_64, linux-aarch64" >&2
    exit 64
    ;;
esac

BINARY=""
for CANDIDATE in \
  "$PLUGIN_DIR/bin/symphony-mcp" \
  "$PLUGIN_DIR/bin/$TARGET/symphony-mcp" \
  "$PLUGIN_DIR/build/symphony-mcp"
do
  if [ -f "$CANDIDATE" ] && [ -x "$CANDIDATE" ]; then
    BINARY="$CANDIDATE"
    break
  fi
done

if [ -z "$BINARY" ]; then
  printf '%s\n' "symphony-mcp: native binary not found or not executable under $PLUGIN_DIR/bin/symphony-mcp; build with 'cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && cmake --install build --prefix \"\$PWD\"'" >&2
  exit 66
fi

exec "$BINARY" "$@"
