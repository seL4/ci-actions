#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetches the branch in ${GITHUB_REF} into a repo manifest checkout

# Assumes a repo manifest checkout, and current working dir in the repo
# to fetch the branch for.

URL="https://github.com/${GITHUB_REPOSITORY}.git"

echo "Fetching ${GITHUB_REF} from ${URL}"
git fetch -q --depth 1 ${URL} ${GITHUB_REF}:${GITHUB_REF}
git checkout -q ${GITHUB_REF}
