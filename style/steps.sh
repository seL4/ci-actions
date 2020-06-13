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
[ ! -z ${GITHUB_BASE_REF+x} ] && fetch-base.sh

echo "::endgroup::"

STYLE="${SEL4_TOOLS}/misc/style.sh"

echo
if [ -z ${GITHUB_BASE_REF+x} ]
then
  # not running in pull request
  ${STYLE} .
else
  # running in a pull request
  echo "Checking the following files:"
  echo "$(git diff --name-only ${GITHUB_BASE_REF} test-revision)"
  echo
  git diff -z --name-only ${GITHUB_BASE_REF} test-revision | xargs -0 ${STYLE}
fi

[ -z "$(git status -uno --porcelain)" ] \
  && echo "Check successful!" \
  || (git diff; exit 1)
