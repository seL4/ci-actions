#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
checkout-manifest.sh

cd seL4/

PR_URL="https://github.com/${GITHUB_REPOSITORY}.git"
echo "Fetching ${GITHUB_REF} from ${PR_URL}"

# make a hopefully locally unique branch name
BRANCH="pull-requests/${GITHUB_SHA}"

# This assumes that the PR is made to a branch compatible with
# the repo manifest.
git checkout -q -b ${BRANCH}

# Pull in PR changes:
git pull -q --no-tags "${PR_URL}" ${GITHUB_REF}
cd ..

echo "::endgroup::"

export L4V_ARCH=${INPUT_L4V_ARCH}

cd l4v
./run_tests -v ${INPUT_SESSION}
