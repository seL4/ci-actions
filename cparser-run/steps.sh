#!/bin/bash
#
# Copyright 2021, Proofcfraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for seL4 cparser test

set -e

echo "::group::Setting up"
export REPO_MANIFEST="default.xml"
export MANIFEST_URL="https://github.com/seL4/sel4test-manifest.git"
checkout-manifest.sh

REPOS="$(pwd)"
SEL4_REPO="${REPOS}/seL4"

# currently this action only works for kernel PRs
cd kernel
fetch-branch.sh
cd ..
echo "::endgroup::"

# start test
python3 /builds/build.py
