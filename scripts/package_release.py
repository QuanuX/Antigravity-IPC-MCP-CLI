#!/usr/bin/env python3
"""Create a reproducible source-and-skill archive excluding local build/profile artifacts."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

INCLUDED_FILES = (
    "CMakeLists.txt",
    "LICENSE",
    "README.md",
    "GEMINI.md",
    "plugin.json",
    "mcp_config.json",
    "mcp.json",
    ".mcp.json",
    "gemini-extension.json",
    "server.json",
    ".gitignore",
    ".gitattributes",
)
INCLUDED_DIRS = (
    ".agents",
    ".claude-plugin",
    ".codex-plugin",
    "adapters",
    "assets",
    "catalog",
    "ci",
    "docs",
    "include",
    "packaging",
    "rules",
    "scripts",
    "skills",
    "src",
    "tests",
    "third_party",
)
EXCLUDED_NAMES = {"__pycache__", ".DS_Store", "connection.json"}


def iter_release_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in INCLUDED_FILES:
        candidate = root / name
        if candidate.is_symlink():
            raise RuntimeError(f"Release file must not be a symlink: {candidate}")
        if candidate.is_file():
            files.append(candidate)
    for folder in INCLUDED_DIRS:
        base = root / folder
        if not base.exists():
            continue
        if base.is_symlink():
            raise RuntimeError(f"Release directory must not be a symlink: {base}")
        for path in sorted(base.rglob("*")):
            if any(part in EXCLUDED_NAMES for part in path.parts) or path.suffix == ".pyc":
                continue
            if path.is_symlink():
                raise RuntimeError(f"Release archive must not contain symlinks: {path}")
            if path.is_file():
                files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--output", required=True, type=Path, help="Output .tar.gz path")
    args = parser.parse_args()

    source = args.source.resolve(strict=True)
    output = args.output.expanduser().resolve()
    if output.is_relative_to(source) and output.parent != source / "dist":
        raise SystemExit("Write release archives to dist/ or outside the source tree")
    output.parent.mkdir(parents=True, exist_ok=True)

    files = iter_release_files(source)
    manifest: dict[str, str] = {}
    raw_tar = io.BytesIO()
    with tarfile.open(fileobj=raw_tar, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in files:
            rel = path.relative_to(source).as_posix()
            data = path.read_bytes()
            manifest[rel] = "sha256:" + hashlib.sha256(data).hexdigest()
            info = tarfile.TarInfo(name=f"symphony-agent-plugin/{rel}")
            info.size = len(data)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = "root"
            info.gname = "root"
            info.mode = 0o755 if path.suffix in {".py", ".sh"} else 0o644
            archive.addfile(info, io.BytesIO(data))

    with output.open("wb") as raw_out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_out, mtime=0) as gz:
            gz.write(raw_tar.getvalue())

    archive_digest = "sha256:" + hashlib.sha256(output.read_bytes()).hexdigest()
    receipt = {
        "schema": "symphony.agent.release-package.v1",
        "archive": output.name,
        "archive_sha256": archive_digest,
        "file_count": len(manifest),
        "files": manifest,
    }
    receipt_path = output.with_suffix(".manifest.json")
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"archive": str(output), "archive_sha256": archive_digest, "manifest": str(receipt_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
