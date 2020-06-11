#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Clones target repo (of push or pull request) into current directory

: ${REPO_URL:="https://github.com/${GITHUB_REPOSITORY}.git"}
: ${DEPTH:=1}

echo "Cloning ${REPO_URL}@${GITHUB_REF}"
git init -q .
git remote add origin ${REPO_URL}
git fetch -q --no-tags --depth ${DEPTH} origin +${GITHUB_REF}:refs/heads/test-revision
git checkout -q test-revision
