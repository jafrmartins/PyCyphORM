#!/usr/bin/env bash
# Sourced by every script in this directory. Resolves the repo root and loads .env.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

set -a
. "${SCRIPT_DIR}/.env"
set +a

VENV_PATH="${REPO_ROOT}/${VENV_DIR}"
VENV_PY="${VENV_PATH}/bin/python"
VENV_PIP="${VENV_PATH}/bin/pip"

log() { printf '\033[1;34m[%s]\033[0m %s\n' "${PACKAGE_NAME}" "$*"; }
die() { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

require_venv() {
    [ -x "${VENV_PY}" ] || die "venv not found at ${VENV_PATH}. Run sys/Scripts/install.sh first."
}
