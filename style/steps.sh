#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
install-python.sh

echo "Installing seL4 python deps"
pip3 install -q sel4-deps

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
  # on pull request: check against BASE_REF
  BASE=${GITHUB_BASE_REF}
else
  # on push: check against BASE if requested
  if [ -n "${INPUT_DIFF_ONLY}" ] && [ "${GITHUB_EVENT_NAME}" = "push" ]
  then
    BASE=$(jq -r ".before" "${GITHUB_EVENT_PATH}")
    echo "On push, base is ${BASE}, fetching history."
    git fetch -q --no-tags --unshallow
    echo "done"
  fi
fi

if [ -n "${BASE}" ]
then
  # comparing against BASE
  echo "Checking the following files:"
  echo "$(git diff --name-only ${BASE} test-revision)"
  echo
  git diff -z --name-only ${BASE} test-revision | xargs -0 \
    ${SEL4_TOOLS}/misc/style.sh
else
  # check everything
  ${SEL4_TOOLS}/misc/style-all.sh .
fi

[ -z "$(git status -uno --porcelain)" ] \
  && echo "Check successful!" \
  || (git diff; exit 1)
