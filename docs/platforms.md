# Supported Platforms

`symphony-mcp` targets POSIX operating systems with native Unix-domain peer credential inspection and process-group control:

| Platform | Architectures | Peer-UID Verification | Status |
| :--- | :--- | :--- | :--- |
| **macOS** (14+) | `arm64`, `x86_64` | `getpeereid()` | Native POSIX support |
| **Ubuntu Linux** (22.04, 24.04, 26.04) | `x86_64`, `aarch64` (`arm64`) | `getsockopt(SO_PEERCRED)` | Native POSIX support |
| **Windows 11 via WSL2** (Ubuntu) | `x86_64`, `aarch64` | `getsockopt(SO_PEERCRED)` inside WSL2 | Supported via `wsl.exe` bridge |

Native Windows (`win32` outside WSL2) is intentionally unsupported so that POSIX `fork`/`execve`, `0600` file permission checks, and kernel peer-UID socket verification remain fail-closed.
