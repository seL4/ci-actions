#!/bin/bash
#
# Copyright 2021, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PATH="$DIR/../scripts":~/.local/bin:$PATH

[ -z ${GITHUB_BASE_REF+x} ] && (echo "Action only works on pull requests"; exit 1)

echo "::group::Setting up"
install-python.sh

checkout.sh
# fetch pull request base
fetch-base.sh
echo "::endgroup::"

if [ -z "$INPUT_DISABLE" ]
then
  DISABLE=""
else
  DISABLE="--disable $INPUT_DISABLE"
fi

echo
echo "Checking the following files:"
echo "$(git diff --name-only ${GITHUB_BASE_REF} test-revision)"
echo
git diff -z --name-only ${GITHUB_BASE_REF} test-revision | xargs -0 \
  "$DIR/thylint.py" $DISABLE --json --diff-only ${GITHUB_BASE_REF}..test-revision
