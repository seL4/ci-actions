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

# FIXME: factor this out into scripts/ and/or reuse code from there
# additional setup if we're running in an GitHub action:
if [ -n "${GITHUB_ACTIONS}" ]
then
  # GitHub generates refs of the form "refs/pull/<n>/merge", which are not
  # cloned by default. We make a branch locally, so that they are later
  # included in the test script clones

  PR_URL="https://github.com/${GITHUB_REPOSITORY}.git"
  echo "Fetching ${TEST_REF} from ${PR_URL}"

  # make a hopefully locally unique branch name
  BRANCH="pull-requests/${GITHUB_SHA}"

  # This assumes that the PR is made to a branch compatible with
  # the repo manifest.
  git -C ${SEL4_REPO} checkout -q -b ${BRANCH}

  # Pull in PR changes:
  # ${TEST_REF} will exist in the repository the PR was made to, even
  # if the PR comes from a forked repository.
  # The PR base repository may be different from the manifest base.
  git -C ${SEL4_REPO} pull -q --no-tags "${PR_URL}" ${TEST_REF}

  # Use sha from here
  TEST_REF=$(git -C ${SEL4_REPO} rev-parse HEAD)

  # restore previous state
  git -C ${SEL4_REPO} checkout -q ${MANIFEST_REV}
fi

# provide precompiled c-parser
cp -r /c-parser "${REPOS}/l4v/tools/"
echo "::endgroup::"

# start test
test_munge.sh -ac -p "${REPOS}" $MANIFEST_REV $TEST_REF
