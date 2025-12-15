#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for seL4 preprocess test

set -e

# required parameters:
export L4V_ARCH="${INPUT_L4V_ARCH}"
export L4V_FEATURES="${INPUT_L4V_FEATURES}"

# actions:
echo "::group::Setting up"
checkout-manifest.sh

REPOS="$(pwd)"
SEL4_REPO="${REPOS}/seL4"
MANIFEST_REV=$(git -C ${SEL4_REPO} rev-parse HEAD)

cd "${SEL4_REPO}"
export BRANCH_NAME="github-ci-work/pr-branch"
fetch-branch.sh

# Use sha from here
TEST_REF=$(git rev-parse HEAD)

# restore previous state
git checkout -q ${MANIFEST_REV}
cd - > /dev/null

repo-util hashes

# provide precompiled c-parser
cp -r /c-parser "${REPOS}/l4v/tools/"
echo "::endgroup::"

# one test for the default L4V_ARCH/L4V_FEATURES combination
test_munge.sh -ac -p "${REPOS}" $MANIFEST_REV $TEST_REF

# then all platform combinations if any exist

# find all L4V_PLAT for the provided L4V_ARCH/L4V_FEATURES combination in
# seL4/configs/ and store them in the array CONFIGS
FEAT="${L4V_FEATURES:+${L4V_FEATURES}_}"

shopt -s nullglob
cd "${SEL4_REPO}/configs/"
CONFIGS=$(echo ${L4V_ARCH}_${FEAT}[a-z0-9]*_verified.cmake)
cd - > /dev/null

for CONFIG in ${CONFIGS}; do
  L4V_PLAT=${CONFIG##${L4V_ARCH}_${FEAT}}
  export L4V_PLAT=${L4V_PLAT%_verified.cmake}
  test_munge.sh -ac -p "${REPOS}" $MANIFEST_REV $TEST_REF
done
