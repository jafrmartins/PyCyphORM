#!/usr/bin/env bash
# Full release pipeline: bump -> clean -> install -> test -> build -> TestPyPI -> PyPI.
#
# Stops at the first failing step. Asks for explicit confirmation before any
# step that pushes to a remote (publish-test, publish), because those are
# externally observable / irreversible.
#
# Usage:
#   sys/Scripts/buildandpublish.sh             # interactive (asks before remote steps)
#   sys/Scripts/buildandpublish.sh --yes       # non-interactive, no prompts
#   sys/Scripts/buildandpublish.sh --local     # stop after local build (no push, no tag)
#   sys/Scripts/buildandpublish.sh --no-bump   # skip the versionbump step

. "$(dirname "$0")/_common.sh"

ASSUME_YES=0
LOCAL_ONLY=0
NO_BUMP=0
for arg in "$@"; do
    case "${arg}" in
        --yes|-y)    ASSUME_YES=1 ;;
        --local)     LOCAL_ONLY=1 ;;
        --no-bump)   NO_BUMP=1 ;;
        -h|--help)
            sed -n '2,13p' "$0"
            exit 0
            ;;
        *) die "unknown argument: ${arg}" ;;
    esac
done

confirm() {
    [ "${ASSUME_YES}" -eq 1 ] && return 0
    local prompt="$1"
    printf '\033[1;33m[confirm]\033[0m %s [y/N] ' "${prompt}"
    read -r answer
    [ "${answer}" = "y" ] || [ "${answer}" = "Y" ]
}

step() { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }

cd "${REPO_ROOT}"

step "1/7  versionbump (YY.M.D from today)"
if [ "${NO_BUMP}" -eq 1 ]; then
    log "--no-bump set, skipping"
else
    if ! git diff --quiet pyproject.toml sys/Scripts/.env; then
        die "pyproject.toml or sys/Scripts/.env have uncommitted changes — commit or revert first"
    fi
    "${SCRIPT_DIR}/versionbump.sh"
    if ! git diff --quiet pyproject.toml sys/Scripts/.env; then
        # versionbump changed files — reload PACKAGE_VERSION and auto-commit.
        set -a; . "${SCRIPT_DIR}/.env"; set +a
        log "committing version bump to ${PACKAGE_VERSION}"
        git add pyproject.toml sys/Scripts/.env
        git commit -m "bump: ${PACKAGE_VERSION}" >/dev/null
    fi
fi

step "2/7  clean"
"${SCRIPT_DIR}/clean.sh"

step "3/7  install (idempotent)"
"${SCRIPT_DIR}/install.sh"

step "4/7  test"
"${SCRIPT_DIR}/test.sh"

step "5/7  build + twine check"
"${SCRIPT_DIR}/build.sh"

if [ "${LOCAL_ONLY}" -eq 1 ]; then
    log "--local set, stopping after local build."
    exit 0
fi

step "6/7  publish to TestPyPI (push branch)"
confirm "push '${GIT_BRANCH}' to '${GIT_REMOTE}'? this triggers TestPyPI publish via CI." \
    || { log "aborted before publish-test"; exit 1; }
"${SCRIPT_DIR}/publish-test.sh"

step "7/7  publish to PyPI (tag + push)"
confirm "tag ${PACKAGE_VERSION} and push? this triggers PyPI publish via CI (needs manual approval in GitHub)." \
    || { log "aborted before publish. testpypi push already happened."; exit 1; }
"${SCRIPT_DIR}/publish.sh"

step "done"
log "TestPyPI: https://test.pypi.org/p/${PACKAGE_NAME}"
log "PyPI:     https://pypi.org/p/${PACKAGE_NAME}"
log "Approve the 'pypi' environment in the GitHub Actions run to complete the PyPI upload."
