#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

set -e

[ -z ${GITHUB_BASE_REF+x} ] && (echo "Action only works on pull requests"; exit 1)

echo "::group::Setting up"
checkout.sh
fetch-base.sh
echo "::endgroup::"

echo "Checking for trailing whitespace and conflict markers"
git diff --check ${GITHUB_BASE_REF} && echo "Check successful!"
