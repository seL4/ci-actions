#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

[ -z "${GITHUB_BASE_REF}" ] \
  && (echo "Action only works on pull requests."; exit 1)

echo "::group::Setting up"

. ${SCRIPTS}/fetch-sel4-tools.sh

checkout.sh
# fetch pull request base if PR
[ -n "${GITHUB_BASE_REF}" ] && fetch-base.sh

echo "::endgroup::"

echo
echo "Checking the following files:"
echo "$(git diff --name-only ${GITHUB_BASE_REF} test-revision)"
echo
git diff -z --name-only ${GITHUB_BASE_REF} test-revision | xargs -0 \
  ${SEL4_TOOLS}/misc/is-valid-shell-script && echo "Check successful!"
