#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
[ -x .venv/bin/python ] || python3.12 -m venv .venv
mkdir -p data/images data/logs data/tmp
[ -f .env ] || cp .env.example .env
printf '%s\n' 'Local environment prepared. No dependencies or browsers were installed.'
printf '%s\n' 'Review DEPENDENCIES.md, LOCKING.md and uv.lock before any installation.'
