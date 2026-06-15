#!/bin/bash
#
# Copyright 2026, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# expects:
# - sel4bench-results repo to be checked out under sel4bench-results/ with push rights
# - json run results under results/
# - INPUT_MANIFEST_SHA to be set

# runs:
# - SHA extraction for kernel+sel4bench from sel4bench manifest repo
# - result extraction from json in results/
# - git commit/push to sel4bench-results repo

echo "::group::Setting up"
export ACTION_DIR="${SCRIPTS}/.."

# repo
BINDIR="${RUNNER_TEMP}/bin"
mkdir -p "${BINDIR}"
curl https://storage.googleapis.com/git-repo-downloads/repo > "${BINDIR}/repo"
chmod a+x "${BINDIR}/repo"

PATH="${BINDIR}":$PATH

# python env
sudo apt-get install -y --no-install-recommends libffi-dev
. ${SCRIPTS}/setup-python-venv.sh
pip3 install "junitparser==3.*" sel4-deps
export PYTHONPATH="${ACTION_DIR}/seL4-platforms"
echo "::endgroup::"

echo "::group::Reading manifest"
mkdir manifest
cd manifest
export MANIFEST_URL="https://github.com/seL4/sel4bench-manifest"
export REPO_MANIFEST="default.xml"
export REPO_BRANCH="${INPUT_MANIFEST_SHA}"
export REPO_NO_SYNC="1"
${SCRIPTS}/checkout-manifest.sh

MANIFEST=.repo/manifests/default.xml
manifest_revision() {
  xmllint --xpath "string(//project[@name='$1']/@revision)" "${MANIFEST}"
}

export INPUT_SEL4_SHA=$(manifest_revision seL4.git)
export INPUT_SEL4BENCH_SHA=$(manifest_revision seL4bench.git)
cd -
echo "::endgroup::"

# extract results and update sel4bench-results working copy
python3 "${ACTION_DIR}/${INPUT_ACTION_NAME}/build.py" --metrics

cd sel4bench-results
git add .
git commit -m "CI: add new benchmark results"
git push origin main
