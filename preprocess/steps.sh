#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Docker entrypoint for seL4 preprocess test

set -e

# required parameters:
TEST_REF="${GITHUB_REF}"
export L4V_ARCH="${INPUT_L4V_ARCH}"

# actions:
echo "::group::Setting up"
checkout-manifest.sh

REPOS="$(pwd)"
SEL4_REPO="${REPOS}/seL4"
MANIFEST_REV=$(git -C ${SEL4_REPO} rev-parse HEAD)

# additional setup if we're running in an GitHub action:
if [ -n "${GITHUB_ACTIONS}" ]
then
  cd seL4
  fetch-pr.sh

  # Use sha from here
  TEST_REF=$(git rev-parse HEAD)

  # restore previous state
  git checkout -q ${MANIFEST_REV}
  cd ..
fi

# provide precompiled c-parser
cp -r /c-parser "${REPOS}/l4v/tools/"
echo "::endgroup::"

# start test
test_munge.sh -ac -p "${REPOS}" $MANIFEST_REV $TEST_REF
