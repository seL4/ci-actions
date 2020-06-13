#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
install-python.sh

echo "Installing seL4 python deps"
pip install -q sel4-deps

echo "Installing astyle"
sudo apt-get install -qq astyle > /dev/null

. ${SCRIPTS}/fetch-sel4-tools.sh

checkout.sh
# fetch pull request base if PR
[ -n "${GITHUB_BASE_REF}" ] && fetch-base.sh

echo "::endgroup::"

echo
if [ -n "${GITHUB_BASE_REF}" ]
then
  # running in a pull request
  echo "Checking the following files:"
  echo "$(git diff --name-only ${GITHUB_BASE_REF} test-revision)"
  echo
  git diff -z --name-only ${GITHUB_BASE_REF} test-revision | xargs -0 \
    ${SEL4_TOOLS}/misc/style.sh
else
  # not running in pull request
  ${SEL4_TOOLS}/misc/style-all.sh
fi

[ -z "$(git status -uno --porcelain)" ] \
  && echo "Check successful!" \
  || (git diff; exit 1)
