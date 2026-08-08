#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
[ -x .venv/bin/python ] || { echo 'Project .venv is missing.' >&2; exit 1; }
[ -f uv.lock ] || { echo 'Reviewed uv.lock is required.' >&2; exit 1; }
[ -x tools/uv/uv ] || { echo 'Reviewed project-local uv is required.' >&2; exit 1; }
tools/uv/uv sync --frozen --extra dev --python .venv/bin/python
