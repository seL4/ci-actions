#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

echo "::group::Setting up"
# Use a pinned static astyle binary
ASTYLE_URL=https://github.com/seL4/ci-actions/releases/download/astyle-3.1/astyle-linux-x86_64
ASTYLE_SHA256=1209feea9864407e61cec6646c052d3c9c674076fadd8e5096080dd64e7b36b9

echo "Installing astyle 3.1"
ASTYLE_TMP=$(mktemp -d)
curl -sSfL --retry 3 -o "${ASTYLE_TMP}/astyle" "${ASTYLE_URL}"
echo "${ASTYLE_SHA256}  ${ASTYLE_TMP}/astyle" | sha256sum -c --quiet -
sudo install -m 755 "${ASTYLE_TMP}/astyle" /usr/local/bin/astyle
rm -rf "${ASTYLE_TMP}"

install-python.sh

echo "Installing seL4 python deps"
. ${SCRIPTS}/setup-python-venv.sh
pip3 install -q sel4-deps

. ${SCRIPTS}/fetch-sel4-tools.sh

checkout.sh
# fetch pull request base if PR
[ -n "${GITHUB_BASE_REF}" ] && fetch-base.sh

# make sure the pinned astyle is the one the style scripts will pick up
if [ "$(command -v astyle)" != /usr/local/bin/astyle ]
then
  echo "::error::Expected astyle in /usr/local/bin, found $(command -v astyle)"
  exit 1
fi
astyle --version
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
  echo "$(git diff --name-only --diff-filter=rd ${BASE} test-revision)"
  echo
  git diff -z --name-only --diff-filter=rd ${BASE} test-revision | xargs -0 \
    ${SEL4_TOOLS}/misc/style.sh
else
  # check everything
  ${SEL4_TOOLS}/misc/style-all.sh .
fi

[ -z "$(git status -uno --porcelain)" ] \
  && echo "Check successful!" \
  || (git diff; exit 1)
