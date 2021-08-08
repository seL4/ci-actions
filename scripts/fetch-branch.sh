#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetches the branch in ${GITHUB_REF} into a repo manifest checkout

# Assumes a repo manifest checkout, and current working dir in the repo
# to fetch the branch for.

URL="https://github.com/${GITHUB_REPOSITORY}.git"

# if an explicit SHA is set as INPUT (e.g. for pull request target), prefer that over GITHUB_REF
if [ -n "${INPUT_SHA}" ]
then
  REF=${INPUT_SHA}
else
  REF=${GITHUB_REF}
fi

echo "Fetching ${REF} from ${URL}"
git fetch -q --depth 1 ${URL} ${REF}:${REF}
git checkout -q ${REF}
