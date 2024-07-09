#!/bin/sh
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Clones target repo (of push or pull request) into current directory

: ${REPO_PATH:="github.com/${GITHUB_REPOSITORY}.git"}
: ${DEPTH:=1}

if [ -n "${INPUT_TOKEN}" ]
then
  REPO_URL="https://${INPUT_TOKEN}@${REPO_PATH}"
  REPO_PATH="token@${REPO_PATH}"
else
  REPO_URL="https://${REPO_PATH}"
fi

# if an explicit PR number is set as INPUT (e.g. for pull_request_target), prefer that
if [ -n "${INPUT_PR_NUM}" ]
then
  REF="refs/pull/${INPUT_PR_NUM}/head"
else
  REF="${GITHUB_REF}"
fi

echo "Cloning ${REPO_PATH}@${REF}"
git init -q .
git remote add origin ${REPO_URL}
git fetch -q --no-tags --depth ${DEPTH} origin +${REF}:refs/heads/test-revision
git checkout -q test-revision
