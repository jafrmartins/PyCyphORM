#!/usr/bin/env bash
# Push current branch to GitHub. CI then builds and uploads to TestPyPI.

. "$(dirname "$0")/_common.sh"

cd "${REPO_ROOT}"

git remote get-url "${GIT_REMOTE}" >/dev/null 2>&1 \
    || die "git remote '${GIT_REMOTE}' not configured. Add it with: git remote add ${GIT_REMOTE} <url>"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[ "${CURRENT_BRANCH}" = "${GIT_BRANCH}" ] \
    || die "current branch is '${CURRENT_BRANCH}', expected '${GIT_BRANCH}'"

if ! git diff --quiet || ! git diff --cached --quiet; then
    die "working tree has uncommitted changes. commit or stash them first."
fi

log "pushing ${CURRENT_BRANCH} to ${GIT_REMOTE}"
git push "${GIT_REMOTE}" "${CURRENT_BRANCH}"

log "watch the run: gh run watch  (or open the Actions tab)"
log "after success, verify with:"
log "  pip install --index-url ${TESTPYPI_INDEX} --extra-index-url ${PYPI_INDEX} ${PACKAGE_NAME}"
