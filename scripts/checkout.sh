#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# Clones target repo (of push or pull request) into current directory

: ${REPO_URL:="https://github.com/${GITHUB_REPOSITORY}.git"}
: ${DEPTH:=1}

echo "Cloning ${REPO_URL}@${GITHUB_REF}"
echo ${GITHUB_SHA}
git clone -q --no-tags --depth ${DEPTH} -b ${GITHUB_REF} ${REPO_URL} .
