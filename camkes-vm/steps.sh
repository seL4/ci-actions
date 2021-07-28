#!/bin/bash
#
# Copyright 2021, Proofcfraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for seL4 CAmkES VM test

set -e

echo "::group::Setting up"
export REPO_MANIFEST="master.xml"
export MANIFEST_URL="https://github.com/seL4/camkes-vm-examples-manifest.git"
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
