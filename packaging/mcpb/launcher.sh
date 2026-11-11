#!/bin/sh
set -eu

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
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

BINARY="$DIR/bin/$TARGET/symphony-mcp"
if [ ! -f "$BINARY" ] || [ ! -x "$BINARY" ]; then
  printf '%s\n' "symphony-mcp: bundled binary is missing or not executable: $BINARY" >&2
  exit 66
fi

exec "$BINARY" "$@"
