#!/usr/bin/env bash
# Remove build artifacts and caches. Does NOT delete .venv.

. "$(dirname "$0")/_common.sh"

cd "${REPO_ROOT}"

log "removing build artifacts"
rm -rf dist build
find . -type d -name '*.egg-info' -prune -exec rm -rf {} +
find . -type d -name '__pycache__' -prune -exec rm -rf {} +
find . -type f -name '*.pyc' -delete

log "clean"
