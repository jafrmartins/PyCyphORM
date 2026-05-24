#!/usr/bin/env bash
# Build sdist + wheel into dist/ and validate with twine check.

. "$(dirname "$0")/_common.sh"
require_venv

cd "${REPO_ROOT}"

log "cleaning previous build artifacts"
rm -rf dist build
find . -type d -name '*.egg-info' -prune -exec rm -rf {} +

log "building sdist + wheel"
"${VENV_PY}" -m build

log "twine check"
"${VENV_PATH}/bin/twine" check dist/*

log "artifacts:"
ls -la dist/
