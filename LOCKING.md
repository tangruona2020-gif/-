# Dependency locking policy

## Current audit state

`pyproject.toml` is the authoritative declaration. All runtime, development,
and build dependencies selected directly by this project use exact `==`
versions. `requirements.direct.lock` is a human-reviewable mirror.

A transitive `uv.lock` was generated on 2026-08-07 with project-local
`uv 0.11.32` and CPython 3.12.10. `uv lock --check` passed. The lock contains
54 packages and 198 SHA-256 artifact hashes. Static source review found only
the registry `https://pypi.org/simple` plus the local editable project (`.`),
with no Git, GitHub, GitLab, or arbitrary direct-URL dependencies.

The lock is generated and auditable, but dependency installation remains
unapproved until the user explicitly approves the reviewed lock.

## Lock regeneration procedure (requires explicit approval)

Run from the repository root, using a reviewed local `uv.exe`; do not pipe a
remote script into a shell and do not install uv globally:

```powershell
& ".\tools\uv\uv.exe" lock --python ".\.venv\Scripts\python.exe"
& ".\tools\uv\uv.exe" lock --check
```

Review the resulting `uv.lock` for:

1. package names and exact versions;
2. registry source (`https://pypi.org/simple` only unless explicitly approved);
3. wheels compatible with CPython 3.12 and the target OS;
4. SHA-256 hashes for downloaded artifacts;
5. unexpected optional dependencies or editable/path sources;
6. absence of Git URLs, direct executable downloads and remote scripts.

Only after that review may installation be performed, and only into
`goods-popup-monitor/.venv`:

```powershell
& ".\tools\uv\uv.exe" sync --frozen --extra dev --python ".\.venv\Scripts\python.exe"
```

`--frozen` is mandatory: installation must fail instead of silently changing
the lock. Administrator rights, global installs, PATH changes and writes to
other projects are prohibited.

## Pip fallback

Pip is not the preferred locker. If uv is unavailable, generate a hash-locked
requirements file in a separately approved resolution step, review it, then
install with both `--require-virtualenv` and `--require-hashes`. Never treat
`requirements.direct.lock` as a complete transitive lock.
