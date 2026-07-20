# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the MCP Godot Agent, please
**do not** open a public issue.

Instead, email the maintainer directly. You should receive a response
within 48 hours. Please include:

- A description of the vulnerability
- Steps to reproduce
- Affected versions
- Any potential mitigations you've identified

## Scope

Security concerns include but are not limited to:

- Unauthorized file system access outside the project directory
- Exposure of API keys or credentials
- Network binds on `0.0.0.0` instead of `127.0.0.1`
- Remote code execution via crafted inputs
- Path traversal attacks

## Supported Versions

| Version | Supported |
|---|---|
| latest `main` | ✅ |
| older | ❌ |

## Design Decisions

This project has specific security constraints by design:

- All network services bind exclusively on `127.0.0.1` (loopback)
- Subprocess execution uses `stdin=DEVNULL` via `run_subprocess_safe()`
- Path traversal is checked by `_check_path_traversal()` before any file operation
- API keys are never stored in versioned files — use environment variables

If you find a bypass for any of these, it is a valid vulnerability report.
