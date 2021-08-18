#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Checks out the verification repo manifest in current directory

set -e

: ${MANIFEST_URL:="https://github.com/seL4/verification-manifest.git"}
: ${REPO_DEPTH:=1}
: ${REPO_BRANCH:="master"}
: ${REPO_MANIFEST:="devel.xml"}

: ${REPO:="repo"}

# repo expects git to be set up; provide defaults if they don't exist
git config user.name > /dev/null || \
  git config --global user.name "repo"
git config user.email > /dev/null || \
  git config --global user.email "repo@no.mail"
git config color.ui > /dev/null || \
  git config --global color.ui false

echo "Starting repo checkout on branch ${REPO_BRANCH} with manifest ${REPO_MANIFEST}:"

if [ "${REPO_DEPTH}" -eq "0" ]
then
  DEPTH=""
else
  DEPTH="--depth=${REPO_DEPTH}"
fi

$REPO init ${DEPTH} -m ${REPO_MANIFEST} -b ${REPO_BRANCH} -u "${MANIFEST_URL}"

# if explicit manifest is provided via input XML, switch to that instead
if [ -n "${INPUT_XML}" ]
then
  TEST_XML="the-test.xml"
  echo "${INPUT_XML}" > ".repo/manifests/${TEST_XML}"
  $REPO init ${DEPTH} -m "${TEST_XML}"
fi

$REPO sync -j 4
