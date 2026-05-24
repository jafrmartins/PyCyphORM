#!/usr/bin/env bash
# Set PACKAGE_VERSION to today's date in CalVer YY.M.D form (no zero padding,
# so it stays canonical under PEP 440 normalization). Updates both
# pyproject.toml and sys/Scripts/.env so publish.sh's drift check passes.
#
# Usage:
#   sys/Scripts/versionbump.sh              # use today's date
#   sys/Scripts/versionbump.sh 26.5.25      # explicit version

. "$(dirname "$0")/_common.sh"

if [ $# -gt 0 ]; then
    NEW_VERSION="$1"
else
    NEW_VERSION="$(date +'%-y.%-m.%-d')"
fi

[[ "${NEW_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] \
    || die "version '${NEW_VERSION}' is not YY.M.D"

CURRENT="$(grep -E '^version = ' "${REPO_ROOT}/pyproject.toml" | head -n1 | sed -E 's/.*"([^"]+)".*/\1/')"

if [ "${CURRENT}" = "${NEW_VERSION}" ]; then
    log "already at ${NEW_VERSION}, nothing to do"
    exit 0
fi

sed -i -E "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" "${REPO_ROOT}/pyproject.toml"
sed -i -E "s/^PACKAGE_VERSION=.*/PACKAGE_VERSION=${NEW_VERSION}/" "${SCRIPT_DIR}/.env"

log "bumped ${CURRENT} -> ${NEW_VERSION}"
log "  pyproject.toml"
log "  sys/Scripts/.env"
