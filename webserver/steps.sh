#!/bin/bash
#
# Copyright 2022, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for seL4 web server demo app test

set -e

echo "::group::Setting up"
export REPO_MANIFEST="master.xml"
export MANIFEST_URL="https://github.com/seL4/sel4webserver-manifest.git"
checkout-manifest.sh

fetch-branches.sh
echo "::endgroup::"

# GitHub sets its own home dir, but we want the caches set up in /root
export HOME=/root
. /root/.bashrc

# start test
python3 /builds/build.py
