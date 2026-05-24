#!/usr/bin/env bash
# Run the CRUD tests against the editable install.

. "$(dirname "$0")/_common.sh"
require_venv

cd "${REPO_ROOT}"

log "running tests/test_crud.py"
"${VENV_PY}" tests/test_crud.py
