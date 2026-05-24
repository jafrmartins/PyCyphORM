#!/usr/bin/env bash
# Tag PACKAGE_VERSION and push the tag to GitHub. CI then publishes to PyPI
# (after manual approval on the 'pypi' environment) and creates a signed GitHub Release.

. "$(dirname "$0")/_common.sh"

cd "${REPO_ROOT}"

git remote get-url "${GIT_REMOTE}" >/dev/null 2>&1 \
    || die "git remote '${GIT_REMOTE}' not configured. Add it with: git remote add ${GIT_REMOTE} <url>"

if ! git diff --quiet || ! git diff --cached --quiet; then
    die "working tree has uncommitted changes. commit them first."
fi

PYPROJECT_VERSION="$(grep -E '^version' "${REPO_ROOT}/pyproject.toml" | head -n1 | sed -E 's/.*"([^"]+)".*/\1/')"
[ "${PYPROJECT_VERSION}" = "${PACKAGE_VERSION}" ] \
    || die "version mismatch: .env=${PACKAGE_VERSION} pyproject.toml=${PYPROJECT_VERSION}. update both first."

if git rev-parse "${PACKAGE_VERSION}" >/dev/null 2>&1; then
    die "tag ${PACKAGE_VERSION} already exists locally. bump PACKAGE_VERSION first."
fi

log "tagging ${PACKAGE_VERSION}"
git tag "${PACKAGE_VERSION}"

log "pushing tag to ${GIT_REMOTE}"
git push "${GIT_REMOTE}" "${PACKAGE_VERSION}"

log "CI will pause for manual approval on the 'pypi' environment."
log "approve from the Actions run page: https://github.com/$(git remote get-url ${GIT_REMOTE} | sed -E 's#.*[:/]([^/:]+/[^/:]+)\.git#\1#')/actions"
