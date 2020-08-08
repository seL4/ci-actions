#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetches the pull request in ${GITHUB_REF} into a repo manifest checkout

# Assumes a repo manifest checkout, and current working dir in the repo
# to fetch the PR for.

PR_URL="https://github.com/${GITHUB_REPOSITORY}.git"

echo "Fetching ${GITHUB_BASE_REF} from ${PR_URL}"
git fetch -q --depth 1 ${PR_URL} ${GITHUB_BASE_REF}
git checkout -q ${GITHUB_BASE_REF}

echo "Fetching ${GITHUB_REF} from ${PR_URL}"

# make a hopefully locally unique branch name
BRANCH="pull-requests/${GITHUB_SHA}"

# This assumes that the PR is made to a branch compatible with
# the repo manifest.
git checkout -q -b ${BRANCH}

# Pull in PR changes:
git pull -q --no-tags "${PR_URL}" ${GITHUB_REF}
