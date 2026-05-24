#!/usr/bin/env bash
# Create .venv and install the package (editable) with build/test tooling.

. "$(dirname "$0")/_common.sh"

cd "${REPO_ROOT}"

if [ ! -d "${VENV_PATH}" ]; then
    log "creating venv at ${VENV_PATH}"
    "${PYTHON}" -m venv "${VENV_PATH}"
fi

log "upgrading pip"
"${VENV_PIP}" install --upgrade pip >/dev/null

log "installing ${PACKAGE_NAME} (editable) + build/twine"
"${VENV_PIP}" install -e . build twine

log "done. activate with: source ${VENV_PATH}/bin/activate"
