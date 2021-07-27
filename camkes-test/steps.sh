#!/bin/bash
#
# Copyright 2021, Proofcfraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for seL4 CAmkES test

set -e

# It's a bit overkill to pull a huge docker container for just dumping the build
# matrix, but it's not really worth setting up a separate action for it, either.
if [ -n "${INPUT_MATRIX}" ]
then
  python3 /builds/build.py --matrix
  exit 0
fi

echo "::group::Setting up"
export REPO_MANIFEST="master.xml"
export MANIFEST_URL="https://github.com/seL4/camkes-manifest.git"
checkout-manifest.sh

cd $(repo-util path ${GITHUB_REPOSITORY})
fetch-branch.sh
cd - >/dev/null

repo-util hashes
echo "::endgroup::"

# GitHub sets its own home dir, but we want the caches set up in /root
export HOME=/root
. /root/.bashrc

# start test
python3 /builds/build.py
