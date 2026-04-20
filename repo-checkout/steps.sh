#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

echo "::group::Setting up"

BINDIR="${RUNNER_TEMP}/bin"
mkdir -p "${BINDIR}"
curl https://storage.googleapis.com/git-repo-downloads/repo > "${BINDIR}/repo"
chmod a+x "${BINDIR}/repo"

PATH="${BINDIR}":$PATH

pip3 install -U PyGithub

echo "::endgroup::"

echo "::group::Repo checkout"

if echo "$INPUT_MANIFEST_REPO" | grep -q "/" 2>/dev/null; then
  export MANIFEST_URL="https://github.com/${INPUT_MANIFEST_REPO}"
else
  export MANIFEST_URL="https://github.com/seL4/${INPUT_MANIFEST_REPO}"
fi
export REPO_MANIFEST="${INPUT_MANIFEST}"
export REPO_BRANCH="${INPUT_MANIFEST_BRANCH}"
checkout-manifest.sh

fetch-branches.sh

echo "::endgroup::"

XML="$(repo manifest -r --suppress-upstream-revision | nl-escape.sh)"

if [ -z "${GITHUB_OUTPUT}" ]; then
  echo "Warning: GITHUB_OUTPUT not set"
  GITHUB_OUTPUT="github.output"
fi
echo "xml=${XML}" >> ${GITHUB_OUTPUT}
