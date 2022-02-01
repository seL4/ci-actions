#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Fetches the branch in ${GITHUB_REF} into a repo manifest checkout.
# Does nothing if INPUT_XML is set, because that means we have already done this.

if [ -z "${INPUT_XML}" ]
then

  # Assumes a repo manifest checkout, and current working dir in the repo
  # to fetch the branch for.

  REPO_PATH="github.com/${GITHUB_REPOSITORY}.git"

  if [ -n "${INPUT_TOKEN}" ]
  then
    URL="https://${INPUT_TOKEN}@${REPO_PATH}"
    REPO_PATH="token@${REPO_PATH}"
  else
    URL="https://${REPO_PATH}"
  fi

  # if an explicit SHA is set as INPUT (e.g. for pull request target), prefer that over GITHUB_REF
  if [ -n "${INPUT_SHA}" ]
  then
    REF=${INPUT_SHA}
    FETCH=${REF}
  else
    REF=${GITHUB_REF}
    FETCH=${REF}:${REF}
  fi

  echo "Fetching ${REF} from ${REPO_PATH}"
  git fetch -q --depth 1 ${URL} ${FETCH}
  git checkout -q ${REF}
  if [ -n "${BRANCH_NAME}" ]
  then
    git checkout -b "${BRANCH_NAME}"
  fi
fi
