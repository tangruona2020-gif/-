#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$PWD/data/playwright-browsers"
exec .venv/bin/python -m app.cli.scan --source the_chara
