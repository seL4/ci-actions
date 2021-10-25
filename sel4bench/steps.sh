#!/bin/bash
#
# Copyright 2021, Proofcfraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for sel4bench builds

set -e

echo "::group::Setting up"
export REPO_MANIFEST="master.xml"
export MANIFEST_URL="https://github.com/seL4/sel4bench-manifest.git"
checkout-manifest.sh

fetch-branches.sh
echo "::endgroup::"

# start test
python3 /builds/build.py
